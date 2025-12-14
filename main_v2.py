"""
Finance App - Version 2: Category Analysis & Basic Reporting

This script:
1. Loads combined transaction data
2. Performs daily/monthly analysis
3. Creates category breakdowns
4. Generates spending reports
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_combined_csv
from src.analyzer import (
    get_daily_summary,
    get_monthly_summary,
    get_category_breakdown,
    get_income_vs_spending,
    get_top_merchants,
)
from src.reporter import (
    generate_text_report,
    save_report_csv,
    print_report,
)


def main():
    print("=" * 60)
    print("Finance App - Version 2: Category Analysis & Reporting")
    print("=" * 60)
    print()
    
    # Load combined data
    print("Loading transaction data...")
    try:
        df = load_combined_csv()
        print(f"  Loaded {len(df)} transactions")
    except FileNotFoundError:
        print("  Error: combined_transactions.csv not found.")
        print("  Please run main_v1.py first to generate the data.")
        return
    print()
    
    # Run analyses
    print("Running analysis...")
    print("-" * 40)
    
    analysis_results = {}
    
    # Daily summary
    print("  • Calculating daily summary...")
    analysis_results['daily'] = get_daily_summary(df)
    
    # Monthly summary
    print("  • Calculating monthly summary...")
    analysis_results['monthly'] = get_monthly_summary(df)
    
    # Category breakdown
    print("  • Analyzing spending by category...")
    analysis_results['categories'] = get_category_breakdown(df)
    
    # Income vs Spending
    print("  • Calculating income vs spending...")
    analysis_results['overall'] = get_income_vs_spending(df)
    
    # Top merchants
    print("  • Finding top merchants...")
    analysis_results['top_merchants'] = get_top_merchants(df)
    
    print()
    
    # Generate report
    print("Generating report...")
    print()
    
    report = generate_text_report(analysis_results)
    print_report(report)
    
    # Save CSV reports
    print()
    print("Saving CSV reports...")
    saved_files = save_report_csv(analysis_results)
    for path in saved_files:
        print(f"  • {path}")
    
    print()
    print("Version 2 complete! ✓")
    
    return analysis_results


if __name__ == '__main__':
    main()
