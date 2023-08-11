from django.contrib import admin
from django_celery_beat.models import PeriodicTask, IntervalSchedule


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ("name", "task", "enabled")


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(admin.ModelAdmin):
    list_display = ("every", "period")
