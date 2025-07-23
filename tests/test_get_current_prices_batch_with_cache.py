import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, date
from app.services.price_service import PriceService

class TestBatchAPIProcessingWithCache(unittest.TestCase):
    
    def setUp(self):
        self.price_service = PriceService()
        self.test_tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
    
    @patch('app.services.price_service.PriceService.get_cached_price')
    @patch('app.services.price_service.PriceService.batch_fetch_prices')
    @patch('app.services.price_service.PriceService.cache_price_data')
    def test_get_current_prices_batch_with_cache(self, mock_cache, mock_batch_fetch, mock_get_cached):
        # Setup mocks
        today = date.today()
        
        # First ticker has fresh cache, second has stale cache, others have no cache
        def get_cached_side_effect(ticker, price_date):
            if ticker == 'AAPL':
                return 155.0  # Cached price
            elif ticker == 'MSFT':
                return 305.0  # Cached price
            return None
        
        def is_cache_fresh_side_effect(ticker, price_date, freshness_minutes=5):
            return ticker == 'AAPL'  # Only AAPL has fresh cache
        
        mock_get_cached.side_effect = get_cached_side_effect
        self.price_service.is_cache_fresh = MagicMock(side_effect=is_cache_fresh_side_effect)
        
        # Setup mock DataFrames for each ticker
        mock_result = {}
        stale_tickers = ['MSFT', 'AMZN', 'GOOGL', 'META']
        
        for ticker in stale_tickers:
            df = pd.DataFrame({'Close': [float(ord(ticker[0]))]})  # Use ASCII value for predictable test values
            df.index = [datetime.now()]
            mock_result[ticker] = df
        
        # API returns new prices for non-cached tickers
        mock_batch_fetch.return_value = mock_result
        
        # Call the method with use_cache=True
        result = self.price_service.get_current_prices_batch(self.test_tickers, use_cache=True)
        
        # Verify results
        self.assertEqual(result['AAPL'], 155.0)  # Should use fresh cache
        
        # Verify batch_fetch was called with only non-fresh tickers
        mock_batch_fetch.assert_called_once()
        args, kwargs = mock_batch_fetch.call_args
        self.assertNotIn('AAPL', args[0])  # AAPL should not be in API call
        self.assertIn('MSFT', args[0])  # MSFT should be in API call (stale cache)