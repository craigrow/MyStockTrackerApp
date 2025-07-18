"""Test for chart data generation with large number of tickers."""
import pytest
from datetime import date, timedelta
from app.views.main import generate_chart_data
from app.models.portfolio import Portfolio
from app.models.portfolio import StockTransaction
from app import db

class TestChartThreshold:
    """Test chart data generation with large number of tickers."""
    
    def test_chart_generation_with_many_tickers(self, app):
        """Test that chart data is generated even with more than 20 tickers."""
        with app.app_context():
            # Create a mock portfolio service
            class MockPortfolioService:
                def get_portfolio_transactions(self, portfolio_id):
                    return self.transactions
                
                def __init__(self, transactions):
                    self.transactions = transactions
            
            # Create a mock price service
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
            
            # Print chart data summary
            print(f"Generated chart data with {len(transactions)} tickers:")
            print(f"- Dates: {len(chart_data['dates'])} points")
            print(f"- Portfolio values: {len(chart_data['portfolio_values'])} points")
            print(f"- VOO values: {len(chart_data['voo_values'])} points")
            print(f"- QQQ values: {len(chart_data['qqq_values'])} points")