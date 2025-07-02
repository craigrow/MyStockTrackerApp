#!/usr/bin/env python3
"""
Script to delete duplicate HOOD transaction from production database.
Transaction: HOOD buy on 7/1/2025, 1.068 shares at $6.36
"""

import os
import sys
from datetime import date
from app import create_app, db
from app.models.portfolio import StockTransaction, Portfolio

def delete_duplicate_hood_transaction():
    """Delete the duplicate HOOD transaction from production."""
    
    # Set environment to production
    os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', '')
    
    app = create_app()
    
    with app.app_context():
        # First, show all portfolios
        portfolios = Portfolio.query.all()
        print(f"Found {len(portfolios)} portfolios:")
        for portfolio in portfolios:
            print(f"  Portfolio: {portfolio.name} (ID: {portfolio.id})")
        print()
        
        # Check recent transactions around July 1st, 2025
        recent_transactions = StockTransaction.query.filter(
            StockTransaction.date >= date(2025, 6, 30),
            StockTransaction.date <= date(2025, 7, 2)
        ).all()
        
        print(f"All transactions between June 30 - July 2, 2025:")
        for transaction in recent_transactions:
            portfolio = Portfolio.query.get(transaction.portfolio_id)
            portfolio_name = portfolio.name if portfolio else "Unknown"
            print(f"  ID: {transaction.id}, Portfolio: {portfolio_name}")
            print(f"  Ticker: {transaction.ticker}, Date: {transaction.date}")
            print(f"  Type: {transaction.transaction_type}, Shares: {transaction.shares}, Price: ${transaction.price_per_share}")
            print(f"  Total: ${transaction.total_value}")
            print()
        
        # Also check all HOOD transactions
        all_hood_transactions = StockTransaction.query.filter_by(ticker='HOOD').all()
        print(f"All HOOD transactions in database ({len(all_hood_transactions)} found):")
        for transaction in all_hood_transactions:
            portfolio = Portfolio.query.get(transaction.portfolio_id)
            portfolio_name = portfolio.name if portfolio else "Unknown"
            print(f"  ID: {transaction.id}, Portfolio: {portfolio_name}")
            print(f"  Date: {transaction.date}, Type: {transaction.transaction_type}")
            print(f"  Shares: {transaction.shares}, Price: ${transaction.price_per_share}, Total: ${transaction.total_value}")
            print()
        
        # Find HOOD transactions with similar criteria (allowing for slight variations)
        hood_transactions = StockTransaction.query.filter(
            StockTransaction.ticker == 'HOOD',
            StockTransaction.transaction_type == 'BUY',
            StockTransaction.date == date(2025, 7, 1),
            StockTransaction.shares.between(1.06, 1.07),
            StockTransaction.price_per_share.between(6.30, 6.40)
        ).all()
        
        print(f"\nFound {len(hood_transactions)} transactions matching exact criteria:")
        
        for i, transaction in enumerate(hood_transactions):
            print(f"  {i+1}. ID: {transaction.id}")
            print(f"     Portfolio: {transaction.portfolio_id}")
            print(f"     Date: {transaction.date}")
            print(f"     Shares: {transaction.shares}")
            print(f"     Price: ${transaction.price_per_share}")
            print(f"     Total: ${transaction.total_value}")
            print()
        
        if len(hood_transactions) > 1:
            # Delete the duplicate (keep the first one, delete the rest)
            for transaction in hood_transactions[1:]:
                print(f"Deleting duplicate transaction ID: {transaction.id}")
                db.session.delete(transaction)
            
            db.session.commit()
            print(f"Successfully deleted {len(hood_transactions) - 1} duplicate transaction(s)")
            
        elif len(hood_transactions) == 1:
            print("Only one transaction found - no duplicates to delete")
            
        else:
            print("No matching HOOD transactions found")

if __name__ == "__main__":
    delete_duplicate_hood_transaction()