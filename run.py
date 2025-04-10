import os
import sys
from analysis import analyze_and_value_royalty

# Load inputs from file if provided
if len(sys.argv) > 1:
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        lines = f.read().splitlines()
        listing_id = lines[0].strip()
        csv_file = lines[1].strip()
        years_remaining = float(lines[2].strip())
        listing_price = float(lines[3].strip())
        min_bid = float(lines[4].strip())
        last_transaction = float(lines[5].strip())
        marketplace_median = float(lines[6].strip())

    # Try renamed file if original is missing
    if not os.path.exists(csv_file):
        alt_csv = f"{listing_id}_earnings.csv"
        if os.path.exists(alt_csv):
            csv_file = alt_csv
        else:
            print(f"CSV file not found: {csv_file} or {alt_csv}")
            sys.exit(1)
else:
    listing_id = input("Enter the Listing ID: ").strip()
    csv_file = input("Enter the path to the royalty earnings CSV file: ").strip()
    years_remaining = float(input("Enter the number of years remaining on the contract: "))
    listing_price = float(input("Enter the listing price (or 0 if not applicable): "))
    min_bid = float(input("Enter the minimum bid (or 0 if not applicable): "))
    last_transaction = float(input("Enter the last transaction price (or 0 if unknown): "))
    marketplace_median = float(input("Enter the marketplace median value (or 0 if unknown): "))

    # Save inputs to file
    input_filename = f"{listing_id}_listing_data"
    with open(input_filename, 'w') as f:
        f.write("\n".join([
            listing_id,
            csv_file,
            str(years_remaining),
            str(listing_price),
            str(min_bid),
            str(last_transaction),
            str(marketplace_median)
        ]))

# Run analysis
results = analyze_and_value_royalty(
    csv_file=csv_file,
    years_remaining=years_remaining,
    listing_price=listing_price,
    min_bid=min_bid,
    last_transaction=last_transaction,
    marketplace_median=marketplace_median
)

# Rename original file to [ListingID]_earnings.csv
earnings_file_renamed = f"{listing_id}_earnings.csv"
if os.path.exists(csv_file) and csv_file != earnings_file_renamed:
    os.rename(csv_file, earnings_file_renamed)

# Define output CSV filename with rating
rating = results.get("Rating", "Unrated")
output_csv = f"{listing_id}_{rating}_deal_summary.csv"

# Save results to CSV
with open(output_csv, mode='w', newline='') as file:
    import csv
    writer = csv.writer(file)
    writer.writerow(results.keys())
    writer.writerow(results.values())

# Print results
print("\n--- Deal Analysis Summary ---")
for key, value in results.items():
    print(f"{key}: {value}")

