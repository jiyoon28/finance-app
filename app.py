"""
Finance Web App - Flask Application
Interactive dashboard for spending/income analysis
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import COMBINED_CSV_PATH, DATA_DIR, KRW_TO_GBP_RATE

# Upload history file path
UPLOAD_HISTORY_PATH = os.path.join(DATA_DIR, 'upload_history.json')
from src.data_loader import load_combined_csv, save_combined_csv
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
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Global dataframe cache
_df_cache = None
_df_cache_time = None


def get_data():
    """Load and cache transaction data."""
    global _df_cache, _df_cache_time
    
    # Check if file was modified
    try:
        file_mtime = os.path.getmtime(COMBINED_CSV_PATH)
    except:
        file_mtime = 0
    
    if _df_cache is None or _df_cache_time != file_mtime:
        try:
            _df_cache = load_combined_csv()
            _df_cache_time = file_mtime
        except FileNotFoundError:
            _df_cache = pd.DataFrame()
    
    return _df_cache


def reload_data():
    """Force reload data from file."""
    global _df_cache, _df_cache_time
    _df_cache = None
    _df_cache_time = None
    return get_data()


def get_upload_history():
    """Load upload history from JSON file."""
    try:
        if os.path.exists(UPLOAD_HISTORY_PATH):
            with open(UPLOAD_HISTORY_PATH, 'r') as f:
                return json.load(f)
    except:
        pass
    return {'files': []}


def save_upload_history(history):
    """Save upload history to JSON file."""
    with open(UPLOAD_HISTORY_PATH, 'w') as f:
        json.dump(history, f, indent=2)


def add_to_upload_history(filename, bank, transactions, currency):
    """Add a new file to upload history."""
    history = get_upload_history()
    
    # Check if file already exists and update it
    for file_entry in history['files']:
        if file_entry['filename'] == filename:
            file_entry['transactions'] = transactions
            file_entry['uploaded_at'] = datetime.now().isoformat()
            save_upload_history(history)
            return
    
    # Add new entry
    history['files'].append({
        'filename': filename,
        'bank': bank,
        'transactions': transactions,
        'currency': currency,
        'uploaded_at': datetime.now().isoformat(),
        'source': 'upload'
    })
    save_upload_history(history)


# ============== Pages ==============

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/category/<name>')
def category_detail(name):
    """Category detail page."""
    return render_template('category.html', category_name=name)


@app.route('/upload')
def upload_page():
    """File upload page."""
    return render_template('upload.html')


@app.route('/trends')
def trends_page():
    """Trends analysis page."""
    return render_template('trends.html')


# ============== API Endpoints ==============

@app.route('/api/summary')
def api_summary():
    """Get overall summary metrics."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    summary = get_income_vs_spending(df)
    
    # Add date range
    summary['date_from'] = df['date'].min().strftime('%Y-%m-%d')
    summary['date_to'] = df['date'].max().strftime('%Y-%m-%d')
    summary['transaction_count'] = len(df)
    
    return jsonify(summary)


@app.route('/api/monthly')
def api_monthly():
    """Get monthly breakdown."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    monthly = get_monthly_summary(df)
    monthly['month'] = monthly['month'].astype(str)
    
    return jsonify(monthly.to_dict(orient='records'))


@app.route('/api/quarterly')
def api_quarterly():
    """Get quarterly breakdown."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    quarterly = get_quarterly_summary(df)
    quarterly['quarter'] = quarterly['quarter'].astype(str)
    
    return jsonify(quarterly.to_dict(orient='records'))


@app.route('/api/yearly')
def api_yearly():
    """Get yearly breakdown."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    yearly = get_yearly_summary(df)
    yearly['year'] = yearly['year'].astype(int)
    
    return jsonify(yearly.to_dict(orient='records'))


@app.route('/api/categories')
def api_categories():
    """Get category breakdown."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    categories = get_category_breakdown(df)
    
    return jsonify(categories.to_dict(orient='records'))


@app.route('/api/category/<name>/<period>')
def api_category_detail(name, period):
    """Get category data for a specific time period."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    # Filter to category
    cat_df = df[df['category'].str.lower() == name.lower()].copy()
    
    if cat_df.empty:
        return jsonify({'error': f'Category "{name}" not found'})
    
    cat_df['date'] = pd.to_datetime(cat_df['date'])
    
    if period == 'daily':
        cat_df['period'] = cat_df['date'].dt.strftime('%Y-%m-%d')
    elif period == 'monthly':
        cat_df['period'] = cat_df['date'].dt.to_period('M').astype(str)
    elif period == 'quarterly':
        cat_df['period'] = cat_df['date'].dt.to_period('Q').astype(str)
    elif period == 'yearly':
        cat_df['period'] = cat_df['date'].dt.year.astype(str)
    else:
        return jsonify({'error': 'Invalid period. Use: daily, monthly, quarterly, yearly'})
    
    # Group by period
    grouped = cat_df.groupby('period').agg({
        'amount_gbp': 'sum',
    }).reset_index()
    
    grouped['amount_gbp'] = grouped['amount_gbp'].abs()
    grouped.columns = ['period', 'amount']
    
    # Get transactions for the table
    transactions = cat_df[['date', 'merchant', 'amount_gbp', 'type']].copy()
    transactions['date'] = transactions['date'].dt.strftime('%Y-%m-%d')
    transactions['amount_gbp'] = transactions['amount_gbp'].round(2)
    
    return jsonify({
        'chart_data': grouped.to_dict(orient='records'),
        'transactions': transactions.to_dict(orient='records'),
        'total': cat_df['amount_gbp'].abs().sum(),
        'count': len(cat_df),
    })


@app.route('/api/merchants')
def api_merchants():
    """Get top merchants."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    merchants = get_top_merchants(df, n=10)
    
    return jsonify(merchants.to_dict(orient='records'))


@app.route('/api/trends')
def api_trends():
    """Get spending trends data."""
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data loaded'})
    
    # Monthly spending by category
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    # Get top 5 categories
    top_cats = get_category_breakdown(df).head(5)['category'].tolist()
    
    # Filter to spending and top categories
    spending = df[(~df['is_income']) & (df['category'].isin(top_cats))]
    
    # Pivot
    pivot = spending.pivot_table(
        values='amount_gbp',
        index='month',
        columns='category',
        aggfunc='sum',
        fill_value=0
    ).abs()
    
    # Format for Chart.js
    result = {
        'labels': pivot.index.tolist(),
        'datasets': []
    }
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6']
    for i, cat in enumerate(pivot.columns):
        result['datasets'].append({
            'label': cat,
            'data': pivot[cat].tolist(),
            'borderColor': colors[i % len(colors)],
            'fill': False,
        })
    
    return jsonify(result)


@app.route('/api/upload-history')
def api_upload_history():
    """Get upload history with file statistics."""
    history = get_upload_history()
    
    # Calculate totals
    total_transactions = sum(f.get('transactions', 0) for f in history['files'])
    total_files = len(history['files'])
    
    return jsonify({
        'files': history['files'],
        'total_files': total_files,
        'total_transactions': total_transactions
    })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.csv'):
            # Read CSV
            content = file.read().decode('utf-8')
            new_df = pd.read_csv(io.StringIO(content))
            
            # Detect format and normalize
            new_df = normalize_uploaded_data(new_df, 'csv')
            
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            # Read Excel
            content = file.read()
            content_buffer = io.BytesIO(content)
            
            # Check if file is encrypted (CDFV2 format)
            content_buffer.seek(0)
            header = content_buffer.read(8)
            content_buffer.seek(0)
            
            # CDFV2 encrypted files start with D0 CF 11 E0
            is_encrypted = header[:4] == b'\xd0\xcf\x11\xe0'
            
            if is_encrypted:
                # Try to decrypt with msoffcrypto
                try:
                    import msoffcrypto
                    decrypted = io.BytesIO()
                    ms_file = msoffcrypto.OfficeFile(content_buffer)
                    
                    # Try empty password first (some files have no real password)
                    try:
                        ms_file.load_key(password='')
                        ms_file.decrypt(decrypted)
                        decrypted.seek(0)
                        new_df = pd.read_excel(decrypted, engine='openpyxl')
                    except:
                        return jsonify({
                            'error': 'This Excel file is password-protected. Please export it as an unencrypted CSV or provide the password via the CLI: KOREAN_BANK_PASSWORD=xxx python main_v1.py'
                        }), 400
                except ImportError:
                    return jsonify({
                        'error': 'This Excel file is password-protected. Please install msoffcrypto-tool or export as CSV.'
                    }), 400
            else:
                # Try openpyxl first for .xlsx, then xlrd for .xls
                try:
                    # First, try reading to detect format
                    test_df = pd.read_excel(content_buffer, engine='openpyxl', header=None, nrows=15)
                    content_buffer.seek(0)
                    
                    # Check if this is a Korean TravelWallet format (headers on row 12)
                    header_row = None
                    for i in range(min(15, len(test_df))):
                        row_vals = [str(v) for v in test_df.iloc[i].tolist() if pd.notna(v)]
                        if any('날짜' in v or '종류' in v or '가맹점' in v for v in row_vals):
                            header_row = i
                            break
                    
                    if header_row is not None:
                        # Korean format - read with correct header row
                        new_df = pd.read_excel(content_buffer, engine='openpyxl', header=header_row)
                    else:
                        new_df = pd.read_excel(content_buffer, engine='openpyxl')
                        
                except Exception as e1:
                    content_buffer.seek(0)
                    try:
                        new_df = pd.read_excel(content_buffer, engine='xlrd')
                    except Exception as e2:
                        return jsonify({'error': f'Failed to read Excel file. Error: {str(e1)}'}), 400
            
            # Detect format and normalize
            new_df = normalize_uploaded_data(new_df, 'excel')
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or Excel.'}), 400
        
        if new_df.empty:
            return jsonify({'error': 'No valid data found in file'}), 400
        
        # Load existing data and append
        try:
            existing_df = load_combined_csv()
            combined = pd.concat([existing_df, new_df], ignore_index=True)
            combined = combined.drop_duplicates()
        except:
            combined = new_df
        
        # Detect bank type for history
        bank_type = 'Unknown'
        currency = 'GBP'
        if 'bank' in new_df.columns:
            bank_type = new_df['bank'].iloc[0] if len(new_df) > 0 else 'Unknown'
        if 'original_currency' in new_df.columns:
            currency = new_df['original_currency'].iloc[0] if len(new_df) > 0 else 'GBP'
        
        # Save
        save_combined_csv(combined)
        reload_data()
        
        # Update upload history
        add_to_upload_history(file.filename, bank_type, len(new_df), currency)
        
        return jsonify({
            'success': True,
            'message': f'Added {len(new_df)} transactions',
            'total': len(combined),
            'bank': bank_type,
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def normalize_uploaded_data(df, source_type):
    """Normalize uploaded data to match our schema."""
    normalized = pd.DataFrame()
    
    # Try to detect Monzo format
    if 'Transaction ID' in df.columns or 'Date' in df.columns:
        # Monzo format
        if 'Date' in df.columns:
            normalized['date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        if 'Time' in df.columns:
            normalized['time'] = df['Time']
        else:
            normalized['time'] = ''
        
        normalized['bank'] = 'Monzo'
        normalized['type'] = df.get('Type', '')
        normalized['merchant'] = df.get('Name', '')
        normalized['category'] = df.get('Category', 'Other')
        
        if 'Amount' in df.columns:
            normalized['amount_gbp'] = pd.to_numeric(df['Amount'], errors='coerce')
        elif 'Money Out' in df.columns:
            out = pd.to_numeric(df['Money Out'], errors='coerce').fillna(0)
            in_val = pd.to_numeric(df['Money In'], errors='coerce').fillna(0)
            normalized['amount_gbp'] = in_val - out.abs()
        
        normalized['original_currency'] = 'GBP'
        normalized['original_amount'] = normalized['amount_gbp']
        
        if 'Money In' in df.columns:
            normalized['is_income'] = pd.to_numeric(df['Money In'], errors='coerce').fillna(0) > 0
        else:
            normalized['is_income'] = normalized['amount_gbp'] > 0
    
    # Try Korean format (detect by Korean characters or specific columns)
    elif any('가맹점' in str(col) or '종류' in str(col) or '원화금액' in str(col) for col in df.columns):
        # Korean bank format (TravelWallet)
        
        # Find the KRW amount column (원화금액)
        krw_col = None
        for col in df.columns:
            if '원화금액' in str(col) or 'KRW' in str(col):
                krw_col = col
                break
        
        if krw_col:
            # Parse amount (may have commas)
            krw_amount = df[krw_col].astype(str).str.replace(',', '').str.replace(' ', '')
            krw_amount = pd.to_numeric(krw_amount, errors='coerce')
        else:
            # Fallback to last numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                krw_amount = pd.to_numeric(df[numeric_cols[-1]], errors='coerce')
            else:
                krw_amount = pd.Series([0] * len(df))
        
        normalized['original_amount'] = krw_amount.abs()
        normalized['amount_gbp'] = krw_amount.abs() * KRW_TO_GBP_RATE
        normalized['original_currency'] = 'KRW'
        
        # Find date column
        for col in df.columns:
            if '날짜' in str(col) or 'date' in str(col).lower():
                # Parse Korean date format (YYYY.MM.DD)
                date_str = df[col].astype(str).str.replace('.', '-')
                normalized['date'] = pd.to_datetime(date_str, errors='coerce')
                break
        else:
            normalized['date'] = pd.NaT
        
        # Find time column
        for col in df.columns:
            if '시간' in str(col) or 'time' in str(col).lower():
                normalized['time'] = df[col].astype(str)
                break
        else:
            normalized['time'] = ''
        
        normalized['bank'] = 'TravelWallet (Korea)'
        
        # Find type column and determine if income
        for col in df.columns:
            if '종류' in str(col):
                normalized['type'] = df[col].astype(str)
                # 충전(charge) = income/top-up, 결제(payment) = spending
                normalized['is_income'] = df[col].astype(str).str.contains('충전|charge', case=False, na=False)
                break
        else:
            normalized['type'] = ''
            normalized['is_income'] = False
        
        # Find merchant column
        for col in df.columns:
            if '가맹점' in str(col):
                normalized['merchant'] = df[col].fillna('Unknown')
                normalized['category'] = df[col].fillna('Other')
                break
        else:
            normalized['merchant'] = 'Unknown'
            normalized['category'] = 'Other'
        
        # Make spending amounts negative for consistency
        normalized.loc[~normalized['is_income'], 'amount_gbp'] = -normalized.loc[~normalized['is_income'], 'amount_gbp'].abs()
    
    # Generic format - try common column names
    else:
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        if date_cols:
            normalized['date'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
        else:
            normalized['date'] = pd.NaT
        
        normalized['time'] = ''
        normalized['bank'] = 'Uploaded'
        normalized['type'] = ''
        
        # Find amount
        amount_cols = [c for c in df.columns if 'amount' in c.lower() or 'value' in c.lower()]
        if amount_cols:
            normalized['amount_gbp'] = pd.to_numeric(df[amount_cols[0]], errors='coerce')
        else:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                normalized['amount_gbp'] = df[numeric_cols[0]]
            else:
                normalized['amount_gbp'] = 0
        
        normalized['original_currency'] = 'GBP'
        normalized['original_amount'] = normalized['amount_gbp']
        
        # Find category/merchant
        cat_cols = [c for c in df.columns if 'category' in c.lower() or 'type' in c.lower()]
        if cat_cols:
            normalized['category'] = df[cat_cols[0]]
        else:
            normalized['category'] = 'Other'
        
        name_cols = [c for c in df.columns if 'name' in c.lower() or 'merchant' in c.lower() or 'description' in c.lower()]
        if name_cols:
            normalized['merchant'] = df[name_cols[0]]
        else:
            normalized['merchant'] = ''
        
        normalized['is_income'] = normalized['amount_gbp'] > 0
    
    # Clean up
    normalized = normalized.dropna(subset=['date', 'amount_gbp'], how='all')
    
    return normalized


if __name__ == '__main__':
    print("=" * 60)
    print("Finance Web App")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Open http://localhost:5001 in your browser")
    print()
    app.run(debug=True, host='0.0.0.0', port=5001)
