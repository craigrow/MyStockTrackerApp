#!/usr/bin/env python3

import os
import sys

# Simple debug script that doesn't import yfinance
def debug_basic():
    print("=== BASIC DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check environment
    print(f"TESTING env: {os.environ.get('TESTING', 'Not set')}")
    print(f"DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    
    try:
        from app import create_app
        print("✓ App import successful")
        
        app = create_app()
        print("✓ App creation successful")
        
        with app.app_context():
            print("✓ App context successful")
            
            from app.services.portfolio_service import PortfolioService
            print("✓ Portfolio service import successful")
            
            ps = PortfolioService()
            portfolios = ps.get_all_portfolios()
            print(f"✓ Found {len(portfolios)} portfolios")
            
            if portfolios:
                portfolio = portfolios[0]
                print(f"✓ Portfolio: {portfolio.name} (ID: {portfolio.id})")
                
                # Get basic data without price service
                transactions = ps.get_portfolio_transactions(portfolio.id)
                holdings = ps.get_current_holdings(portfolio.id)
                cash_balance = ps.get_cash_balance(portfolio.id)
                
                print(f"✓ Transactions: {len(transactions)}")
                print(f"✓ Holdings: {len(holdings)} stocks")
                print(f"✓ Cash balance: ${cash_balance}")
                
                # Check if we can import the main view functions
                try:
                    from app.views.main import is_market_open_now, get_last_market_date
                    market_open = is_market_open_now()
                    last_market_date = get_last_market_date()
                    print(f"✓ Market open: {market_open}")
                    print(f"✓ Last market date: {last_market_date}")
                except Exception as e:
                    print(f"✗ Market functions error: {e}")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_basic()