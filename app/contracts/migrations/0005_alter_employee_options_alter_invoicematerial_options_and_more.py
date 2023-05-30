# Generated by Django 4.2.1 on 2023-05-29 15:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contracts', '0004_position_rename_invocematerial_invoicematerial_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
        migrations.AlterModelOptions(
            name='invoicematerial',
            options={'verbose_name': 'Материал', 'verbose_name_plural': 'Материалы'},
        ),
        migrations.AlterModelOptions(
            name='invoiceservice',
            options={'verbose_name': 'Услуга', 'verbose_name_plural': 'Услуги'},
        ),
        migrations.AlterField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='materials',
            field=models.ManyToManyField(related_name='invoices', through='contracts.InvoiceMaterial', to='contracts.material'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='services',
            field=models.ManyToManyField(related_name='invoices', through='contracts.InvoiceService', to='contracts.service'),
        ),
    ]
