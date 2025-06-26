"""Integration tests for complete portfolio workflows."""
import pytest
from tests.utils.factories import PortfolioFactory, TransactionFactory
from tests.utils.assertions import assert_response_success, assert_api_response_structure


@pytest.mark.slow
@pytest.mark.database
class TestPortfolioWorkflows:
    """Test complete portfolio management workflows."""
    
    def test_complete_portfolio_creation_workflow(self, app, client):
        """Test complete workflow from portfolio creation to viewing."""
        with app.app_context():
            # Step 1: Create portfolio
            portfolio = PortfolioFactory.create_simple(name="Integration Test Portfolio")
            
            # Step 2: Add transactions
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10.0, 150.00)
            TransactionFactory.create_buy(portfolio.id, "GOOGL", 2.0, 2500.00)
            
            # Step 3: View dashboard
            response = client.get(f'/?portfolio_id={portfolio.id}')
            assert_response_success(response)
            
            # Step 4: View transactions
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            assert_response_success(response)
            
            # Step 5: Refresh prices
            response = client.get(f'/api/refresh-holdings/{portfolio.id}')
            assert_response_success(response)
            data = response.get_json()
            assert_api_response_structure(data, ['success', 'holdings', 'timestamp'])
    
    def test_portfolio_performance_calculation_workflow(self, app, client, mock_price_service):
        """Test complete performance calculation workflow."""
        with app.app_context():
            # Step 1: Create portfolio with price data
            portfolio = PortfolioFactory.create_with_price_data()
            
            # Step 2: Calculate current performance
            response = client.get(f'/api/refresh-all-prices/{portfolio.id}')
            assert_response_success(response)
            
            # Step 3: Get ETF performance comparison
            response = client.get('/api/etf-performance/VOO/2023-01-01')
            assert_response_success(response)
            data = response.get_json()
            assert_api_response_structure(data, ['ticker', 'performance'])
    
    def test_csv_import_workflow(self, app, client):
        """Test CSV import workflow (placeholder for future implementation)."""
        with app.app_context():
            # This would test the complete CSV import workflow
            # when that functionality is implemented
            portfolio = PortfolioFactory.create_simple()
            
            # For now, just verify portfolio exists
            assert portfolio.id is not None
            assert portfolio.name is not None