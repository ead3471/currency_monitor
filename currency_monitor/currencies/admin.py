from django.contrib import admin
from .models import CurrencyValue
from simple_history.admin import SimpleHistoryAdmin


@admin.register(CurrencyValue)
class CurrencyValueAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in CurrencyValue._meta.get_fields()]
