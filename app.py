from crypt import methods
from flask import Flask, jsonify, render_template
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)
load_dotenv()
apikey = os.getenv('API_KEY')
crypto = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'USDT': 'Tether',
    'BNB': 'Binance Coin',
    'ADA': 'Cardano',
    'XRP': 'Ripple',
    'SOL': 'Solana',
    'MATIC': 'Polygon',
    'DOGE': 'Dogecoin',
    'AVAX': 'Avalanche',
    'FTM': 'Fantom',
    'UNI': 'Uniswap',
    'XLM': 'Stellar',
    'NEAR': 'Near Protocol',
    'PUSH': 'EPNS',
    'SHIB': 'Shiba Inu'

}
exchanges = ["WazirX", "CoinDCX", "Bitbns", "Zebpay"]


def exLink(ex, name):
    if ex == "WazirX":
        return "https://wazirx.com/exchange/%s" % (name)
    elif (ex == "CoinDCX"):
        return "https://coindcx.com/trade/%s" % name
    elif (ex == "Bitbns"):
        return "https://bitbns.com/trade/#/%s" % (name.replace("INR", "")).lower()
    elif (ex == "Zebpay"):
        return "https://zebpay.com/exchange/%s" % name.replace("INR", "-INR")


def createInstance():
    coindcx = (requests.get("https://api.coindcx.com/exchange/ticker")).json()
    wazirx = (requests.get("https://api.wazirx.com/api/v2/tickers")).json()
    bitbns = (requests.get("https://api.bitbns.com/api/trade/v1/tickers",
                           headers={'X-BITBNS-APIKEY': apikey})).json()
    zebpay = (requests.get("https://www.zebapi.com/pro/v1/market/")).json()
    data = []

    def coinData(name):
        wrxFormat = name.lower()
        zepFormat = name.replace("INR", "-INR")
        bnsFormat = name.replace("INR", '')
        # coindcx
        for item in coindcx:
            if item['market'] == name:
                dcx = (item['last_price'])
        # wazirx
        wrx = wazirx[wrxFormat]['last']
        # bitbns
        try:
            bns = bitbns[bnsFormat]['last_traded_price']
        except:
            bns = "99999999"
        # zebpay
        try:
            for c in zebpay:
                if(c['pair'] == zepFormat):
                    if float(c['buy']) > 0:
                        zep = c['buy']
        except:
            zep = "99999999"
        priceData = [wrx, dcx, bns, zep]
        bestEx = exchanges[priceData.index(
            min(priceData, key=lambda x: float(x)))]
        buyLink = exLink(bestEx, name)
        coin = {
            'name': crypto[name.replace("INR", "")],
            'wrx': float(wrx),
            'dcx': float(dcx),
            'bns': bns if float(bns) < 9999999 else "NA",
            'zep': float(zep) if float(zep) < 99999999 and float(zep) > 0 else "NA",
            'best': bestEx,
            'exlink': buyLink
        }
        data.append(coin)

    for x in crypto:
        y = x+'INR'
        coinData(y)
    return data


@ app.route("/",methods=["GET"])
def index():
    d = createInstance()
    re = {
        'id': 1,
        'data': d
    }
    response = jsonify(d)
    return response


if __name__ == "__main__":
    app.run(debug=True, port=8088)
