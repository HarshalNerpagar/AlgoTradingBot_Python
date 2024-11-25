from fyers_apiv3 import fyersModel
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta, gamma, rho, theta, vega
from datetime import datetime, timedelta
import pandas as pd
import time
from NSE_OptionChain.nse_option_Chain_reading import GetOptionChain
from NSE_OptionChain.nse_option_Chain_reading import FetchOptionChainfromNSE
from Logging import logger


client_id = "OVUPFX8VX5-100"
# file1 = open('../Fyers_Authentication/access_token', 'r')
file1 = open('Fyers_Authentication/access_token', 'r')
access_token = file1.readline().strip()
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")


def expiry_convert(expiry):
    day = int(expiry[:2])
    month_str = expiry[2:5]
    year = int('20' + expiry[5:7])

    # Map month abbreviations to month numbers
    month_map = {
        'JAN': 1,
        'FEB': 2,
        'MAR': 3,
        'APR': 4,
        'MAY': 5,
        'JUN': 6,
        'JUL': 7,
        'AUG': 8,
        'SEP': 9,
        'OCT': 10,
        'NOV': 11,
        'DEC': 12
    }
    month = month_map[month_str.upper()]
    # Create a datetime object with the desired time (15:30:00)
    date_time_obj = datetime(year, month, day, 15, 30, 0)
    return date_time_obj

def find_next_expiry():
    expiry_dates = [
        '08-08-2024', '14-08-2024', '22-08-2024', '29-08-2024', '05-09-2024',
        '26-09-2024', '31-10-2024', '26-12-2024', '27-03-2025', '26-06-2025',
        '24-12-2025', '25-06-2026', '31-12-2026', '24-06-2027', '30-12-2027',
        '29-06-2028', '28-12-2028', '28-06-2029'
    ]

    str_date = datetime.now().strftime('%Y-%m-%d')
    current_date = datetime.strptime(str_date, '%Y-%m-%d')

    expiry_dates_dt = [datetime.strptime(date, '%d-%m-%Y') for date in expiry_dates]

    # Find the next expiry date
    next_expiry_date = None
    for date in expiry_dates_dt:
        if date >= current_date:
            next_expiry_date = date
            break

    if next_expiry_date:
        # Convert the next expiry date to the desired format
        return next_expiry_date.strftime('%d%b%y').upper()
    else:
        return None


expiry = find_next_expiry()
# print(expiry)

def fetch_option_greeks():
    # logger.info('Fetching option greeks')
    def convert_date_format(date_str):
        # Define the input format
        input_format = "%d%b%y"
        # Parse the date string to a datetime object
        date_obj = datetime.strptime(date_str, input_format)
        # Define the output format
        output_format = "%d-%b-%Y"
        # Format the datetime object to the desired output format
        formatted_date = date_obj.strftime(output_format)
        return formatted_date
    Option_chain = GetOptionChain('NIFTY', convert_date_format(expiry))
    Option_chain.to_csv('./Options_Data/NIFTY_OptionChian.csv', index=False)
    # time.sleep(1)
    call_side = []
    put_side = []
    index_ltp = FetchOptionChainfromNSE('NIFTY')['underlyingValue']

    options_iv_dict = {}
    nse_option_chain = pd.read_csv('./Options_Data/NIFTY_OptionChian.csv')
    for i in range(len(nse_option_chain.index)):
        options_iv_dict[nse_option_chain.at[i, 'strikePrice']] = {
            'ce_ltp': nse_option_chain.at[i, 'CE_LTP'],
            'pe_ltp': nse_option_chain.at[i, 'PE_LTP'],
            'ce_iv': nse_option_chain.at[i, 'CE_IV'],
            'pe_iv': nse_option_chain.at[i, 'PE_IV'],
        }

    start = (round(index_ltp / 50) * 50) - 100
    end = (round(index_ltp / 50) * 50) + 100

    for strick in range(start, end + 50, 50):
        # 'NIFTY08AUG24C24400'
        price = options_iv_dict[strick]['ce_ltp']
        S = index_ltp
        K = strick
        t = (expiry_convert(expiry) - datetime.now()) / timedelta(days=1) / 365
        # t = (expiry_convert(expiry) - datetime(2024, 8, 6, 15, 30, 0)) / timedelta(days=1) / 365
        r = 0.1
        flag = 'c'
        IV = implied_volatility(price, S, K, t, r, flag) if options_iv_dict[strick]['ce_iv'] < 1 else options_iv_dict[strick]['ce_iv'] / 100
        delta_value = round(delta(flag, S, K, t, r, IV), 3)
        theta_value = round(theta(flag, S, K, t, r, IV), 2)
        gamma_value = round(gamma(flag, S, K, t, r, IV), 4)
        rho_value = round(rho(flag, S, K, t, r, IV), 2)
        vega_value = round(vega(flag, S, K, t, r, IV), 4)

        call_side.append([strick, price, round(IV*100, 2), delta_value, theta_value, gamma_value, rho_value, vega_value])
        # call_side.append([strick, price, delta_value, gamma_value])

    for strick in range(start, end + 50, 50):
        price = options_iv_dict[strick]['pe_ltp']
        S = index_ltp
        K = strick
        t = (expiry_convert(expiry) - datetime.now()) / timedelta(days=1) / 365
        # t = (expiry_convert(expiry) - datetime(2024, 8, 6, 15, 30, 0)) / timedelta(days=1) / 365
        r = 0.1
        flag = 'p'
        IV = implied_volatility(price, S, K, t, r, flag) if options_iv_dict[strick]['pe_iv'] < 1 else options_iv_dict[strick]['pe_iv'] / 100
        delta_value = abs(round(delta(flag, S, K, t, r, IV), 3))
        theta_value = round(theta(flag, S, K, t, r, IV), 2)
        gamma_value = round(gamma(flag, S, K, t, r, IV), 4)
        rho_value = round(rho(flag, S, K, t, r, IV), 2)
        vega_value = round(vega(flag, S, K, t, r, IV), 4)
        put_side.append([strick, price, round(IV*100, 2), delta_value, theta_value, gamma_value, rho_value, vega_value])
        # put_side.append([strick, price, delta_value, gamma_value])

    call_option_chain = pd.DataFrame(call_side,columns=['strick', 'ltp', 'iv', 'delta', 'theta', 'gamma', 'rho', 'vega'])
    call_option_chain.to_csv('./Options_Data/call_option_chain.csv', mode='w', index=False)
    put_option_chain = pd.DataFrame(put_side,columns=['strick', 'ltp', 'iv', 'delta', 'theta', 'gamma', 'rho', 'vega'])
    put_option_chain.to_csv('./Options_Data/put_option_chain.csv', mode='w', index=False)
    # time.sleep(1)


def strick_selection(long=True, short=True):
    call_OC = pd.read_csv('./Options_Data/call_option_chain.csv')
    put_OC = pd.read_csv('./Options_Data/put_option_chain.csv')
    if not(long):
        arr = list(call_OC['delta'])
        arr_02 = list(call_OC['gamma'])
        arr_03 = list(call_OC['theta'])
        arr_04 = list(call_OC['vega'])
        strick_lst = list(call_OC['strick'])
        arr.sort()
        arr_02.sort()
        arr_03.sort()
        arr_04.sort()
        strick_lst.sort(reverse=True)

        for i in range(len(arr)):
            if arr[i] > 0.50:
                # print(i)
                return {
                    'strick': strick_lst[i],
                    'symbol': f'NIFTY{expiry}C{strick_lst[i]}',
                    'delta': float(call_OC.at[i, 'delta']),
                    'gamma': float(call_OC.at[i, 'gamma']),
                    'theta': float(call_OC.at[i, 'theta']),
                    'vega': float(call_OC.at[i, 'vega'])
                }
    elif not(short):
        arr = list(put_OC['delta'])
        strick_lst = list(put_OC['strick'])
        arr_02 = list(put_OC['gamma'])
        arr_03 = list(put_OC['theta'])
        arr_04 = list(put_OC['vega'])
        arr.sort()
        arr_02.sort()
        arr_03.sort()
        arr_04.sort()
        strick_lst.sort()

        for i in range(len(arr)):
            if arr[i] > 0.50:
                # print(i)
                return {
                    'strick': strick_lst[i],
                    'symbol': f'NIFTY{expiry}P{strick_lst[i]}',
                    'delta': float(put_OC.at[i, 'delta']),
                    'gamma': float(put_OC.at[i, 'gamma']),
                    'theta': float(put_OC.at[i, 'theta']),
                    'vega': float(put_OC.at[i, 'vega'])
                }


def get_option_greeks(strike, long=True, short=True):

    call_OC = pd.read_csv('./Options_Data/call_option_chain.csv')
    put_OC = pd.read_csv('./Options_Data/put_option_chain.csv')
    if not(long):
        strike = int(strike.split('C')[-1])

        index = list(call_OC['strick']).index(strike)
        print(strike, index)
        return {
            'delta': call_OC.at[index, 'delta'],
            'gamma': call_OC.at[index, 'gamma'],
            'theta': call_OC.at[index, 'theta'],
            'vega': call_OC.at[index, 'vega']
        }
    elif not(short):
        strike = int(strike.split('P')[-1])
        index = list(put_OC['strick']).index(strike)
        return {
            'delta': put_OC.at[index, 'delta'],
            'gamma': put_OC.at[index, 'gamma'],
            'theta': put_OC.at[index, 'theta'],
            'vega': put_OC.at[index, 'vega']

        }


