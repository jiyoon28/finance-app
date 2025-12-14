"""
Data loading module for Finance App
Handles loading data from Monzo CSV and Korean bank Excel files
"""
import pandas as pd
import os
import io
from datetime import datetime

try:
    import msoffcrypto
    HAS_MSOFFCRYPTO = True
except ImportError:
    HAS_MSOFFCRYPTO = False

from src.config import (
    MONZO_CSV_PATH,
    KOREAN_EXCEL_PATH,
    COMBINED_CSV_PATH,
    KRW_TO_GBP_RATE,
    MONZO_COLUMNS,
    KOREAN_COLUMNS,
    KOREAN_INCOME_TYPE,
)


def load_monzo_csv(filepath=None):
    """
    Load and parse Monzo bank CSV file.
    
    Returns:
        pd.DataFrame: Normalized transaction data
    """
    if filepath is None:
        filepath = MONZO_CSV_PATH
    
    print(f"Loading Monzo CSV from: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Parse date
    df['date'] = pd.to_datetime(df[MONZO_COLUMNS['date']], format='%d/%m/%Y')
    
    # Create normalized dataframe
    normalized = pd.DataFrame({
        'date': df['date'],
        'time': df[MONZO_COLUMNS['time']],
        'bank': 'Monzo',
        'type': df[MONZO_COLUMNS['type']],
        'merchant': df[MONZO_COLUMNS['merchant']],
        'category': df[MONZO_COLUMNS['category']],
        'amount_gbp': df[MONZO_COLUMNS['amount']].astype(float),
        'original_currency': 'GBP',
        'original_amount': df[MONZO_COLUMNS['amount']].astype(float),
    })
    
    # Determine if income or expense
    money_in = df[MONZO_COLUMNS['money_in']].fillna(0).astype(float)
    normalized['is_income'] = money_in > 0
    
    print(f"  Loaded {len(normalized)} transactions from Monzo")
    
    return normalized


def load_korean_excel(filepath=None, password=None):
    """
    Load and parse Korean bank (TravelWallet) Excel file.
    The file is password-protected.
    
    Args:
        filepath: Path to Excel file
        password: Password to decrypt the file
        
    Returns:
        pd.DataFrame: Normalized transaction data with amounts converted to GBP
    """
    if filepath is None:
        filepath = KOREAN_EXCEL_PATH
    
    print(f"Loading Korean bank Excel from: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  Warning: File not found: {filepath}")
        return pd.DataFrame()
    
    try:
        if password and HAS_MSOFFCRYPTO:
            # Decrypt the file
            decrypted = io.BytesIO()
            with open(filepath, 'rb') as f:
                file = msoffcrypto.OfficeFile(f)
                file.load_key(password=password)
                file.decrypt(decrypted)
            decrypted.seek(0)
            df = pd.read_excel(decrypted, engine='openpyxl')
        else:
            # Try to read directly (may fail if encrypted)
            df = pd.read_excel(filepath, engine='openpyxl')
    except Exception as e:
        print(f"  Error loading Korean Excel: {e}")
        print("  The file may be password-protected. Please provide the password.")
        return pd.DataFrame()
    
    if df.empty:
        print("  No data loaded from Korean bank file")
        return pd.DataFrame()
    
    # Find the amount column (typically the last numeric column)
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        print("  Warning: No numeric columns found for amount")
        return pd.DataFrame()
    
    amount_col = numeric_cols[-1]  # Last numeric column
    print(f"  Using '{amount_col}' as amount column")
    
    # Get merchant/category column
    merchant_col = None
    for col in df.columns:
        if '가맹점' in str(col) or 'merchant' in str(col).lower():
            merchant_col = col
            break
    
    # Get payment type column
    payment_type_col = None
    for col in df.columns:
        if '종류' in str(col) or 'type' in str(col).lower():
            payment_type_col = col
            break
    
    # Get date column
    date_col = None
    for col in df.columns:
        if '날짜' in str(col) or 'date' in str(col).lower():
            date_col = col
            break
    
    # Create normalized dataframe
    normalized = pd.DataFrame({
        'date': pd.to_datetime(df[date_col]) if date_col else pd.NaT,
        'time': '',
        'bank': 'TravelWallet (Korea)',
        'type': df[payment_type_col] if payment_type_col else '',
        'merchant': df[merchant_col] if merchant_col else '',
        'category': df[merchant_col] if merchant_col else '',  # Use merchant as category
        'original_currency': 'KRW',
        'original_amount': df[amount_col].astype(float),
    })
    
    # Convert KRW to GBP
    normalized['amount_gbp'] = normalized['original_amount'] * KRW_TO_GBP_RATE
    
    # Determine if income (when payment_type is "charge")
    if payment_type_col:
        normalized['is_income'] = df[payment_type_col].str.lower().str.strip() == KOREAN_INCOME_TYPE
    else:
        normalized['is_income'] = normalized['amount_gbp'] > 0
    
    print(f"  Loaded {len(normalized)} transactions from Korean bank")
    print(f"  Converted KRW to GBP using rate: 1 GBP = {1/KRW_TO_GBP_RATE:.0f} KRW")
    
    return normalized


def normalize_and_merge(monzo_df, korean_df):
    """
    Merge dataframes from both banks into a unified format.
    
    Returns:
        pd.DataFrame: Combined transaction data
    """
    print("\nMerging data from all sources...")
    
    dfs_to_merge = []
    
    if not monzo_df.empty:
        dfs_to_merge.append(monzo_df)
    
    if not korean_df.empty:
        dfs_to_merge.append(korean_df)
    
    if not dfs_to_merge:
        print("  No data to merge!")
        return pd.DataFrame()
    
    combined = pd.concat(dfs_to_merge, ignore_index=True)
    
    # Sort by date
    combined = combined.sort_values('date').reset_index(drop=True)
    
    print(f"  Total transactions: {len(combined)}")
    
    return combined


def save_combined_csv(df, filepath=None):
    """
    Save the combined dataframe to CSV.
    """
    if filepath is None:
        filepath = COMBINED_CSV_PATH
    
    # Format date for output
    df_out = df.copy()
    df_out['date'] = df_out['date'].dt.strftime('%Y-%m-%d')
    
    df_out.to_csv(filepath, index=False)
    print(f"\nSaved combined data to: {filepath}")
    
    return filepath


def load_combined_csv(filepath=None):
    """
    Load the previously saved combined CSV.
    """
    if filepath is None:
        filepath = COMBINED_CSV_PATH
    
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    
    return df
