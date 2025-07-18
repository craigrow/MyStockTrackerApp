"""
Database migration to create cash flows and IRR calculation tables
Run with: python create_cash_flows_tables.py
"""

from app import create_app, db
from app.models.portfolio import Portfolio  # Import Portfolio model first
from app.models.cash_flow import CashFlow, IRRCalculation
from sqlalchemy import text


def create_cash_flows_tables():
    """Create cash flows and IRR calculation tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            
            # Add hash tracking column to portfolios table if it doesn't exist
            try:
                db.session.execute(text(
                    "ALTER TABLE portfolios ADD COLUMN cash_flow_data_hash VARCHAR(64)"
                ))
                db.session.commit()
                print("✅ Added cash_flow_data_hash column to portfolios table")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print("ℹ️  cash_flow_data_hash column already exists")
                else:
                    print(f"⚠️  Could not add hash column: {e}")
                db.session.rollback()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'cash_flows' in tables:
                print("✅ cash_flows table created successfully")
            else:
                print("❌ cash_flows table not found")
                
            if 'irr_calculations' in tables:
                print("✅ irr_calculations table created successfully")
            else:
                print("❌ irr_calculations table not found")
            
            print("\n🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise


if __name__ == "__main__":
    create_cash_flows_tables()