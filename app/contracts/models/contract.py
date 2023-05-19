from django.db import models

from .employee import Employee
from .client import Client
from .service import Service
from .material import Material


class Contract(models.Model):
    signed_at = models.DateField(verbose_name='Дата подписания')
    executed_at = models.DateField(verbose_name='Дата исполнения')
    description = models.TextField(verbose_name='Описание')

    client = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name='Клиент'
    )
    manager = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name='Менеджер'
    )

    services = models.ManyToManyField(
        to=Service,
        through='ContractService',
        related_name='contracts'
    )
    materials = models.ManyToManyField(
        to=Material,
        through='ContractMaterial',
        related_name='contracts'
    )

    def __str__(self):
        return f'{self.client.name} | {self.signed_at}'
    
    class Meta:
        verbose_name = 'Контракт'
        verbose_name_plural = 'Контракты'


class ContractService(models.Model):

    contract = models.ForeignKey(
        to=Contract,
        on_delete=models.CASCADE,
        verbose_name='Контракт'
    )
    service = models.ForeignKey(
        to=Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга'
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость за одну'
    )
    quantity = models.IntegerField(verbose_name='Количество')


class ContractMaterial(models.Model):

    contract = models.ForeignKey(
        to=Contract,
        on_delete=models.CASCADE,
        verbose_name='Контракт'
    )
    material = models.ForeignKey(
        to=Material,
        on_delete=models.CASCADE,
        verbose_name='Материал'
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость за одну'
    )
    quantity = models.IntegerField(verbose_name='Количество')