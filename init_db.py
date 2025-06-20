#!/usr/bin/env python3
"""Initialize the database with all tables."""

from app import create_app, db

def init_database():
    app = create_app()
    with app.app_context():
        # Import all models to ensure they're registered
        from app.models.stock import Stock
        from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
        from app.models.price import PriceHistory
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print table names to verify
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")

if __name__ == "__main__":
    init_database()