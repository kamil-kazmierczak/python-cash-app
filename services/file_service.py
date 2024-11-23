import json
import csv

DIGITAL_KEY = "Time Series (Digital Currency Daily)"
KEY = "Time Series (Daily)"


class FileService:

    @staticmethod
    def save_json(data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        print('Zapisane do pliku')

    @staticmethod
    def read_btc_price(date):
        with open('json/btc.json', 'r') as file:
            data = json.load(file)[DIGITAL_KEY][date]["1. open"]
        return data

    @staticmethod
    def read_eth_price(date):
        with open('json/eth.json', 'r') as file:
            data = json.load(file)

            eth_price = data[DIGITAL_KEY][date]["1. open"]
        return eth_price

    @staticmethod
    def read_dot_price(date):
        with open('json/dot.json', 'r') as file:
            data = json.load(file)[DIGITAL_KEY][date]["1. open"]
        return data

    @staticmethod
    def read_vuaa_price(date):
        with open('json/vuaa.json', 'r') as file:
            data = json.load(file)[KEY][date]["1. open"]
        return data

    @staticmethod
    def read_usd_price_in_pln():
        with open('json/usd.json', 'r') as file:
            data = json.load(file)["rates"]["PLN"]
        return data

    @staticmethod
    def read_assets():
        assets_per_name = {}
        with open('csv/assets.csv', 'r') as file:
            csv_reader = csv.reader(file, delimiter='|')
            for row in csv_reader:
                asset_name = row[0]
                asset_amount = float(row[1])
                assets_per_name[asset_name] = asset_amount
        return assets_per_name
