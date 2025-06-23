import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from app.views.main import dashboard


class TestDashboardCaching:
    
    def test_zero_value_cache_detection_triggers_recalculation(self, client, sample_portfolio, app):
        """Test that cached stats with zero values trigger fresh calculation"""
        with app.app_context():
            with patch('app.views.main.get_cached_portfolio_stats') as mock_get_cache, \
                 patch('app.views.main.calculate_portfolio_stats') as mock_calc_stats, \
                 patch('app.views.main.is_market_open_now') as mock_market_open:
                
                # Setup: cached data with zero values
                mock_get_cache.return_value = {
                    'current_value': 0,  # Zero value should trigger recalculation
                    'total_gain_loss': 0,
                    'voo_equivalent': 0
                }
                
                # Fresh calculation returns real values
                mock_calc_stats.return_value = {
                    'current_value': 50000,
                    'total_gain_loss': 5000,
                    'gain_loss_percentage': 10.0,
                    'voo_equivalent': 45000,
                    'qqq_equivalent': 44000,
                    'voo_gain_loss': 4000,
                    'qqq_gain_loss': 3500,
                    'voo_gain_loss_percentage': 8.9,
                    'qqq_gain_loss_percentage': 8.0,
                    'portfolio_daily_change': 1.5,
                    'portfolio_daily_dollar_change': 750,
                    'voo_daily_change': 1.2,
                    'voo_daily_dollar_change': 540,
                    'qqq_daily_change': 1.8,
                    'qqq_daily_dollar_change': 792
                }
                
                mock_market_open.return_value = False  # Market closed, should use cache
                
                response = client.get(f'/?portfolio_id={sample_portfolio.id}')
                
                # Should detect zero values and recalculate
                mock_calc_stats.assert_called_once()
                assert response.status_code == 200

    def test_valid_cache_with_fresh_daily_changes(self, client, sample_portfolio, app):
        """Test that valid cached stats are used but daily changes are recalculated"""
        with app.app_context():
            with patch('app.views.main.get_cached_portfolio_stats') as mock_get_cache, \
                 patch('app.views.main.calculate_daily_changes') as mock_daily_changes, \
                 patch('app.views.main.calculate_portfolio_stats') as mock_calc_stats, \
                 patch('app.views.main.is_market_open_now') as mock_market_open:
                
                # Setup: valid cached data (non-zero values)
                mock_get_cache.return_value = {
                    'current_value': 50000,  # Non-zero, should use cache
                    'total_gain_loss': 5000,
                    'gain_loss_percentage': 10.0,
                    'voo_equivalent': 45000,
                    'qqq_equivalent': 44000,
                    'voo_gain_loss': 4000,
                    'qqq_gain_loss': 3500,
                    'voo_gain_loss_percentage': 8.9,
                    'qqq_gain_loss_percentage': 8.0
                }
                
                # Fresh daily changes
                mock_daily_changes.return_value = {
                    'portfolio_daily_change': 1.5,
                    'portfolio_daily_dollar_change': 750,
                    'voo_daily_change': 1.2,
                    'voo_daily_dollar_change': 540
                }
                
                mock_market_open.return_value = False  # Market closed
                
                response = client.get(f'/?portfolio_id={sample_portfolio.id}')
                
                # Should use cached stats but recalculate daily changes
                mock_calc_stats.assert_not_called()
                mock_daily_changes.assert_called_once()
                assert response.status_code == 200

    def test_no_cache_triggers_fresh_calculation(self, client, sample_portfolio, app):
        """Test that missing cache triggers fresh calculation"""
        with app.app_context():
            with patch('app.views.main.get_cached_portfolio_stats') as mock_get_cache, \
                 patch('app.views.main.calculate_portfolio_stats') as mock_calc_stats, \
                 patch('app.views.main.is_market_open_now') as mock_market_open:
                
                # Setup: no cached data
                mock_get_cache.return_value = None
                
                mock_calc_stats.return_value = {
                    'current_value': 50000,
                    'total_gain_loss': 5000,
                    'gain_loss_percentage': 10.0,
                    'voo_equivalent': 45000,
                    'qqq_equivalent': 44000,
                    'voo_gain_loss': 4000,
                    'qqq_gain_loss': 3500,
                    'voo_gain_loss_percentage': 8.9,
                    'qqq_gain_loss_percentage': 8.0,
                    'portfolio_daily_change': 1.5,
                    'portfolio_daily_dollar_change': 750,
                    'voo_daily_change': 1.2,
                    'voo_daily_dollar_change': 540,
                    'qqq_daily_change': 1.8,
                    'qqq_daily_dollar_change': 792
                }
                
                mock_market_open.return_value = False
                
                response = client.get(f'/?portfolio_id={sample_portfolio.id}')
                
                # Should calculate fresh stats
                mock_calc_stats.assert_called_once()
                assert response.status_code == 200

    def test_market_open_bypasses_cache(self, client, sample_portfolio, app):
        """Test that when market is open, cache is bypassed"""
        with app.app_context():
            with patch('app.views.main.get_cached_portfolio_stats') as mock_get_cache, \
                 patch('app.views.main.calculate_portfolio_stats') as mock_calc_stats, \
                 patch('app.views.main.is_market_open_now') as mock_market_open:
                
                mock_get_cache.return_value = {
                    'current_value': 50000,
                    'total_gain_loss': 5000
                }
                
                mock_calc_stats.return_value = {
                    'current_value': 51000,  # Updated value
                    'total_gain_loss': 5500,
                    'gain_loss_percentage': 10.8,
                    'voo_equivalent': 46000,
                    'qqq_equivalent': 45000,
                    'voo_gain_loss': 4500,
                    'qqq_gain_loss': 4000,
                    'voo_gain_loss_percentage': 9.8,
                    'qqq_gain_loss_percentage': 8.9,
                    'portfolio_daily_change': 2.0,
                    'portfolio_daily_dollar_change': 1000,
                    'voo_daily_change': 1.5,
                    'voo_daily_dollar_change': 690,
                    'qqq_daily_change': 2.2,
                    'qqq_daily_dollar_change': 990
                }
                
                mock_market_open.return_value = True  # Market open, should bypass cache
                
                response = client.get(f'/?portfolio_id={sample_portfolio.id}')
                
                # Should calculate fresh stats when market is open
                mock_calc_stats.assert_called_once()
                assert response.status_code == 200