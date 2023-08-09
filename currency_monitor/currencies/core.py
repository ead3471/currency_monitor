from dotenv import load_dotenv
import os
import requests

load_dotenv()

COINLAYER_API_KEY = os.getenv('COINLAYER_API_KEY')


def get_currency_value(currency_code: str):
    """Returns a currency rated to USD

    Parameters
    ----------
    currency_code : str
        currency code
    """
    url = "http://api.coinlayer.com/live"
    params = {
            "access_key": COINLAYER_API_KEY,
            "symbols": "BTC"
            }
    responce = requests.get(url, params=params)
    print(responce.json())


if __name__ == "__main__":
    get_currency_value('BTC')
