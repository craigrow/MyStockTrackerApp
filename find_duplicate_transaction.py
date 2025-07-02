#!/usr/bin/env python3
"""
Script to find duplicate HOOD transaction in production database.
Transaction: HOOD buy on 7/1/2025, 1.068 shares at $6.36
"""

import os
import sys
from datetime import date
from app import create_app, db
from app.models.portfolio import StockTransaction, Portfolio

def find_duplicate_hood_transaction():
    """Find the duplicate HOOD transaction in production."""
    
    app = create_app()
    
    with app.app_context():
        # Find HOOD transactions matching the criteria
        hood_transactions = StockTransaction.query.filter(
            StockTransaction.ticker == 'HOOD',
            StockTransaction.transaction_type == 'BUY',
            StockTransaction.date == date(2025, 7, 1),
            StockTransaction.shares.between(1.06, 1.07),
            StockTransaction.price_per_share.between(6.30, 6.40)
        ).all()
        
        print(f"Found {len(hood_transactions)} HOOD transactions matching criteria:")
        print("Buy, HOOD, 7/1/2025, ~1.068 shares at ~$6.36")
        print("-" * 50)
        
        for i, transaction in enumerate(hood_transactions):
            portfolio = Portfolio.query.get(transaction.portfolio_id)
            portfolio_name = portfolio.name if portfolio else "Unknown"
            
            print(f"Transaction {i+1}:")
            print(f"  ID: {transaction.id}")
            print(f"  Portfolio: {portfolio_name} (ID: {transaction.portfolio_id})")
            print(f"  Date: {transaction.date}")
            print(f"  Type: {transaction.transaction_type}")
            print(f"  Shares: {transaction.shares}")
            print(f"  Price: ${transaction.price_per_share}")
            print(f"  Total: ${transaction.total_value}")
            print()
        
        if len(hood_transactions) > 1:
            print(f"DUPLICATE FOUND: {len(hood_transactions)} identical transactions detected!")
        elif len(hood_transactions) == 1:
            print("Only one transaction found - no duplicates detected")
        else:
            print("No matching transactions found")

if __name__ == "__main__":
    find_duplicate_hood_transaction()