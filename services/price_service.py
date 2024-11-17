import requests

API_KEY_ALPHA_VANTAGE = 'IH2HAUUSGQSG69DT'
API_KEY_FX_RATES = 'fxr_live_d374de9d27c3038b38513faad079dcfe6026'


class PriceService:

    @staticmethod
    def fetch_usd_price_in_pln():
        url = 'https://api.fxratesapi.com/latest?api_key=' + API_KEY_FX_RATES + '&currencies=PLN&base=USD'
        json_string = requests.get(url).json()
        return json_string


    @staticmethod
    def fetch_crypto_price_in_usd(cryptocurrency_ticker):
        url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' + cryptocurrency_ticker + '&market=USD&apikey=' + API_KEY_ALPHA_VANTAGE
        response = requests.get(url).json()
        return response


    @staticmethod
    def fetch_vuaa_price_in_usd():
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=VUAA.LON&apikey=' + API_KEY_ALPHA_VANTAGE
        response = requests.get(url).json()
        return response