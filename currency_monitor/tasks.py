import os
from dotenv import load_dotenv
from datetime import datetime
from django.utils import timezone
from api.core import (
    get_coins_rates,
    get_coin_info,
    get_coins_info,
)

from celery import shared_task
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "currency_monitor.settings")

load_dotenv()


logger = logging.getLogger(__name__)


@shared_task
def retrieve_data():
    from currencies.models import CurrencyValue

    logger.info("Start retrieving data task")
    coins_for_scan = {
        coin.code: coin
        for coin in CurrencyValue.objects.filter(is_scan_on=True).all()
    }

    logger.info(f"Found {len(coins_for_scan)} coins marked for retrieve data")
    if len(coins_for_scan) > 0:
        logger.info(f"Coins list:{coins_for_scan}")
    else:
        logger.info("Skip requesting")
        return

    recieved_coins_rates = get_coins_rates(coins_for_scan)

    for coin_code, coin_rate in recieved_coins_rates.items():
        if coin_code in coins_for_scan:
            coin = coins_for_scan[coin_code]
            coin.rate = coin_rate.rate
            coin.timestamp = datetime.fromtimestamp(
                coin_rate.timestamp,
                tz=timezone.utc,
            )
            coin.save()
    logger.info("Task ended")


@shared_task
def register_coin(coin_code: str, is_scan_on: bool):
    from currencies.models import CurrencyValue

    logger.debug(f" Register {coin_code}, scan enables={is_scan_on}")

    existed_currency = CurrencyValue.objects.filter(code=coin_code).first()
    if existed_currency:
        logger.debug("Currency already exists")
        existed_currency.is_scan_on = is_scan_on
    else:
        coin_info = get_coin_info(coin_code)
        CurrencyValue.objects.create(
            code=coin_code, is_scan_on=is_scan_on, name=coin_info.name
        )


@shared_task
def retrieve_coins_rates(coins_codes: list[str]):
    from currencies.models import CurrencyValue

    logger.debug("Start retrieving coins rates")
    registered_coins_codes = CurrencyValue.objects.values_list(
        "code", flat=True
    )
    missing_coins_codes = set(coins_codes) - set(registered_coins_codes)
    missing_coins_infos = get_coins_info(missing_coins_codes)

    logger.debug(f"{len(missing_coins_codes)} not registerd coins found")
    if len(missing_coins_codes) > 0:
        logger.debug(f"Not registered coins:{missing_coins_codes}")

    coins_rates = get_coins_rates(list(coins_codes))

    for code in set(coins_codes):
        if code in missing_coins_codes:
            logger.debug(f"Coin {code} is not registered. Create new one")
            coin_info = missing_coins_infos[code]
            new_currency = CurrencyValue(
                code=code,
                name=coin_info.name,
                rate=coins_rates[code].rate,
                timestamp=datetime.fromtimestamp(
                    coins_rates[code].timestamp,
                    tz=timezone.utc,
                ),
            )
            new_currency.save()
        else:
            logger.debug(f"Coin {code} is registered. Update data")
            currency = CurrencyValue.objects.get(code=code)
            currency.rate = coins_rates[code].rate
            currency.timestamp = datetime.fromtimestamp(
                coins_rates[code].timestamp,
                tz=timezone.utc,
            )
            currency.save()
