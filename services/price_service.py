import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from datetime import date, datetime

API_KEY_ALPHA_VANTAGE = 'IH2HAUUSGQSG69DT'
API_KEY_FX_RATES = 'fxr_live_d374de9d27c3038b38513faad079dcfe6026'

DIGITAL_KEY = "Time Series (Digital Currency Daily)"
KEY = "Time Series (Daily)"


class PriceDto:
    def __init__(self, name: str, value: float, date_: date):
        self.name = name
        self.value = value
        self.date_ = date_

    def __repr__(self):
        return f'PriceDto(name={self.name!r}, value={self.value!r}, date_={self.date_!r}'


class PriceService:

    @staticmethod
    def fetch_usd_price_in_pln() -> PriceDto:
        url = 'https://api.fxratesapi.com/latest?api_key=' + API_KEY_FX_RATES + '&currencies=PLN&base=USD'
        json_string = requests.get(url).json()
        date_ = datetime.fromisoformat(json_string['date'].rstrip('Z')).date()
        return PriceDto('USD', float(json_string['rates']['PLN']), date_)

    @staticmethod
    def fetch_crypto_price_in_usd(cryptocurrency_ticker) -> PriceDto:
        url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' + cryptocurrency_ticker + '&market=USD&apikey=' + API_KEY_ALPHA_VANTAGE
        response = requests.get(url).json()
        date_ = list(response[DIGITAL_KEY].keys())[0]
        return PriceDto(cryptocurrency_ticker, float(response[DIGITAL_KEY][date_]['1. open']), date.fromisoformat(date_))

    @staticmethod
    def fetch_vuaa_price_in_usd() -> PriceDto:
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=VUAA.LON&apikey=' + API_KEY_ALPHA_VANTAGE
        response = requests.get(url).json()
        date_ = list(response[KEY].keys())[0]
        return PriceDto('VUAA.UK', float(response[KEY][date_]['1. open']), date.fromisoformat(date_))

    @staticmethod
    def fetch_gold_one_oz_coin_price_in_pln() -> PriceDto:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto('https://mennicakapitalowa.pl/Skup-zlotych-monet-cennik-i-zasady-ccms-pol-65.html')

            try:
                page.locator('a[data-cookie-view="basic minimal consents privacy"]').wait_for()
                page.locator('a[data-cookie-view="basic minimal consents privacy"]').click()
            except:
                print('Nie znaleziono przycisku do zatwierdzenie plikow cookie')

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', class_='table_column', string='Liść Klonu 1 oz')
        value_string = div.find_next_sibling('div', class_='table_column').text

        value = re.sub(r"[^\d..,]", "", value_string).replace(",", "")

        return PriceDto('GOLD', float(value), date.today())

