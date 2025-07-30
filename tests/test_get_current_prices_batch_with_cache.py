import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, date
from app.services.price_service import PriceService
from app import create_app, db

class TestBatchAPIProcessingWithCache(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        self.price_service = PriceService()
        self.test_tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @patch('app.services.price_service.PriceService.get_cached_price')
    @patch('app.services.price_service.PriceService.batch_fetch_current_prices')
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
        
        # Setup mock return values for batch_fetch_current_prices
        mock_batch_prices = {}
        stale_tickers = ['MSFT', 'AMZN', 'GOOGL', 'META']
        
        for ticker in stale_tickers:
            # Use ASCII value for predictable test values
            mock_batch_prices[ticker] = float(ord(ticker[0]))
        
        # API returns new prices for non-cached tickers
        mock_batch_fetch.return_value = mock_batch_prices
        
        # Call the method with use_cache=True
        result = self.price_service.get_current_prices_batch(self.test_tickers, use_cache=True)
        
        # Verify results
        self.assertEqual(result['AAPL'], 155.0)  # Should use fresh cache
        
        # Verify batch_fetch was called with only non-fresh tickers
        mock_batch_fetch.assert_called_once()
        args, kwargs = mock_batch_fetch.call_args
        self.assertNotIn('AAPL', args[0])  # AAPL should not be in API call
        self.assertIn('MSFT', args[0])  # MSFT should be in API call (stale cache)