import unittest
import pytest
from unittest.mock import patch, MagicMock, call
from app.services.background_tasks import BackgroundPriceUpdater, BackgroundChartGenerator
import time
from datetime import datetime, timedelta, date
import asyncio

class TestBackgroundPriceUpdater(unittest.TestCase):
    
    def setUp(self):
        self.updater = BackgroundPriceUpdater()
        self.portfolio_id = '123'
        
        # Mock portfolio_service and price_service
        self.updater.portfolio_service = MagicMock()
        self.updater.price_service = MagicMock()
        
        # Set up mock holdings
        self.updater.portfolio_service.get_current_holdings.return_value = {
            'AAPL': 10,
            'MSFT': 5,
            'GOOGL': 2
        }
    
    def test_queue_portfolio_price_updates(self):
        """Test queuing price updates for a portfolio"""
        # Mock _check_stale_data
        self.updater._check_stale_data = MagicMock(return_value=['AAPL'])
        
        # Mock threading to avoid actual background processing
        with patch('threading.Thread') as mock_thread:
            # Mock the thread instance
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Call the method
            self.updater.queue_portfolio_price_updates(self.portfolio_id)
            
            # Verify portfolio_service.get_current_holdings was called
            self.updater.portfolio_service.get_current_holdings.assert_called_once_with(self.portfolio_id)
            
            # Verify _check_stale_data was called with the right tickers
            self.updater._check_stale_data.assert_called_once_with(['AAPL', 'MSFT', 'GOOGL', 'VOO', 'QQQ'])
            
            # Verify update_queue contains all tickers
            self.assertEqual(set(self.updater.update_queue), {'AAPL', 'MSFT', 'GOOGL', 'VOO', 'QQQ'})
            
            # Verify progress was updated
            self.assertEqual(self.updater.progress['status'], 'queued')
            self.assertEqual(self.updater.progress['total'], 5)
            self.assertEqual(self.updater.progress['current'], 0)
            self.assertEqual(self.updater.progress['stale_data'], ['AAPL'])
            self.assertEqual(self.updater.progress['portfolio_id'], self.portfolio_id)
            
            # Verify thread was created and started
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_process_queue_batch(self):
        """Test batch processing of price updates"""
        # Set up test data
        self.updater.update_queue = ['AAPL', 'MSFT', 'GOOGL', 'VOO', 'QQQ']
        self.updater.batch_size = 2
        
        # Mock price_service.batch_fetch_current_prices
        self.updater.price_service.batch_fetch_current_prices.return_value = {
            'AAPL': 150.0,
            'MSFT': 300.0
        }
        
        # Mock time.sleep to avoid delays
        with patch('time.sleep'):
            # Call the method directly (avoiding threading)
            self.updater._process_queue_batch()
            
            # Verify batch_fetch_current_prices was called multiple times
            self.assertEqual(self.updater.price_service.batch_fetch_current_prices.call_count, 3)
            
            # Verify batch_cache_price_data was called multiple times
            self.assertEqual(self.updater.price_service.batch_cache_price_data.call_count, 3)
            
            # Verify progress was updated
            self.assertEqual(self.updater.progress['status'], 'completed')
            self.assertEqual(self.updater.progress['current'], 5)
            self.assertIn('execution_time', self.updater.progress)
            self.assertIn('updated_count', self.updater.progress)
    
    @pytest.mark.asyncio
    async def test_process_queue_parallel(self):
        """Test parallel processing of price updates"""
        # Set up test data
        self.updater.update_queue = ['AAPL', 'MSFT', 'GOOGL', 'VOO', 'QQQ']
        
        # Mock price_service.fetch_current_prices_parallel
        self.updater.price_service.fetch_current_prices_parallel = MagicMock()
        self.updater.price_service.fetch_current_prices_parallel.return_value = {
            'AAPL': 150.0,
            'MSFT': 300.0,
            'GOOGL': 2000.0,
            'VOO': 400.0,
            'QQQ': 350.0
        }
        
        # Call the method directly (avoiding threading)
        await self.updater._process_queue_parallel()
        
        # Verify fetch_current_prices_parallel was called
        self.updater.price_service.fetch_current_prices_parallel.assert_called_once_with(
            self.updater.update_queue,
            max_workers=self.updater.max_workers,
            chunk_size=self.updater.batch_size
        )
        
        # Verify batch_cache_price_data was called
        self.updater.price_service.batch_cache_price_data.assert_called_once()
        
        # Verify progress was updated
        self.assertEqual(self.updater.progress['status'], 'completed')
        self.assertEqual(self.updater.progress['current'], 5)
        self.assertEqual(self.updater.progress['updated_count'], 5)
        self.assertIn('execution_time', self.updater.progress)
    
    def test_get_progress(self):
        """Test getting progress"""
        # Set up test data
        self.updater.progress = {
            'status': 'updating',
            'current': 3,
            'total': 5
        }
        
        # Get progress
        progress = self.updater.get_progress()
        
        # Verify progress is a copy
        self.assertEqual(progress, self.updater.progress)
        self.assertIsNot(progress, self.updater.progress)


class TestBackgroundChartGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = BackgroundChartGenerator()
        self.portfolio_id = '123'
        
        # Mock portfolio_service and price_service
        self.generator.portfolio_service = MagicMock()
        self.generator.price_service = MagicMock()
    
    def test_generate_chart_data(self):
        """Test queuing chart data generation"""
        # Mock the database access functions to avoid application context issues
        with patch('app.views.main.get_cached_chart_data', return_value=None):
            with patch('app.views.main.get_last_market_date', return_value=date.today()):
                # Mock _generate_chart_data to avoid threading
                self.generator._generate_chart_data = MagicMock()
                
                # Call the method
                result = self.generator.generate_chart_data(self.portfolio_id)
                
                # Verify result
                self.assertTrue(result)
                
                # Verify progress was updated
                self.assertEqual(self.generator.progress['status'], 'queued')
                self.assertEqual(self.generator.progress['portfolio_id'], self.portfolio_id)
        self.assertIn('start_time', self.generator.progress)
        
        # Verify _generate_chart_data was called
        self.generator._generate_chart_data.assert_called_once_with(self.portfolio_id)
    
    def test_generate_chart_data_already_running(self):
        """Test queuing chart data generation when already running"""
        # Set is_running to True
        self.generator.is_running = True
        
        # Call the method
        result = self.generator.generate_chart_data(self.portfolio_id)
        
        # Verify result
        self.assertFalse(result)
    
    def test_generate_chart_data_cached(self):
        """Test chart data generation with cached data"""
        # Set up cached chart data
        self.generator.chart_data = {
            self.portfolio_id: {'dates': ['2025-01-01'], 'portfolio_values': [1000]}
        }
        self.generator.progress = {
            'status': 'completed',
            'portfolio_id': self.portfolio_id,
            'start_time': datetime.utcnow() - timedelta(hours=1)
        }
        
        # Mock the database access functions
        with patch('app.views.main.get_cached_chart_data', return_value=None):
            with patch('app.views.main.get_last_market_date', return_value=date.today()):
                # Mock _generate_chart_data to track if it's called
                with patch.object(self.generator, '_generate_chart_data') as mock_generate:
                    # Call the method
                    result = self.generator.generate_chart_data(self.portfolio_id)
                    
                    # Verify result
                    self.assertTrue(result)
                    
                    # Verify _generate_chart_data was not called (using cached data)
                    mock_generate.assert_not_called()
    
    @patch('app.views.main.generate_chart_data')
    def test_generate_chart_data_implementation(self, mock_generate_chart_data):
        """Test chart data generation implementation"""
        # Mock generate_chart_data
        mock_chart_data = {
            'dates': ['2025-01-01', '2025-01-02'],
            'portfolio_values': [1000, 1100],
            'voo_values': [900, 950],
            'qqq_values': [800, 850]
        }
        mock_generate_chart_data.return_value = mock_chart_data
        
        # Mock _cache_chart_data
        self.generator._cache_chart_data = MagicMock()
        
        # Call the method directly
        self.generator._generate_chart_data(self.portfolio_id)
        
        # Verify generate_chart_data was called
        mock_generate_chart_data.assert_called_once_with(
            self.portfolio_id,
            self.generator.portfolio_service,
            self.generator.price_service
        )
        
        # Verify _cache_chart_data was called
        self.generator._cache_chart_data.assert_called_once_with(self.portfolio_id, mock_chart_data)
        
        # Verify progress was updated
        self.assertEqual(self.generator.progress['status'], 'completed')
        self.assertIn('completion_time', self.generator.progress)
        
        # Verify chart_data was updated
        self.assertEqual(self.generator.chart_data[self.portfolio_id], mock_chart_data)
    
    @patch('app.views.main.generate_chart_data')
    def test_generate_chart_data_error_handling(self, mock_generate_chart_data):
        """Test chart data generation error handling"""
        # Mock generate_chart_data to raise an exception
        mock_generate_chart_data.side_effect = Exception("Test error")
        
        # Mock _generate_minimal_chart_data
        self.generator._generate_minimal_chart_data = MagicMock()
        minimal_chart_data = {
            'dates': ['2025-01-01'],
            'portfolio_values': [1000],
            'voo_values': [900],
            'qqq_values': [800],
            'is_fallback': True
        }
        self.generator._generate_minimal_chart_data.return_value = minimal_chart_data
        
        # Call the method directly
        self.generator._generate_chart_data(self.portfolio_id)
        
        # Verify generate_chart_data was called
        mock_generate_chart_data.assert_called_once()
        
        # Verify _generate_minimal_chart_data was called
        self.generator._generate_minimal_chart_data.assert_called_once_with(self.portfolio_id)
        
        # Verify progress was updated
        self.assertEqual(self.generator.progress['status'], 'completed_with_fallback')
        
        # Verify chart_data was updated with fallback data
        self.assertEqual(self.generator.chart_data[self.portfolio_id], minimal_chart_data)
    
    def test_get_progress(self):
        """Test getting progress"""
        # Set up test data
        self.generator.progress = {
            'status': 'generating',
            'portfolio_id': self.portfolio_id
        }
        
        # Get progress
        progress = self.generator.get_progress()
        
        # Verify progress is a copy
        self.assertEqual(progress, self.generator.progress)
        self.assertIsNot(progress, self.generator.progress)
    
    def test_get_chart_data(self):
        """Test getting chart data"""
        # Set up test data
        chart_data = {
            'dates': ['2025-01-01', '2025-01-02'],
            'portfolio_values': [1000, 1100],
            'voo_values': [900, 950],
            'qqq_values': [800, 850]
        }
        self.generator.chart_data = {self.portfolio_id: chart_data}
        
        # Get chart data
        result = self.generator.get_chart_data(self.portfolio_id)
        
        # Verify result
        self.assertEqual(result, chart_data)
        
        # Test with non-existent portfolio
        result = self.generator.get_chart_data('non-existent')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
