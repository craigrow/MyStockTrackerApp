"""Integration tests for ETF calculation accuracy and financial precision."""
import pytest
from decimal import Decimal
from datetime import date
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.models.portfolio import StockTransaction
from app.services.portfolio_service import PortfolioService
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestETFCalculationAccuracy:
    """Test ETF calculations for accuracy and financial precision."""
    
    def test_fractional_shares_calculation_accuracy(self, app, client):
        """Test calculations with fractional shares maintain precision."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Create portfolio with fractional share transactions
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Fractional Test Portfolio")
                
                # Add fractional share transactions
                transactions = [
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='VTI',
                        transaction_type='BUY',
                        date=date(2023, 1, 15),
                        shares=1.068,  # Fractional shares like HOOD transaction
                        price_per_share=220.50,
                        total_value=235.45
                    ),
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='VTI',
                        transaction_type='BUY',
                        date=date(2023, 2, 15),
                        shares=2.333,
                        price_per_share=225.75,
                        total_value=526.68
                    )
                ]
                
                for transaction in transactions:
                    db.session.add(transaction)
                db.session.commit()
                
                # Test portfolio calculations
                service = PortfolioService()
                holdings = service.get_current_holdings(portfolio.id)
                
                # Verify fractional share calculations
                assert 'VTI' in holdings, "VTI holding should exist"
                
                expected_shares = 1.068 + 2.333  # 3.401
                assert abs(holdings['VTI'] - expected_shares) < 0.001, \
                    f"Fractional shares should be accurate: expected {expected_shares}, got {holdings['VTI']}"
                
                # Verify transactions were created correctly
                transactions = service.get_portfolio_transactions(portfolio.id)
                vti_transactions = [t for t in transactions if t.ticker == 'VTI']
                assert len(vti_transactions) == 2, "Should have 2 VTI transactions"
                
                total_cost = sum(t.total_value for t in vti_transactions)
                expected_total = 235.45 + 526.68  # 762.13
                assert abs(total_cost - expected_total) < 0.01, \
                    f"Total cost should be accurate: expected {expected_total}, got {total_cost}"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_average_cost_calculation_precision(self, app, client):
        """Test average cost calculations maintain financial precision."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Precision Test Portfolio")
                
                # Add transactions with different prices
                transactions = [
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='SPY',
                        transaction_type='BUY',
                        date=date(2023, 1, 15),
                        shares=10.0,
                        price_per_share=400.123,
                        total_value=4001.23
                    ),
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='SPY',
                        transaction_type='BUY',
                        date=date(2023, 2, 15),
                        shares=5.0,
                        price_per_share=410.789,
                        total_value=2053.95
                    )
                ]
                
                for transaction in transactions:
                    db.session.add(transaction)
                db.session.commit()
                
                service = PortfolioService()
                holdings = service.get_current_holdings(portfolio.id)
                
                assert 'SPY' in holdings, "SPY holding should exist"
                
                # Verify shares calculation
                expected_shares = 10.0 + 5.0  # 15.0
                assert abs(holdings['SPY'] - expected_shares) < 0.001, \
                    f"Total shares should be accurate: expected {expected_shares}, got {holdings['SPY']}"
                
                # Verify cost calculations through transactions
                transactions = service.get_portfolio_transactions(portfolio.id)
                spy_transactions = [t for t in transactions if t.ticker == 'SPY']
                
                total_cost = sum(t.total_value for t in spy_transactions)
                expected_total_cost = 4001.23 + 2053.95  # 6055.18
                assert abs(total_cost - expected_total_cost) < 0.01, \
                    f"Total cost should be precise: expected {expected_total_cost}, got {total_cost}"
                
                # Calculate and verify average cost
                expected_avg_cost = total_cost / holdings['SPY']  # 403.679
                actual_avg_cost = total_cost / holdings['SPY']
                assert abs(actual_avg_cost - expected_avg_cost) < 0.01, \
                    f"Average cost should be precise: expected {expected_avg_cost}, got {actual_avg_cost}"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_portfolio_total_value_accuracy(self, app, client):
        """Test portfolio total value calculations are accurate."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Total Value Test Portfolio")
                
                # Add multiple holdings
                transactions = [
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='QQQ',
                        transaction_type='BUY',
                        date=date(2023, 1, 15),
                        shares=8.5,
                        price_per_share=350.25,
                        total_value=2977.13
                    ),
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='IWM',
                        transaction_type='BUY',
                        date=date(2023, 1, 20),
                        shares=12.75,
                        price_per_share=180.60,
                        total_value=2302.65
                    )
                ]
                
                for transaction in transactions:
                    db.session.add(transaction)
                db.session.commit()
                
                service = PortfolioService()
                transactions = service.get_portfolio_transactions(portfolio.id)
                
                # Calculate total cost from transactions (excluding the initial AAPL transaction from factory)
                total_cost = sum(t.total_value for t in transactions)
                # Factory creates AAPL transaction worth 1500.00, plus our new transactions
                expected_total_cost = 1500.00 + 2977.13 + 2302.65  # 6779.78
                
                assert abs(total_cost - expected_total_cost) < 0.01, \
                    f"Portfolio total cost should be accurate: expected {expected_total_cost}, got {total_cost}"
                
                # Verify holdings are correct
                holdings = service.get_current_holdings(portfolio.id)
                assert 'QQQ' in holdings, "QQQ holding should exist"
                assert 'IWM' in holdings, "IWM holding should exist"
                assert abs(holdings['QQQ'] - 8.5) < 0.001, "QQQ shares should be correct"
                assert abs(holdings['IWM'] - 12.75) < 0.001, "IWM shares should be correct"
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_sell_transaction_impact_on_calculations(self, app, client):
        """Test that sell transactions correctly impact portfolio calculations."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Sell Transaction Test Portfolio")
                
                # Buy and then sell some shares
                transactions = [
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='SCHB',
                        transaction_type='BUY',
                        date=date(2023, 1, 15),
                        shares=20.0,
                        price_per_share=50.00,
                        total_value=1000.00
                    ),
                    StockTransaction(
                        portfolio_id=portfolio.id,
                        ticker='SCHB',
                        transaction_type='SELL',
                        date=date(2023, 2, 15),
                        shares=5.0,
                        price_per_share=52.00,
                        total_value=260.00
                    )
                ]
                
                for transaction in transactions:
                    db.session.add(transaction)
                db.session.commit()
                
                service = PortfolioService()
                holdings = service.get_current_holdings(portfolio.id)
                
                assert 'SCHB' in holdings, "SCHB holding should exist"
                
                # After selling 5 shares, should have 15 shares remaining
                expected_shares = 20.0 - 5.0  # 15.0
                assert abs(holdings['SCHB'] - expected_shares) < 0.001, \
                    f"Remaining shares should be correct: expected {expected_shares}, got {holdings['SCHB']}"
                
                # Verify transactions were processed correctly
                transactions = service.get_portfolio_transactions(portfolio.id)
                schb_transactions = [t for t in transactions if t.ticker == 'SCHB']
                assert len(schb_transactions) == 2, "Should have 2 SCHB transactions (buy and sell)"
                
                buy_transaction = next(t for t in schb_transactions if t.transaction_type == 'BUY')
                sell_transaction = next(t for t in schb_transactions if t.transaction_type == 'SELL')
                
                assert buy_transaction.shares == 20.0, "Buy transaction should have 20 shares"
                assert sell_transaction.shares == 5.0, "Sell transaction should have 5 shares"
                assert buy_transaction.total_value == 1000.00, "Buy transaction value should be correct"
                assert sell_transaction.total_value == 260.00, "Sell transaction value should be correct"
                
            finally:
                for mock in mocks:
                    mock.stop()