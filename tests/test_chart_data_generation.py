"""Tests for chart data generation functionality."""
import pytest
from datetime import date, timedelta
from app.views.main import generate_chart_data
from app.models.transaction import StockTransaction

class TestChartDataGeneration:
    """Test chart data generation functionality."""
    
    def test_chart_data_with_many_tickers(self, app):
        """Test that chart data is generated even with many unique tickers."""
        with app.app_context():
            # Create mock services
            class MockPortfolioService:
                def get_portfolio_transactions(self, portfolio_id):
                    return self.transactions
                
                def __init__(self, transactions):
                    self.transactions = transactions
            
            class MockPriceService:
                def get_current_price(self, ticker, use_stale=False):
                    return 100.0
                
                def get_data_freshness(self, ticker, current_date):
                    return 0
            
            # Create test data with 30 different tickers (exceeds original 20 threshold)
            today = date.today()
            transactions = []
            
            # Create 30 transactions with different tickers
            for i in range(1, 31):
                ticker = f"STOCK{i}"
                transaction = StockTransaction(
                    id=f"test-transaction-{i}",
                    portfolio_id="test-portfolio",
                    ticker=ticker,
                    transaction_type="BUY",
                    date=today - timedelta(days=30),
                    price_per_share=100.0,
                    shares=1.0,
                    total_value=100.0
                )
                transactions.append(transaction)
            
            # Create mock services
            portfolio_service = MockPortfolioService(transactions)
            price_service = MockPriceService()
            
            # Generate chart data
            chart_data = generate_chart_data("test-portfolio", portfolio_service, price_service)
            
            # Assert that chart data is not empty
            assert len(chart_data['dates']) > 0, "Chart data dates should not be empty"
            assert len(chart_data['portfolio_values']) > 0, "Chart data portfolio values should not be empty"
            assert len(chart_data['voo_values']) > 0, "Chart data VOO values should not be empty"
            assert len(chart_data['qqq_values']) > 0, "Chart data QQQ values should not be empty"
    
    def test_chart_data_error_handling(self, app):
        """Test that chart data generation handles errors gracefully."""
        with app.app_context():
            # Create mock services with error-inducing behavior
            class MockPortfolioService:
                def get_portfolio_transactions(self, portfolio_id):
                    return self.transactions
                
                def __init__(self, transactions):
                    self.transactions = transactions
            
            class MockPriceService:
                def get_current_price(self, ticker, use_stale=False):
                    if ticker == "ERROR_TICKER":
                        raise Exception("Simulated price fetch error")
                    return 100.0
                
                def get_data_freshness(self, ticker, current_date):
                    return 0
            
            # Create test data with a mix of normal and error-inducing tickers
            today = date.today()
            transactions = []
            
            # Add normal transactions
            for i in range(1, 5):
                ticker = f"STOCK{i}"
                transaction = StockTransaction(
                    id=f"test-transaction-{i}",
                    portfolio_id="test-portfolio",
                    ticker=ticker,
                    transaction_type="BUY",
                    date=today - timedelta(days=30),
                    price_per_share=100.0,
                    shares=1.0,
                    total_value=100.0
                )
                transactions.append(transaction)
            
            # Add error-inducing transaction
            error_transaction = StockTransaction(
                id="test-transaction-error",
                portfolio_id="test-portfolio",
                ticker="ERROR_TICKER",
                transaction_type="BUY",
                date=today - timedelta(days=30),
                price_per_share=100.0,
                shares=1.0,
                total_value=100.0
            )
            transactions.append(error_transaction)
            
            # Create mock services
            portfolio_service = MockPortfolioService(transactions)
            price_service = MockPriceService()
            
            # Generate chart data - should not raise exception
            chart_data = generate_chart_data("test-portfolio", portfolio_service, price_service)
            
            # Assert that chart data is not empty despite errors
            assert len(chart_data['dates']) > 0, "Chart data dates should not be empty despite errors"
            assert len(chart_data['portfolio_values']) > 0, "Chart data portfolio values should not be empty despite errors"