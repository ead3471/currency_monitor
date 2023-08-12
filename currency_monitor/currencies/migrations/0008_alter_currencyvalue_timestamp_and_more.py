# Generated by Django 4.2.4 on 2023-08-11 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0007_alter_currencyvalue_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyvalue',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Currency last update'),
        ),
        migrations.AlterField(
            model_name='historicalcurrencyvalue',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Currency last update'),
        ),
    ]
