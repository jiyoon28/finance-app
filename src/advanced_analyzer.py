"""
Advanced analysis module for Finance App
Provides quarterly, yearly analysis and trend detection
"""
import pandas as pd
from datetime import datetime


def get_quarterly_summary(df):
    """
    Get quarterly spending and income totals.
    
    Returns:
        pd.DataFrame: Quarterly summary with spending, income, and net
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['quarter'] = df['date'].dt.to_period('Q')
    
    # Separate spending and income
    spending = df[~df['is_income']].groupby('quarter')['amount_gbp'].sum().abs()
    income = df[df['is_income']].groupby('quarter')['amount_gbp'].sum()
    
    # Combine into summary
    summary = pd.DataFrame({
        'spending': spending,
        'income': income,
    }).fillna(0)
    
    summary['net'] = summary['income'] - summary['spending']
    summary = summary.reset_index()
    summary.columns = ['quarter', 'spending', 'income', 'net']
    
    return summary.sort_values('quarter')


def get_yearly_summary(df):
    """
    Get yearly spending and income totals.
    
    Returns:
        pd.DataFrame: Yearly summary with spending, income, and net
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    # Separate spending and income
    spending = df[~df['is_income']].groupby('year')['amount_gbp'].sum().abs()
    income = df[df['is_income']].groupby('year')['amount_gbp'].sum()
    
    # Combine into summary
    summary = pd.DataFrame({
        'spending': spending,
        'income': income,
    }).fillna(0)
    
    summary['net'] = summary['income'] - summary['spending']
    summary = summary.reset_index()
    summary.columns = ['year', 'spending', 'income', 'net']
    
    return summary.sort_values('year')


def get_trend_analysis(df):
    """
    Calculate month-over-month spending changes.
    
    Returns:
        pd.DataFrame: Monthly trends with percentage changes
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M')
    
    # Get monthly spending
    monthly_spending = df[~df['is_income']].groupby('year_month')['amount_gbp'].sum().abs()
    
    trend_df = pd.DataFrame({
        'month': monthly_spending.index,
        'spending': monthly_spending.values,
    })
    
    # Calculate month-over-month change
    trend_df['change'] = trend_df['spending'].diff()
    trend_df['change_pct'] = trend_df['spending'].pct_change() * 100
    
    # Moving average (3-month)
    trend_df['moving_avg_3m'] = trend_df['spending'].rolling(window=3, min_periods=1).mean()
    
    return trend_df


def get_category_trends(df, top_n=5):
    """
    Get monthly spending trends for top categories.
    
    Returns:
        pd.DataFrame: Category spending by month
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M')
    
    # Get top categories
    top_categories = (
        df[~df['is_income']]
        .groupby('category')['amount_gbp']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )
    
    # Filter to top categories
    filtered = df[(~df['is_income']) & (df['category'].isin(top_categories))]
    
    # Pivot by month and category
    pivot = filtered.pivot_table(
        values='amount_gbp',
        index='year_month',
        columns='category',
        aggfunc='sum',
        fill_value=0
    ).abs()
    
    return pivot.reset_index()
