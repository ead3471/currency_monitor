from django.db import models
from simple_history.models import HistoricalRecords
from django.db.models import (
    CharField,
    DecimalField,
    DateTimeField,
    BooleanField,
)


class CurrencyValue(models.Model):
    name = CharField(max_length=10, verbose_name="Currency name", null=True)
    code = CharField(
        max_length=3, unique=True, verbose_name="Currency short code"
    )
    rate = DecimalField(
        max_digits=15, decimal_places=6, verbose_name="Currency rate to USD"
    )
    timestamp = DateTimeField(verbose_name="Currency last update")
    is_scan_on = BooleanField(
        default=False, verbose_name="Currency scan is on"
    )

    history = HistoricalRecords(
        cascade_delete_history=True, excluded_fields=["name", "code"]
    )
