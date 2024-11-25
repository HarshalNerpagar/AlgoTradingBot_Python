import pyotp
from api_helper import ShoonyaApiPy
from Logging import logger
import pandas as pd

api = ShoonyaApiPy()
token = 'GX5NA7N356WK245LUN5X352C2OKHU573'
otp = pyotp.TOTP(token).now()

# credentials
user = 'FA366783'
pwd = 'Hn@08072005'
factor2 = otp
vc = 'FA366783_U'
app_key = '86d7d185be0ec8a08da8d59cd92baa75'
imei = 'abc1234'

ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)

# EXPIRY = '25JUL24'
LOT_SIZE = 25


def StopLimitOrder(price, symbol , trade='B'):
    price = (price // 0.05) * 0.05
    ORDER = api.place_order(buy_or_sell=trade,
                            product_type='M',
                            exchange='NFO', tradingsymbol=symbol,
                            quantity=LOT_SIZE, discloseqty=0, price_type='SL-LMT', price=price, trigger_price=price)
    return ORDER

def PlaceOrder(symbol, trade='S'):
    ORDER = api.place_order(buy_or_sell=trade, product_type='M',
                            exchange='NFO', tradingsymbol=symbol,
                            quantity=LOT_SIZE, discloseqty=0, price_type='MKT')
    return ORDER




def LimitOrder(price, symbol):
    ORDER = api.place_order(buy_or_sell='S', product_type='M',
                            exchange='NFO', tradingsymbol=symbol,
                            quantity=LOT_SIZE, discloseqty=0, price_type='LMT', price=price, trigger_price=None)
    return ORDER



def ExitOrder(symbol):
    ORDER = api.place_order(buy_or_sell='B', product_type='M',
                            exchange='NFO', tradingsymbol=symbol,
                            quantity=LOT_SIZE, discloseqty=0, price_type='MKT')
    return ORDER




