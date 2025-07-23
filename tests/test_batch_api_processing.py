import unittest
import pytest
from unittest.mock import patch, MagicMock
from app.services.price_service import PriceService
import pandas as pd
import asyncio
import time
from datetime import date, datetime, timedelta

class TestBatchAPIProcessing(unittest.TestCase):
    
    def setUp(self):
        self.price_service = PriceService()
        self.test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        
    @patch('app.services.price_service.yf.download')
    def test_batch_fetch_current_prices(self, mock_download):
        """Test batch fetching of current prices"""
        # Mock the yfinance download response
        mock_data = pd.DataFrame({
            'Close': [150.0, 151.0]
        }, index=[datetime.now() - timedelta(days=1), datetime.now()])
        
        # For multiple tickers, yfinance returns a different structure
        mock_multi_data = pd.DataFrame()
        for ticker in self.test_tickers:
            mock_multi_data[ticker, 'Close'] = [150.0, 151.0]
        mock_multi_data.index = [datetime.now() - timedelta(days=1), datetime.now()]
        
        # Set up the mock to return different data based on input
        def side_effect(*args, **kwargs):
            if len(kwargs.get('tickers', '').split()) == 1:
                return mock_data
            else:
                return mock_multi_data
                
        mock_download.side_effect = side_effect
        
        # Test with a single ticker
        result = self.price_service.batch_fetch_current_prices(['AAPL'])
        self.assertIn('AAPL', result)
        self.assertEqual(result['AAPL'], 151.0)  # Should get the latest price
        
        # Test with multiple tickers
        result = self.price_service.batch_fetch_current_prices(self.test_tickers)
        for ticker in self.test_tickers:
            self.assertIn(ticker, result)
            self.assertEqual(result[ticker], 151.0)
    
    @patch('app.services.price_service.yf.download')
    def test_batch_fetch_current_prices_error_handling(self, mock_download):
        """Test error handling in batch fetching"""
        # Mock the yfinance download to raise an exception
        mock_download.side_effect = Exception("API Error")
        
        # Should fall back to individual fetches
        with patch.object(self.price_service, '_fallback_batch_fetch') as mock_fallback:
            mock_fallback.return_value = {'AAPL': 150.0}
            result = self.price_service.batch_fetch_current_prices(['AAPL'])
            self.assertEqual(result, {'AAPL': 150.0})
            mock_fallback.assert_called_once()
    
    @patch('app.services.price_service.yf.download')
    def test_fallback_batch_fetch(self, mock_download):
        """Test fallback batch fetching with smaller batches"""
        # Mock the yfinance download response
        mock_data = pd.DataFrame({
            'Close': [150.0, 151.0]
        }, index=[datetime.now() - timedelta(days=1), datetime.now()])
        
        mock_download.return_value = mock_data
        
        # Test fallback with batch size of 2
        result = self.price_service._fallback_batch_fetch(self.test_tickers, batch_size=2)
        
        # Should have called download multiple times
        self.assertEqual(mock_download.call_count, 3)  # 5 tickers with batch size 2 = 3 calls
        
        # Should have results for all tickers
        for ticker in self.test_tickers:
            self.assertIn(ticker, result)
            self.assertEqual(result[ticker], 151.0)
    
    @patch('app.services.price_service.yf.download')
    def test_batch_fetch_prices_historical(self, mock_download):
        """Test batch fetching of historical prices"""
        # Mock the yfinance download response for historical data
        mock_data = pd.DataFrame({
            'Close': [140.0, 145.0, 150.0]
        }, index=[
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1)
        ])
        
        # For multiple tickers, yfinance returns a different structure
        mock_multi_data = pd.DataFrame()
        for ticker in self.test_tickers:
            mock_multi_data[ticker, 'Close'] = [140.0, 145.0, 150.0]
        mock_multi_data.index = [
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1)
        ]
        
        # Set up the mock to return different data based on input
        def side_effect(*args, **kwargs):
            if len(kwargs.get('tickers', '').split()) == 1:
                return mock_data
            else:
                return mock_multi_data
                
        mock_download.side_effect = side_effect
        
        # Test with a single ticker
        start_date = date.today() - timedelta(days=3)
        end_date = date.today()
        result = self.price_service.batch_fetch_prices(['AAPL'], start_date=start_date, end_date=end_date)
        
        self.assertIn('AAPL', result)
        self.assertEqual(len(result['AAPL']), 3)  # Should have 3 days of data
        
        # Test with multiple tickers
        result = self.price_service.batch_fetch_prices(self.test_tickers, start_date=start_date, end_date=end_date)
        for ticker in self.test_tickers:
            self.assertIn(ticker, result)
            self.assertEqual(len(result[ticker]), 3)  # Should have 3 days of data
    
    @pytest.mark.asyncio
    async def test_fetch_prices_parallel(self):
        """Test parallel fetching of prices"""
        # Mock the batch_fetch_prices method
        with patch.object(self.price_service, 'batch_fetch_prices') as mock_batch_fetch:
            def mock_batch_fetch_impl(tickers, *args, **kwargs):
                # Simulate API delay
                time.sleep(0.1)
                return {ticker: pd.DataFrame({'Close': [150.0]}) for ticker in tickers}
            
            mock_batch_fetch.side_effect = mock_batch_fetch_impl
            
            # Test with multiple tickers
            start_time = time.time()
            result = await self.price_service.fetch_prices_parallel(
                self.test_tickers, 
                max_workers=2,
                chunk_size=2
            )
            end_time = time.time()
            
            # Should have results for all tickers
            for ticker in self.test_tickers:
                self.assertIn(ticker, result)
            
            # Should have called batch_fetch_prices multiple times
            self.assertEqual(mock_batch_fetch.call_count, 3)  # 5 tickers with chunk size 2 = 3 calls
            
            # Execution time should be less than sequential (which would be ~0.5s)
            # With 2 workers and 3 batches, should take ~0.2s
            self.assertLess(end_time - start_time, 0.4)
    
    @pytest.mark.asyncio
    async def test_fetch_current_prices_parallel(self):
        """Test parallel fetching of current prices"""
        # Mock the batch_fetch_current_prices method
        with patch.object(self.price_service, 'batch_fetch_current_prices') as mock_batch_fetch:
            def mock_batch_fetch_impl(tickers, *args, **kwargs):
                # Simulate API delay
                time.sleep(0.1)
                return {ticker: 150.0 for ticker in tickers}
            
            mock_batch_fetch.side_effect = mock_batch_fetch_impl
            
            # Also mock batch_cache_price_data to avoid DB operations
            with patch.object(self.price_service, 'batch_cache_price_data') as mock_cache:
                # Test with multiple tickers
                start_time = time.time()
                result = await self.price_service.fetch_current_prices_parallel(
                    self.test_tickers, 
                    max_workers=2,
                    chunk_size=2
                )
                end_time = time.time()
                
                # Should have results for all tickers
                for ticker in self.test_tickers:
                    self.assertIn(ticker, result)
                    self.assertEqual(result[ticker], 150.0)
                
                # Should have called batch_fetch_current_prices multiple times
                self.assertEqual(mock_batch_fetch.call_count, 3)  # 5 tickers with chunk size 2 = 3 calls
                
                # Should have called batch_cache_price_data once
                mock_cache.assert_called_once()
                
                # Execution time should be less than sequential (which would be ~0.5s)
                # With 2 workers and 3 batches, should take ~0.2s
                self.assertLess(end_time - start_time, 0.4)
    
    @patch('app.services.price_service.PriceHistory')
    def test_get_market_aware_cache_freshness(self, mock_price_history):
        """Test market-aware cache freshness"""
        # Mock the is_market_open_now function
        with patch('app.views.main.is_market_open_now') as mock_market_open:
            # Test during market hours
            mock_market_open.return_value = True
            freshness = self.price_service.get_market_aware_cache_freshness()
            self.assertEqual(freshness, 5)  # Should be 5 minutes during market hours
            
            # Test after market hours
            mock_market_open.return_value = False
            freshness = self.price_service.get_market_aware_cache_freshness()
            self.assertEqual(freshness, 60)  # Should be 60 minutes after market hours

if __name__ == '__main__':
    unittest.main()
