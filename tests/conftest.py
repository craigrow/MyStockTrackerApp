import pytest
import tempfile
import os
from datetime import datetime, date
from app import create_app, db
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.stock import Stock
from app.models.price import PriceHistory


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    # Clean up
    with app.app_context():
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user_id():
    """Return a sample user ID for testing."""
    return "test_user_123"


@pytest.fixture
def sample_stock(app):
    """Create a sample stock for testing."""
    with app.app_context():
        stock = Stock(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology"
        )
        db.session.add(stock)
        db.session.commit()
        return stock


@pytest.fixture
def sample_etf_stock(app):
    """Create a sample ETF stock for testing."""
    with app.app_context():
        etf = Stock(
            ticker="VOO",
            name="Vanguard S&P 500 ETF",
            sector="ETF"
        )
        db.session.add(etf)
        db.session.commit()
        return etf


@pytest.fixture
def sample_portfolio(app, sample_user_id):
    """Create a sample portfolio for testing."""
    with app.app_context():
        portfolio = Portfolio(
            name="Test Portfolio",
            description="A portfolio for testing",
            user_id=sample_user_id
        )
        db.session.add(portfolio)
        db.session.commit()
        return portfolio


@pytest.fixture
def sample_transaction(app, sample_portfolio, sample_stock):
    """Create a sample transaction for testing."""
    with app.app_context():
        transaction = StockTransaction(
            portfolio_id=sample_portfolio.id,
            ticker=sample_stock.ticker,
            transaction_type="BUY",
            date=date(2023, 1, 1),
            price_per_share=150.00,
            shares=10.0,
            total_value=1500.00
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction


@pytest.fixture
def sample_dividend(app, sample_portfolio, sample_stock):
    """Create a sample dividend for testing."""
    with app.app_context():
        dividend = Dividend(
            portfolio_id=sample_portfolio.id,
            ticker=sample_stock.ticker,
            payment_date=date(2023, 3, 15),
            total_amount=25.50
        )
        db.session.add(dividend)
        db.session.commit()
        return dividend


@pytest.fixture
def sample_cash_balance(app, sample_portfolio):
    """Create a sample cash balance for testing."""
    with app.app_context():
        cash_balance = CashBalance(
            portfolio_id=sample_portfolio.id,
            balance=1000.00
        )
        db.session.add(cash_balance)
        db.session.commit()
        return cash_balance


@pytest.fixture
def sample_price_history(app, sample_stock):
    """Create sample price history for testing."""
    with app.app_context():
        price_history = PriceHistory(
            ticker=sample_stock.ticker,
            date=date.today(),
            close_price=160.00,
            is_intraday=False,
            price_timestamp=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        db.session.add(price_history)
        db.session.commit()
        return price_history


@pytest.fixture
def multiple_transactions(app, sample_portfolio):
    """Create multiple transactions for testing."""
    with app.app_context():
        transactions = [
            StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            ),
            StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker="GOOGL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=2500.00,
                shares=2.0,
                total_value=5000.00
            ),
            StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date(2023, 6, 1),
                price_per_share=180.00,
                shares=3.0,
                total_value=540.00
            )
        ]
        
        for transaction in transactions:
            db.session.add(transaction)
        db.session.commit()
        return transactions


@pytest.fixture
def multiple_dividends(app, sample_portfolio):
    """Create multiple dividends for testing."""
    with app.app_context():
        dividends = [
            Dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date(2023, 3, 15),
                total_amount=25.50
            ),
            Dividend(
                portfolio_id=sample_portfolio.id,
                ticker="GOOGL",
                payment_date=date(2023, 4, 20),
                total_amount=15.75
            ),
            Dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date(2023, 6, 15),
                total_amount=28.00
            )
        ]
        
        for dividend in dividends:
            db.session.add(dividend)
        db.session.commit()
        return dividends