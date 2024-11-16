import requests

API_KEY_ALPHA_VANTAGE = 'IH2HAUUSGQSG69DT'
API_KEY_FX_RATES = 'fxr_live_d374de9d27c3038b38513faad079dcfe6026'


class PriceService:

    @staticmethod
    def get_current_usd_price_in_pln():
        url = 'https://api.fxratesapi.com/latest?api_key=' + API_KEY_FX_RATES + '&currencies=PLN&base=USD'
        response = requests.get(url).json()

        usd_price = response['rates']['PLN']

        return round(float(usd_price), 2)

    @staticmethod
    def get_current_crypto_price_in_usd(cryptocurrency_ticker):
        url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' + cryptocurrency_ticker + '&market=USD&apikey=' + API_KEY_ALPHA_VANTAGE
        price = requests.get(url).json()['Time Series (Digital Currency Daily)']['2024-11-08']['1. open']

        return round(float(price), 2)

    @staticmethod
    def get_current_vuaa_price_in_usd():
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=VUAA.LON&apikey=' + API_KEY_ALPHA_VANTAGE
        price_vuaa_uk = requests.get(url).json()['Time Series (Daily)']['2024-11-08']['1. open']

        return round(float(price_vuaa_uk), 2)
