"""
Finance App - Version 1: Data Loading & Currency Conversion

This script:
1. Loads Monzo bank CSV (GBP)
2. Loads Korean bank Excel (KRW) - requires password if encrypted
3. Converts KRW to GBP
4. Merges and saves as combined_transactions.csv
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import (
    load_monzo_csv,
    load_korean_excel,
    normalize_and_merge,
    save_combined_csv,
)
from src.config import KRW_TO_GBP_RATE


def main():
    print("=" * 60)
    print("Finance App - Version 1: Data Loading & Currency Conversion")
    print("=" * 60)
    print()
    
    # Load Monzo data
    print("Step 1: Loading Monzo bank data (GBP)")
    print("-" * 40)
    monzo_df = load_monzo_csv()
    print()
    
    # Load Korean bank data
    print("Step 2: Loading Korean bank data (KRW)")
    print("-" * 40)
    
    # Check if password is provided via environment variable or command line
    password = os.environ.get('KOREAN_BANK_PASSWORD')
    if len(sys.argv) > 1:
        password = sys.argv[1]
    
    korean_df = load_korean_excel(password=password)
    
    if korean_df.empty:
        print("\n  Note: Korean bank data not loaded.")
        print("  To include Korean bank data, either:")
        print("    1. Set KOREAN_BANK_PASSWORD environment variable")
        print("    2. Run: python main_v1.py <password>")
        print("    3. Export the Excel as unencrypted CSV")
    print()
    
    # Merge data
    print("Step 3: Merging data sources")
    print("-" * 40)
    combined_df = normalize_and_merge(monzo_df, korean_df)
    print()
    
    # Save to CSV
    print("Step 4: Saving combined data")
    print("-" * 40)
    output_path = save_combined_csv(combined_df)
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Monzo transactions:  {len(monzo_df)}")
    print(f"  Korean transactions: {len(korean_df)}")
    print(f"  Total transactions:  {len(combined_df)}")
    print(f"  Exchange rate used:  1 GBP = {1/KRW_TO_GBP_RATE:.0f} KRW")
    print(f"  Output file:         {output_path}")
    print()
    
    # Show sample data
    if not combined_df.empty:
        print("Sample data (first 5 rows):")
        print("-" * 40)
        print(combined_df[['date', 'bank', 'merchant', 'amount_gbp', 'is_income']].head().to_string())
    
    print()
    print("Version 1 complete! ✓")
    
    return combined_df


if __name__ == '__main__':
    main()
