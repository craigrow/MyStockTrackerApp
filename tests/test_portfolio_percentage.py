import pytest
from app.views.main import get_holdings_with_performance
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from tests.utils.factories import PortfolioFactory, TransactionFactory
from tests.utils.mocks import MockPriceService
from datetime import date


class TestPortfolioPercentage:
    """Test portfolio percentage calculation and sorting"""
    
    def test_portfolio_percentage_calculation(self, app):
        """Test that portfolio percentages are calculated correctly"""
        with app.app_context():
            # Create test portfolio with known values
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            
            # Create transactions with known market values
            # AAPL: 10 shares * $100 = $1000 (57.14% of $1750)
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10, 100.0, date(2023, 1, 1))
            # MSFT: 5 shares * $100 = $500 (28.57% of $1750)  
            TransactionFactory.create_buy(portfolio.id, "MSFT", 5, 100.0, date(2023, 1, 1))
            # GOOGL: 2.5 shares * $100 = $250 (14.29% of $1750)
            TransactionFactory.create_buy(portfolio.id, "GOOGL", 2.5, 100.0, date(2023, 1, 1))
            
            # Mock price service to return $100 for all tickers
            mock_price_service = MockPriceService()
            mock_price_service.set_price("AAPL", 100.0)
            mock_price_service.set_price("MSFT", 100.0) 
            mock_price_service.set_price("GOOGL", 100.0)
            
            portfolio_service = PortfolioService()
            holdings = get_holdings_with_performance(
                portfolio.id, portfolio_service, mock_price_service, use_stale=True
            )
            
            # Verify percentages are calculated correctly
            assert len(holdings) == 3
            
            # Find holdings by ticker
            aapl_holding = next(h for h in holdings if h['ticker'] == 'AAPL')
            msft_holding = next(h for h in holdings if h['ticker'] == 'MSFT')
            googl_holding = next(h for h in holdings if h['ticker'] == 'GOOGL')
            
            # Verify portfolio percentages (with tolerance for floating point)
            assert abs(aapl_holding['portfolio_percentage'] - 57.14) < 0.01
            assert abs(msft_holding['portfolio_percentage'] - 28.57) < 0.01
            assert abs(googl_holding['portfolio_percentage'] - 14.29) < 0.01
    
    def test_portfolio_percentage_sorting(self, app):
        """Test that holdings are sorted by portfolio percentage descending"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            
            # Create transactions with different values
            TransactionFactory.create_buy(portfolio.id, "SMALL", 1, 50.0, date(2023, 1, 1))  # $50
            TransactionFactory.create_buy(portfolio.id, "LARGE", 5, 100.0, date(2023, 1, 1))  # $500
            TransactionFactory.create_buy(portfolio.id, "MEDIUM", 2, 75.0, date(2023, 1, 1))  # $150
            
            mock_price_service = MockPriceService()
            mock_price_service.set_price("SMALL", 50.0)
            mock_price_service.set_price("LARGE", 100.0)
            mock_price_service.set_price("MEDIUM", 75.0)
            
            portfolio_service = PortfolioService()
            holdings = get_holdings_with_performance(
                portfolio.id, portfolio_service, mock_price_service, use_stale=True
            )
            
            # Verify holdings are sorted by portfolio percentage descending
            assert holdings[0]['ticker'] == 'LARGE'  # Highest percentage
            assert holdings[1]['ticker'] == 'MEDIUM'  # Middle percentage
            assert holdings[2]['ticker'] == 'SMALL'  # Lowest percentage
            
            # Verify percentages are in descending order
            for i in range(len(holdings) - 1):
                assert holdings[i]['portfolio_percentage'] >= holdings[i + 1]['portfolio_percentage']
    
    def test_portfolio_percentage_edge_cases(self, app):
        """Test edge cases for portfolio percentage calculation"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            portfolio_service = PortfolioService()
            mock_price_service = MockPriceService()
            
            # Test empty portfolio
            holdings = get_holdings_with_performance(
                portfolio.id, portfolio_service, mock_price_service, use_stale=True
            )
            assert len(holdings) == 0
            
            # Test single holding (should be 100%)
            TransactionFactory.create_buy(portfolio.id, "SINGLE", 1, 100.0, date(2023, 1, 1))
            mock_price_service.set_price("SINGLE", 100.0)
            
            holdings = get_holdings_with_performance(
                portfolio.id, portfolio_service, mock_price_service, use_stale=True
            )
            
            assert len(holdings) == 1
            assert abs(holdings[0]['portfolio_percentage'] - 100.0) < 0.01
    
    def test_portfolio_percentage_zero_value_handling(self, app):
        """Test handling of zero portfolio value"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            
            # Create transaction but mock zero prices
            TransactionFactory.create_buy(portfolio.id, "ZERO", 1, 100.0, date(2023, 1, 1))
            
            mock_price_service = MockPriceService()
            mock_price_service.set_price("ZERO", 0.0)  # Zero current price
            
            portfolio_service = PortfolioService()
            holdings = get_holdings_with_performance(
                portfolio.id, portfolio_service, mock_price_service, use_stale=True
            )
            
            # Should handle zero portfolio value gracefully
            assert len(holdings) == 1
            assert holdings[0]['portfolio_percentage'] == 0.0


class TestDashboardPortfolioPercentage:
    """Integration tests for portfolio percentage display on dashboard"""
    
    def test_dashboard_includes_portfolio_percentage_column(self, app, client):
        """Test that dashboard includes portfolio percentage column"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            TransactionFactory.create_buy(portfolio.id, "TEST", 1, 100.0, date(2023, 1, 1))
            
            # Mock price service for the request
            from unittest.mock import patch
            with patch('app.services.price_service.PriceService') as mock_price_class:
                mock_price_service = MockPriceService()
                mock_price_service.set_price("TEST", 100.0)
                mock_price_class.return_value = mock_price_service
                
                response = client.get(f'/?portfolio_id={portfolio.id}')
                assert response.status_code == 200
                
                # Check that % of Portfolio column header exists
                assert b'% of Portfolio' in response.data
                
                # Check that percentage value is displayed
                assert b'100.00%' in response.data