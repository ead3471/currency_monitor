# Generated by Django 4.2.4 on 2023-08-09 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcurrencyvalue',
            name='code',
        ),
        migrations.RemoveField(
            model_name='historicalcurrencyvalue',
            name='name',
        ),
    ]
