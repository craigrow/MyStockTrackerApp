#!/usr/bin/env python3
from datetime import date
from app import create_app, db
from app.models.portfolio import StockTransaction, Portfolio

app = create_app()
with app.app_context():
    # Show all portfolios first
    portfolios = Portfolio.query.all()
    print(f"Total portfolios: {len(portfolios)}")
    for p in portfolios:
        print(f"  {p.name} (ID: {p.id})")
    print()
    
    # Find HOOD transactions around July 1, 2025
    hood_transactions = StockTransaction.query.filter(
        StockTransaction.ticker == 'HOOD',
        StockTransaction.date >= date(2025, 6, 30),
        StockTransaction.date <= date(2025, 7, 2)
    ).all()
    
    print(f"HOOD transactions near 7/1/2025: {len(hood_transactions)}")
    for t in hood_transactions:
        p = Portfolio.query.get(t.portfolio_id)
        print(f"Portfolio: {p.name if p else 'Unknown'}")
        print(f"Date: {t.date}, Type: {t.transaction_type}")
        print(f"Shares: {t.shares}, Price: ${t.price_per_share}, Total: ${t.total_value}")
        print(f"ID: {t.id}")
        print()