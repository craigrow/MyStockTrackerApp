import pytest
from datetime import date
from unittest.mock import Mock, patch
from app.services.etf_comparison_service import ETFComparisonService
from app.services.cash_flow_service import CashFlowService
from app.services.price_service import PriceService
from app.models.portfolio import Portfolio, StockTransaction
from app import db
import pandas as pd


class TestETFDividendCalculationFix:
    """Test cases for fixing ETF dividend calculation bug"""
    
    @pytest.fixture
    def etf_service(self):
        return ETFComparisonService()
    
    @pytest.fixture
    def mock_price_service(self):
        """Mock price service with predictable prices"""
        mock = Mock(spec=PriceService)
        # VOO prices: $400 on 2024-01-01, $420 on 2024-06-30
        mock.get_cached_price.side_effect = lambda ticker, date_val: {
            ('VOO', date(2024, 1, 1)): 400.0,
            ('VOO', date(2024, 6, 30)): 420.0,
            ('VOO', date(2024, 12, 30)): 440.0,
        }.get((ticker, date_val), 400.0)
        mock.get_current_price.return_value = 450.0
        return mock
    
    @pytest.fixture
    def mock_yfinance_dividends(self):
        """Mock yfinance dividend data"""
        # Create mock dividend series
        dividend_data = {
            pd.Timestamp('2024-06-30'): 1.50,  # $1.50 dividend on June 30
            pd.Timestamp('2024-12-30'): 1.60,  # $1.60 dividend on Dec 30
        }
        return pd.Series(dividend_data)
    
    def test_dividend_calculation_with_single_deposit(self, app, etf_service, mock_price_service, mock_yfinance_dividends):
        """Test dividend calculation with single deposit before dividend"""
        with app.app_context():
            # Mock the services
            etf_service.price_service = mock_price_service
            
            # Mock yfinance
            with patch('yfinance.Ticker') as mock_ticker:
                mock_ticker.return_value.dividends = mock_yfinance_dividends
                
                # Create mock deposits: $1000 on Jan 1 (buys 2.5 shares at $400/share)
                deposits = [{'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'}]
                
                # Test dividend calculation - no longer pass total_shares parameter
                dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, None)
                
                # Should have 2 dividends
                assert len(dividend_flows) == 2
                
                # First dividend (June 30): $1.50 × 2.5 shares = $3.75
                june_dividend = next(df for df in dividend_flows if df['date'] == date(2024, 6, 30))
                assert june_dividend['amount'] == 3.75  # $1.50 × 2.5 shares
                assert june_dividend['flow_type'] == 'DIVIDEND'
                assert '$1.50 per share' in june_dividend['description']
                
                # Second dividend (Dec 30): Should account for reinvestment from June dividend
                # June dividend: $3.75 reinvested at $420 = 0.0089 additional shares
                # Total shares by Dec 30: 2.5 + 0.0089 = 2.5089 shares
                # Dec dividend: $1.60 × 2.5089 = $4.014
                dec_dividend = next(df for df in dividend_flows if df['date'] == date(2024, 12, 30))
                expected_dec_amount = 1.60 * (2.5 + (3.75 / 420.0))  # Original shares + reinvested shares
                assert dec_dividend['amount'] == pytest.approx(expected_dec_amount, rel=1e-3)
    
    def test_dividend_calculation_with_multiple_deposits(self, app, etf_service, mock_price_service, mock_yfinance_dividends):
        """Test dividend calculation with multiple deposits before dividend"""
        with app.app_context():
            # Setup portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Two transactions requiring deposits
            transaction1 = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2024, 1, 1),
                price_per_share=150.00,
                shares=6.67,
                total_value=1000.00
            )
            transaction2 = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='MSFT',
                transaction_type='BUY',
                date=date(2024, 3, 1),
                price_per_share=200.00,
                shares=2.5,
                total_value=500.00
            )
            db.session.add_all([transaction1, transaction2])
            db.session.commit()
            
            etf_service.price_service = mock_price_service
            
            with patch('yfinance.Ticker') as mock_ticker:
                mock_ticker.return_value.dividends = mock_yfinance_dividends
                
                # Mock deposits: $1000 on Jan 1 (2.5 shares), $500 on Mar 1 (1.25 shares)
                deposits = [
                    {'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'},
                    {'date': date(2024, 3, 1), 'amount': 500.0, 'flow_type': 'DEPOSIT'}
                ]
                
                # Total shares by June 30: 2.5 + 1.25 = 3.75 shares
                dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, 3.75)
                
                # June dividend: $1.50 × 3.75 shares = $5.625
                june_dividend = next(df for df in dividend_flows if df['date'] == date(2024, 6, 30))
                assert june_dividend['amount'] == 5.625
    
    def test_dividend_calculation_with_reinvestment(self, app, etf_service, mock_price_service):
        """Test dividend calculation accounting for previous reinvestments"""
        with app.app_context():
            # Setup portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2024, 1, 1),
                price_per_share=150.00,
                shares=6.67,
                total_value=1000.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            etf_service.price_service = mock_price_service
            
            # Mock dividends with two payment dates
            dividend_data = {
                pd.Timestamp('2024-06-30'): 1.50,  # First dividend
                pd.Timestamp('2024-12-30'): 1.60,  # Second dividend
            }
            mock_dividends = pd.Series(dividend_data)
            
            with patch('yfinance.Ticker') as mock_ticker:
                mock_ticker.return_value.dividends = mock_dividends
                
                deposits = [{'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'}]
                
                # Initial shares: $1000 / $400 = 2.5 shares
                # First dividend: $1.50 × 2.5 = $3.75, reinvested at $420 = 0.0089 shares
                # Total shares by Dec 30: 2.5 + 0.0089 = 2.5089 shares
                # Second dividend should be: $1.60 × 2.5089 = $4.014
                
                dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, 2.5089)
                
                # This test will expose the bug: current implementation uses 2.5089 for BOTH dividends
                # But it should use 2.5 for first dividend and 2.5089 for second dividend
                june_dividend = next(df for df in dividend_flows if df['date'] == date(2024, 6, 30))
                dec_dividend = next(df for df in dividend_flows if df['date'] == date(2024, 12, 30))
                
                # With the bug, both will use total_shares (2.5089)
                # June should be $1.50 × 2.5 = $3.75 (not $1.50 × 2.5089)
                # Dec should be $1.60 × 2.5089 = $4.014
                
                # These assertions will fail with current buggy implementation
                assert june_dividend['amount'] == 3.75  # Should use 2.5 shares, not 2.5089
                assert dec_dividend['amount'] == pytest.approx(4.014, rel=1e-3)  # Should use 2.5089 shares
    
    def test_empty_deposits_returns_empty_dividends(self, etf_service):
        """Test that empty deposits return empty dividend flows"""
        dividend_flows = etf_service._get_etf_dividend_flows('VOO', [], 0)
        assert dividend_flows == []
    
    def test_no_dividends_in_period_returns_empty(self, etf_service, mock_price_service):
        """Test that no dividends in period returns empty list"""
        etf_service.price_service = mock_price_service
        
        # Mock empty dividend series
        empty_dividends = pd.Series(dtype=float)
        
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.dividends = empty_dividends
            
            deposits = [{'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'}]
            dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, 2.5)
            
            assert dividend_flows == []
    
    def test_api_failure_returns_empty_gracefully(self, etf_service, mock_price_service):
        """Test that API failure is handled gracefully"""
        etf_service.price_service = mock_price_service
        
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.side_effect = Exception("API Error")
            
            deposits = [{'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'}]
            dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, 2.5)
            
            assert dividend_flows == []
    
    def test_dividend_before_first_deposit_ignored(self, etf_service, mock_price_service):
        """Test that dividends before first deposit are ignored"""
        etf_service.price_service = mock_price_service
        
        # Mock dividend before deposit date
        dividend_data = {
            pd.Timestamp('2023-12-30'): 1.40,  # Before first deposit
            pd.Timestamp('2024-06-30'): 1.50,  # After first deposit
        }
        mock_dividends = pd.Series(dividend_data)
        
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.dividends = mock_dividends
            
            deposits = [{'date': date(2024, 1, 1), 'amount': 1000.0, 'flow_type': 'DEPOSIT'}]
            dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, 2.5)
            
            # Should only have one dividend (June), not December 2023
            assert len(dividend_flows) == 1
            assert dividend_flows[0]['date'] == date(2024, 6, 30)
            assert dividend_flows[0]['amount'] == 3.75  # $1.50 × 2.5 shares