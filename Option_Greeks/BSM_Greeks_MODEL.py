import math
from scipy.stats import norm
import ShoonyaApi


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

# chatgpt link : https://chatgpt.com/share/7027605d-f96e-4bc2-8255-50641216f2c5
# Example usage:
# api = ShoonyaApi()  # Initialize your API
# calculator = OptionPriceCalculator(api)
# updated_sl_price = calculator.calculate_option_price(option_symbol='NIFTY23AUG17500CE', index_sl=17400,
#                                                      delta=0.5, gamma=0.01, theta=-0.02, vega=0.1, r=0.05, option_type='call')
# print(updated_sl_price)

