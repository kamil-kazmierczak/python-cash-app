import requests
from datetime import date, datetime
from enum import Enum
from models.entities import CurrencyRate, db

API_KEY_FX_RATES = 'fxr_live_d374de9d27c3038b38513faad079dcfe6026'


class Currency(Enum):
    USD = 'USD'
    PLN = 'PLN'


class CurrencyRateDto:
    def __init__(self, base: Currency, target: Currency, value: float, date_: date):
        self.base = base
        self.target = target
        self.value = value
        self.date_ = date_

    def __repr__(self):
        return f'CurrencyRateDto(base={self.base!r}, target={self.target!r}, value={self.value!r}, date_={self.date_!r}'


class CurrencyService:

    @staticmethod
    def __fetch_currency_rate__(base_currency: Currency, target_currency: Currency) -> CurrencyRateDto:
        url = f'https://api.fxratesapi.com/latest?api_key={API_KEY_FX_RATES}&currencies={target_currency.value}&base={base_currency.value}'
        json_string = requests.get(url).json()
        date_ = datetime.fromisoformat(json_string['date'].rstrip('Z')).date()
        return CurrencyRateDto(base_currency, target_currency, float(json_string['rates'][target_currency.value]),
                               date_)

    @staticmethod
    def get_current_rate(base_currency: Currency, target_currency: Currency) -> CurrencyRate:
        return CurrencyRate.query.filter_by(base_currency=base_currency.value,
                                            target_currency=target_currency.value).order_by(
            CurrencyRate.date.desc()).first()

    @staticmethod
    def save_currency_rate(base_currency: Currency, target_currency: Currency) -> None:
        dto = CurrencyService.__fetch_currency_rate__(base_currency, target_currency)
        rate = CurrencyRate(base_currency=dto.base.value, target_currency=dto.target.value, value=dto.value,
                            date=dto.date_)
        db.session.add(rate)
        db.session.commit()
        print(f'CurrencyRate saved. {rate}')
