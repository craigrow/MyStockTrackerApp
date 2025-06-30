"""Mock utilities for integration tests to improve performance."""
import unittest.mock
from datetime import date, datetime, timedelta


class IntegrationTestMocks:
    """Mocks for integration tests to avoid slow API calls."""
    
    @staticmethod
    def mock_price_service():
        """Mock PriceService to return fast, consistent prices."""
        def mock_get_current_price(self, ticker, use_stale=False):
            # Return consistent test prices
            prices = {
                'AAPL': 150.00,
                'GOOGL': 2500.00,
                'MSFT': 300.00,
                'VOO': 400.00,
                'QQQ': 350.00,
                'AMZN': 3000.00,
                'TSLA': 800.00
            }
            return prices.get(ticker, 100.00)
        
        def mock_get_data_freshness(self, ticker, target_date):
            # Return fresh data (0 minutes old)
            return 0
        
        return unittest.mock.patch.multiple(
            'app.services.price_service.PriceService',
            get_current_price=mock_get_current_price,
            get_data_freshness=mock_get_data_freshness
        )
    
    @staticmethod
    def mock_historical_prices():
        """Mock historical price functions to avoid API calls."""
        def mock_get_historical_price(ticker, target_date):
            # Return consistent historical prices
            base_prices = {
                'AAPL': 150.00,
                'GOOGL': 2500.00,
                'MSFT': 300.00,
                'VOO': 400.00,
                'QQQ': 350.00
            }
            return base_prices.get(ticker, 100.00)
        
        def mock_get_ticker_price_dataframe(ticker, start_date, end_date):
            # Return empty DataFrame to skip expensive operations
            import pandas as pd
            return pd.DataFrame()
        
        return unittest.mock.patch.multiple(
            'app.views.main',
            get_historical_price=mock_get_historical_price,
            get_ticker_price_dataframe=mock_get_ticker_price_dataframe
        )
    
    @staticmethod
    def mock_market_functions():
        """Mock market-related functions for consistent testing."""
        def mock_is_market_open_now():
            return False  # Assume market closed for consistent behavior
        
        def mock_get_last_market_date():
            return date.today()
        
        return unittest.mock.patch.multiple(
            'app.views.main',
            is_market_open_now=mock_is_market_open_now,
            get_last_market_date=mock_get_last_market_date
        )
    
    @staticmethod
    def apply_all_mocks():
        """Apply all performance mocks for integration tests."""
        return [
            IntegrationTestMocks.mock_price_service(),
            IntegrationTestMocks.mock_historical_prices(),
            IntegrationTestMocks.mock_market_functions()
        ]