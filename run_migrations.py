from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    from migrations.add_price_history_indexes import upgrade
    with app.app_context():
        upgrade()
        print("Database migrations completed successfully!")
