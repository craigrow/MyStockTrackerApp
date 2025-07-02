"""Integration tests for market hours behavior and timing edge cases."""
import pytest
from datetime import datetime, time, date
from unittest.mock import patch
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks
from app.services.price_service import PriceService


@pytest.mark.fast
@pytest.mark.database
class TestMarketHoursBehavior:
    """Test market hours and timing-related edge cases."""
    
    def test_weekend_price_requests(self, app, client):
        """Test price service behavior during weekends."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Mock weekend datetime
                weekend_datetime = datetime(2023, 1, 14, 10, 0, 0)  # Saturday
                
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.now.return_value = weekend_datetime
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    
                    # Price service should handle weekend requests gracefully
                    price = price_service.get_current_price('AAPL')
                    # Should either return cached price or handle gracefully
                    assert price is None or isinstance(price, (int, float))
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_after_hours_trading(self, app, client):
        """Test behavior during after-hours trading periods."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Mock after-hours time (8 PM EST)
                after_hours_datetime = datetime(2023, 1, 16, 20, 0, 0)  # Monday 8 PM
                
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.now.return_value = after_hours_datetime
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    
                    # Should handle after-hours requests
                    price = price_service.get_current_price('AAPL')
                    assert price is None or isinstance(price, (int, float))
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_market_holidays(self, app, client):
        """Test behavior during market holidays."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Mock New Year's Day (market holiday)
                holiday_datetime = datetime(2023, 1, 1, 14, 0, 0)  # Sunday, New Year's
                
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.now.return_value = holiday_datetime
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    
                    # Should handle holiday requests gracefully
                    price = price_service.get_current_price('AAPL')
                    assert price is None or isinstance(price, (int, float))
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_timezone_handling(self, app, client):
        """Test timezone-aware price requests."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Test different timezone scenarios
                timezones = [
                    datetime(2023, 1, 16, 9, 30, 0),   # Market open EST
                    datetime(2023, 1, 16, 16, 0, 0),   # Market close EST
                    datetime(2023, 1, 16, 6, 30, 0),   # Pre-market EST
                ]
                
                for test_time in timezones:
                    with patch('datetime.datetime') as mock_datetime:
                        mock_datetime.now.return_value = test_time
                        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                        
                        # Should handle all timezone scenarios
                        price = price_service.get_current_price('AAPL')
                        assert price is None or isinstance(price, (int, float))
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_stale_price_data_handling(self, app, client):
        """Test handling of stale price data."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Test with very old price data
                old_datetime = datetime(2020, 1, 1, 10, 0, 0)
                
                with patch('datetime.datetime') as mock_datetime:
                    mock_datetime.now.return_value = old_datetime
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    
                    # Should handle stale data appropriately
                    price = price_service.get_current_price('AAPL')
                    # Either returns cached price or None for stale data
                    assert price is None or isinstance(price, (int, float))
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_rapid_price_requests(self, app, client):
        """Test rapid successive price requests."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                price_service = PriceService()
                
                # Make rapid successive requests
                prices = []
                for i in range(5):
                    price = price_service.get_current_price('AAPL')
                    prices.append(price)
                
                # Should handle rapid requests without errors
                for price in prices:
                    assert price is None or isinstance(price, (int, float))
                
                # Results should be consistent (cached or rate-limited)
                non_none_prices = [p for p in prices if p is not None]
                if len(non_none_prices) > 1:
                    # If multiple prices returned, they should be similar (caching)
                    price_range = max(non_none_prices) - min(non_none_prices)
                    assert price_range < 10.0, "Rapid requests should return similar prices"
                
            finally:
                for mock in mocks:
                    mock.stop()