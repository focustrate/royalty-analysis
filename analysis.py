import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import csv

# Function to perform earnings analysis, forecast, valuation, and deal rating
def analyze_and_value_royalty(
    csv_file,
    years_remaining,
    discount_rates=[0.10, 0.125, 0.15],
    listing_price=0,
    min_bid=0,
    last_transaction=0,
    marketplace_median=0,
    output_csv=None
):
    # Load earnings data
    earnings_data = pd.read_csv(csv_file)

    # Summarize annual earnings
    annual_earnings = earnings_data.groupby('distribution_year')['payable_amount'].sum().reset_index()
    annual_earnings = annual_earnings.sort_values('distribution_year')

    # Linear regression to determine trend
    X = annual_earnings['distribution_year'].values.reshape(-1, 1)
    y = annual_earnings['payable_amount'].values

    lin_model = LinearRegression()
    lin_model.fit(X, y)
    slope = float(lin_model.coef_[0])

    # Earnings volatility (clipped to reduce impact of outliers)
    changes = np.diff(y) / y[:-1]
    changes = np.clip(changes, -1, 1)
    volatility = np.std(changes)

    # Select forecast model based on slope
    use_exp = slope < -100

    if use_exp:
        t = (annual_earnings['distribution_year'] - annual_earnings['distribution_year'].min()).values.reshape(-1, 1)
        y_pos_mask = y > 0
        t_pos = t[y_pos_mask]
        log_y = np.log(y[y_pos_mask])

        exp_model = LinearRegression()
        exp_model.fit(t_pos, log_y)

        t_forecast = np.arange(t.max() + 1, t.max() + 1 + years_remaining).reshape(-1, 1)
        log_forecast = exp_model.predict(t_forecast)
        forecast_earnings = np.exp(log_forecast)
        trend = "Declining (Exponential)"
    else:
        forecast_years = np.arange(annual_earnings['distribution_year'].max() + 1, annual_earnings['distribution_year'].max() + years_remaining + 1).reshape(-1, 1)
        forecast_earnings = np.maximum(lin_model.predict(forecast_years), 0)
        trend = "Stable/Linear"

    # CAGR
    years_of_data = annual_earnings['distribution_year'].iloc[-1] - annual_earnings['distribution_year'].iloc[0]
    cagr = ((y[-1] / y[0]) ** (1 / years_of_data) - 1) if y[0] > 0 else 0

    # Valuation (Discounted Cash Flow)
    valuations = {}
    for rate in discount_rates:
        discounted_cash_flows = [earning / ((1 + rate) ** idx) for idx, earning in enumerate(forecast_earnings, start=1)]
        valuations[f"valuation_{int(rate*100)}%"] = float(sum(discounted_cash_flows))

    # Value Score based on Min Bid
    base_price = min_bid if min_bid > 0 else listing_price
    if base_price <= valuations['valuation_10%']:
        value_score = 10
    elif base_price <= valuations['valuation_12%']:
        value_score = 8
    elif base_price <= valuations['valuation_15%']:
        value_score = 6
    elif base_price > 0:
        value_score = 4
    else:
        value_score = 0

    # Market Score using better of Min Bid or List Price
    market_price = base_price if listing_price == 0 else min(min_bid or listing_price, listing_price)
    if market_price > 0:
        if market_price < marketplace_median and market_price < last_transaction:
            market_score = 10
        elif market_price < marketplace_median or market_price < last_transaction:
            market_score = 7
        elif abs(market_price - marketplace_median) < 500 or abs(market_price - last_transaction) < 500:
            market_score = 5
        else:
            market_score = 3
    else:
        market_score = 0

    # Trend Score
    if slope > 100 and volatility < 0.3:
        trend_score = 10
    elif abs(slope) < 50 and volatility < 0.3:
        trend_score = 8
    elif slope < -100 and volatility > 0.5:
        trend_score = 4
    elif volatility > 0.7:
        trend_score = 3
    else:
        trend_score = 6

    # Auction Score
    auction_score = 0
    if min_bid > 0:
        if min_bid <= valuations['valuation_15%']:
            auction_score += 2
        if min_bid <= valuations['valuation_10%']:
            auction_score += 1
    if slope < 0 and listing_price > last_transaction > 0:
        auction_score -= 2
    if 0 < listing_price < last_transaction:
        auction_score += 2

    # Final Rating Score
    final_score = (
        value_score * 0.4 +
        market_score * 0.25 +
        trend_score * 0.2 +
        auction_score * 0.15
    )

    if final_score >= 9:
        rating = "A+"
    elif final_score >= 8:
        rating = "A"
    elif final_score >= 7:
        rating = "B+"
    elif final_score >= 6:
        rating = "B"
    elif final_score >= 5:
        rating = "C"
    else:
        rating = "D"

    # Calculate implied annual return if list price is accepted
    implied_return = None
    if listing_price > 0 and sum(forecast_earnings) > 0:
        try:
            from scipy.optimize import newton
            def npv(rate):
                return sum([cf / (1 + rate) ** i for i, cf in enumerate(forecast_earnings, start=1)]) - listing_price
            implied_return = newton(npv, 0.1)
        except:
            implied_return = None

    results = {
        "Earnings Trend": trend,
        "CAGR": float(cagr),
        "Volatility": float(volatility),
        "Total Forecast": float(sum(forecast_earnings)),
        "Avg Annual Forecast": float(np.mean(forecast_earnings)),
        "Years Remaining": years_remaining,
        "Valuation 10%": valuations['valuation_10%'],
        "Valuation 12.5%": valuations['valuation_12%'],
        "Valuation 15%": valuations['valuation_15%'],
        "Listing Price": listing_price,
        "Min Bid": min_bid,
        "Last Transaction": last_transaction,
        "Marketplace Median": marketplace_median,
        "Value Score": value_score,
        "Market Score": market_score,
        "Trend Score": trend_score,
        "Auction Score": auction_score,
        "Rating": rating,
        "Implied Return (if Buy It Now)": round(implied_return * 100, 2) if implied_return is not None else "N/A"
    }

    # Optional: output to CSV for easier copy/paste
    if output_csv:
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(results.keys())
            writer.writerow(results.values())

    return results

