"""Integration tests for multi-portfolio scenarios and data interactions."""
import pytest
from datetime import date
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from tests.integration.utils.assertion_helpers import ResponseAssertions
from app.models.portfolio import Portfolio, StockTransaction
from app.services.portfolio_service import PortfolioService


@pytest.mark.fast
@pytest.mark.database
class TestMultiPortfolioScenarios:
    """Test complex data interactions across multiple portfolios."""
    
    def test_multiple_portfolios_data_isolation(self, app, client):
        """Test that portfolios maintain data isolation."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create multiple portfolios using multi-scenario factory
                portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
                portfolio1 = portfolios[0]  # Tech Portfolio
                portfolio2 = portfolios[1]  # Mixed Portfolio
                
                # Add different transactions to each portfolio
                service = PortfolioService()
                service.add_transaction(portfolio1.id, 'MSFT', 'BUY', date(2023, 2, 1), 300.00, 5.0)
                service.add_transaction(portfolio2.id, 'JPM', 'BUY', date(2023, 2, 1), 140.00, 8.0)
                
                # Act & Assert: Verify data isolation
                portfolio1_transactions = StockTransaction.query.filter_by(portfolio_id=portfolio1.id).all()
                portfolio2_transactions = StockTransaction.query.filter_by(portfolio_id=portfolio2.id).all()
                
                # Verify each portfolio has its own transactions
                portfolio1_tickers = {t.ticker for t in portfolio1_transactions}
                portfolio2_tickers = {t.ticker for t in portfolio2_transactions}
                
                assert 'MSFT' in portfolio1_tickers, "Portfolio 1 should have MSFT"
                assert 'MSFT' not in portfolio2_tickers, "Portfolio 2 should not have MSFT"
                assert 'JPM' in portfolio2_tickers, "Portfolio 2 should have JPM"
                assert 'JPM' not in portfolio1_tickers, "Portfolio 1 should not have JPM"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_portfolio_switching_maintains_context(self, app, client):
        """Test that switching between portfolios maintains correct context."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolios with distinct characteristics
                portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
                tech_portfolio = portfolios[0]
                energy_portfolio = portfolios[1]
                
                # Act: Test dashboard for each portfolio
                tech_response = client.get(f'/dashboard?portfolio_id={tech_portfolio.id}')
                energy_response = client.get(f'/dashboard?portfolio_id={energy_portfolio.id}')
                
                # Assert: Each dashboard shows correct portfolio data
                ResponseAssertions.assert_response_success(tech_response)
                ResponseAssertions.assert_response_success(energy_response)
                
                # Verify portfolio names appear in responses
                assert tech_portfolio.name.encode() in tech_response.data, "Tech portfolio name should appear"
                assert energy_portfolio.name.encode() in energy_response.data, "Energy portfolio name should appear"
                
                # Verify cross-contamination doesn't occur
                assert energy_portfolio.name.encode() not in tech_response.data, "Energy portfolio should not appear in tech dashboard"
                assert tech_portfolio.name.encode() not in energy_response.data, "Tech portfolio should not appear in energy dashboard"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_concurrent_portfolio_operations(self, app, client):
        """Test that concurrent operations on different portfolios work correctly."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create multiple portfolios
                portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
                
                service = PortfolioService()
                
                # Act: Perform operations on all portfolios simultaneously
                for i, portfolio in enumerate(portfolios):
                    # Add different stocks to each portfolio
                    tickers = ['AAPL', 'GOOGL', 'MSFT']
                    service.add_transaction(portfolio.id, tickers[i], 'BUY', date(2023, 3, 1), 100.00 + i*10, 10.0)
                
                # Assert: Verify each portfolio has correct data
                for i, portfolio in enumerate(portfolios):
                    transactions = StockTransaction.query.filter_by(portfolio_id=portfolio.id).all()
                    expected_ticker = ['AAPL', 'GOOGL', 'MSFT'][i]
                    
                    # Find the specific transaction we added
                    added_transaction = next((t for t in transactions if t.ticker == expected_ticker), None)
                    assert added_transaction is not None, f"Portfolio {i+1} should have {expected_ticker} transaction"
                    assert added_transaction.price_per_share == 100.00 + i*10, f"Portfolio {i+1} should have correct price"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_portfolio_performance_calculations_independent(self, app, client):
        """Test that portfolio performance calculations are independent."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolios with different performance profiles
                portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
                winning_portfolio = portfolios[0]
                losing_portfolio = portfolios[1]
                
                service = PortfolioService()
                
                # Add transactions that should have different performance
                # Winner: Buy low, current price higher (mocked)
                service.add_transaction(winning_portfolio.id, 'WINNER', 'BUY', date(2023, 1, 1), 50.00, 10.0)
                
                # Loser: Buy high, current price lower (mocked)  
                service.add_transaction(losing_portfolio.id, 'LOSER', 'BUY', date(2023, 1, 1), 200.00, 10.0)
                
                # Act: Calculate performance for both portfolios
                winning_stats = service.get_portfolio_stats(winning_portfolio.id)
                losing_stats = service.get_portfolio_stats(losing_portfolio.id)
                
                # Assert: Performance calculations are independent
                assert winning_stats is not None, "Winning portfolio should have stats"
                assert losing_stats is not None, "Losing portfolio should have stats"
                
                # Verify portfolios have different values (due to different stocks/prices)
                assert winning_stats != losing_stats, "Portfolio stats should be different"
                
            finally:
                for mock in mocks:
                    mock.stop()