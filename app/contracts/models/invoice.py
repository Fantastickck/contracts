from django.db import models

from .employee import Employee
from .contract import Contract


class Invoice(models.Model):
    
    created_at = models.DateTimeField(verbose_name='Дата составления')
    description = models.TextField(verbose_name='Описание')

    user = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Составитель'
    )
    contract = models.ForeignKey(
        to=Contract,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Контракт'
    )

    class Meta:
        verbose_name = 'Смета'
        verbose_name_plural = 'Сметы'
