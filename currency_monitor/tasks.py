from celery.schedules import crontab
import os
from dotenv import load_dotenv

from currencies.core import get_current_currency_values

# from currency_monitor.celery import app
from celery import shared_task
import logging


from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "currency_monitor.settings")

# app = Celery("currency_monitor")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()


load_dotenv()


logger = logging.getLogger(__name__)

SCAN_RATES_PERIOD = os.getenv("SCAN_RATES_PERIOD")


SET_RETRIEVER_STATE_TASK_NAME = "set_retriever_state"

RETRIEVER_TASK_NAME = "coins_info_retriever"
# DEFAULT_SCHEDULE_CONFIG = {
#     "RETRIEVE_DATA": {
#         "task": RETRIEVER_TASK_NAME,
#         "schedule": crontab(minute=f"*/{SCAN_RATES_PERIOD}"),
#     },
# }


# app.conf.beat_schedule = DEFAULT_SCHEDULE_CONFIG
# app.conf.broker_url = "redis://redis:6379/0"


@shared_task
def retrieve_data():
    from currencies.models import CurrencyValue

    logger.info("Start retrieving data task")
    coins_for_scan = {
        coin.code: coin
        for coin in CurrencyValue.objects.filter(is_scan_on=True).all()
    }

    logger.info(f"Found {len(coins_for_scan)} coins marked for retrieve data")

    recieved_coins_rates = get_current_currency_values(coins_for_scan)

    for coin_rate in recieved_coins_rates:
        if coin_rate.code in coins_for_scan:
            coin = coins_for_scan[coin_rate.code]
            coin.rate = coin_rate.rate
            coin.timestamp = coin_rate.timestamp
            coin.save()
    logger.info("Task ended")
