def calculate_option_price(index_ltp, index_target, index_sl, option_ltp, delta, gamma, theta, vega, IV, rho,
                           time_fraction=10 / 1440, iv_change=0.01):


    # Calculate the index moves
    sl_index_move = index_sl - index_ltp
    target_index_move = index_target - index_ltp

    # Calculate the Delta impact
    delta_impact_sl = delta * sl_index_move
    delta_impact_target = delta * target_index_move

    # Adjust for Gamma
    gamma_adjustment_sl = gamma * (sl_index_move ** 2) / 2
    gamma_adjustment_target = gamma * (target_index_move ** 2) / 2

    # Factor in Vega (if volatility changes)
    vega_impact = vega * iv_change

    # Consider Theta (time decay)
    theta_impact = theta * time_fraction

    # Total option price change
    total_change_sl = delta_impact_sl + gamma_adjustment_sl + vega_impact + theta_impact
    total_change_target = delta_impact_target + gamma_adjustment_target + vega_impact + theta_impact

    # Calculate new option prices
    sl_option_price = option_ltp + total_change_sl
    target_option_price = option_ltp + total_change_target

    return sl_option_price, target_option_price


# Example usage
index_ltp = 24050
index_target = 24100
index_sl = 24020
option_ltp = 221
delta = 0.52
gamma = 0.0008
theta = -35
vega = 9
IV = 23.99  # Given in percentage; if needed in decimal form, divide by 100
rho = 0.05

sl_option_price, target_option_price = calculate_option_price(index_ltp, index_target, index_sl, option_ltp, delta,
                                                              gamma, theta, vega, IV, rho)
print(f"Stop-Loss Option Price: {sl_option_price:.2f}")
print(f"Target Option Price: {target_option_price:.2f}")
