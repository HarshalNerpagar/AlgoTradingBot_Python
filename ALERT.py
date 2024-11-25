import urllib
from datetime import datetime
import requests
Telegram_TOKEN = '7444820914:AAGkQfqOKX-PqzCc6JtbUSr9poSOrevroVc'
Telegram_chat_ID = '5026711227'
now = datetime.now()
curr_time = now.strftime("%H:%M:%S")

# print(curr_time)

def position_message(long, short, entry, sl, target, strategy=''):
    if long:
        msg = (f'<b>💹🚀📈💸 TRADE ALERT 💸📈🚀💹</b>\n'
               f'\n'
               f'━━━━━━━━━━━({strategy})━━━━━━━━━━━\n'
               f'\n'
               f'\n'
               f'🕒 <b>TIME : </b> {curr_time}\n'
               f'\n'
               f'💵 <b>ENTRY PRICE : </b> {entry}\n'
               f'\n'
               f'🔻 <b>STOP LOSS : </b> {sl}\n'
               f'\n'
               f'🎯 <b>TARGET : </b> {target}\n'
               f'\n'
               f'\n'
               f'━━━━━━━━━━━━━━━━━━━━━━\n'
               f'\n'
               f'📈 <b>POSITION:</b> LONG\n'
               f'\n'
               f'━━━━━━━━━━━━━━━━━━━━━━\n'
               f'\n'
               f'<b>💹🚀📈💸 GOOD LUCK! 💸📈🚀💹</b>\n')

        encoded_message = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{Telegram_TOKEN}/sendMessage?chat_id={Telegram_chat_ID}&text={encoded_message}&parse_mode=HTML"
        requests.get(url)
    elif short:
        msg = (f'<b>💹🚀📈💸 TRADE ALERT 💸📈🚀💹</b>\n'
               f'\n'
               f'━━━━━━━━━━━({strategy})━━━━━━━━━━━\n'
               f'\n'
               f'\n'
               f'🕒 <b>TIME : </b> {curr_time}\n'
               f'\n'
               f'💵 <b>ENTRY PRICE : </b> {entry}\n'
               f'\n'
               f'🔻 <b>STOP LOSS : </b> {sl}\n'
               f'\n'
               f'🎯 <b>TARGET : </b> {target}\n'
               f'\n'
               f'\n'
               f'━━━━━━━━━━━━━━━━━━━━━━\n'
               f'\n'
               f'📈 <b>POSITION:</b> SHORT\n'
               f'\n'
               f'━━━━━━━━━━━━━━━━━━━━━━\n'
               f'\n'
               f'<b>💹🚀📈💸 GOOD LUCK! 💸📈🚀💹</b>\n')
        encoded_message = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{Telegram_TOKEN}/sendMessage?chat_id={Telegram_chat_ID}&text={encoded_message}&parse_mode=HTML"
        requests.get(url)


# position_message(True, False, 2345, 23344, 24560)

def modifyed_orders(request_response, price=0, rr=" ", strategy=''):
    if request_response == 'SLM':
        msg = (
            f'<b>🚨🔔- - - - - - SL_UPDATE - - - - - -🔔🚨</b>\n'
            f'\n'
            f'━━━━━━━━━━━({strategy})━━━━━━━━━━━\n'
            f'📍 <b>STOP LOSS:</b> {price}\n'
            f'💸 <b>POINT:</b> {rr}\n'
            f'\n'
            f'<b>🚨🔔- - - - - - SL_UPDATE - - - - - -🔔🚨</b>\n'
        )
        encoded_message = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{Telegram_TOKEN}/sendMessage?chat_id={Telegram_chat_ID}&text={encoded_message}&parse_mode=HTML"
        requests.get(url)
    elif request_response == "E":
        msg = (
            f'<b>🚀🔔- - - - - - EXIT - - - - - -🔔🚀</b>\n'
            f'\n'
            f'━━━━━━━━━━━({strategy})━━━━━━━━━━━\n'
            f'📍 <b>EXIT PRICE:</b> {price}\n'
            f'⏳️ <b>TIME:</b> {curr_time}\n'
            f'\n'
            f'<b>🚀🔔- - - - - - EXIT - - - - - -🔔🚀</b>\n'
        )
        encoded_message = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{Telegram_TOKEN}/sendMessage?chat_id={Telegram_chat_ID}&text={encoded_message}&parse_mode=HTML"
        requests.get(url)

def server_alrt(message):
    now = datetime.now()
    curr_time = now.strftime("%H:%M:%S")
    msg = (
        f'<b>🚀🔔- - - - - - ALERT - - - - - -🔔🚀</b>\n'
        f'\n'
        f'⏳️ <b> {message} </b>\n'
        f'⏳️ <b>TIME:</b> {curr_time}\n'
        f'\n'
        f'<b>🚀🔔- - - - - - ALERT - - - - - - 🚀🔔</b>\n'
    )
    encoded_message = urllib.parse.quote(msg)
    url = f"https://api.telegram.org/bot{Telegram_TOKEN}/sendMessage?chat_id={Telegram_chat_ID}&text={encoded_message}&parse_mode=HTML"
    requests.get(url)
