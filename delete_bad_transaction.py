#!/usr/bin/env python3
"""Delete transaction with incorrect ticker."""

from app import create_app, db
from app.models.portfolio import StockTransaction

def delete_bad_transaction():
    app = create_app()
    with app.app_context():
        # Find transactions with bad ticker
        bad_transactions = StockTransaction.query.filter(
            StockTransaction.ticker.like('%APPL%')
        ).all()
        
        print(f"Found {len(bad_transactions)} transactions with APPL-like tickers:")
        for t in bad_transactions:
            print(f"ID: {t.id}, Ticker: {t.ticker}, Type: {t.transaction_type}, Shares: {t.shares}")
        
        if bad_transactions:
            for t in bad_transactions:
                db.session.delete(t)
            db.session.commit()
            print(f"Deleted {len(bad_transactions)} bad transactions")
        else:
            print("No bad transactions found")

if __name__ == "__main__":
    delete_bad_transaction()