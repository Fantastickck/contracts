from django.db import models

from .contract import Contract
from .employee import Employee
from .material import Material


class Estimate(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата составления')
    description = models.TextField(verbose_name='Описание')

    tech_lid = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name='estimates',
        verbose_name='Начальник отдела производства'
    )
    contract = models.ForeignKey(
        to=Contract, 
        on_delete=models.CASCADE, 
        related_name='estimates',
        verbose_name='Контракт'
    )

    materials = models.ManyToManyField(
        to=Material, 
        through='EstimateMaterial',
        related_name='estimates'
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Смета'
        verbose_name_plural = 'Сметы'


class EstimateMaterial(models.Model):

    estimate = models.ForeignKey(
        to=Estimate(),
        on_delete=models.CASCADE,
        verbose_name='Накладная'
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
