"""
Report generation module for Finance App
Creates formatted text and CSV reports
"""
import pandas as pd
import os
from src.config import REPORTS_DIR


def generate_text_report(analysis_results):
    """
    Generate a formatted text report from analysis results.
    
    Args:
        analysis_results: Dictionary with analysis data
        
    Returns:
        str: Formatted report text
    """
    lines = []
    
    lines.append("=" * 70)
    lines.append("FINANCE REPORT - SPENDING & INCOME ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    
    # Overall Summary
    if 'overall' in analysis_results:
        overall = analysis_results['overall']
        lines.append("📊 OVERALL SUMMARY")
        lines.append("-" * 40)
        lines.append(f"  Total Income:    £{overall['total_income']:,.2f}")
        lines.append(f"  Total Spending:  £{overall['total_spending']:,.2f}")
        lines.append(f"  Net Cash Flow:   £{overall['net_cash_flow']:,.2f}")
        lines.append("")
        lines.append(f"  Income transactions:   {overall['income_count']}")
        lines.append(f"  Spending transactions: {overall['spending_count']}")
        lines.append(f"  Average spending:      £{overall['average_spending']:,.2f}")
        lines.append("")
    
    # Monthly Summary
    if 'monthly' in analysis_results:
        monthly = analysis_results['monthly']
        lines.append("📅 MONTHLY BREAKDOWN")
        lines.append("-" * 40)
        lines.append(f"  {'Month':<12} {'Spending':>12} {'Income':>12} {'Net':>12}")
        lines.append("  " + "-" * 50)
        for _, row in monthly.iterrows():
            net_symbol = "+" if row['net'] >= 0 else ""
            lines.append(f"  {str(row['month']):<12} £{row['spending']:>10,.2f} £{row['income']:>10,.2f} {net_symbol}£{row['net']:>9,.2f}")
        lines.append("")
    
    # Category Breakdown
    if 'categories' in analysis_results:
        categories = analysis_results['categories']
        lines.append("🏷️  SPENDING BY CATEGORY")
        lines.append("-" * 40)
        lines.append(f"  {'Category':<20} {'Total':>12} {'%':>8} {'Count':>8}")
        lines.append("  " + "-" * 50)
        for _, row in categories.head(15).iterrows():
            lines.append(f"  {row['category'][:20]:<20} £{row['total']:>10,.2f} {row['percentage']:>7.1f}% {row['count']:>7}")
        lines.append("")
    
    # Top Merchants
    if 'top_merchants' in analysis_results:
        merchants = analysis_results['top_merchants']
        lines.append("🏪 TOP MERCHANTS BY SPENDING")
        lines.append("-" * 40)
        lines.append(f"  {'Merchant':<25} {'Total':>12} {'Count':>8}")
        lines.append("  " + "-" * 47)
        for _, row in merchants.iterrows():
            lines.append(f"  {row['merchant'][:25]:<25} £{row['total']:>10,.2f} {row['count']:>7}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def save_report_csv(analysis_results, filename_prefix="report"):
    """
    Save analysis results as CSV files.
    
    Args:
        analysis_results: Dictionary with analysis data
        filename_prefix: Prefix for output files
        
    Returns:
        list: Paths of saved files
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    saved_files = []
    
    if 'monthly' in analysis_results:
        path = os.path.join(REPORTS_DIR, f"{filename_prefix}_monthly.csv")
        df = analysis_results['monthly'].copy()
        df['month'] = df['month'].astype(str)
        df.to_csv(path, index=False)
        saved_files.append(path)
    
    if 'categories' in analysis_results:
        path = os.path.join(REPORTS_DIR, f"{filename_prefix}_categories.csv")
        analysis_results['categories'].to_csv(path, index=False)
        saved_files.append(path)
    
    if 'top_merchants' in analysis_results:
        path = os.path.join(REPORTS_DIR, f"{filename_prefix}_merchants.csv")
        analysis_results['top_merchants'].to_csv(path, index=False)
        saved_files.append(path)
    
    if 'daily' in analysis_results:
        path = os.path.join(REPORTS_DIR, f"{filename_prefix}_daily.csv")
        analysis_results['daily'].to_csv(path, index=False)
        saved_files.append(path)
    
    return saved_files


def print_report(report_text):
    """Print the report to console."""
    print(report_text)
