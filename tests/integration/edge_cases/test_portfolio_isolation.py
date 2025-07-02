"""Integration tests for multi-portfolio edge cases and isolation."""
import pytest
from datetime import date
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import StockTransaction
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestMultiPortfolioScenarios:
    """Test edge cases with multiple portfolios."""
    
    def test_portfolio_isolation(self, app, client):
        """Test that portfolios are properly isolated from each other."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create multiple portfolios
                portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
                service = PortfolioService()
                
                # Verify each portfolio has only its own transactions
                for i, portfolio in enumerate(portfolios):
                    transactions = service.get_portfolio_transactions(portfolio.id)
                    assert len(transactions) == 1, f"Portfolio {i} should have exactly 1 transaction"
                    
                    # Verify transaction belongs to correct portfolio
                    for transaction in transactions:
                        assert transaction.portfolio_id == portfolio.id, \
                            f"Transaction should belong to portfolio {portfolio.id}"
                
                # Verify holdings are isolated
                holdings_1 = service.get_current_holdings(portfolios[0].id)
                holdings_2 = service.get_current_holdings(portfolios[1].id)
                holdings_3 = service.get_current_holdings(portfolios[2].id)
                
                assert 'AAPL' in holdings_1 and 'AAPL' not in holdings_2 and 'AAPL' not in holdings_3
                assert 'GOOGL' in holdings_2 and 'GOOGL' not in holdings_1 and 'GOOGL' not in holdings_3
                assert 'MSFT' in holdings_3 and 'MSFT' not in holdings_1 and 'MSFT' not in holdings_2
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_same_ticker_different_portfolios(self, app, client):
        """Test same ticker in different portfolios maintains separate calculations."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create two portfolios with same ticker at different prices
                portfolio1 = IntegrationTestFactory.create_portfolio_with_chart_data(name="Portfolio 1")
                
                # Create second portfolio without chart data to avoid price history conflicts
                from app.models.portfolio import Portfolio
                portfolio2 = Portfolio(
                    name="Portfolio 2",
                    description="Second portfolio for testing",
                    user_id="test_user"
                )
                db.session.add(portfolio2)
                db.session.flush()
                
                # Add initial AAPL transaction to portfolio2
                initial_transaction = StockTransaction(
                    portfolio_id=portfolio2.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 15),
                    shares=10.0,
                    price_per_share=150.00,
                    total_value=1500.00
                )
                db.session.add(initial_transaction)
                db.session.commit()
                
                # Add AAPL to both portfolios at different prices
                transactions = [
                    StockTransaction(
                        portfolio_id=portfolio1.id,
                        ticker='AAPL',
                        transaction_type='BUY',
                        date=date(2023, 2, 1),
                        shares=5.0,
                        price_per_share=160.00,
                        total_value=800.00
                    ),
                    StockTransaction(
                        portfolio_id=portfolio2.id,
                        ticker='AAPL',
                        transaction_type='BUY',
                        date=date(2023, 2, 1),
                        shares=10.0,
                        price_per_share=140.00,
                        total_value=1400.00
                    )
                ]
                
                for transaction in transactions:
                    db.session.add(transaction)
                db.session.commit()
                
                service = PortfolioService()
                
                # Verify separate holdings calculations
                holdings1 = service.get_current_holdings(portfolio1.id)
                holdings2 = service.get_current_holdings(portfolio2.id)
                
                # Portfolio 1: original 10 shares + new 5 shares = 15 shares
                assert abs(holdings1['AAPL'] - 15.0) < 0.001
                
                # Portfolio 2: original 10 shares + new 10 shares = 20 shares  
                assert abs(holdings2['AAPL'] - 20.0) < 0.001
                
                # Verify cost calculations are separate
                transactions1 = service.get_portfolio_transactions(portfolio1.id)
                transactions2 = service.get_portfolio_transactions(portfolio2.id)
                
                aapl_cost1 = sum(t.total_value for t in transactions1 if t.ticker == 'AAPL')
                aapl_cost2 = sum(t.total_value for t in transactions2 if t.ticker == 'AAPL')
                
                # Portfolio 1: 1500 (original) + 800 (new) = 2300
                assert abs(aapl_cost1 - 2300.00) < 0.01
                
                # Portfolio 2: 1500 (original) + 1400 (new) = 2900
                assert abs(aapl_cost2 - 2900.00) < 0.01
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_empty_portfolio_edge_cases(self, app, client):
        """Test edge cases with empty portfolios."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create empty portfolio (without using factory that adds transactions)
                from app.models.portfolio import Portfolio
                empty_portfolio = Portfolio(
                    name="Empty Portfolio",
                    description="Portfolio with no transactions",
                    user_id="test_user"
                )
                db.session.add(empty_portfolio)
                db.session.commit()
                
                service = PortfolioService()
                
                # Test empty portfolio operations
                transactions = service.get_portfolio_transactions(empty_portfolio.id)
                assert len(transactions) == 0, "Empty portfolio should have no transactions"
                
                holdings = service.get_current_holdings(empty_portfolio.id)
                assert len(holdings) == 0, "Empty portfolio should have no holdings"
                
                dividends = service.get_portfolio_dividends(empty_portfolio.id)
                assert len(dividends) == 0, "Empty portfolio should have no dividends"
                
                cash_balance = service.get_cash_balance(empty_portfolio.id)
                assert cash_balance == 0.0, "Empty portfolio should have zero cash balance"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_large_portfolio_performance(self, app, client):
        """Test performance with larger portfolio data sets."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create portfolio with performance test data
                portfolio = IntegrationTestFactory.create_performance_test_data()
                service = PortfolioService()
                
                # Test operations complete in reasonable time
                import time
                
                start_time = time.time()
                transactions = service.get_portfolio_transactions(portfolio.id)
                transaction_time = time.time() - start_time
                
                start_time = time.time()
                holdings = service.get_current_holdings(portfolio.id)
                holdings_time = time.time() - start_time
                
                # Verify data integrity
                assert len(transactions) == 5, "Should have 5 transactions"
                assert len(holdings) == 5, "Should have 5 holdings"
                
                # Performance assertions (should be fast with mocked data)
                assert transaction_time < 1.0, f"Transaction query too slow: {transaction_time}s"
                assert holdings_time < 1.0, f"Holdings calculation too slow: {holdings_time}s"
                
            finally:
                for mock in mocks:
                    mock.stop()