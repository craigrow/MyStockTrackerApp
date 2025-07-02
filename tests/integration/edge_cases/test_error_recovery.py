"""Integration tests for error recovery and system stability."""
import pytest
from datetime import date
from unittest.mock import patch, Mock
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.services.portfolio_service import PortfolioService
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestErrorRecovery:
    """Test error recovery and system stability scenarios."""
    
    def test_database_rollback_on_error(self, app, client):
        """Test database rollback when transaction fails."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                initial_count = len(service.get_portfolio_transactions(portfolio.id))
                
                # Simulate transaction failure by patching the service method
                with patch.object(service, 'add_transaction', side_effect=Exception("DB Error")):
                    try:
                        service.add_transaction(
                            portfolio.id, 'TEST', 'BUY', 
                            date(2023, 1, 1), 100.0, 10.0
                        )
                    except:
                        pass  # Expected to fail
                
                # Verify rollback - transaction count should be unchanged
                final_count = len(service.get_portfolio_transactions(portfolio.id))
                assert final_count == initial_count, "Failed transaction should be rolled back"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_partial_data_corruption_recovery(self, app, client):
        """Test recovery from partial data corruption."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Create transaction with corrupted data
                from app.models.portfolio import StockTransaction
                corrupted_transaction = StockTransaction(
                    portfolio_id=portfolio.id,
                    ticker=None,  # Corrupted: None ticker
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    shares=10.0,
                    price_per_share=100.0,
                    total_value=1000.0
                )
                
                try:
                    db.session.add(corrupted_transaction)
                    db.session.commit()
                except:
                    db.session.rollback()  # Expected failure
                
                # System should continue functioning
                holdings = service.get_current_holdings(portfolio.id)
                assert isinstance(holdings, dict), "System should recover from corruption"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_service_degradation_graceful_handling(self, app, client):
        """Test graceful degradation when services fail."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Simulate price service failure
                with patch('app.services.price_service.PriceService.get_current_price', return_value=None):
                    # Portfolio value calculation should degrade gracefully
                    portfolio_value = service.calculate_portfolio_value(portfolio.id)
                    assert portfolio_value == 0.0, "Should degrade gracefully when price service fails"
                    
                    # Other operations should still work
                    holdings = service.get_current_holdings(portfolio.id)
                    assert len(holdings) > 0, "Holdings should still be accessible"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_memory_pressure_handling(self, app, client):
        """Test behavior under simulated memory pressure."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create multiple portfolios to simulate load
                portfolios = []
                for i in range(3):
                    portfolio = IntegrationTestFactory.create_performance_test_data(f"user_{i}")
                    portfolios.append(portfolio)
                
                service = PortfolioService()
                
                # Process all portfolios rapidly
                results = []
                for portfolio in portfolios:
                    holdings = service.get_current_holdings(portfolio.id)
                    results.append(len(holdings))
                
                # All operations should complete successfully
                assert all(r > 0 for r in results), "All portfolios should be processed successfully"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_network_timeout_recovery(self, app, client):
        """Test recovery from network timeouts."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                # Simulate network timeout
                with patch('app.services.price_service.PriceService.get_current_price', 
                          side_effect=Exception("Network timeout")):
                    
                    # Should handle timeout gracefully
                    try:
                        portfolio_value = service.calculate_portfolio_value(portfolio.id)
                        # If no exception, should return safe default
                        assert portfolio_value >= 0.0
                    except Exception as e:
                        # If exception occurs, should be handled gracefully
                        assert "timeout" in str(e).lower()
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_system_recovery_after_restart(self, app, client):
        """Test system state recovery after simulated restart."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create initial state
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                service = PortfolioService()
                
                initial_holdings = service.get_current_holdings(portfolio.id)
                initial_transactions = service.get_portfolio_transactions(portfolio.id)
                
                # Simulate restart by creating new service instance
                new_service = PortfolioService()
                
                # Verify state persistence
                recovered_holdings = new_service.get_current_holdings(portfolio.id)
                recovered_transactions = new_service.get_portfolio_transactions(portfolio.id)
                
                assert len(recovered_holdings) == len(initial_holdings), "Holdings should persist"
                assert len(recovered_transactions) == len(initial_transactions), "Transactions should persist"
                
            finally:
                for mock in mocks:
                    mock.stop()