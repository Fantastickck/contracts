# Generated by Django 4.2.1 on 2023-05-29 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0006_alter_estimate_options_remove_estimate_contract_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='estimate',
            old_name='user',
            new_name='employee',
        ),
    ]