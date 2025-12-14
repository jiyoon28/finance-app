"""
Visualization module for Finance App
Creates charts and graphs using matplotlib
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from src.config import CHARTS_DIR


# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12


def plot_monthly_spending(monthly_df, save_path=None):
    """
    Create bar chart of monthly spending and income.
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    months = [str(m) for m in monthly_df['month']]
    x = range(len(months))
    width = 0.35
    
    # Plot bars
    bars1 = ax.bar([i - width/2 for i in x], monthly_df['spending'], width, 
                   label='Spending', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], monthly_df['income'], width,
                   label='Income', color='#2ecc71', alpha=0.8)
    
    # Customize
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount (£)')
    ax.set_title('Monthly Spending vs Income')
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    
    plt.close()
    return fig


def plot_category_pie(categories_df, save_path=None):
    """
    Create pie chart of spending by category.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Get top 8 categories, group rest as "Other"
    top_categories = categories_df.head(8).copy()
    if len(categories_df) > 8:
        other_total = categories_df.iloc[8:]['total'].sum()
        other_row = pd.DataFrame({'category': ['Other'], 'total': [other_total]})
        top_categories = pd.concat([top_categories, other_row], ignore_index=True)
    
    # Colors
    colors = plt.cm.Set3(range(len(top_categories)))
    
    # Create pie
    wedges, texts, autotexts = ax.pie(
        top_categories['total'],
        labels=top_categories['category'],
        autopct='%1.1f%%',
        colors=colors,
        explode=[0.02] * len(top_categories),
        pctdistance=0.75,
    )
    
    ax.set_title('Spending by Category')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    
    plt.close()
    return fig


def plot_income_vs_spending_trend(monthly_df, save_path=None):
    """
    Create line chart of income vs spending over time.
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    months = range(len(monthly_df))
    
    # Plot lines
    ax.plot(months, monthly_df['spending'], 'o-', label='Spending', 
            color='#e74c3c', linewidth=2, markersize=6)
    ax.plot(months, monthly_df['income'], 's-', label='Income',
            color='#2ecc71', linewidth=2, markersize=6)
    ax.plot(months, monthly_df['net'], '^--', label='Net Cash Flow',
            color='#3498db', linewidth=1.5, markersize=5, alpha=0.7)
    
    # Fill between
    ax.fill_between(months, 0, monthly_df['net'], 
                    where=monthly_df['net'] >= 0, alpha=0.2, color='green')
    ax.fill_between(months, 0, monthly_df['net'],
                    where=monthly_df['net'] < 0, alpha=0.2, color='red')
    
    # Zero line
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    
    # Customize
    month_labels = [str(m) for m in monthly_df['month']]
    ax.set_xticks(months)
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount (£)')
    ax.set_title('Cash Flow Trend Over Time')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    
    plt.close()
    return fig


def plot_quarterly_comparison(quarterly_df, save_path=None):
    """
    Create bar chart comparing quarters.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    quarters = [str(q) for q in quarterly_df['quarter']]
    x = range(len(quarters))
    
    # Grouped bars
    width = 0.25
    ax.bar([i - width for i in x], quarterly_df['spending'], width,
           label='Spending', color='#e74c3c', alpha=0.8)
    ax.bar(x, quarterly_df['income'], width,
           label='Income', color='#2ecc71', alpha=0.8)
    ax.bar([i + width for i in x], quarterly_df['net'], width,
           label='Net', color='#3498db', alpha=0.8)
    
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Amount (£)')
    ax.set_title('Quarterly Financial Summary')
    ax.set_xticks(x)
    ax.set_xticklabels(quarters, rotation=45, ha='right')
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    
    plt.close()
    return fig


def plot_top_merchants(merchants_df, save_path=None):
    """
    Create horizontal bar chart of top merchants.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Reverse for horizontal bar chart (top merchant at top)
    merchants = merchants_df['merchant'].tolist()[::-1]
    totals = merchants_df['total'].tolist()[::-1]
    
    colors = plt.cm.Reds([0.3 + 0.5 * i / len(merchants) for i in range(len(merchants))])
    
    ax.barh(merchants, totals, color=colors, alpha=0.8)
    
    # Add value labels
    for i, (name, val) in enumerate(zip(merchants, totals)):
        ax.text(val + 5, i, f'£{val:,.0f}', va='center', fontsize=9)
    
    ax.set_xlabel('Total Spending (£)')
    ax.set_title('Top 10 Merchants by Spending')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    
    plt.close()
    return fig


def save_all_charts(analysis_results, output_dir=None):
    """
    Generate and save all charts.
    
    Returns:
        list: Paths of saved chart files
    """
    if output_dir is None:
        output_dir = CHARTS_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []
    
    if 'monthly' in analysis_results:
        path = os.path.join(output_dir, 'monthly_spending_income.png')
        plot_monthly_spending(analysis_results['monthly'], path)
        saved_files.append(path)
        
        path = os.path.join(output_dir, 'cash_flow_trend.png')
        plot_income_vs_spending_trend(analysis_results['monthly'], path)
        saved_files.append(path)
    
    if 'categories' in analysis_results:
        path = os.path.join(output_dir, 'category_breakdown.png')
        plot_category_pie(analysis_results['categories'], path)
        saved_files.append(path)
    
    if 'quarterly' in analysis_results:
        path = os.path.join(output_dir, 'quarterly_comparison.png')
        plot_quarterly_comparison(analysis_results['quarterly'], path)
        saved_files.append(path)
    
    if 'top_merchants' in analysis_results:
        path = os.path.join(output_dir, 'top_merchants.png')
        plot_top_merchants(analysis_results['top_merchants'], path)
        saved_files.append(path)
    
    return saved_files
