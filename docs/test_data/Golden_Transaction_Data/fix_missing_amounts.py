#!/usr/bin/env python3
"""
Fix missing Amount values in Foolish_Transactions.csv
"""

import pandas as pd

def fix_missing_amounts():
    """Fix missing Amount values in Foolish_Transactions.csv"""
    print("Fixing missing Amount values in Foolish_Transactions.csv...")
    
    # Load the file
    df = pd.read_csv('Foolish_Transactions.csv')
    
    # Count missing values before fix
    missing_before = df['Amount'].isna().sum()
    print(f"Found {missing_before} transactions with missing Amount values")
    
    # Calculate Amount for rows with missing values
    mask = df['Amount'].isna()
    if mask.any():
        df.loc[mask, 'Price'] = df.loc[mask, 'Price'].astype(float)
        df.loc[mask, 'Shares'] = df.loc[mask, 'Shares'].astype(float)
        df.loc[mask, 'Amount'] = df.loc[mask, 'Price'] * df.loc[mask, 'Shares']
        
        # Format the Amount values to match the existing format
        df['Amount'] = df['Amount'].round(8)
    
    # Count missing values after fix
    missing_after = df['Amount'].isna().sum()
    print(f"Fixed {missing_before - missing_after} transactions")
    print(f"Remaining transactions with missing Amount values: {missing_after}")
    
    # Save the updated file
    df.to_csv('Foolish_Transactions.csv', index=False)
    print("Updated Foolish_Transactions.csv saved")

if __name__ == "__main__":
    fix_missing_amounts()