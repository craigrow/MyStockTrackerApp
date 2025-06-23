import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from app.views.main import calculate_daily_changes


class TestDailyChangesCalculation:
    
    def test_calculate_daily_changes_success(self, sample_portfolio, app):
        """Test successful daily changes calculation"""
        with app.app_context():
            with patch('app.views.main.get_last_market_date') as mock_last_date, \
                 patch('app.views.main.get_previous_trading_day') as mock_prev_date, \
                 patch('app.views.main.calculate_etf_daily_change_for_portfolio') as mock_etf_change, \
                 patch('app.views.main.calculate_portfolio_daily_change') as mock_portfolio_change:
                
                # Setup dates
                mock_last_date.return_value = date(2025, 6, 23)
                mock_prev_date.return_value = date(2025, 6, 22)
                
                # Setup ETF changes
                mock_etf_change.side_effect = [
                    {'percentage': 1.5, 'dollar': 750},  # VOO
                    {'percentage': 2.0, 'dollar': 1000}  # QQQ
                ]
                
                # Setup portfolio change
                mock_portfolio_change.return_value = {'percentage': 1.8, 'dollar': 900}
                
                from app.services.portfolio_service import PortfolioService
                from app.services.price_service import PriceService
                
                result = calculate_daily_changes(
                    sample_portfolio.id,
                    PortfolioService(),
                    PriceService()
                )
                
                assert result['voo_daily_change'] == 1.5
                assert result['voo_daily_dollar_change'] == 750
                assert result['qqq_daily_change'] == 2.0
                assert result['qqq_daily_dollar_change'] == 1000
                assert result['portfolio_daily_change'] == 1.8
                assert result['portfolio_daily_dollar_change'] == 900

    def test_calculate_daily_changes_error_handling(self, sample_portfolio, app):
        """Test that errors in daily changes calculation return zeros"""
        with app.app_context():
            with patch('app.views.main.get_last_market_date') as mock_last_date:
                
                # Simulate an error
                mock_last_date.side_effect = Exception("Database error")
                
                from app.services.portfolio_service import PortfolioService
                from app.services.price_service import PriceService
                
                result = calculate_daily_changes(
                    sample_portfolio.id,
                    PortfolioService(),
                    PriceService()
                )
                
                # Should return zeros on error
                assert result['voo_daily_change'] == 0
                assert result['voo_daily_dollar_change'] == 0
                assert result['qqq_daily_change'] == 0
                assert result['qqq_daily_dollar_change'] == 0
                assert result['portfolio_daily_change'] == 0
                assert result['portfolio_daily_dollar_change'] == 0

    def test_calculate_daily_changes_invalid_etf_response(self, sample_portfolio, app):
        """Test handling of invalid ETF change responses"""
        with app.app_context():
            with patch('app.views.main.get_last_market_date') as mock_last_date, \
                 patch('app.views.main.get_previous_trading_day') as mock_prev_date, \
                 patch('app.views.main.calculate_etf_daily_change_for_portfolio') as mock_etf_change, \
                 patch('app.views.main.calculate_portfolio_daily_change') as mock_portfolio_change:
                
                mock_last_date.return_value = date(2025, 6, 23)
                mock_prev_date.return_value = date(2025, 6, 22)
                
                # Return invalid responses (not dicts)
                mock_etf_change.side_effect = [None, "invalid"]
                mock_portfolio_change.return_value = 0  # Not a dict
                
                from app.services.portfolio_service import PortfolioService
                from app.services.price_service import PriceService
                
                result = calculate_daily_changes(
                    sample_portfolio.id,
                    PortfolioService(),
                    PriceService()
                )
                
                # Should handle invalid responses gracefully
                assert result['voo_daily_change'] == 0
                assert result['voo_daily_dollar_change'] == 0
                assert result['qqq_daily_change'] == 0
                assert result['qqq_daily_dollar_change'] == 0
                assert result['portfolio_daily_change'] == 0
                assert result['portfolio_daily_dollar_change'] == 0