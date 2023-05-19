from django.db import models


class MeasureType(models.Model):
    name = models.CharField(max_length=63, verbose_name='Наименование')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Material(models.Model):
    name = models.CharField(
        max_length=255, verbose_name='Наименование')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2, 
        verbose_name='Стоимость за штуку'
    )
    measure_type = models.ForeignKey(
        to=MeasureType,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Единицы измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

