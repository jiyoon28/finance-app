"""
Analysis module for Finance App
Provides spending/income analysis by category and time period
"""
import pandas as pd
from datetime import datetime


def get_daily_summary(df):
    """
    Get daily spending and income totals.
    
    Returns:
        pd.DataFrame: Daily summary with spending, income, and net
    """
    df = df.copy()
    df['date_only'] = pd.to_datetime(df['date']).dt.date
    
    # Separate spending and income
    spending = df[~df['is_income']].groupby('date_only')['amount_gbp'].sum().abs()
    income = df[df['is_income']].groupby('date_only')['amount_gbp'].sum()
    
    # Combine into summary
    summary = pd.DataFrame({
        'spending': spending,
        'income': income,
    }).fillna(0)
    
    summary['net'] = summary['income'] - summary['spending']
    summary = summary.reset_index()
    summary.columns = ['date', 'spending', 'income', 'net']
    
    return summary.sort_values('date')


def get_monthly_summary(df):
    """
    Get monthly spending and income totals.
    
    Returns:
        pd.DataFrame: Monthly summary with spending, income, and net
    """
    df = df.copy()
    df['year_month'] = pd.to_datetime(df['date']).dt.to_period('M')
    
    # Separate spending and income
    spending = df[~df['is_income']].groupby('year_month')['amount_gbp'].sum().abs()
    income = df[df['is_income']].groupby('year_month')['amount_gbp'].sum()
    
    # Combine into summary
    summary = pd.DataFrame({
        'spending': spending,
        'income': income,
    }).fillna(0)
    
    summary['net'] = summary['income'] - summary['spending']
    summary = summary.reset_index()
    summary.columns = ['month', 'spending', 'income', 'net']
    
    return summary.sort_values('month')


def get_category_breakdown(df, period=None):
    """
    Get spending breakdown by category.
    
    Args:
        df: Transaction dataframe
        period: Optional period to filter ('month', 'quarter', 'year' with value like '2024-10')
    
    Returns:
        pd.DataFrame: Category breakdown with total spending and percentage
    """
    # Filter to spending only (negative amounts)
    spending_df = df[~df['is_income']].copy()
    
    if spending_df.empty:
        return pd.DataFrame(columns=['category', 'total', 'percentage', 'count'])
    
    # Group by category
    category_totals = spending_df.groupby('category').agg({
        'amount_gbp': ['sum', 'count']
    }).reset_index()
    
    category_totals.columns = ['category', 'total', 'count']
    category_totals['total'] = category_totals['total'].abs()
    
    # Calculate percentage
    total_spending = category_totals['total'].sum()
    category_totals['percentage'] = (category_totals['total'] / total_spending * 100).round(1)
    
    # Sort by total spending
    category_totals = category_totals.sort_values('total', ascending=False)
    
    return category_totals


def get_income_vs_spending(df):
    """
    Get overall income vs spending comparison.
    
    Returns:
        dict: Summary statistics
    """
    spending = df[~df['is_income']]['amount_gbp'].sum()
    income = df[df['is_income']]['amount_gbp'].sum()
    
    return {
        'total_spending': abs(spending),
        'total_income': income,
        'net_cash_flow': income + spending,  # spending is negative
        'spending_count': len(df[~df['is_income']]),
        'income_count': len(df[df['is_income']]),
        'average_spending': abs(spending) / max(1, len(df[~df['is_income']])),
        'average_income': income / max(1, len(df[df['is_income']])),
    }


def get_top_merchants(df, n=10):
    """
    Get top merchants by spending.
    
    Returns:
        pd.DataFrame: Top merchants with total spending
    """
    spending_df = df[~df['is_income']].copy()
    
    merchant_totals = spending_df.groupby('merchant').agg({
        'amount_gbp': ['sum', 'count']
    }).reset_index()
    
    merchant_totals.columns = ['merchant', 'total', 'count']
    merchant_totals['total'] = merchant_totals['total'].abs()
    
    return merchant_totals.sort_values('total', ascending=False).head(n)
