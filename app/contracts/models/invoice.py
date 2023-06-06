from django.db import models

from .employee import Employee
from .contract import Contract
from .material import Material
from .service import Service


class Invoice(models.Model):
    created_at = models.DateTimeField(verbose_name="Дата составления")
    description = models.TextField(verbose_name="Описание")

    user = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Составитель",
    )
    contract = models.ForeignKey(
        to=Contract,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Контракт",
    )

    services = models.ManyToManyField(
        to=Service, through="InvoiceService", related_name="invoices"
    )
    materials = models.ManyToManyField(
        to=Material, through="InvoiceMaterial", related_name="invoices"
    )

    def __str__(self):
        return f"Смета №{self.pk}"
    
    def total_price_materials(self):
        total_price = 0
        for material in self.invoicematerial_set.all():
            total_price += material.unit_price * material.quantity
        return total_price 
       
    def total_price_services(self):
        total_price = 0
        for material in self.invoiceservice_set.all():
            total_price += material.unit_price * material.quantity
        return total_price

    def total_price(self):
        return self.total_price_materials() + self.total_price_services()

    class Meta:
        verbose_name = "Смета"
        verbose_name_plural = "Сметы"


class InvoiceService(models.Model):
    invoice = models.ForeignKey(
        to=Invoice, on_delete=models.CASCADE, verbose_name="Контракт"
    )
    service = models.ForeignKey(
        to=Service, on_delete=models.CASCADE, verbose_name="Услуга"
    )

    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Стоимость за одну"
    )
    quantity = models.IntegerField(verbose_name="Количество")

    def __str__(self):
        return f"Позиция №{self.pk}"
    
    def total_price(self):
        return self.quantity * self.unit_price
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class InvoiceMaterial(models.Model):
    invoice = models.ForeignKey(
        to=Invoice, on_delete=models.CASCADE, verbose_name="Контракт"
    )
    material = models.ForeignKey(
        to=Material, on_delete=models.CASCADE, verbose_name="Материал"
    )

    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Стоимость за одну"
    )
    quantity = models.IntegerField(verbose_name="Количество")

    def __str__(self):
        return f"Позиция №{self.pk}"
    
    def total_price(self):
        return self.quantity * self.unit_price
    
    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
