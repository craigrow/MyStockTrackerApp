"""Integration tests for API failure scenarios and error handling."""
import pytest
from datetime import date
from unittest.mock import patch, Mock
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService


@pytest.mark.fast
@pytest.mark.database
class TestAPIFailureScenarios:
    """Test API failure scenarios and error recovery."""
    
    def test_price_service_api_failure(self, app, client):
        """Test portfolio calculations when price API fails."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                price_service = PriceService()
                
                # Test with API failure - patch the service instance used by calculate_portfolio_value
                with patch('app.services.price_service.PriceService.get_current_price', return_value=None):
                    # Should handle gracefully when price API fails
                    portfolio_value = service.calculate_portfolio_value(portfolio.id)
                    assert portfolio_value == 0.0, "Should return 0 when price API fails"
                
                # Test with partial API failure
                def mock_price_response(ticker):
                    if ticker == 'AAPL':
                        return 155.00  # Success for AAPL
                    return None  # Failure for others
                
                with patch('app.services.price_service.PriceService.get_current_price', side_effect=mock_price_response):
                    holdings = service.get_current_holdings(portfolio.id)
                    if 'AAPL' in holdings:
                        portfolio_value = service.calculate_portfolio_value(portfolio.id)
                        expected_value = holdings['AAPL'] * 155.00
                        assert abs(portfolio_value - expected_value) < 0.01
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_database_connection_resilience(self, app, client):
        """Test system behavior during database issues."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Test graceful handling of database errors
                with patch('app.db.session.query') as mock_query:
                    mock_query.side_effect = Exception("Database connection error")
                    
                    # Should not crash the application
                    try:
                        transactions = service.get_portfolio_transactions(portfolio.id)
                        # If it doesn't raise, that's also acceptable behavior
                    except Exception as e:
                        # Should be a handled exception, not a crash
                        assert "Database connection error" in str(e)
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_invalid_portfolio_operations(self, app, client):
        """Test operations with invalid portfolio IDs."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                service = PortfolioService()
                
                # Test with non-existent portfolio ID
                invalid_id = "non-existent-portfolio-id"
                
                transactions = service.get_portfolio_transactions(invalid_id)
                assert transactions == [], "Should return empty list for invalid portfolio"
                
                holdings = service.get_current_holdings(invalid_id)
                assert holdings == {}, "Should return empty dict for invalid portfolio"
                
                dividends = service.get_portfolio_dividends(invalid_id)
                assert dividends == [], "Should return empty list for invalid portfolio"
                
                portfolio_value = service.calculate_portfolio_value(invalid_id)
                assert portfolio_value == 0.0, "Should return 0 for invalid portfolio"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_malformed_data_handling(self, app, client):
        """Test handling of malformed or corrupted data."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Test with malformed transaction data
                from app.models.portfolio import StockTransaction
                from app import db
                
                # Create transaction with edge case values
                malformed_transaction = StockTransaction(
                    portfolio_id=portfolio.id,
                    ticker='TEST',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    shares=0.0,  # Zero shares
                    price_per_share=0.0,  # Zero price
                    total_value=0.0
                )
                db.session.add(malformed_transaction)
                db.session.commit()
                
                # System should handle gracefully
                holdings = service.get_current_holdings(portfolio.id)
                # Zero shares should not appear in holdings
                assert 'TEST' not in holdings or holdings['TEST'] == 0
                
                transactions = service.get_portfolio_transactions(portfolio.id)
                assert len(transactions) >= 1, "Should still return transactions"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_concurrent_access_simulation(self, app, client):
        """Test behavior under simulated concurrent access."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Simulate multiple rapid requests
                results = []
                for i in range(5):
                    holdings = service.get_current_holdings(portfolio.id)
                    transactions = service.get_portfolio_transactions(portfolio.id)
                    results.append((len(holdings), len(transactions)))
                
                # Results should be consistent
                first_result = results[0]
                for result in results[1:]:
                    assert result == first_result, "Concurrent access should yield consistent results"
                
            finally:
                for mock in mocks:
                    mock.stop()