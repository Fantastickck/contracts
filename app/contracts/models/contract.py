from django.db import models

from .employee import Employee
from .client import Client


class Contract(models.Model):
    signed_at = models.DateField(verbose_name="Дата подписания")
    executed_at = models.DateField(verbose_name="Дата исполнения")
    description = models.TextField(verbose_name="Описание")

    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Клиент",
    )
    manager = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Менеджер",
    )

    def __str__(self):
        return f"{self.client.name} | {self.signed_at}"

    def total_invoice_price(self):
        total_price_materials = self.invoices.aggregate(
            total_price=models.Sum(
                models.F("invoicematerial__unit_price")
                * models.F("invoicematerial__quantity")
            )
        )["total_price"]
        total_price_services = self.invoices.aggregate(
            total_price=models.Sum(
                models.F("invoiceservice__unit_price")
                * models.F("invoiceservice__quantity")
            )
        )["total_price"]
        total_price = 0
        if total_price_materials:
            total_price += total_price_materials
        if total_price_services:
            total_price += total_price_services
        return total_price

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракты"
