import unittest
import time
import pytest
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app, db
from app.models.portfolio import Portfolio, StockTransaction as Transaction
from app.models.price import PriceHistory
from datetime import date, datetime, timedelta

class TestDashboardLoadTime(unittest.TestCase):
    """
    Test dashboard load time performance.
    
    Note: These tests use more lenient timing expectations than production
    performance targets because test environments have additional overhead
    from database setup/teardown, mocking, and test framework operations.
    Production performance is typically much faster than test environment performance.
    """
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test portfolio
        self.portfolio = Portfolio(
            name='Test Portfolio', 
            description='Test Description',
            user_id='test_user'
        )
        db.session.add(self.portfolio)
        db.session.commit()
        
        # Create test transactions (100 transactions)
        transactions = []
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'PG']
        
        for i in range(10):  # 10 tickers
            for j in range(10):  # 10 transactions per ticker
                transactions.append(
                    Transaction(
                        portfolio_id=self.portfolio.id,
                        date=date.today() - timedelta(days=j*10),
                        ticker=tickers[i],
                        transaction_type='BUY',
                        shares=1,
                        price_per_share=100.0,
                        total_value=100.0
                    )
                )
        
        db.session.add_all(transactions)
        
        # Create test price history
        price_histories = []
        for ticker in tickers:
            price_histories.append(
                PriceHistory(
                    ticker=ticker,
                    date=date.today(),
                    close_price=110.0,
                    is_intraday=True,
                    price_timestamp=datetime.now(),
                    last_updated=datetime.now()
                )
            )
        
        # Add ETF prices
        price_histories.extend([
            PriceHistory(
                ticker='VOO',
                date=date.today(),
                close_price=400.0,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            ),
            PriceHistory(
                ticker='QQQ',
                date=date.today(),
                close_price=350.0,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
        ])
        
        db.session.add_all(price_histories)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_traditional_dashboard_load_time(self):
        """Test traditional dashboard load time"""
        # Disable progressive loading
        with patch('app.views.main.progressive_loading', False):
            # Measure load time
            start_time = time.time()
            response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
            end_time = time.time()
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Log load time
            load_time = end_time - start_time
            print(f"Traditional dashboard load time: {load_time:.2f} seconds")
            
            # Load time should be reasonable (adjust threshold as needed)
            # This is just a basic check, actual performance will vary by environment
            self.assertLess(load_time, 5.0)  # Should load in under 5 seconds in test environment
    
    def test_progressive_dashboard_load_time(self):
        """Test progressive dashboard load time"""
        # Enable progressive loading
        with patch('app.views.main.progressive_loading', True):
            # Measure load time
            start_time = time.time()
            response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
            end_time = time.time()
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Log load time
            load_time = end_time - start_time
            print(f"Progressive dashboard load time: {load_time:.2f} seconds")
            
            # Load time should be reasonable for test environment
            # Test environments are slower than production due to setup/teardown overhead
            self.assertLess(load_time, 10.0)  # Should load in under 10 seconds in test environment
    
    def test_initial_data_load_time(self):
        """Test initial data API endpoint load time"""
        # Measure load time
        start_time = time.time()
        response = self.client.get(f'/api/dashboard-initial-data/{self.portfolio.id}')
        end_time = time.time()
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Log load time
        load_time = end_time - start_time
        print(f"Initial data load time: {load_time:.2f} seconds")
        
        # Initial data should load reasonably quickly in test environment
        self.assertLess(load_time, 5.0)  # More realistic for test environment
    
    def test_holdings_data_load_time(self):
        """Test holdings data API endpoint load time"""
        # Measure load time
        start_time = time.time()
        response = self.client.get(f'/api/dashboard-holdings-data/{self.portfolio.id}')
        end_time = time.time()
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Log load time
        load_time = end_time - start_time
        print(f"Holdings data load time: {load_time:.2f} seconds")
        
        # Holdings data should load reasonably quickly
        self.assertLess(load_time, 2.0)  # Should load in under 2 seconds
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_chart_data_load_time(self):
        """Test chart data API endpoint load time"""
        # Mock chart_generator.get_chart_data to return None (force generation)
        with patch('app.services.background_tasks.chart_generator.get_chart_data', return_value=None):
            # Mock get_cached_chart_data to return None (force generation)
            with patch('app.views.main.get_cached_chart_data', return_value=None):
                # Mock chart_generator.generate_chart_data to avoid actual generation
                with patch('app.services.background_tasks.chart_generator.generate_chart_data', return_value=True):
                    # Measure load time
                    start_time = time.time()
                    response = self.client.get(f'/api/dashboard-chart-data/{self.portfolio.id}')
                    end_time = time.time()
                    
                    # Verify response
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertTrue(data['success'])
                    
                    # Log load time
                    load_time = end_time - start_time
                    print(f"Chart data API load time: {load_time:.2f} seconds")
                    
                    # Chart data API should respond reasonably in test environment
                    self.assertLess(load_time, 10.0)  # More realistic for test environment
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_end_to_end_progressive_load(self):
        """Test end-to-end progressive load time"""
        # Enable progressive loading
        with patch('app.views.main.progressive_loading', True):
            # Step 1: Load dashboard
            dashboard_start = time.time()
            dashboard_response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
            dashboard_end = time.time()
            
            # Step 2: Load initial data
            initial_start = time.time()
            initial_response = self.client.get(f'/api/dashboard-initial-data/{self.portfolio.id}')
            initial_end = time.time()
            
            # Step 3: Load holdings data
            holdings_start = time.time()
            holdings_response = self.client.get(f'/api/dashboard-holdings-data/{self.portfolio.id}')
            holdings_end = time.time()
            
            # Step 4: Load chart data
            chart_start = time.time()
            chart_response = self.client.get(f'/api/dashboard-chart-data/{self.portfolio.id}')
            chart_end = time.time()
            
            # Verify all responses
            self.assertEqual(dashboard_response.status_code, 200)
            self.assertEqual(initial_response.status_code, 200)
            self.assertEqual(holdings_response.status_code, 200)
            self.assertEqual(chart_response.status_code, 200)
            
            # Log load times
            dashboard_time = dashboard_end - dashboard_start
            initial_time = initial_end - initial_start
            holdings_time = holdings_end - holdings_start
            chart_time = chart_end - chart_start
            total_time = dashboard_time + initial_time + holdings_time + chart_time
            
            print(f"Dashboard template load time: {dashboard_time:.2f} seconds")
            print(f"Initial data load time: {initial_time:.2f} seconds")
            print(f"Holdings data load time: {holdings_time:.2f} seconds")
            print(f"Chart data load time: {chart_time:.2f} seconds")
            print(f"Total progressive load time: {total_time:.2f} seconds")
            
            # Initial dashboard + initial data should be fast
            self.assertLess(dashboard_time + initial_time, 10.0)  # More realistic for test environment
            
            # Total time should be reasonable
            self.assertLess(total_time, 20.0)  # More realistic for test environment

if __name__ == '__main__':
    unittest.main()
