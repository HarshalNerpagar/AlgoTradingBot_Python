from datetime import datetime
from fyers_apiv3 import fyersModel
import math
from scipy.stats import norm
from Shoonya_Api import api as ShoonyaApi

client_id = "OVUPFX8VX5-100"
file1 = open('../Fyers_Authentication/access_token', 'r')
access_token = file1.readline().strip()
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

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
# def calculate_option_price(index_ltp,option_ltp,index_sl, delta, gamma, theta, vega, time_fraction=3/1440, iv_change=0.01):
#     """
#     Calculate the option price considering various Greeks.
#
#     Parameters:
#     - index_ltp: Current index price
#     - index_sl: Stop-loss index price
#     - option_ltp: Current option price
#     - delta: Delta of the option
#     - gamma: Gamma of the option
#     - theta: Theta of the option
#     - vega: Vega of the option
#     - time_fraction: Fraction of the day for time decay (default: 10 minutes out of 1440 minutes)
#     - iv_change: Change in implied volatility (default: 0.01 or 1%)
#
#     Returns:
#     - sl_option_price: Option price at stop-loss index level
#     """
#
#     # data = {
#     #     "symbols": f"NSE:NIFTY50-INDEX, {convert_symbol(option_symbol)}"
#     # }
#     # response = fyers.quotes(data=data)
#     # data = {
#     #     "symbols": "NSE:NIFTY50-INDEX"
#     # }
#     # response = fyers.quotes(data=data)
#     # index_ltp = float(response.get('d')[0].get('v').get('lp'))
#
#     sl_index_move = abs(index_sl - index_ltp)
#     delta_impact_sl = delta * sl_index_move
#     gamma_adjustment_sl = 0.5 * gamma * (sl_index_move ** 2)
#     vega_impact = vega * iv_change
#     theta_impact = theta * time_fraction
#     total_change_sl = delta_impact_sl + gamma_adjustment_sl + vega_impact + theta_impact
#     #
#     # total_change_sl = delta_impact_sl + gamma_adjustment_sl + vega_impact
#     sl_option_price = option_ltp + total_change_sl
#
#     return sl_option_price





# Example usage



class OptionPriceCalculator:

    def __init__(self, api):
        self.api = api

    def fetch_price(self, exchange, token):
        """Fetches the latest price for a given token."""
        return float(self.api.get_quotes(exchange=exchange, token=token).get('lp'))

    def fetch_implied_volatility(self, option_symbol):
        """Fetches the latest implied volatility from NSE for the given option symbol."""
        # You need to implement this method according to the actual data source or API for IV
        return float(self.api.get_implied_volatility(option_symbol))

    def black_scholes_price(self, S, K, T, r, sigma, option_type='call'):
        """Calculates the Black-Scholes price for European options."""
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        if option_type == 'call':
            price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return price

    def calculate_option_price(self, option_symbol, index_sl, delta, gamma, theta, vega, price=0.0,
                               time_fraction=5 / 1440, r=0.05, option_type='call'):
        """
        Calculate the option price considering various Greeks and Black-Scholes model.

        Parameters:
        - option_symbol: Symbol of the option
        - index_sl: Stop-loss index price
        - delta: Delta of the option
        - gamma: Gamma of the option
        - theta: Theta of the option
        - vega: Vega of the option
        - price: Override the current option price (default: 0.0)
        - time_fraction: Fraction of the day for time decay (default: 5 minutes out of 1440 minutes)
        - r: Risk-free interest rate (default: 0.05)
        - option_type: Type of the option ('call' or 'put')

        Returns:
        - sl_option_price: Option price at stop-loss index level
        """

        # Fetch current index and option prices
        index_ltp = self.fetch_price(exchange='NSE', token='26000')
        symb_token = self.api.searchscrip(exchange='NFO', searchtext=option_symbol).get('values')[0].get('token')
        option_ltp = price if price else self.fetch_price(exchange='NFO', token=symb_token)

        # Fetch the latest implied volatility
        iv = self.fetch_implied_volatility(option_symbol)

        # Calculate Black-Scholes price
        T = time_fraction  # Time to expiration in years (fraction of the trading day)
        S = index_ltp  # Current index price
        K = index_sl  # Strike price (used as stop-loss level here)
        sigma = iv  # Implied volatility
        bsm_price = self.black_scholes_price(S, K, T, r, sigma, option_type)

        # Calculate the change in the option's price due to movements in the underlying index
        sl_index_move = abs(index_ltp - index_sl)
        delta_impact_sl = delta * sl_index_move
        gamma_adjustment_sl = 0.5 * gamma * (sl_index_move ** 2)

        # Calculate the impact of volatility and time decay
        vega_impact = vega * iv  # Assuming the change in volatility directly affects Vega
        theta_impact = theta * time_fraction

        # Sum all impacts to estimate the change in the option's price
        total_change_sl = delta_impact_sl + gamma_adjustment_sl + vega_impact - theta_impact
        sl_option_price = bsm_price + total_change_sl

        return sl_option_price


# Example usage:
# api = ShoonyaApi()  # Initialize your API
# calculator = OptionPriceCalculator(api)
# updated_sl_price = calculator.calculate_option_price(option_symbol='NIFTY23AUG17500CE', index_sl=17400,
#                                                      delta=0.5, gamma=0.01, theta=-0.02, vega=0.1, r=0.05, option_type='call')
# print(updated_sl_price)


option_symbol = 'NIFTY08AUG24C24200'
index_ltp = 24233.40
option_ltp = 131.15
index_sl = index_ltp - 10
delta = 0.55
gamma = 0.001
theta = -13
vega = 11.91

X = OptionPriceCalculator(ShoonyaApi)

sl_option_price = X.calculate_option_price(index_ltp,option_ltp,index_sl, delta, gamma, theta, vega)
print(f"Stop-Loss Option Price: {sl_option_price:.2f}")

# Stop-Loss Option Price: 150.84

# Stop-Loss Option Price: 201.77
# Stop-Loss Option Price: 150.97

# print(round(201.73 - 175, 2), round(175 - 150.93, 2)) #DeltaGammaVegaTheta
#
# print(round(201.77 - 175, 2), round(175 - 150.97, 2)) #DeltaGammaVega
#
# print(round(201.65 - 175, 2), round(175 - 150.85, 2)) #Delta&Gamma
#
# print(round( 200.40 - 175, 2), round(175 - 149.60, 2)) #onlyDelta

