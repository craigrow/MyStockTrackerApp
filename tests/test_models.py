import pytest
from datetime import datetime, date
from decimal import Decimal
from app.models.stock import Stock
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.price import PriceHistory
from app import db


class TestStock:
    def test_stock_creation(self, app):
        with app.app_context():
            stock = Stock(ticker="AAPL", name="Apple Inc.", sector="Technology")
            db.session.add(stock)
            db.session.commit()
            
            assert stock.ticker == "AAPL"
            assert stock.name == "Apple Inc."
            assert stock.sector == "Technology"

    def test_stock_ticker_required(self, app):
        with app.app_context():
            with pytest.raises(Exception):
                stock = Stock(name="Apple Inc.")
                db.session.add(stock)
                db.session.commit()

    def test_stock_unique_ticker(self, app):
        with app.app_context():
            stock1 = Stock(ticker="AAPL", name="Apple Inc.")
            stock2 = Stock(ticker="AAPL", name="Apple Inc. Duplicate")
            
            db.session.add(stock1)
            db.session.commit()
            
            db.session.add(stock2)
            with pytest.raises(Exception):
                db.session.commit()


class TestPortfolio:
    def test_portfolio_creation(self, app):
        with app.app_context():
            portfolio = Portfolio(
                name="Test Portfolio",
                description="A test portfolio",
                user_id="test_user"
            )
            db.session.add(portfolio)
            db.session.commit()
            
            assert portfolio.name == "Test Portfolio"
            assert portfolio.description == "A test portfolio"
            assert portfolio.user_id == "test_user"
            assert portfolio.creation_date is not None
            assert portfolio.last_updated is not None

    def test_portfolio_name_required(self, app):
        with app.app_context():
            with pytest.raises(Exception):
                portfolio = Portfolio(user_id="test_user")
                db.session.add(portfolio)
                db.session.commit()

    def test_portfolio_auto_timestamps(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            creation_time = portfolio.creation_date
            updated_time = portfolio.last_updated
            
            assert creation_time is not None
            assert updated_time is not None
            assert creation_time == updated_time


class TestStockTransaction:
    def test_transaction_creation(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.5,
                total_value=1575.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.ticker == "AAPL"
            assert transaction.transaction_type == "BUY"
            assert transaction.shares == 10.5
            assert transaction.total_value == 1575.00

    def test_transaction_fractional_shares(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=0.333,
                total_value=49.95
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.shares == 0.333

    def test_transaction_type_validation(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            # Valid transaction types
            buy_transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10,
                total_value=1500.00
            )
            
            sell_transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date.today(),
                price_per_share=160.00,
                shares=5,
                total_value=800.00
            )
            
            db.session.add_all([buy_transaction, sell_transaction])
            db.session.commit()
            
            assert buy_transaction.transaction_type == "BUY"
            assert sell_transaction.transaction_type == "SELL"

    def test_transaction_portfolio_relationship(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            assert transaction.portfolio_id == portfolio.id
            assert transaction in portfolio.transactions


class TestDividend:
    def test_dividend_creation(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            dividend = Dividend(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            db.session.add(dividend)
            db.session.commit()
            
            assert dividend.ticker == "AAPL"
            assert dividend.total_amount == 25.50
            assert dividend.payment_date == date.today()

    def test_dividend_portfolio_relationship(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            dividend = Dividend(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            db.session.add(dividend)
            db.session.commit()
            
            assert dividend.portfolio_id == portfolio.id
            assert dividend in portfolio.dividends

    def test_dividend_positive_amount(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            dividend = Dividend(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=0.01
            )
            db.session.add(dividend)
            db.session.commit()
            
            assert dividend.total_amount > 0


class TestCashBalance:
    def test_cash_balance_creation(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            cash_balance = CashBalance(
                portfolio_id=portfolio.id,
                balance=1000.00
            )
            db.session.add(cash_balance)
            db.session.commit()
            
            assert cash_balance.balance == 1000.00
            assert cash_balance.last_updated is not None

    def test_cash_balance_portfolio_relationship(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            cash_balance = CashBalance(
                portfolio_id=portfolio.id,
                balance=1000.00
            )
            db.session.add(cash_balance)
            db.session.commit()
            
            assert cash_balance.portfolio_id == portfolio.id
            assert portfolio.cash_balance == cash_balance

    def test_cash_balance_update_timestamp(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            cash_balance = CashBalance(
                portfolio_id=portfolio.id,
                balance=1000.00
            )
            db.session.add(cash_balance)
            db.session.commit()
            
            original_timestamp = cash_balance.last_updated
            
            # Update balance
            cash_balance.balance = 1500.00
            cash_balance.last_updated = datetime.utcnow()
            db.session.commit()
            
            assert cash_balance.last_updated > original_timestamp


class TestPriceHistory:
    def test_price_history_creation(self, app):
        with app.app_context():
            price_history = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow()
            )
            db.session.add(price_history)
            db.session.commit()
            
            assert price_history.ticker == "AAPL"
            assert price_history.close_price == 150.00
            assert price_history.is_intraday is False

    def test_price_history_composite_key(self, app):
        with app.app_context():
            price1 = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow()
            )
            
            # Same ticker, different date - should work
            price2 = PriceHistory(
                ticker="AAPL",
                date=date(2023, 1, 1),
                close_price=140.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow()
            )
            
            db.session.add_all([price1, price2])
            db.session.commit()
            
            assert price1.ticker == price2.ticker
            assert price1.date != price2.date

    def test_price_history_duplicate_key(self, app):
        with app.app_context():
            price1 = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow()
            )
            
            price2 = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=155.00,
                is_intraday=True,
                price_timestamp=datetime.utcnow()
            )
            
            db.session.add(price1)
            db.session.commit()
            
            db.session.add(price2)
            with pytest.raises(Exception):
                db.session.commit()

    def test_price_history_intraday_flag(self, app):
        with app.app_context():
            intraday_price = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=True,
                price_timestamp=datetime.utcnow()
            )
            
            closing_price = PriceHistory(
                ticker="GOOGL",
                date=date.today(),
                close_price=2500.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow()
            )
            
            db.session.add_all([intraday_price, closing_price])
            db.session.commit()
            
            assert intraday_price.is_intraday is True
            assert closing_price.is_intraday is False