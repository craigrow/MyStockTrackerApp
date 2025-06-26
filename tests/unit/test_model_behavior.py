"""Unit tests for model behavior using factories."""
import pytest
from datetime import date
from tests.utils.factories import PortfolioFactory, StockFactory, TransactionFactory
from tests.utils.assertions import assert_portfolio_data, assert_transaction_data


@pytest.mark.fast
@pytest.mark.database
class TestPortfolioBehavior:
    """Test portfolio model behavior using factories."""
    
    def test_portfolio_creation_behavior(self, app):
        """Test portfolio creation with expected behavior."""
        with app.app_context():
            # Act: Create portfolio using factory
            portfolio = PortfolioFactory.create_simple(
                user_id="test_user",
                name="Test Portfolio"
            )
            
            # Assert: Portfolio has expected behavior
            assert_portfolio_data(
                portfolio,
                expected_name="Test Portfolio",
                expected_user_id="test_user"
            )
    
    def test_portfolio_with_transactions_behavior(self, app):
        """Test portfolio with transactions behaves correctly."""
        with app.app_context():
            # Act: Create portfolio with transactions
            portfolio = PortfolioFactory.create_with_transactions(
                user_id="test_user",
                transaction_count=2
            )
            
            # Assert: Portfolio has transactions
            assert len(portfolio.transactions) == 2
            assert_portfolio_data(portfolio, expected_user_id="test_user")
            
            # Assert: Transactions have expected behavior
            for transaction in portfolio.transactions:
                assert_transaction_data(transaction)


@pytest.mark.fast
@pytest.mark.database
class TestTransactionBehavior:
    """Test transaction model behavior using factories."""
    
    def test_buy_transaction_behavior(self, app):
        """Test buy transaction creation behavior."""
        with app.app_context():
            # Arrange: Create portfolio
            portfolio = PortfolioFactory.create_simple()
            
            # Act: Create buy transaction
            transaction = TransactionFactory.create_buy(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                shares=10.0,
                price=150.00
            )
            
            # Assert: Transaction has expected behavior
            assert_transaction_data(
                transaction,
                expected_ticker="AAPL",
                expected_type="BUY",
                expected_shares=10.0
            )
            assert transaction.total_value == 1500.00
    
    def test_sell_transaction_behavior(self, app):
        """Test sell transaction creation behavior."""
        with app.app_context():
            # Arrange: Create portfolio
            portfolio = PortfolioFactory.create_simple()
            
            # Act: Create sell transaction
            transaction = TransactionFactory.create_sell(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                shares=5.0,
                price=160.00
            )
            
            # Assert: Transaction has expected behavior
            assert_transaction_data(
                transaction,
                expected_ticker="AAPL",
                expected_type="SELL",
                expected_shares=5.0
            )
            assert transaction.total_value == 800.00


@pytest.mark.fast
@pytest.mark.database
class TestStockBehavior:
    """Test stock model behavior using factories."""
    
    def test_stock_creation_behavior(self, app):
        """Test stock creation with factory."""
        with app.app_context():
            # Act: Create stock using factory
            stock = StockFactory.create(
                ticker="AAPL",
                name="Apple Inc.",
                sector="Technology"
            )
            
            # Assert: Stock has expected properties
            assert stock.ticker == "AAPL"
            assert stock.name == "Apple Inc."
            assert stock.sector == "Technology"
    
    def test_multiple_stocks_creation_behavior(self, app):
        """Test creating multiple stocks with factory."""
        with app.app_context():
            # Act: Create multiple stocks
            stocks = StockFactory.create_multiple(["AAPL", "GOOGL", "MSFT"])
            
            # Assert: All stocks created correctly
            assert len(stocks) == 3
            tickers = [stock.ticker for stock in stocks]
            assert "AAPL" in tickers
            assert "GOOGL" in tickers
            assert "MSFT" in tickers