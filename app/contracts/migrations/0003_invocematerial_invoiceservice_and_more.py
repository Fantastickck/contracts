# Generated by Django 4.2.1 on 2023-05-20 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_alter_contract_client_alter_contract_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoceMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость за одну')),
                ('quantity', models.IntegerField(verbose_name='Количество')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contracts.invoice', verbose_name='Контракт')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contracts.material', verbose_name='Материал')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость за одну')),
                ('quantity', models.IntegerField(verbose_name='Количество')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contracts.invoice', verbose_name='Контракт')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contracts.service', verbose_name='Услуга')),
            ],
        ),
        migrations.RemoveField(
            model_name='contractservice',
            name='contract',
        ),
        migrations.RemoveField(
            model_name='contractservice',
            name='service',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='materials',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='services',
        ),
        migrations.DeleteModel(
            name='ContractMaterial',
        ),
        migrations.DeleteModel(
            name='ContractService',
        ),
        migrations.AddField(
            model_name='invoice',
            name='materials',
            field=models.ManyToManyField(related_name='contracts', through='contracts.InvoceMaterial', to='contracts.material'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='services',
            field=models.ManyToManyField(related_name='contracts', through='contracts.InvoiceService', to='contracts.service'),
        ),
    ]
