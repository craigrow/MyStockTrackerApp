#!/usr/bin/env python3
"""
Consolidated stock file processor
Processes XLSX files from Fidelity Roth, Fidelity BrokerageLink, and Robinhood accounts
Follows naming convention: Institution_accountName_year.csv
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

def convert_xlsx_to_csv():
    """Convert all xlsx files to csv"""
    xlsx_files = glob.glob('*.xlsx')
    print(f"Found {len(xlsx_files)} xlsx files: {xlsx_files}")
    
    for xlsx_file in xlsx_files:
        if xlsx_file.startswith('~$'):
            print(f"Skipping temporary file: {xlsx_file}")
            continue
            
        csv_file = xlsx_file.replace('.xlsx', '.csv')
        print(f"Converting {xlsx_file} to {csv_file}")
        
        try:
            df_temp = pd.read_excel(xlsx_file)
            df_temp.to_csv(csv_file, index=False)
            print(f"  - Shape: {df_temp.shape}")
        except Exception as e:
            print(f"  - Error: {e}")

def process_fidelity_file(file_path, account_type):
    """Process Fidelity files (both Roth and BrokerageLink)"""
    print(f"\n=== Processing {file_path} ===")
    
    # Extract year from filename
    year = file_path.split('_')[-1].replace('.csv', '')
    base_name = file_path.replace('.csv', '')
    
    # Load CSV file
    df = pd.read_csv(file_path, skiprows=2)
    
    # Reorder columns
    df = df[['Symbol', 'Action', 'Run Date', 'Price ($)', 'Quantity', 'Amount ($)']]
    
    # Rename columns
    df.columns = ['Ticker', 'Type', 'Date', 'Price', 'Shares', 'Amount']
    
    # BrokerageLink specific CUSIP replacements
    if account_type == 'BrokerageLink':
        df.loc[df['Ticker'] == '86800U104', 'Ticker'] = 'SMCI'
        df.loc[df['Ticker'] == '512807108', 'Ticker'] = 'LRCX'
    
    # Fix the date column: Remove the timestamp
    df['Date'] = df['Date'].str.split(' ').str[0]
    
    # Format columns
    df['Price'] = df['Price'].apply(lambda x: f"{x:.2f}")
    df['Amount'] = df['Amount'].apply(lambda x: f"{x:.2f}")
    df['Shares'] = df['Shares'].apply(lambda x: f"{x:.4f}")
    
    # Delete unwanted transaction types
    unwanted_types = ['CONVERSION', 'REINVESTMENT', 'FOREIGN TAX']
    if account_type == 'BrokerageLink':
        unwanted_types.extend(['TRANSFERRED', 'DISTRIBUTION', 'MERGER'])
    
    for unwanted in unwanted_types:
        df = df[~df['Type'].str.contains(unwanted, na=False)]
    
    # Modify transaction types
    df.loc[df['Type'].str.contains('SOLD', na=False), 'Type'] = 'SELL'
    df.loc[df['Type'].str.contains('BOUGHT', na=False), 'Type'] = 'BUY'
    df.loc[df['Type'].str.contains('DIVIDEND', na=False), 'Type'] = 'DIVIDEND'
    
    # Sort by Date
    df = df.sort_values('Date')
    
    # Eliminate irrelevant tickers
    excluded_tickers = ['BRKB', 'CEF', 'SPAXX', 'IVV']
    if account_type == 'BrokerageLink':
        excluded_tickers.append('FDRXX')
    df = df[~df['Ticker'].isin(excluded_tickers)]
    
    print(f"Number of rows: {len(df)}")
    
    # Merge duplicate transactions
    df = merge_duplicate_transactions(df)
    
    # Create output files
    create_fidelity_output_files(df, base_name)

def merge_duplicate_transactions(df):
    """Merge transactions with same ticker and date"""
    df['Price_num'] = df['Price'].astype(float)
    df['Shares_num'] = df['Shares'].astype(float)
    
    grouped = df.groupby(['Ticker', 'Date'])
    merged_rows = []
    keep_indices = []
    
    for (ticker, date), group in grouped:
        if len(group) > 1:
            combined_shares = group['Shares_num'].sum()
            weighted_avg_price = (group['Price_num'] * group['Shares_num']).sum() / combined_shares
            
            original_info = ", ".join([f"${p:.2f}@{s:.4f}" for p, s in zip(group['Price_num'], group['Shares_num'])])
            print(f"Merging {ticker} on {date}: {len(group)} transactions ({original_info}) -> ${weighted_avg_price:.2f}@{combined_shares:.4f}")
            
            merged_row = group.iloc[0].copy()
            merged_row['Shares'] = f"{combined_shares:.4f}"
            merged_row['Price'] = f"{weighted_avg_price:.2f}"
            
            # Only update Amount if it exists in the dataframe
            if 'Amount' in df.columns:
                merged_row['Amount'] = group['Amount'].sum()
                
            merged_rows.append(merged_row)
        else:
            keep_indices.extend(group.index)
    
    if merged_rows:
        df_merged = pd.DataFrame(merged_rows)
        df_kept = df.loc[keep_indices]
        df = pd.concat([df_kept, df_merged], ignore_index=True)
    
    df.drop(columns=['Price_num', 'Shares_num'], inplace=True)
    return df.sort_values('Date')

def create_fidelity_output_files(df, base_name):
    """Create output CSV files for Fidelity data"""
    # ETF transactions (TQQQ, QLD)
    df_etf = df[(df['Ticker'].isin(['TQQQ', 'QLD'])) & (df['Type'].isin(['BUY', 'SELL']))]
    
    # Calculate Amount column (Price * Shares) if it doesn't exist
    if 'Amount' not in df_etf.columns or df_etf['Amount'].isna().any():
        df_etf['Price_num'] = df_etf['Price'].astype(float)
        df_etf['Shares_num'] = df_etf['Shares'].astype(float)
        df_etf['Amount'] = df_etf['Price_num'] * df_etf['Shares_num']
        df_etf.drop(columns=['Price_num', 'Shares_num'], inplace=True)
    
    df_etf = df_etf[['Ticker', 'Type', 'Date', 'Price', 'Shares', 'Amount']]
    df_etf.to_csv(f'{base_name}_ETF_Transactions.csv', index=False)
    
    # Other transactions
    df_other = df[(df['Type'].isin(['BUY', 'SELL'])) & (~df['Ticker'].isin(['TQQQ', 'QLD']))]
    
    # Calculate Amount column (Price * Shares) if it doesn't exist
    if 'Amount' not in df_other.columns or df_other['Amount'].isna().any():
        df_other['Price_num'] = df_other['Price'].astype(float)
        df_other['Shares_num'] = df_other['Shares'].astype(float)
        df_other['Amount'] = df_other['Price_num'] * df_other['Shares_num']
        df_other.drop(columns=['Price_num', 'Shares_num'], inplace=True)
    
    df_other = df_other[['Ticker', 'Type', 'Date', 'Price', 'Shares', 'Amount']]
    df_other.to_csv(f'{base_name}_Transactions.csv', index=False)
    
    # ETF dividends
    df_etf_div = df[(df['Type'] == 'DIVIDEND') & (df['Ticker'].isin(['TQQQ', 'QLD']))]
    df_etf_div = df_etf_div[['Ticker', 'Date', 'Amount']]
    df_etf_div.to_csv(f'{base_name}_ETF_Dividends.csv', index=False)
    
    # Other dividends
    df_div = df[(df['Type'] == 'DIVIDEND') & (~df['Ticker'].isin(['TQQQ', 'QLD']))]
    df_div = df_div[['Ticker', 'Date', 'Amount']]
    df_div.to_csv(f'{base_name}_Dividends.csv', index=False)
    
    # Validation
    csv_total = len(df_etf) + len(df_other) + len(df_etf_div) + len(df_div)
    print(f"Number of rows in df: {len(df)}")
    print(f"Number of rows in {base_name}_ETF_Transactions.csv: {len(df_etf)}")
    print(f"Number of rows in {base_name}_Transactions.csv: {len(df_other)}")
    print(f"Number of rows in {base_name}_ETF_Dividends.csv: {len(df_etf_div)}")
    print(f"Number of rows in {base_name}_Dividends.csv: {len(df_div)}")
    print(f"Total rows in CSV files: {csv_total}")

def process_robinhood_file(file_path):
    """Process Robinhood files"""
    print(f"\n=== Processing {file_path} ===")
    
    base_name = file_path.replace('.xlsx', '')
    
    # Load Excel file
    df = pd.read_excel(file_path)
    print(f"Shape: {df.shape}")
    
    # Reorder columns
    df = df[['Instrument', 'Trans Code', 'Activity Date', 'Price', 'Quantity', 'Amount']]
    
    # Rename columns
    df = df.rename(columns={
        'Activity Date': 'Date',
        'Instrument': 'Ticker', 
        'Trans Code': 'Type',
        'Quantity': 'Shares',
    })
    
    # Delete blank rows
    df = df.dropna(how='all')
    
    # Delete unwanted transaction types
    df = df[~df['Type'].isin(['SLIP', 'DTAX', 'SPL', 'CFRI', 'ACH', 'ITRF', 'XENT', 'REC'])]
    
    # Replace transaction type values
    df.loc[df['Type'] == 'CDIV', 'Type'] = 'DIVIDEND'
    df.loc[df['Type'] == 'Buy', 'Type'] = 'BUY'
    
    # Create output files
    df_transactions = df[df['Type'].isin(['BUY', 'SELL'])]
    df_transactions = df_transactions[['Ticker', 'Type', 'Date', 'Price', 'Shares']]
    
    # Calculate Amount column (Price * Shares) before merging
    df_transactions['Price'] = df_transactions['Price'].astype(float)
    df_transactions['Shares'] = df_transactions['Shares'].astype(float)
    df_transactions['Amount'] = df_transactions['Price'] * df_transactions['Shares']
    df_transactions['Price'] = df_transactions['Price'].astype(str)
    df_transactions['Shares'] = df_transactions['Shares'].astype(str)
    
    # Merge duplicate transactions
    df_transactions = merge_duplicate_transactions(df_transactions)
    
    df_transactions.to_csv(f'{base_name}_Transactions.csv', index=False)
    
    df_dividends = df[df['Type'] == 'DIVIDEND']
    df_dividends = df_dividends[['Ticker', 'Date', 'Amount']]
    df_dividends.to_csv(f'{base_name}_Dividends.csv', index=False)
    
    # Validation
    csv_total = len(df_transactions) + len(df_dividends)
    print(f"Number of rows in df: {len(df)}")
    print(f"Number of rows in {base_name}_Transactions.csv: {len(df_transactions)}")
    print(f"Number of rows in {base_name}_Dividends.csv: {len(df_dividends)}")
    print(f"Total rows in CSV files: {csv_total}")

def consolidate_csv_files():
    """Consolidate CSV files into master files"""
    
    # 1. Merge all *_Transactions.csv (excluding ETF and existing consolidated files) into Foolish_Transactions.csv
    # Filter out TQQQ and QLD transactions from non-ETF files
    transaction_files = [f for f in glob.glob('*_Transactions.csv') if 'ETF' not in f and not f.startswith('Foolish_')]
    merge_files_with_etf_filter(transaction_files, 'Foolish_Transactions.csv', exclude_etf=True)
    
    # Apply merge_duplicate_transactions to the consolidated file
    print("\nMerging duplicate transactions in Foolish_Transactions.csv...")
    df_transactions = pd.read_csv('Foolish_Transactions.csv')
    df_transactions = merge_duplicate_transactions(df_transactions)
    df_transactions.to_csv('Foolish_Transactions.csv', index=False)
    print(f"  -> Foolish_Transactions.csv: {len(df_transactions)} rows after merging duplicates")
    
    # 2. Merge all *_Dividends.csv (excluding ETF and existing consolidated files) into Foolish_Dividends.csv
    # Filter out TQQQ and QLD dividends from non-ETF files
    dividend_files = [f for f in glob.glob('*_Dividends.csv') if 'ETF' not in f and not f.startswith('Foolish_')]
    merge_files_with_etf_filter(dividend_files, 'Foolish_Dividends.csv', exclude_etf=True)
    
    # 3. Merge all *_ETF_Transactions.csv plus ETF transactions from other files into ETF_Transactions.csv
    etf_transaction_files = glob.glob('*_ETF_Transactions.csv')
    other_transaction_files = [f for f in glob.glob('*_Transactions.csv') if 'ETF' not in f and not f.startswith('Foolish_') and not f.startswith('ETF_')]
    merge_etf_files(etf_transaction_files, other_transaction_files, 'ETF_Transactions.csv')
    
    # Apply merge_duplicate_transactions to the consolidated ETF file
    print("\nMerging duplicate transactions in ETF_Transactions.csv...")
    df_etf_transactions = pd.read_csv('ETF_Transactions.csv')
    df_etf_transactions = merge_duplicate_transactions(df_etf_transactions)
    df_etf_transactions.to_csv('ETF_Transactions.csv', index=False)
    print(f"  -> ETF_Transactions.csv: {len(df_etf_transactions)} rows after merging duplicates")
    
    # 4. Merge all *_ETF_Dividends.csv plus ETF dividends from other files into ETF_Dividends.csv
    etf_dividend_files = glob.glob('*_ETF_Dividends.csv')
    other_dividend_files = [f for f in glob.glob('*_Dividends.csv') if 'ETF' not in f and not f.startswith('Foolish_') and not f.startswith('ETF_')]
    merge_etf_files(etf_dividend_files, other_dividend_files, 'ETF_Dividends.csv')

def merge_files_with_etf_filter(file_list, output_filename, exclude_etf=False):
    """Merge multiple CSV files into one, optionally filtering ETF transactions"""
    if not file_list:
        print(f"No files found for {output_filename}")
        return
    
    print(f"\nMerging {len(file_list)} files into {output_filename}:")
    
    combined_df = pd.DataFrame()
    total_source_rows = 0
    total_filtered_rows = 0
    
    for file in sorted(file_list):
        df = pd.read_csv(file)
        source_rows = len(df)
        total_source_rows += source_rows
        
        if exclude_etf:
            # Filter out TQQQ and QLD transactions
            df_filtered = df[~df['Ticker'].isin(['TQQQ', 'QLD'])]
            filtered_count = source_rows - len(df_filtered)
            if filtered_count > 0:
                print(f"  {file}: {source_rows} rows ({filtered_count} ETF transactions filtered out)")
            else:
                print(f"  {file}: {source_rows} rows")
            df = df_filtered
        else:
            print(f"  {file}: {source_rows} rows")
        
        total_filtered_rows += len(df)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Sort by date if Date column exists
    if 'Date' in combined_df.columns:
        combined_df = combined_df.sort_values('Date')
    
    # Save merged file
    combined_df.to_csv(output_filename, index=False)
    output_rows = len(combined_df)
    
    print(f"  -> {output_filename}: {output_rows} rows")
    if exclude_etf:
        print(f"  Total source rows: {total_source_rows}, Filtered rows: {total_filtered_rows}, Output rows: {output_rows}")

def merge_etf_files(etf_files, other_files, output_filename):
    """Merge ETF files plus ETF transactions from other files"""
    print(f"\nMerging ETF transactions into {output_filename}:")
    
    combined_df = pd.DataFrame()
    total_rows = 0
    
    # Add dedicated ETF files
    for file in etf_files:
        df = pd.read_csv(file)
        print(f"  {file}: {len(df)} rows")
        combined_df = pd.concat([combined_df, df], ignore_index=True)
        total_rows += len(df)
    
    # Add ETF transactions from other files
    for file in other_files:
        df = pd.read_csv(file)
        etf_df = df[df['Ticker'].isin(['TQQQ', 'QLD'])]
        if len(etf_df) > 0:
            print(f"  {file}: {len(etf_df)} ETF transactions")
            combined_df = pd.concat([combined_df, etf_df], ignore_index=True)
            total_rows += len(etf_df)
    
    # Sort by date if Date column exists
    if 'Date' in combined_df.columns:
        combined_df = combined_df.sort_values('Date')
    
    # Save merged file
    combined_df.to_csv(output_filename, index=False)
    output_rows = len(combined_df)
    
    print(f"  -> {output_filename}: {output_rows} rows")
    print(f"  Total ETF rows collected: {total_rows}, Output rows: {output_rows}")

def main():
    """Main processing function"""
    print("=== Stock File Processor ===")
    
    # Step 1: Convert XLSX to CSV
    print("\n1. Converting XLSX files to CSV...")
    convert_xlsx_to_csv()
    
    # Step 2: Process files based on naming convention
    print("\n2. Processing CSV files...")
    
    # Process original source files based on XLSX files present
    xlsx_files = glob.glob('*.xlsx')
    
    for xlsx_file in xlsx_files:
        if xlsx_file.startswith('~$'):
            continue
            
        # Determine file type from filename
        if xlsx_file.startswith('Fidelity_'):
            csv_file = xlsx_file.replace('.xlsx', '.csv')
            if 'Roth' in xlsx_file:
                process_fidelity_file(csv_file, 'Roth')
            elif 'BrokerageLink' in xlsx_file:
                process_fidelity_file(csv_file, 'BrokerageLink')
        elif xlsx_file.startswith('Robinhood_'):
            process_robinhood_file(xlsx_file)
    
    # Step 3: Consolidate files
    print("\n3. Consolidating CSV files...")
    consolidate_csv_files()
    
    print("\n=== Processing Complete ===")

if __name__ == "__main__":
    main()