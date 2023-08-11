from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv
from currencies.models import CurrencyValue
from currencies.core import get_current_currency_values


load_dotenv()

SCAN_RATES_PERIOD = os.getenv("SCAN_RATES_PERIOD")


app = Celery("coins_retriever")
app.conf.beat_schedule = {
    "task-name": {
        "task": "coins_retriever",
        "schedule": crontab(minute=f"*/{SCAN_RATES_PERIOD}"),
    },
}


app.conf.broker_url = "redis://redis:6379/0"


@app.task(name="coins_retriever")
def test_task():
    coins_for_scan = {
        coin.code: coin
        for coin in CurrencyValue.objects.filter(is_scan_on=True).all()
    }

    recieved_coins_rates = get_current_currency_values(coins_for_scan)

    for coin_rate in recieved_coins_rates:
        if coin_rate.code in coins_for_scan:
            coin = coins_for_scan[coin_rate.code]
            coin.rate = coin_rate.rate
            coin.timestamp = coin_rate.timestamp
            coin.save()
