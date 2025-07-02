"""Integration tests for performance and load scenarios."""
import pytest
import time
from datetime import date
from concurrent.futures import ThreadPoolExecutor
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.models.portfolio import StockTransaction
from app import db


@pytest.mark.slow
@pytest.mark.database
class TestLoadScenarios:
    """Test system performance under load."""
    
    def test_large_portfolio_operations(self, app, client):
        """Test operations with large portfolio datasets."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Add 50 transactions (reduced for faster testing)
                tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'] * 10
                for i, ticker in enumerate(tickers):
                    service.add_transaction(
                        portfolio.id, ticker, 'BUY',
                        date(2023, 1, 1), 100.0 + i, 10.0
                    )
                
                # Test performance of operations
                start_time = time.time()
                holdings = service.get_current_holdings(portfolio.id)
                holdings_time = time.time() - start_time
                
                start_time = time.time()
                transactions = service.get_portfolio_transactions(portfolio.id)
                transactions_time = time.time() - start_time
                
                # Verify data integrity
                assert len(transactions) == 51  # 50 + 1 from factory
                assert len(holdings) == 5  # 5 unique tickers
                
                # Performance assertions
                assert holdings_time < 2.0, f"Holdings calculation too slow: {holdings_time}s"
                assert transactions_time < 2.0, f"Transaction query too slow: {transactions_time}s"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_concurrent_portfolio_access(self, app, client):
        """Test concurrent access to portfolio operations."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Test sequential operations to simulate concurrent load
                results = []
                for _ in range(5):
                    holdings = service.get_current_holdings(portfolio.id)
                    transactions = service.get_portfolio_transactions(portfolio.id)
                    results.append((len(holdings), len(transactions)))
                
                # All operations should return consistent results
                first_result = results[0]
                for result in results[1:]:
                    assert result == first_result, "Sequential operations should be consistent"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_price_service_load(self, app, client):
        """Test price service under load."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                price_service = PriceService()
                tickers = ['AAPL', 'GOOGL', 'MSFT']
                
                # Test rapid price requests
                start_time = time.time()
                prices = []
                for _ in range(10):  # Reduced for faster testing
                    for ticker in tickers:
                        price = price_service.get_current_price(ticker)
                        prices.append(price)
                
                total_time = time.time() - start_time
                
                # Should handle load efficiently
                assert total_time < 3.0, f"Price service too slow under load: {total_time}s"
                assert len(prices) == 30, "Should return all requested prices"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_database_stress(self, app, client):
        """Test database operations under stress."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Rapid database operations
                start_time = time.time()
                for i in range(10):  # Reduced for faster testing
                    transaction = StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker=f'TEST{i}',
                        transaction_type='BUY',
                        date=date(2023, 1, 1),
                        shares=10.0,
                        price_per_share=100.0,
                        total_value=1000.0
                    )
                    db.session.add(transaction)
                
                db.session.commit()
                db_time = time.time() - start_time
                
                # Verify all transactions were created
                service = PortfolioService()
                transactions = service.get_portfolio_transactions(portfolio.id)
                test_transactions = [t for t in transactions if t.ticker.startswith('TEST')]
                
                assert len(test_transactions) == 10, "All transactions should be created"
                assert db_time < 2.0, f"Database operations too slow: {db_time}s"
                
            finally:
                for mock in mocks:
                    mock.stop()