"""
Configuration settings for Finance App
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data file paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
MONZO_CSV_PATH = os.path.join(DATA_DIR, 'Monzo Data Export - CSV (Sunday, 14 December 2025).csv')
KOREAN_EXCEL_PATH = os.path.join(DATA_DIR, 'TravelWallet Data Export.xlsx')
COMBINED_CSV_PATH = os.path.join(DATA_DIR, 'combined_transactions.csv')

# Output directories
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')

# Currency conversion rate
# 1 GBP = 1750 KRW (approximate rate)
KRW_TO_GBP_RATE = 1 / 1750

# Monzo CSV column mappings
MONZO_COLUMNS = {
    'date': 'Date',
    'time': 'Time',
    'type': 'Type',
    'merchant': 'Name',
    'category': 'Category',
    'amount': 'Amount',
    'currency': 'Currency',
    'money_out': 'Money Out',
    'money_in': 'Money In',
}

# Korean bank column mappings (TravelWallet)
KOREAN_COLUMNS = {
    'merchant': '가맹점 이름(Name of the merchant)',
    'payment_type': '종류(Payment type)',
    # The amount column is typically the last column
}

# Korean income identifier
KOREAN_INCOME_TYPE = 'charge'  # "charge" means money added from another bank
