#!/usr/bin/env python3

import yfinance as yf
from datetime import date, datetime

def test_etf_dividends():
    """Test ETF dividend retrieval"""
    
    print("Testing ETF dividend retrieval...")
    
    # Test VOO dividends
    print("\n=== VOO Dividends ===")
    try:
        voo = yf.Ticker("VOO")
        voo_dividends = voo.dividends
        
        if not voo_dividends.empty:
            print(f"Found {len(voo_dividends)} VOO dividend payments")
            # Show last 5 dividends
            recent_divs = voo_dividends.tail(5)
            for div_date, div_amount in recent_divs.items():
                print(f"  {div_date.date()}: ${div_amount:.4f}")
        else:
            print("No VOO dividends found")
            
    except Exception as e:
        print(f"Error getting VOO dividends: {e}")
    
    # Test QQQ dividends
    print("\n=== QQQ Dividends ===")
    try:
        qqq = yf.Ticker("QQQ")
        qqq_dividends = qqq.dividends
        
        if not qqq_dividends.empty:
            print(f"Found {len(qqq_dividends)} QQQ dividend payments")
            # Show last 5 dividends
            recent_divs = qqq_dividends.tail(5)
            for div_date, div_amount in recent_divs.items():
                print(f"  {div_date.date()}: ${div_amount:.4f}")
        else:
            print("No QQQ dividends found")
            
    except Exception as e:
        print(f"Error getting QQQ dividends: {e}")

if __name__ == "__main__":
    test_etf_dividends()