"""
Finance App - Version 3: Advanced Analytics & Visualization

This script:
1. Loads combined transaction data
2. Runs all analyses (daily, monthly, quarterly, yearly)
3. Generates visualizations
4. Creates comprehensive dashboard summary
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
from src.advanced_analyzer import (
    get_quarterly_summary,
    get_yearly_summary,
    get_trend_analysis,
)
from src.reporter import (
    generate_text_report,
    save_report_csv,
)
from src.visualizer import save_all_charts


def print_advanced_summary(results):
    """Print advanced analytics summary."""
    print()
    print("=" * 70)
    print("ADVANCED ANALYTICS SUMMARY")
    print("=" * 70)
    
    # Quarterly summary
    if 'quarterly' in results:
        print()
        print("📊 QUARTERLY BREAKDOWN")
        print("-" * 50)
        print(f"  {'Quarter':<12} {'Spending':>12} {'Income':>12} {'Net':>12}")
        print("  " + "-" * 50)
        for _, row in results['quarterly'].iterrows():
            net_symbol = "+" if row['net'] >= 0 else ""
            print(f"  {str(row['quarter']):<12} £{row['spending']:>10,.2f} £{row['income']:>10,.2f} {net_symbol}£{row['net']:>9,.2f}")
    
    # Yearly summary
    if 'yearly' in results:
        print()
        print("📅 YEARLY BREAKDOWN")
        print("-" * 50)
        print(f"  {'Year':<12} {'Spending':>12} {'Income':>12} {'Net':>12}")
        print("  " + "-" * 50)
        for _, row in results['yearly'].iterrows():
            net_symbol = "+" if row['net'] >= 0 else ""
            print(f"  {row['year']:<12} £{row['spending']:>10,.2f} £{row['income']:>10,.2f} {net_symbol}£{row['net']:>9,.2f}")
    
    # Trend analysis
    if 'trends' in results and len(results['trends']) > 1:
        trends = results['trends']
        print()
        print("📈 SPENDING TRENDS")
        print("-" * 50)
        
        # Most expensive month
        max_idx = trends['spending'].idxmax()
        print(f"  Highest spending month: {trends.loc[max_idx, 'month']} (£{trends.loc[max_idx, 'spending']:,.2f})")
        
        # Lowest spending month (excluding 0)
        non_zero = trends[trends['spending'] > 0]
        if not non_zero.empty:
            min_idx = non_zero['spending'].idxmin()
            print(f"  Lowest spending month:  {non_zero.loc[min_idx, 'month']} (£{non_zero.loc[min_idx, 'spending']:,.2f})")
        
        # Average
        avg = trends['spending'].mean()
        print(f"  Average monthly spend:  £{avg:,.2f}")
        
        # 3-month moving average (latest)
        latest_ma = trends['moving_avg_3m'].iloc[-1]
        print(f"  Current 3-month avg:    £{latest_ma:,.2f}")
    
    print()
    print("=" * 70)


def main():
    print("=" * 70)
    print("Finance App - Version 3: Advanced Analytics & Visualization")
    print("=" * 70)
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
    
    # Run all analyses
    print("Running comprehensive analysis...")
    print("-" * 40)
    
    analysis_results = {}
    
    # Basic analyses (from v2)
    print("  • Daily summary...")
    analysis_results['daily'] = get_daily_summary(df)
    
    print("  • Monthly summary...")
    analysis_results['monthly'] = get_monthly_summary(df)
    
    print("  • Category breakdown...")
    analysis_results['categories'] = get_category_breakdown(df)
    
    print("  • Income vs spending...")
    analysis_results['overall'] = get_income_vs_spending(df)
    
    print("  • Top merchants...")
    analysis_results['top_merchants'] = get_top_merchants(df)
    
    # Advanced analyses (v3)
    print("  • Quarterly summary...")
    analysis_results['quarterly'] = get_quarterly_summary(df)
    
    print("  • Yearly summary...")
    analysis_results['yearly'] = get_yearly_summary(df)
    
    print("  • Trend analysis...")
    analysis_results['trends'] = get_trend_analysis(df)
    
    print()
    
    # Generate standard report
    print("Generating reports...")
    report = generate_text_report(analysis_results)
    print(report)
    
    # Print advanced summary
    print_advanced_summary(analysis_results)
    
    # Save reports
    print()
    print("Saving reports...")
    saved_reports = save_report_csv(analysis_results)
    for path in saved_reports:
        print(f"  • {path}")
    
    # Generate visualizations
    print()
    print("Generating visualizations...")
    saved_charts = save_all_charts(analysis_results)
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total transactions analyzed: {len(df)}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Reports saved: {len(saved_reports)} files")
    print(f"  Charts saved:  {len(saved_charts)} files")
    print()
    print("Output locations:")
    print("  • Reports: output/reports/")
    print("  • Charts:  output/charts/")
    print()
    print("Version 3 complete! ✓")
    
    return analysis_results


if __name__ == '__main__':
    main()
