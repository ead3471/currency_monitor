from django.db import models
from simple_history.models import HistoricalRecords
from django.db.models import CharField, DecimalField


class CurrencyValue(models.Model):
    name = CharField(max_length=10, unique=True)
    code = CharField(max_length=3, unique=True)
    rate = DecimalField(max_digits=15, decimal_places=6)

    history = HistoricalRecords(excluded_fields=['name', 'code'])
