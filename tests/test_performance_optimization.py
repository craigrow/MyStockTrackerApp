"""Tests for performance optimization features."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import pandas as pd
import asyncio
from app.services.price_service import PriceService
from app import db

class TestBatchApiProcessing:
    """Test batch API processing optimizations."""
    
    @pytest.fixture
    def price_service(self, app):
        with app.app_context():
            return PriceService()
    
    @patch('yfinance.download')
    def test_batch_fetch_prices(self, mock_download, price_service, app):
        """Test that batch_fetch_prices correctly processes multiple tickers in a single API call."""
        with app.app_context():
            # Mock the yfinance download response
            mock_data = {
                'AAPL': pd.DataFrame({
                    'Close': [150.0, 151.0],
                    'Open': [149.0, 150.5],
                    'High': [152.0, 153.0],
                    'Low': [148.0, 149.5],
                    'Volume': [1000000, 1100000]
                }, index=[date.today() - timedelta(days=1), date.today()]),
                'MSFT': pd.DataFrame({
                    'Close': [250.0, 252.0],
                    'Open': [249.0, 251.0],
                    'High': [253.0, 254.0],
                    'Low': [248.0, 250.0],
                    'Volume': [2000000, 2100000]
                }, index=[date.today() - timedelta(days=1), date.today()]),
                'GOOGL': pd.DataFrame({
                    'Close': [2800.0, 2820.0],
                    'Open': [2790.0, 2810.0],
                    'High': [2830.0, 2840.0],
                    'Low': [2780.0, 2800.0],
                    'Volume': [500000, 520000]
                }, index=[date.today() - timedelta(days=1), date.today()])
            }
            
            # Create a multi-level DataFrame similar to what yfinance returns
            multi_index = pd.MultiIndex.from_product([['AAPL', 'MSFT', 'GOOGL'], ['Close', 'Open', 'High', 'Low', 'Volume']])
            mock_df = pd.DataFrame(columns=multi_index)
            
            # Fill the DataFrame with data
            for ticker in ['AAPL', 'MSFT', 'GOOGL']:
                for column in ['Close', 'Open', 'High', 'Low', 'Volume']:
                    mock_df[(ticker, column)] = mock_data[ticker][column]
            
            mock_download.return_value = mock_df
            
            # Call the batch_fetch_prices method
            tickers = ['AAPL', 'MSFT', 'GOOGL']
            result = price_service.batch_fetch_prices(tickers)
            
            # Verify the method called yfinance.download with the correct parameters
            mock_download.assert_called_once()
            call_args = mock_download.call_args[1]
            assert call_args['tickers'] == ' '.join(tickers)
            assert call_args['group_by'] == 'ticker'
            
            # Verify the result contains data for all tickers
            assert len(result) == 3
            assert 'AAPL' in result
            assert 'MSFT' in result
            assert 'GOOGL' in result
            
            # Verify the price data is correct
            assert result['AAPL'].iloc[-1]['Close'] == 151.0
            assert result['MSFT'].iloc[-1]['Close'] == 252.0
            assert result['GOOGL'].iloc[-1]['Close'] == 2820.0
    
    @patch('yfinance.download')
    def test_batch_fetch_prices_with_date_range(self, mock_download, price_service, app):
        """Test batch_fetch_prices with specific date range."""
        with app.app_context():
            # Mock the yfinance download response
            mock_data = {
                'AAPL': pd.DataFrame({
                    'Close': [150.0, 151.0],
                    'Open': [149.0, 150.5],
                    'High': [152.0, 153.0],
                    'Low': [148.0, 149.5],
                    'Volume': [1000000, 1100000]
                }, index=[date.today() - timedelta(days=1), date.today()]),
                'MSFT': pd.DataFrame({
                    'Close': [250.0, 252.0],
                    'Open': [249.0, 251.0],
                    'High': [253.0, 254.0],
                    'Low': [248.0, 250.0],
                    'Volume': [2000000, 2100000]
                }, index=[date.today() - timedelta(days=1), date.today()])
            }
            
            # Create a multi-level DataFrame similar to what yfinance returns
            multi_index = pd.MultiIndex.from_product([['AAPL', 'MSFT'], ['Close', 'Open', 'High', 'Low', 'Volume']])
            mock_df = pd.DataFrame(columns=multi_index)
            
            # Fill the DataFrame with data
            for ticker in ['AAPL', 'MSFT']:
                for column in ['Close', 'Open', 'High', 'Low', 'Volume']:
                    mock_df[(ticker, column)] = mock_data[ticker][column]
            
            mock_download.return_value = mock_df
            
            # Call the batch_fetch_prices method with date range
            start_date = date.today() - timedelta(days=7)
            end_date = date.today()
            tickers = ['AAPL', 'MSFT']
            result = price_service.batch_fetch_prices(tickers, start_date=start_date, end_date=end_date)
            
            # Verify the method called yfinance.download with the correct parameters
            mock_download.assert_called_once()
            call_args = mock_download.call_args[1]
            assert call_args['tickers'] == ' '.join(tickers)
            assert call_args['start'] == start_date
            assert call_args['end'] == end_date
            
            # Verify the result contains data for all tickers
            assert len(result) == 2
            assert 'AAPL' in result
            assert 'MSFT' in result
    
    @patch('app.services.price_service.yf.Ticker')
    @patch('app.services.price_service.yf.download')
    def test_batch_fetch_prices_error_handling(self, mock_download, mock_ticker, price_service, app):
        """Test batch_fetch_prices handles errors gracefully."""
        with app.app_context():
            # Mock yfinance.download to raise an exception
            mock_download.side_effect = Exception("API rate limit exceeded")
            
            # Mock yfinance.Ticker to also raise an exception (for fallback)
            mock_ticker.side_effect = Exception("API rate limit exceeded")
            
            # Call the batch_fetch_prices method
            tickers = ['AAPL', 'MSFT', 'GOOGL']
            result = price_service.batch_fetch_prices(tickers)
            
            # Verify the method returns an empty dictionary on error
            assert isinstance(result, dict)
            assert len(result) == 0
    
    @patch('app.services.price_service.PriceService.batch_fetch_prices')
    def test_batch_fetch_current_prices(self, mock_batch_fetch, price_service, app):
        """Test batch_fetch_current_prices correctly processes multiple tickers."""
        with app.app_context():
            # Mock the batch_fetch_prices response
            mock_batch_fetch.return_value = {
                'AAPL': pd.DataFrame({
                    'Close': [151.0]
                }, index=[date.today()]),
                'MSFT': pd.DataFrame({
                    'Close': [252.0]
                }, index=[date.today()]),
                'GOOGL': pd.DataFrame({
                    'Close': [2820.0]
                }, index=[date.today()])
            }
            
            # Call the batch_fetch_current_prices method
            tickers = ['AAPL', 'MSFT', 'GOOGL']
            result = price_service.batch_fetch_current_prices(tickers)
            
            # Verify the result contains prices for all tickers
            assert len(result) == 3
            assert result['AAPL'] == 151.0
            assert result['MSFT'] == 252.0
            assert result['GOOGL'] == 2820.0
            
            # Verify batch_fetch_prices was called with the correct parameters
            mock_batch_fetch.assert_called_once_with(tickers, period="1d")

class TestParallelProcessing:
    """Test parallel processing optimizations."""
    
    @pytest.fixture
    def price_service(self, app):
        with app.app_context():
            return PriceService()
    
    @patch('app.services.price_service.PriceService.batch_fetch_prices')
    def test_fetch_prices_parallel(self, mock_batch_fetch, price_service, app):
        """Test that fetch_prices_parallel correctly processes multiple ticker chunks in parallel."""
        with app.app_context():
            # Mock the batch_fetch_prices response for different chunks
            def mock_batch_fetch_side_effect(tickers, **kwargs):
                result = {}
                for ticker in tickers:
                    if ticker == 'AAPL':
                        result[ticker] = pd.DataFrame({
                            'Close': [151.0]
                        }, index=[date.today()])
                    elif ticker == 'MSFT':
                        result[ticker] = pd.DataFrame({
                            'Close': [252.0]
                        }, index=[date.today()])
                    elif ticker == 'GOOGL':
                        result[ticker] = pd.DataFrame({
                            'Close': [2820.0]
                        }, index=[date.today()])
                return result
            
            mock_batch_fetch.side_effect = mock_batch_fetch_side_effect
            
            # Call the fetch_prices_parallel method
            tickers = ['AAPL', 'MSFT', 'GOOGL']
            result = asyncio.run(price_service.fetch_prices_parallel(tickers))
            
            # Verify the result contains data for all tickers
            assert len(result) == 3
            assert 'AAPL' in result
            assert 'MSFT' in result
            assert 'GOOGL' in result
            
            # Verify batch_fetch_prices was called for each chunk
            assert mock_batch_fetch.call_count > 0
    
    @patch('app.services.price_service.PriceService.batch_fetch_prices')
    def test_fetch_current_prices_parallel(self, mock_batch_fetch, price_service, app):
        """Test fetch_current_prices_parallel correctly processes multiple ticker chunks."""
        with app.app_context():
            # Mock the batch_fetch_prices response for different chunks
            def mock_batch_fetch_side_effect(tickers, **kwargs):
                result = {}
                for ticker in tickers:
                    if ticker == 'AAPL':
                        result[ticker] = pd.DataFrame({
                            'Close': [151.0]
                        }, index=[date.today()])
                    elif ticker == 'MSFT':
                        result[ticker] = pd.DataFrame({
                            'Close': [252.0]
                        }, index=[date.today()])
                    elif ticker == 'GOOGL':
                        result[ticker] = pd.DataFrame({
                            'Close': [2820.0]
                        }, index=[date.today()])
                return result
            
            mock_batch_fetch.side_effect = mock_batch_fetch_side_effect
            
            # Call the fetch_current_prices_parallel method
            tickers = ['AAPL', 'MSFT', 'GOOGL']
            result = asyncio.run(price_service.fetch_current_prices_parallel(tickers))
            
            # Verify the result contains prices for all tickers
            assert len(result) == 3
            assert result['AAPL'] == 151.0
            assert result['MSFT'] == 252.0
            assert result['GOOGL'] == 2820.0