from app import create_app, db
from sqlalchemy import create_index, Table, MetaData

app = create_app()

def run_migrations():
    with app.app_context():
        # Create indexes directly using SQLAlchemy
        metadata = MetaData()
        price_history = Table('price_history', metadata, autoload_with=db.engine)
        
        # Create indexes
        create_index('idx_price_history_ticker', price_history, ['ticker'])
        create_index('idx_price_history_date', price_history, ['date'])
        create_index('idx_price_history_last_updated', price_history, ['last_updated'])
        
        print("Database migrations completed successfully!")

if __name__ == '__main__':
    run_migrations()
