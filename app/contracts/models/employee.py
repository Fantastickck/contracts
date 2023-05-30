from django.db import models
from django.contrib.auth.models import User


class Position(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Employee(models.Model):

    gender_choices = (
        ('male', 'Мужской'),
        ('female', 'Женский')
    )
    
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    gender = models.CharField(choices=gender_choices, verbose_name='Пол')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    phone_number = models.CharField(verbose_name='Номер телефона')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', verbose_name='Фото')
    user = models.OneToOneField(
        to=User, 
        on_delete=models.CASCADE, 
        related_name='employee',
        verbose_name='Пользователь',
        blank=True,
        null=True
    )
    position = models.ForeignKey(
        to=Position,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Должность',
        null=True
    )

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
