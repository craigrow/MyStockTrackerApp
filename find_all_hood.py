#!/usr/bin/env python3
from app import create_app, db
from app.models.portfolio import StockTransaction, Portfolio

app = create_app()
with app.app_context():
    hood_transactions = StockTransaction.query.filter_by(ticker='HOOD').all()
    print(f"Found {len(hood_transactions)} HOOD transactions:")
    for t in hood_transactions:
        p = Portfolio.query.get(t.portfolio_id)
        print(f"ID: {t.id}, Portfolio: {p.name if p else 'Unknown'}")
        print(f"Date: {t.date}, Type: {t.transaction_type}, Shares: {t.shares}, Price: ${t.price_per_share}")
        print()