import json

class FileService:

    @staticmethod
    def save_json(data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        print('Zapisane do pliku')

    @staticmethod
    def read_btc_price(date):
        with open('json/btc.json', 'r') as file:
            data = json.load(file)["Time Series (Digital Currency Daily)"][date]["1. open"]
        return data

    @staticmethod
    def read_eth_price(date):
        with open('json/eth.json', 'r') as file:
            data = json.load(file)["Time Series (Digital Currency Daily)"][date]["1. open"]
        return data

    @staticmethod
    def read_dot_price(date):
        with open('json/dot.json', 'r') as file:
            data = json.load(file)["Time Series (Digital Currency Daily)"][date]["1. open"]
        return data


    @staticmethod
    def read_vuaa_price(date):
        with open('json/vuaa.json', 'r') as file:
            data = json.load(file)["Time Series (Daily)"][date]["1. open"]
        return data


    @staticmethod
    def read_usd_price_in_pln():
        with open('json/usd.json', 'r') as file:
            data = json.load(file)["rates"]["PLN"]
        return data