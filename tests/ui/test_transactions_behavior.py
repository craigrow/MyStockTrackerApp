"""Behavior-focused tests for transactions page functionality."""
import pytest
from tests.utils.factories import PortfolioFactory, TransactionFactory
from tests.utils.assertions import (
    assert_response_success, assert_transaction_display, 
    assert_metrics_boxes_present, assert_sortable_table, 
    assert_filter_controls, assert_api_response_structure
)
from tests.utils.mocks import MockAPIResponses


@pytest.mark.ui
@pytest.mark.slow
class TestTransactionsBehavior:
    """Test transactions page behavior without coupling to implementation details."""
    
    def test_displays_portfolio_transactions(self, app, client):
        """Test that transactions page displays portfolio transactions correctly."""
        with app.app_context():
            # Arrange: Create portfolio with transactions
            portfolio = PortfolioFactory.create_with_transactions(transaction_count=2)
            
            # Act: Load transactions page
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            
            # Assert: Page loads and shows transactions
            assert_response_success(response)
            assert_transaction_display(response, portfolio.transactions)
    
    def test_handles_empty_portfolio(self, app, client):
        """Test transactions page behavior with empty portfolio."""
        with app.app_context():
            # Arrange: Create empty portfolio
            portfolio = PortfolioFactory.create_simple()
            
            # Act: Load transactions page
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            
            # Assert: Page loads without errors
            assert_response_success(response)
    
    def test_handles_no_portfolio_selected(self, client):
        """Test transactions page behavior when no portfolio is selected."""
        # Act: Load transactions page without portfolio
        response = client.get('/portfolio/transactions')
        
        # Assert: Page loads with appropriate message
        assert_response_success(response)
    
    def test_displays_performance_metrics(self, app, client):
        """Test that performance metrics boxes are displayed."""
        with app.app_context():
            # Arrange: Create portfolio with price data
            portfolio = PortfolioFactory.create_with_price_data()
            
            # Act: Load transactions page
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            
            # Assert: Metrics boxes are present
            assert_response_success(response)
            assert_metrics_boxes_present(response)
    
    def test_table_sorting_functionality(self, app, client):
        """Test that transaction table supports sorting."""
        with app.app_context():
            # Arrange: Create portfolio with multiple transactions
            portfolio = PortfolioFactory.create_with_transactions(transaction_count=3)
            
            # Act: Load transactions page
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            
            # Assert: Sortable table elements are present
            assert_response_success(response)
            assert_sortable_table(response)
    
    def test_filter_controls_present(self, app, client):
        """Test that filter controls are available."""
        with app.app_context():
            # Arrange: Create portfolio with mixed transactions
            portfolio = PortfolioFactory.create_simple()
            TransactionFactory.create_buy(portfolio.id, "AAPL")
            TransactionFactory.create_sell(portfolio.id, "AAPL")
            
            # Act: Load transactions page
            response = client.get(f'/portfolio/transactions?portfolio_id={portfolio.id}')
            
            # Assert: Filter controls are present
            assert_response_success(response)
            assert_filter_controls(response, ['all', 'buy', 'sell'])
    
    def test_current_price_api_integration(self, app, client, mock_price_service):
        """Test current price API returns expected data structure."""
        with app.app_context():
            # Act: Call current price API
            response = client.get('/api/current-price/AAPL')
            
            # Assert: API returns correct structure
            assert_response_success(response)
            data = response.get_json()
            assert_api_response_structure(data, ['ticker', 'price', 'success'])
            assert data['ticker'] == 'AAPL'
            assert data['success'] is True
    
    def test_etf_performance_api_behavior(self, app, client, mock_price_service):
        """Test ETF performance API returns expected behavior."""
        with app.app_context():
            # Act: Call ETF performance API
            response = client.get('/api/etf-performance/VOO/2025-06-17')
            
            # Assert: API returns performance data
            assert_response_success(response)
            data = response.get_json()
            expected_fields = ['ticker', 'purchase_date', 'purchase_price', 'current_price', 'performance']
            assert_api_response_structure(data, expected_fields)
            assert data['ticker'] == 'VOO'
            assert data['purchase_date'] == '2025-06-17'
    
    def test_portfolio_service_integration_behavior(self, app):
        """Test portfolio service returns transaction data correctly."""
        with app.app_context():
            # Arrange: Create portfolio with known transactions
            portfolio = PortfolioFactory.create_simple()
            transaction = TransactionFactory.create_buy(
                portfolio.id, 
                ticker="AAPL", 
                shares=10.0, 
                price=150.00
            )
            
            # Act: Get transactions through service
            from app.services.portfolio_service import PortfolioService
            service = PortfolioService()
            transactions = service.get_portfolio_transactions(portfolio.id)
            
            # Assert: Service returns expected data
            assert len(transactions) == 1
            assert transactions[0].ticker == "AAPL"
            assert transactions[0].shares == 10.0
            assert transactions[0].price_per_share == 150.00