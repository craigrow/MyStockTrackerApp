import pytest
from datetime import date
from app.services.cash_flow_service import CashFlowService
from app.services.etf_comparison_service import ETFComparisonService
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app import db


class TestCashFlowSorting:
    """Test cases for cash flow sorting functionality"""
    
    def test_cash_flow_same_day_sorting(self, app):
        """Test that cash flows on the same day are sorted correctly"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            portfolio_id = portfolio.id
            
            # Create transactions and dividends all on the same day
            transaction1 = StockTransaction(
                portfolio_id=portfolio_id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 1, 15),
                price_per_share=150.00,
                shares=10,
                total_value=1500.00
            )
            
            transaction2 = StockTransaction(
                portfolio_id=portfolio_id,
                ticker='MSFT',
                transaction_type='BUY',
                date=date(2025, 1, 15),
                price_per_share=250.00,
                shares=5,
                total_value=1250.00
            )
            
            dividend = Dividend(
                portfolio_id=portfolio_id,
                ticker='AAPL',
                payment_date=date(2025, 1, 15),
                total_amount=50.00
            )
            
            db.session.add_all([transaction1, transaction2, dividend])
            db.session.commit()
            
            # Generate cash flows
            cash_flow_service = CashFlowService()
            cash_flows = cash_flow_service.generate_cash_flows(portfolio_id)
            
            # Save cash flows to database
            cash_flow_service.save_cash_flows(portfolio_id, cash_flows)
            
            # Get cash flows from database
            db_cash_flows = cash_flow_service.get_cash_flows(portfolio_id)
            
            # All flows should be on the same date
            assert all(cf.date == date(2025, 1, 15) for cf in db_cash_flows)
            
            # Check the order: dividends, deposits, purchases
            flow_types = [cf.flow_type for cf in db_cash_flows]
            
            # First should be dividend
            assert flow_types[0] == 'DIVIDEND'
            
            # Second should be deposit (inferred from purchases)
            assert flow_types[1] == 'DEPOSIT'
            
            # Last two should be purchases
            assert flow_types[2] == 'PURCHASE'
            assert flow_types[3] == 'PURCHASE'
    
    def test_etf_cash_flow_same_day_sorting(self, app, monkeypatch):
        """Test that ETF cash flows on the same day are sorted correctly"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            portfolio_id = portfolio.id
            
            # Create transactions all on the same day
            transaction = StockTransaction(
                portfolio_id=portfolio_id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 1, 15),
                price_per_share=150.00,
                shares=10,
                total_value=1500.00
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Mock the ETF comparison service to avoid API calls
            etf_service = ETFComparisonService()
            
            # Mock the price service
            class MockPriceService:
                def get_cached_price(self, ticker, date_val):
                    return 100.0
                
                def get_current_price(self, ticker):
                    return 100.0
            
            etf_service.price_service = MockPriceService()
            
            # Mock yfinance to return a dividend on the same day
            import pandas as pd
            from unittest.mock import patch
            
            dividend_data = {
                pd.Timestamp('2025-01-15'): 1.50,  # Dividend on the same day
            }
            mock_dividends = pd.Series(dividend_data)
            
            with patch('yfinance.Ticker') as mock_ticker:
                mock_ticker.return_value.dividends = mock_dividends
                
                # Get ETF cash flows
                etf_cash_flows = etf_service.get_etf_cash_flows(portfolio_id, 'VOO')
                
                # Filter for flows on our test date
                same_day_flows = [flow for flow in etf_cash_flows if flow['date'] == date(2025, 1, 15)]
                
                # Should have at least 3 flows on this day (dividend, deposit, purchase)
                assert len(same_day_flows) >= 3
                
                # Check the order: dividends, deposits, purchases
                flow_types = [flow['flow_type'] for flow in same_day_flows]
                
                # First should be dividend
                assert 'DIVIDEND' in flow_types
                
                # Should have a purchase
                assert 'PURCHASE' in flow_types
                
                # Verify the order is correct (dividends before purchases)
                dividend_index = flow_types.index('DIVIDEND')
                purchase_index = flow_types.index('PURCHASE')
                assert dividend_index < purchase_index
