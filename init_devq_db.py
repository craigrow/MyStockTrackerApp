#!/usr/bin/env python3
"""Initialize devQ database with sample data"""

from app import create_app, db
from app.models.portfolio import Portfolio
from app.models.transactions import Transaction
from datetime import date

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if portfolio already exists
        existing = Portfolio.query.first()
        if existing:
            print(f"Database already has {Portfolio.query.count()} portfolios")
            return
        
        # Create sample portfolio
        portfolio = Portfolio(
            name="Sample Portfolio",
            description="Test portfolio for devQ"
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # Add sample transaction
        transaction = Transaction(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            transaction_type="BUY",
            shares=10,
            price=150.00,
            date=date(2023, 1, 15),
            total_value=1500.00
        )
        db.session.add(transaction)
        db.session.commit()
        
        print(f"Created portfolio {portfolio.id} with 1 transaction")

if __name__ == "__main__":
    init_db()