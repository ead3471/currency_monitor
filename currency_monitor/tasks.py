from celery.schedules import crontab
import os
from dotenv import load_dotenv
from currencies.models import CurrencyValue
from currencies.core import get_current_currency_values
from currency_monitor.celery import app


load_dotenv()

import logging

logger = logging.getLogger(__name__)

SCAN_RATES_PERIOD = os.getenv("SCAN_RATES_PERIOD")

RETRIEVER_TASK_NAME = "coins_info_retriever"
SET_RETRIEVER_STATE_TASK_NAME = "set_retriever_state"

DEFAULT_SCHEDULE_CONFIG = {
    "RETRIEVE_DATA": {
        "task": RETRIEVER_TASK_NAME,
        "schedule": crontab(minute=f"*/{SCAN_RATES_PERIOD}"),
    },
}


app.conf.beat_schedule = DEFAULT_SCHEDULE_CONFIG


app.conf.broker_url = "redis://redis:6379/0"


@app.task(name=RETRIEVER_TASK_NAME)
def retrieve_data():
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


@app.task(name=SET_RETRIEVER_STATE_TASK_NAME)
def set_retriever_state(enable: bool = True):
    if enable:
        logger.info(f"Enable task RETRIEVE_DATA")
        app.conf.beat_schedule["RETRIEVE_DATA"] = DEFAULT_SCHEDULE_CONFIG
    else:
        if "RETRIEVE_DATA" in app.conf.beat_schedule:
            logger.info(f"Disable task RETRIEVE_DATA")
            del app.conf.beat_schedule["RETRIEVE_DATA"]
    logger.info("Current beat_schedule configuration:")
    logger.info(app.conf.beat_schedule)
