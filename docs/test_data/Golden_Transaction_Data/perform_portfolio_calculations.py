#!/usr/bin/env python3
"""
Portfolio calculations script
Processes transaction data and calculates current portfolio values
"""

import pandas as pd
import yfinance as yf
import os

def main():
    """Main function to perform portfolio calculations"""
    print("=== Portfolio Calculations ===")
    
    # Read the transaction data
    df = pd.read_csv('Foolish_Transactions.csv')
    
    # Delete rows with Type SELL
    df = df[df['Type'] != 'SELL']
    
    # Add an Amount column
    df['Amount'] = df['Price'] * df['Shares']
    
    # For each row in Amount, multiply the Price by the Shares and store it in the Amount column
    df['Amount'] = df['Price'] * df['Shares']
    df['Amount'] = (df['Price'] * df['Shares']).round(2)
    
    # Add Current Shares column
    df['Current Shares'] = df['Shares']
    
    # Sort by ticker
    df = df.sort_values('Ticker')
    
    # Update Current Shares for splits
    mask = (df['Ticker'] == 'AVGO') & (df['Date'] < '2024-07-15')
    df.loc[mask, 'Current Shares'] = df.loc[mask, 'Shares'] * 10
    
    mask = (df['Ticker'] == 'LRCX') & (df['Date'] < '2024-10-03')
    df.loc[mask, 'Current Shares'] = df.loc[mask, 'Shares'] * 10
    
    mask = (df['Ticker'] == 'NVDA') & (df['Date'] < '2024-06-10')
    df.loc[mask, 'Current Shares'] = df.loc[mask, 'Shares'] * 10
    
    mask = (df['Ticker'] == 'SMCI') & (df['Date'] < '2024-10-01')
    df.loc[mask, 'Current Shares'] = df.loc[mask, 'Shares'] * 10
    
    # Get current prices and calculate Current Value
    def get_current_price(ticker):
        try:
            stock = yf.Ticker(ticker)
            return stock.history(period="1d")['Close'].iloc[-1]
        except:
            return 0
    
    print("Fetching current stock prices...")
    df['Current Price'] = df['Ticker'].apply(lambda x: get_current_price(x) if x != 'TOTAL' else 0)
    df['Current Value'] = (df['Current Price'] * df['Current Shares']).round(2)
    
    # Add total row
    total_row = pd.DataFrame({
        'Ticker': ['TOTAL'], 
        'Type': [''], 
        'Date': [''], 
        'Price': [0], 
        'Shares': [0], 
        'Amount': [df['Amount'].sum()], 
        'Current Shares': [0], 
        'Current Price': [0], 
        'Current Value': [df['Current Value'].sum()]
    })
    df = pd.concat([df, total_row], ignore_index=True)
    
    # Remove existing output file if it exists
    output_file = 'Foolish_Calculations.csv'
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed existing {output_file}")
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Portfolio calculations saved to {output_file}")
    
    # Print summary
    total_invested = df[df['Ticker'] == 'TOTAL']['Amount'].iloc[0]
    total_current_value = df[df['Ticker'] == 'TOTAL']['Current Value'].iloc[0]
    gain_loss = total_current_value - total_invested
    gain_loss_pct = (gain_loss / total_invested) * 100 if total_invested > 0 else 0
    
    print(f"\n=== Portfolio Summary ===")
    print(f"Total Invested: ${total_invested:,.2f}")
    print(f"Current Value: ${total_current_value:,.2f}")
    print(f"Gain/Loss: ${gain_loss:,.2f} ({gain_loss_pct:+.2f}%)")
    print(f"Number of transactions: {len(df) - 1}")  # Subtract 1 for TOTAL row

if __name__ == "__main__":
    main()