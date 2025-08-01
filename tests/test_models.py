import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.models.stock import Stock
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.price import PriceHistory
from app.models.cache import PortfolioCache
from app import db
import json


@pytest.mark.fast
@pytest.mark.database
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


@pytest.mark.fast
@pytest.mark.database
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
            # Allow for small time differences (within 1 second)
            time_diff = abs((creation_time - updated_time).total_seconds())
            assert time_diff < 1.0


@pytest.mark.fast
@pytest.mark.database
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


@pytest.mark.fast
@pytest.mark.database
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


@pytest.mark.fast
@pytest.mark.database
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


@pytest.mark.fast
@pytest.mark.database
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


@pytest.mark.fast
@pytest.mark.database
class TestPortfolioCache:
    def test_cache_creation(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            cache = PortfolioCache(
                id="test-cache-id",
                portfolio_id=portfolio.id,
                cache_type="stats",
                market_date=date.today()
            )
            test_data = {"current_value": 10000.0, "total_gain_loss": 500.0}
            cache.set_data(test_data)
            
            db.session.add(cache)
            db.session.commit()
            
            assert cache.portfolio_id == portfolio.id
            assert cache.cache_type == "stats"
            assert cache.market_date == date.today()
            assert cache.created_at is not None

    def test_cache_data_serialization(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            cache = PortfolioCache(
                id="test-cache-id",
                portfolio_id=portfolio.id,
                cache_type="chart_data",
                market_date=date.today()
            )
            
            test_data = {
                "dates": ["2024-01-01", "2024-01-02"],
                "portfolio_values": [10000.0, 10500.0],
                "voo_values": [9800.0, 10200.0]
            }
            
            cache.set_data(test_data)
            db.session.add(cache)
            db.session.commit()
            
            # Retrieve and verify data
            retrieved_cache = PortfolioCache.query.filter_by(id="test-cache-id").first()
            retrieved_data = retrieved_cache.get_data()
            
            assert retrieved_data["dates"] == ["2024-01-01", "2024-01-02"]
            assert retrieved_data["portfolio_values"] == [10000.0, 10500.0]
            assert retrieved_data["voo_values"] == [9800.0, 10200.0]

    def test_cache_type_filtering(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            stats_cache = PortfolioCache(
                id="stats-cache",
                portfolio_id=portfolio.id,
                cache_type="stats",
                market_date=date.today()
            )
            stats_cache.set_data({"current_value": 10000.0})
            
            chart_cache = PortfolioCache(
                id="chart-cache",
                portfolio_id=portfolio.id,
                cache_type="chart_data",
                market_date=date.today()
            )
            chart_cache.set_data({"dates": ["2024-01-01"]})
            
            db.session.add_all([stats_cache, chart_cache])
            db.session.commit()
            
            # Query by cache type
            stats_result = PortfolioCache.query.filter_by(
                portfolio_id=portfolio.id,
                cache_type="stats"
            ).first()
            
            chart_result = PortfolioCache.query.filter_by(
                portfolio_id=portfolio.id,
                cache_type="chart_data"
            ).first()
            
            assert stats_result.cache_type == "stats"
            assert chart_result.cache_type == "chart_data"
            assert stats_result.get_data()["current_value"] == 10000.0
            assert chart_result.get_data()["dates"] == ["2024-01-01"]

    def test_cache_market_date_filtering(self, app):
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test_user")
            db.session.add(portfolio)
            db.session.commit()
            
            today_cache = PortfolioCache(
                id="today-cache",
                portfolio_id=portfolio.id,
                cache_type="stats",
                market_date=date.today()
            )
            today_cache.set_data({"current_value": 10000.0})
            
            yesterday_cache = PortfolioCache(
                id="yesterday-cache",
                portfolio_id=portfolio.id,
                cache_type="stats",
                market_date=date.today() - timedelta(days=1)
            )
            yesterday_cache.set_data({"current_value": 9500.0})
            
            db.session.add_all([today_cache, yesterday_cache])
            db.session.commit()
            
            # Query by market date
            today_result = PortfolioCache.query.filter_by(
                portfolio_id=portfolio.id,
                cache_type="stats",
                market_date=date.today()
            ).first()
            
            assert today_result.market_date == date.today()
            assert today_result.get_data()["current_value"] == 10000.0