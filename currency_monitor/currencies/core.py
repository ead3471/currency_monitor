from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from dataclasses import dataclass

from decimal import Decimal
from pytz import timezone


load_dotenv()


@dataclass
class CurrencyRate:
    code: str
    rate: Decimal
    timestamp: int


@dataclass
class CurrencyInfo:
    code: str
    name: str


COINLAYER_API_KEY = os.getenv("COINLAYER_API_KEY")


def get_current_currency_value(currency_code: str) -> CurrencyRate:
    """Returns a currency rated to USD

    Parameters
    ----------
    currency_code : str
        currency code
    """
    return get_current_currency_values(
        [
            currency_code,
        ]
    )[0]


def get_current_currency_values(
    currency_codes: list[str],
) -> list[CurrencyRate]:
    """Returns a list of currencies rated to USD
    Parameters
    ----------
    currency_code : str
        currency code
    """
    url = "http://api.coinlayer.com/live"
    params = {"access_key": COINLAYER_API_KEY, "symbols": currency_codes}
    response_json = requests.get(url, params=params).json()

    timestamp = response_json["timestamp"]
    result = []
    if response_json["success"]:
        for recieved_currency, rate in response_json["rates"].items():
            result.append(
                CurrencyRate(recieved_currency, Decimal(rate), timestamp),
            )
        return result
    else:
        raise ValueError(response_json)


def get_currency_info(currency_code: str) -> CurrencyInfo:
    url = "http://api.coinlayer.com/list"
    params = {"access_key": COINLAYER_API_KEY}
    responce_json = requests.get(url, params=params).json()
    print(responce_json)
    if responce_json["success"]:
        if currency_code in responce_json["crypto"]:
            return CurrencyInfo(
                currency_code,
                responce_json["crypto"][currency_code]["name"],
            )
        else:
            return CurrencyInfo(
                code=currency_code, name=responce_json["fiat"][currency_code]
            )
    else:
        raise ValueError(responce_json)
