from django.db import models


class Supplier(models.Model):

    name = models.CharField(max_length=255, verbose_name='Наименование')
    email = models.CharField(max_length=255, verbose_name='Email')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone_number = models.CharField(max_length=255, verbose_name='Номер телефона')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'