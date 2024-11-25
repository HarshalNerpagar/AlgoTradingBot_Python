def calculate_option_price_change(delta, gamma, index_move):
    """
    Calculate the change in option price using delta and gamma.

    Parameters:
    - delta: Delta of the option
    - gamma: Gamma of the option
    - index_move: Expected index move

    Returns:
    - Change in option price
    """
    delta_impact = delta * index_move
    gamma_impact = 0.5 * gamma * (index_move ** 2)

    total_change = delta_impact + gamma_impact
    return total_change


def calculate_limit_order_entry(index_ltp, index_target, option_ltp, delta, gamma):
    """
    Calculate the limit order entry point for the option using option Greeks.

    Parameters:
    - index_ltp: Current stock price (index price)
    - index_target: Target index price (support/resistance level)
    - option_ltp: Current option price
    - delta: Delta of the option
    - gamma: Gamma of the option

    Returns:
    - Limit order entry price for the option
    """
    # Calculate expected index move
    index_move = index_target - index_ltp

    # Calculate the change in option price using delta and gamma
    price_change = calculate_option_price_change(delta, gamma, index_move)

    # Calculate the limit order entry price
    limit_order_entry_price = option_ltp + price_change

    return limit_order_entry_price


# Example usage
index_ltp = 24179.20
index_target = 24223.90 # Support or Resistance level
option_ltp = 180
delta = 0.51
gamma = 0.001

# Calculate the limit order entry price
limit_order_entry_price = calculate_limit_order_entry(index_ltp, index_target, option_ltp, delta, gamma)

print(f"Limit Order Entry Price: {limit_order_entry_price:.2f}")
