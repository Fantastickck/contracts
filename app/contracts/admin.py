import csv
from urllib import parse
from datetime import datetime

from django import forms
from django.db import models
from django.contrib import admin, messages
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.http.response import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django_object_actions import DjangoObjectActions, action
from nested_admin.nested import NestedTabularInline, NestedModelAdmin
from rangefilter.filters import DateRangeFilterBuilder

from contracts.models import (
    Client,
    Contract,
    MeasureType,
    Material,
    Service,
    Supplier,
    Employee,
    Estimate,
    EstimateMaterial,
    Position,
    Invoice,
    InvoiceMaterial,
    InvoiceService,
)


admin.site.site_title = "Учет контрактов"
admin.site.site_header = "Учет контрактов"
admin.site.index_title = "Информационная система для учета контрактов"


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.register(Employee)
class AdminEmployee(admin.ModelAdmin):
    list_display = (
        "id",
        "last_name",
        "first_name",
        "middle_name",
        "gender",
        "position",
        "phone_number",
        "email",
        "date_of_birth",
        "date_of_hiring",
        "photo_show",
    )
    search_fields = ("last_name", "middle_name", "first_name", "phone_number", "email")
    list_filter = (
        ("position__name", custom_titled_filter(title="Должность")),
        ("date_of_birth", DateRangeFilterBuilder()),
        ("date_of_hiring", DateRangeFilterBuilder()),
    )

    readonly_fields = ("photo_show",)

    def email(self, obj: Employee):
        if obj.user:
            return obj.user.email
        return ""

    def photo_show(self, obj: Employee):
        if obj.photo:
            return mark_safe("<img src='{}' width='80' />".format(obj.photo.url))
        return None

    photo_show.short_description = "Фото"


class InvoicePositionMaterialForm(forms.ModelForm):
    material = forms.ModelChoiceField(Material.objects.all())
    unit_price = forms.DecimalField(max_digits=10, decimal_places=2, label='Стоимость за штуку, руб')
    quantity = forms.IntegerField()


class InvoicePositionMaterialInline(NestedTabularInline):
    model = InvoiceMaterial
    can_delete = True
    readonly_fields = ("price", "measure_type")
    extra = 0
    form = InvoicePositionMaterialForm
    verbose_name = "Материал"
    verbose_name_plural = "Материалы"

    def measure_type(self, obj: InvoiceMaterial):
        return obj.material.measure_type

    def price(self, obj: InvoiceMaterial):
        if obj.pk is not None:
            return obj.quantity * obj.unit_price
        return ""

    price.short_description = "Стоимость позиции, руб"
    measure_type.short_description = "Единицы измерения"


class InvoicePositionServiceForm(forms.ModelForm):
    service = forms.ModelChoiceField(Service.objects.all())
    unit_price = forms.DecimalField(max_digits=10, decimal_places=2, label='Стоимость за одну, руб')
    quantity = forms.IntegerField()

class InvoicePositionServiceInline(NestedTabularInline):
    model = InvoiceService
    form = InvoicePositionServiceForm
    can_delete = True
    readonly_fields = ("price",)
    extra = 0

    def price(self, obj: InvoiceMaterial):
        if obj.pk is not None:
            return obj.quantity * obj.unit_price
        return ""

    price.short_description = "Стоимость позиции, руб"


def truncated_desc(obj):
    name = "%s" % obj.name
    return Truncator(name).chars(20)


class InvoiceInline(NestedTabularInline):
    model = Invoice
    can_delete = True
    show_change_link = True
    readonly_fields = (
        "total_price_materials",
        "total_price_services",
        "total_price",
    )
    extra = 0
    inlines = [InvoicePositionMaterialInline, InvoicePositionServiceInline]

    def total_price_materials(self, obj: Invoice):
        total_price_materials = InvoiceMaterial.objects.filter(invoice=obj).aggregate(
            price=models.Sum(models.F("unit_price") * models.F("quantity"))
        )
        if total_price_materials["price"]:
            return total_price_materials["price"]
        return 0

    def total_price_services(self, obj: Invoice):
        total_price_services = InvoiceService.objects.filter(invoice=obj).aggregate(
            price=models.Sum(models.F("unit_price") * models.F("quantity"))
        )
        if total_price_services["price"] is not None:
            return total_price_services["price"]
        return 0

    def total_price(self, obj: Invoice):
        total_price_materials = InvoiceMaterial.objects.filter(invoice=obj).aggregate(
            price=models.Sum(models.F("unit_price") * models.F("quantity"))
        )
        total_price_services = InvoiceService.objects.filter(invoice=obj).aggregate(
            price=models.Sum(models.F("unit_price") * models.F("quantity"))
        )
        total_price = 0
        if total_price_services["price"]:
            total_price += total_price_services["price"]
        if total_price_materials["price"]:
            total_price += total_price_materials["price"]
        return total_price

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = Employee.objects.filter(
                position__name="Начальник отдела производства"
            ).select_related("position")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    total_price_materials.short_description = "Стоимость материалов, руб"
    total_price_services.short_description = "Стоимость услуг, руб"
    total_price.short_description = "Общая стоимость, руб"


@admin.register(Contract)
class AdminContract(DjangoObjectActions, NestedModelAdmin):
    list_display = (
        "id",
        "client",
        "manager",
        "signed_at",
        "executed_at",
        "total_invoices_price",
    )
    inlines = [InvoiceInline]
    list_filter = (("signed_at", DateRangeFilterBuilder()),)
    search_fields = ("client__name",)
    ordering = ("id",)

    actions = ("export_as_csv",)
    change_actions = ("export_invoices_as_html",)
    changelist_actions = ("export_contracts_as_html",)

    class Media:
        css = {
            "all": ("css/red_star.css",)
        }

    def total_invoices_price(self, obj: Contract):
        invoices_ids = Invoice.objects.values("id").filter(contract=obj)
        total_price_materials = InvoiceMaterial.objects.filter(
            invoice__id__in=invoices_ids
        ).aggregate(price=models.Sum(models.F("unit_price") * models.F("quantity")))
        total_price_services = InvoiceService.objects.filter(
            invoice__id__in=invoices_ids
        ).aggregate(price=models.Sum(models.F("unit_price") * models.F("quantity")))
        total_invoices_price = 0
        if total_price_materials["price"]:
            total_invoices_price += total_price_materials["price"]
        if total_price_services["price"]:
            total_invoices_price += total_price_services["price"]
        return total_invoices_price

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    @action(label="Отчет по контрактам в HTML", attrs={"target": "_blank"})
    def export_contracts_as_html(self, request, queryset):
        queryset = queryset.order_by("id")
        context = {"objects": queryset}

        if "_changelist_filters" in request.GET:
            filter_dict = parse.parse_qs(
                parse.urlsplit("?" + request.GET.get("_changelist_filters")).query
            )
            filter_dict = {key: value[0] for key, value in filter_dict.items()}
            if 'signed_at__range__gte' in filter_dict:
                signed_at_gte = datetime.strptime(
                    filter_dict["signed_at__range__gte"], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
                queryset = queryset.filter(
                    signed_at__gte=signed_at_gte
                )
                context["signed_at_start"] = signed_at_gte
            if 'signed_at__range__lte' in filter_dict:
                signed_at_lte = datetime.strptime(
                    filter_dict["signed_at__range__lte"], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
                queryset = queryset.filter(
                    signed_at__lte=signed_at_lte
                )
                context["signed_at_end"] = signed_at_lte

            context["objects"] = queryset
        total_price = 0
        for contract in queryset:
            total_price += contract.total_invoice_price()
        context['total_price'] = total_price
        return render(request, "contracts/contracts_html_report.html", context)

    @action(label="Сметы в HTML", attrs={"target": "_blank"})
    def export_invoices_as_html(self, request, contract: Contract):
        invoices = Invoice.objects.filter(contract=contract)

        return render(
            request,
            "contracts/invoices_html_report.html",
            {"contract": contract, "invoices": invoices},
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            kwargs["queryset"] = Employee.objects.filter(
                position__name="Менеджер"
            ).select_related("position")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    export_as_csv.short_description = "Выгрузить в формате CSV"
    total_invoices_price.short_description = "Стоимость смет, руб"


@admin.register(Client)
class AdminClient(DjangoObjectActions, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "last_name",
        "first_name",
        "middle_name",
        "email",
        "phone_number",
        "address",
    )
    search_fiels = ("name", "email")
    changelist_actions = ("export_clients_rating_as_html",)

    @action(label="Отчет по общим стоимостям заключенных контрактов клиентами в HTML", attrs={"target": "_blank"})
    def export_clients_rating_as_html(self, request, queryset):
        queryset = sorted(Client.objects.all(), key=lambda x: -x.total_contracts_price)
        import logging
        logging.warn(queryset)
        return render(
            request,
            "contracts/clients_contracts_html_report.html",
            {"clients": queryset},
        )


@admin.register(Position)
class AdminPosition(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MeasureType)
class AdminMeasureType(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Material)
class AdminMaterial(admin.ModelAdmin):
    list_display = (
        "name",
        "get_price",
        "measure_type",
    )
    search_fields = ("name",)

    def get_price(self, obj):
        return obj.price

    get_price.short_description = 'Стоимость за штуку, руб'


@admin.register(Service)
class AdminService(admin.ModelAdmin):
    list_display = ("name", "get_price")
    search_fields = ("name",)

    def get_price(self, obj):
        return obj.price

    get_price.short_description = 'Стоимость за штуку, руб'


@admin.register(Supplier)
class AdminSupplier(admin.ModelAdmin):
    list_display = ("id", "name", "email", "address", "phone_number")
    search_fields = ("email", "name", "phone_number")


class EstimateMaterialInline(NestedTabularInline):
    model = EstimateMaterial
    can_delete = True
    show_change_link = True
    extra = 0
    readonly_fields = ("measure_type", "unit_price", "total_price")

    verbose_name = "Материал"
    verbose_name_plural = "Материалы"

    def measure_type(self, obj: EstimateMaterial):
        return obj.material.measure_type

    def unit_price(self, obj: EstimateMaterial):
        return f"{obj.material.price} руб"

    def total_price(self, obj: EstimateMaterial):
        return f"{obj.material.price * obj.quantity} руб"

    measure_type.short_description = "Стоимость за единицу, руб"
    unit_price.short_description = "Стоимость за единицу, руб"
    total_price.short_description = "Стоимость позиции, руб"


@admin.register(Estimate)
class AdminEstimate(DjangoObjectActions, NestedModelAdmin):
    list_display = ("id", "created_at", "employee", "supplier", "total_price")
    list_filter = (("created_at", DateRangeFilterBuilder()),)
    readonly_fields = ("total_price",)
    changelist_actions = ("export_estimates_as_html",)

    inlines = [EstimateMaterialInline]

    def total_price(self, obj: Estimate):
        total_price = obj.materials.aggregate(
            total_price=models.Sum(
                models.F("estimatematerial__quantity")
                * models.F("estimatematerial__material__price")
            )
        )["total_price"]
        return total_price
    
    @action(label="Отчет по накладным в HTML", attrs={"target": "_blank"})
    def export_estimates_as_html(self, request, queryset):
        queryset = queryset.order_by("id")
        context = {"objects": queryset}

        if "_changelist_filters" in request.GET:
            filter_dict = parse.parse_qs(
                parse.urlsplit("?" + request.GET.get("_changelist_filters")).query
            )
            filter_dict = {key: value[0] for key, value in filter_dict.items()}
            if 'created_at__range__gte' in filter_dict:
                created_at_gte = datetime.strptime(
                    filter_dict["created_at__range__gte"], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
                queryset = queryset.filter(
                    created_at__gte=created_at_gte
                )
                context["created_at_start"] = created_at_gte
            if 'created_at__range__lte' in filter_dict:
                created_at_lte = datetime.strptime(
                    filter_dict["created_at__range__lte"], "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
                queryset = queryset.filter(
                    created_at__lte=created_at_lte
                )
                context["created_at_end"] = created_at_lte

            context["objects"] = queryset
        total_price = 0
        for estimate in queryset:
            total_price += estimate.total_price()
        context['total_price'] = total_price
        return render(request, "contracts/estimates_html_report.html", context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.filter(
                position__name="Специалист по закупкам"
            ).select_related("position")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    total_price.short_description = "Стоимость материалов, руб"
