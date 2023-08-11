from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "currency_monitor.settings")

app = Celery("currency_monitor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
