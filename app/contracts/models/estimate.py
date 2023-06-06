from django.db import models

from .contract import Contract
from .employee import Employee
from .material import Material
from .supplier import Supplier


class Estimate(models.Model):
    created_at = models.DateTimeField(verbose_name='Дата и Время поставки')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    employee = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name='estimates',
        verbose_name='Специалист по закупкам',
    )
    supplier = models.ForeignKey(
        to=Supplier, 
        on_delete=models.CASCADE, 
        related_name='estimates',
        verbose_name='Поставщик',
    )

    materials = models.ManyToManyField(
        to=Material, 
        through='EstimateMaterial',
        related_name='estimates'
    )

    def __str__(self):
        return f'Накладная №{str(self.id)}'
    
    def total_price(self):
        total = self.estimatematerial_set.aggregate(
            total_price=models.Sum(models.F('quantity') * models.F('material__price'))
        )
        if total['total_price']:
            return total['total_price']
        return 0

    class Meta:
        verbose_name = 'Накладная'
        verbose_name_plural = 'Накладные'


class EstimateMaterial(models.Model):

    estimate = models.ForeignKey(
        to=Estimate,
        on_delete=models.CASCADE,
        verbose_name='Накладная'
    )
    material = models.ForeignKey(
        to=Material,
        on_delete=models.CASCADE,
        verbose_name='Материал'
    )

    quantity = models.IntegerField(
        verbose_name='Количество'
    )

    def __str__(self):
        return ''
