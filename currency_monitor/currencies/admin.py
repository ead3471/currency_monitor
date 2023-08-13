from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import CurrencyValue


@admin.register(CurrencyValue)
class CurrencyValueAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in CurrencyValue._meta.get_fields()]
