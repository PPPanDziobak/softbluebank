# Generated by Django 4.2.2 on 2023-06-21 17:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankaccount', '0004_alter_accountmodel_account_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountmodel',
            name='account_number',
            field=models.CharField(default='6858761732', max_length=10, unique=True, verbose_name='Numer konta'),
        ),
        migrations.AlterField(
            model_name='creditcardmodel',
            name='cvc_number',
            field=models.CharField(default='939', max_length=3, verbose_name='Numer CVC'),
        ),
        migrations.AlterField(
            model_name='creditcardmodel',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2028, 6, 19, 17, 56, 47, 964907), verbose_name='Data ważności'),
        ),
        migrations.AlterField(
            model_name='creditcardmodel',
            name='pin_number',
            field=models.CharField(default='1923', max_length=4, verbose_name='Kod PIN'),
        ),
    ]