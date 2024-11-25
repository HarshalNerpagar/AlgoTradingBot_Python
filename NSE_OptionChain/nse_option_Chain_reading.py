import time

import requests
import pandas as pd

sesi = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}
a = sesi.get("https://www.nseindia.com/", headers=headers)

indices = ['BANKNIFTY', 'FINNIFTY', 'NIFTY']


def FetchOptionChainfromNSE(scrip):
    if scrip in indices:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={scrip}"
    else:
        symbol4NSE = scrip.replace('&', '%26')
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol4NSE}"

    a = sesi.get(url, headers=headers)
    return a.json()['records']


def GetOptionChain(name, expiry):
    option_chain = pd.DataFrame()
    option_chain_record = FetchOptionChainfromNSE(name)
    option_chain_data = option_chain_record['data']
    option_chain_data_df = pd.DataFrame(option_chain_data)
    option_chain_data_df = option_chain_data_df[(option_chain_data_df.expiryDate == expiry)]

    # Determine ATM strike price
    underlying_value = option_chain_record['underlyingValue']
    atm_strike = min(option_chain_data_df['strikePrice'], key=lambda x: abs(x - underlying_value))

    # Filter for 10 strikes above and below ATM
    strikes = sorted(option_chain_data_df['strikePrice'].unique())
    atm_index = strikes.index(atm_strike)
    start_index = max(0, atm_index - 10)
    end_index = min(len(strikes), atm_index + 11)
    filtered_strikes = strikes[start_index:end_index]
    option_chain_data_df = option_chain_data_df[option_chain_data_df['strikePrice'].isin(filtered_strikes)]

    OptionChain_CE = pd.DataFrame()
    OptionChain_CE['CE'] = option_chain_data_df['CE']
    OptionChain_CE_expand = pd.concat([OptionChain_CE.drop(['CE'], axis=1), OptionChain_CE['CE'].apply(pd.Series)],
                                      axis=1)

    OptionChain_PE = pd.DataFrame()
    OptionChain_PE['PE'] = option_chain_data_df['PE']
    OptionChain_PE_expand = pd.concat([OptionChain_PE.drop(['PE'], axis=1), OptionChain_PE['PE'].apply(pd.Series)],
                                      axis=1)

    option_chain['CE_IV'] = OptionChain_CE_expand['impliedVolatility']
    option_chain['CE_LTP'] = OptionChain_CE_expand['lastPrice']
    option_chain['strikePrice'] = option_chain_data_df['strikePrice']
    option_chain['PE_LTP'] = OptionChain_PE_expand['lastPrice']
    option_chain['PE_IV'] = OptionChain_PE_expand['impliedVolatility']

    return option_chain


# scripname = 'NIFTY'
# ExpiryDate = '08-Aug-2024'
# # while True:
# Option_chain = GetOptionChain(scripname, ExpiryDate)
# print(Option_chain)
# Option_chain.to_csv(scripname + ".csv", index=False)
# time.sleep(5)
