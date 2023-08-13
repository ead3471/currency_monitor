from dotenv import load_dotenv
import os
import requests
from dataclasses import dataclass
from decimal import Decimal
import logging


load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class CoinRate:
    code: str
    rate: Decimal
    timestamp: int


@dataclass
class CoinInfo:
    code: str
    name: str


COINLAYER_API_KEY = os.getenv("COINLAYER_API_KEY")


def get_coin_rate(coin_code: str) -> CoinRate:
    """Returns a currency rated to USD

    Parameters
    ----------
    currency_code : str
        currency code
    """
    return get_coins_rates(
        [
            coin_code,
        ]
    )[coin_code]


def get_coins_rates(
    coin_codes: list[str],
) -> dict[str, CoinRate]:
    """Returns a dict of currencies rated to USD {code:CoinRate}
    Parameters
    ----------
    coin_codes : list[str]
        coin codes
    """
    logger.debug(f"Get currencies values for {coin_codes}")
    url = "http://api.coinlayer.com/live"
    params = {"access_key": COINLAYER_API_KEY, "symbols": ",".join(coin_codes)}
    response_json = requests.get(url, params=params).json()
    logger.debug(f"Result={response_json}")

    result = {}
    if response_json["success"]:
        timestamp = response_json["timestamp"]
        for coin_code, rate in response_json["rates"].items():
            result[coin_code] = CoinRate(coin_code, Decimal(rate), timestamp)
        return result
    else:
        raise ValueError(response_json)


def get_coin_info(coin_code: str) -> CoinInfo:
    """Return currency info for given currency_code

    Parameters
    ----------
    currency_code : str

    Returns
    -------
    CoinInfo instance
    """
    result = get_coins_info([coin_code])
    return result[coin_code]


def get_coins_info(coin_codes: list[str]) -> dict[str, CoinInfo]:
    """Return infos for given codes list as
    dict[currency_code:CoinInfo]

    Raises
    ------
    ValueError
        in case of bad currency code in given list
    """
    if len(coin_codes) == 0:
        return {}

    url = "http://api.coinlayer.com/list"
    params = {"access_key": COINLAYER_API_KEY}
    responce_json = requests.get(url, params=params).json()
    result = {}
    if responce_json["success"]:
        for coin_code in coin_codes:
            if coin_code in responce_json["crypto"]:
                result[coin_code] = CoinInfo(
                    coin_code,
                    responce_json["crypto"][coin_code]["name"],
                )
            else:
                raise ValueError(
                    f"Currency with code {coin_code} is not supported"
                )
    return result
