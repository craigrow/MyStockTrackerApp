#!/usr/bin/env python
"""Quick fix for Foolish Portfolio timeout by pre-populating current prices"""

import os
import sys
from datetime import date, timedelta
import yfinance as yf
import time

# Foolish Portfolio tickers from the query
FOOLISH_TICKERS = [
    'AAPL', 'ABNB', 'AMZN', 'APP', 'ASML', 'AVGO', 'AXP', 'BROS', 'CELH', 'CMG',
    'CPNG', 'CRWD', 'DASH', 'DOCU', 'ELF', 'EME', 'ENPH', 'GEHC', 'GRAB', 'HIMS',
    'HOOD', 'HWM', 'IONQ', 'KD', 'KNSL', 'LRCX', 'MA', 'MELI', 'META', 'MNST',
    'MSFT', 'NFLX', 'NVDA', 'RBLX', 'RDDT', 'RELY', 'RGTI', 'SHOP', 'SMCI', 'SNOW',
    'SPOT', 'TMC', 'TOST', 'TSLA', 'TSM', 'TTAN', 'TTD', 'U', 'UBER', 'V',
    'VEEV', 'WING', 'XYZ', 'ZG', 'VOO', 'QQQ'
]

def fix_timeout():
    from app import create_app, db
    from app.models.price import PriceHistory
    from datetime import datetime
    
    app = create_app()
    
    with app.app_context():
        today = date.today()
        print(f"Pre-populating current prices for {len(FOOLISH_TICKERS)} tickers...")
        
        total_added = 0
        
        for ticker in FOOLISH_TICKERS:
            try:
                # Check if we have today's price
                existing = PriceHistory.query.filter_by(
                    ticker=ticker,
                    date=today
                ).first()
                
                if existing and existing.last_updated and (datetime.now() - existing.last_updated).seconds < 3600:
                    print(f"  {ticker}: Already have recent price")
                    continue
                
                # Fetch current price
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                
                if hist.empty:
                    print(f"  {ticker}: No data available")
                    continue
                
                current_price = float(hist.iloc[-1]['Close'])
                
                if existing:
                    existing.close_price = current_price
                    existing.last_updated = datetime.now()
                    existing.price_timestamp = datetime.now()
                else:
                    price_record = PriceHistory(
                        ticker=ticker,
                        date=today,
                        close_price=current_price,
                        is_intraday=True,
                        price_timestamp=datetime.now(),
                        last_updated=datetime.now()
                    )
                    db.session.add(price_record)
                
                db.session.commit()
                total_added += 1
                print(f"  {ticker}: ${current_price:.2f}")
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  {ticker}: Error - {e}")
                db.session.rollback()
                continue
        
        print(f"\nCompleted! Updated {total_added} prices")

if __name__ == "__main__":
    fix_timeout()