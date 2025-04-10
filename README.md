
# Royalty Exchange Deal Analyzer

This tool analyzes royalty listing deals from [RoyaltyExchange.com](https://royaltyexchange.com) using historical earnings CSV files and listing metadata.

It produces:
- Forecasted future earnings using either linear or exponential decay modeling
- Valuation based on discounted cash flows (10%, 12.5%, and 15% discount rates)
- Custom rating system (A+ to D) based on value, market comps, trend, and auction dynamics
- Implied IRR (annual return) if the Buy It Now price is accepted

## 📦 Usage

### Interactive Mode
```bash
python3 run.py
```

Prompts for inputs and saves them to a listing data file.

### File Mode
```bash
python3 run.py 6120_listing_data
```

Reads saved inputs and skips prompts.

## 📂 Input Files

- **Earnings CSV**: Named like `6120_earnings.csv`
- **Listing Data**: A `.txt` file with:
  ```
  <Listing ID>
  <Path to earnings CSV>
  <Years Remaining>
  <Listing Price>
  <Min Bid>
  <Last Transaction>
  <Marketplace Median>
  ```

## 📤 Outputs

- `[ListingID]_[Rating]_deal_summary.csv`
- Includes valuation, rating, scores, and implied IRR

## 🧠 Notes

- Forecasting model selection is based on earnings slope
- Volatility is clipped to +/- 100% to reduce the impact of outliers
