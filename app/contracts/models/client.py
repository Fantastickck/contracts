from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    middle_name = models.CharField(max_length=255, verbose_name='Отчество')
    phone_number = models.CharField(max_length=11, verbose_name='Номер телефона')
    email = models.CharField(max_length=255, verbose_name='Email')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return self.name
    
    @property
    def total_contracts_price(self):
        total_price = 0
        for contract in self.contracts.all():
            total_price += contract.total_invoice_price()
        return total_price

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
