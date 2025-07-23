import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app, db
from app.models.portfolio import Portfolio, StockTransaction as Transaction
from app.models.price import PriceHistory
from datetime import date, datetime, timedelta

class TestProgressiveLoading(unittest.TestCase):
    
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
        
        # Create test transactions
        transactions = [
            Transaction(
                portfolio_id=self.portfolio.id,
                date=date.today() - timedelta(days=30),
                ticker='AAPL',
                transaction_type='BUY',
                shares=10,
                price=150.0,
                total_value=1500.0
            ),
            Transaction(
                portfolio_id=self.portfolio.id,
                date=date.today() - timedelta(days=15),
                ticker='MSFT',
                transaction_type='BUY',
                shares=5,
                price=300.0,
                total_value=1500.0
            )
        ]
        db.session.add_all(transactions)
        
        # Create test price history
        price_histories = [
            PriceHistory(
                ticker='AAPL',
                date=date.today(),
                close_price=160.0,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            ),
            PriceHistory(
                ticker='MSFT',
                date=date.today(),
                close_price=320.0,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            ),
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
        ]
        db.session.add_all(price_histories)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_dashboard_initial_data_endpoint(self):
        """Test the dashboard-initial-data endpoint"""
        # Mock calculate_minimal_portfolio_stats
        with patch('app.views.main.calculate_minimal_portfolio_stats') as mock_stats:
            mock_stats.return_value = {
                'current_value': 3000.0,
                'total_invested': 3000.0,
                'total_gain_loss': 0.0,
                'gain_loss_percentage': 0.0,
                'cash_balance': 0.0,
                'total_dividends': 0.0,
                'voo_equivalent': 0.0,
                'qqq_equivalent': 0.0,
                'voo_gain_loss': 0.0,
                'qqq_gain_loss': 0.0,
                'voo_gain_loss_percentage': 0.0,
                'qqq_gain_loss_percentage': 0.0,
                'voo_daily_change': 0.0,
                'voo_daily_dollar_change': 0.0,
                'qqq_daily_change': 0.0,
                'qqq_daily_dollar_change': 0.0,
                'portfolio_daily_change': 0.0,
                'portfolio_daily_dollar_change': 0.0
            }
            
            # Mock get_minimal_holdings
            with patch('app.views.api.get_minimal_holdings') as mock_holdings:
                mock_holdings.return_value = [
                    {
                        'ticker': 'AAPL',
                        'shares': 10,
                        'current_price': 160.0,
                        'market_value': 1600.0,
                        'cost_basis': 1500.0,
                        'gain_loss': 100.0,
                        'gain_loss_percentage': 6.67,
                        'portfolio_percentage': 53.33,
                        'is_stale': False
                    },
                    {
                        'ticker': 'MSFT',
                        'shares': 5,
                        'current_price': 320.0,
                        'market_value': 1600.0,
                        'cost_basis': 1500.0,
                        'gain_loss': 100.0,
                        'gain_loss_percentage': 6.67,
                        'portfolio_percentage': 46.67,
                        'is_stale': False
                    }
                ]
                
                # Mock chart_generator.generate_chart_data
                with patch('app.services.background_tasks.chart_generator.generate_chart_data') as mock_generate:
                    mock_generate.return_value = True
                    
                    # Make request
                    response = self.client.get(f'/api/dashboard-initial-data/{self.portfolio.id}')
                    data = json.loads(response.data)
                    
                    # Verify response
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(data['success'])
                    self.assertIn('portfolio_stats', data)
                    self.assertIn('holdings', data)
                    self.assertIn('recent_transactions', data)
                    self.assertEqual(len(data['holdings']), 2)
                    self.assertEqual(len(data['recent_transactions']), 2)
                    
                    # Verify mock calls
                    mock_stats.assert_called_once()
                    mock_holdings.assert_called_once()
                    mock_generate.assert_called_once_with(self.portfolio.id)
    
    def test_dashboard_chart_data_endpoint(self):
        """Test the dashboard-chart-data endpoint"""
        # Mock chart_generator.get_chart_data
        with patch('app.services.background_tasks.chart_generator.get_chart_data') as mock_get_data:
            chart_data = {
                'dates': ['2025-06-23', '2025-06-24', '2025-06-25'],
                'portfolio_values': [3000.0, 3050.0, 3100.0],
                'voo_values': [2900.0, 2950.0, 3000.0],
                'qqq_values': [2800.0, 2850.0, 2900.0]
            }
            mock_get_data.return_value = chart_data
            
            # Make request
            response = self.client.get(f'/api/dashboard-chart-data/{self.portfolio.id}')
            data = json.loads(response.data)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['chart_data'], chart_data)
            self.assertEqual(data['source'], 'background_generator')
            
            # Verify mock calls
            mock_get_data.assert_called_once_with(self.portfolio.id)
    
    def test_dashboard_chart_data_endpoint_with_cache(self):
        """Test the dashboard-chart-data endpoint with cached data"""
        # Mock chart_generator.get_chart_data to return None (no background data)
        with patch('app.services.background_tasks.chart_generator.get_chart_data') as mock_get_data:
            mock_get_data.return_value = None
            
            # Mock get_cached_chart_data
            with patch('app.views.main.get_cached_chart_data') as mock_get_cached:
                chart_data = {
                    'dates': ['2025-06-23', '2025-06-24', '2025-06-25'],
                    'portfolio_values': [3000.0, 3050.0, 3100.0],
                    'voo_values': [2900.0, 2950.0, 3000.0],
                    'qqq_values': [2800.0, 2850.0, 2900.0]
                }
                mock_get_cached.return_value = chart_data
                
                # Make request
                response = self.client.get(f'/api/dashboard-chart-data/{self.portfolio.id}')
                data = json.loads(response.data)
                
                # Verify response
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                self.assertEqual(data['chart_data'], chart_data)
                self.assertEqual(data['source'], 'cache')
                
                # Verify mock calls
                mock_get_data.assert_called_once_with(self.portfolio.id)
                mock_get_cached.assert_called_once()
    
    def test_dashboard_chart_data_endpoint_with_generation(self):
        """Test the dashboard-chart-data endpoint with chart generation in progress"""
        # Mock chart_generator.get_chart_data to return None (no background data)
        with patch('app.services.background_tasks.chart_generator.get_chart_data') as mock_get_data:
            mock_get_data.return_value = None
            
            # Mock get_cached_chart_data to return None (no cached data)
            with patch('app.views.main.get_cached_chart_data') as mock_get_cached:
                mock_get_cached.return_value = None
                
                # Mock chart_generator.get_progress
                with patch('app.services.background_tasks.chart_generator.get_progress') as mock_get_progress:
                    mock_get_progress.return_value = {
                        'status': 'generating',
                        'portfolio_id': self.portfolio.id
                    }
                    
                    # Make request
                    response = self.client.get(f'/api/dashboard-chart-data/{self.portfolio.id}')
                    data = json.loads(response.data)
                    
                    # Verify response
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(data['success'])
                    self.assertEqual(data['status'], 'generating')
                    self.assertIn('progress', data)
                    self.assertIn('chart_data', data)  # Empty chart data
                    
                    # Verify mock calls
                    mock_get_data.assert_called_once_with(self.portfolio.id)
                    mock_get_cached.assert_called_once()
                    mock_get_progress.assert_called_once()
    
    def test_dashboard_holdings_data_endpoint(self):
        """Test the dashboard-holdings-data endpoint"""
        # Mock get_holdings_with_performance
        with patch('app.views.main.get_holdings_with_performance') as mock_holdings:
            holdings_data = [
                {
                    'ticker': 'AAPL',
                    'shares': 10,
                    'current_price': 160.0,
                    'market_value': 1600.0,
                    'cost_basis': 1500.0,
                    'gain_loss': 100.0,
                    'gain_loss_percentage': 6.67,
                    'portfolio_percentage': 53.33,
                    'voo_performance': 5.0,
                    'qqq_performance': 7.0,
                    'is_stale': False
                },
                {
                    'ticker': 'MSFT',
                    'shares': 5,
                    'current_price': 320.0,
                    'market_value': 1600.0,
                    'cost_basis': 1500.0,
                    'gain_loss': 100.0,
                    'gain_loss_percentage': 6.67,
                    'portfolio_percentage': 46.67,
                    'voo_performance': 4.0,
                    'qqq_performance': 6.0,
                    'is_stale': False
                }
            ]
            mock_holdings.return_value = holdings_data
            
            # Mock calculate_etf_performance_for_holding
            with patch('app.views.main.calculate_etf_performance_for_holding') as mock_etf_perf:
                mock_etf_perf.side_effect = [5.0, 7.0, 4.0, 6.0]  # AAPL-VOO, AAPL-QQQ, MSFT-VOO, MSFT-QQQ
                
                # Make request
                response = self.client.get(f'/api/dashboard-holdings-data/{self.portfolio.id}')
                data = json.loads(response.data)
                
                # Verify response
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                self.assertEqual(data['holdings'], holdings_data)
                self.assertIn('timestamp', data)
                
                # Verify mock calls
                mock_holdings.assert_called_once()
                self.assertEqual(mock_etf_perf.call_count, 4)
    
    def test_chart_generator_progress_endpoint(self):
        """Test the chart-generator-progress endpoint"""
        # Mock chart_generator.get_progress
        with patch('app.services.background_tasks.chart_generator.get_progress') as mock_get_progress:
            mock_get_progress.return_value = {
                'status': 'generating',
                'portfolio_id': self.portfolio.id,
                'percent_complete': 50
            }
            
            # Mock chart_generator.get_chart_data
            with patch('app.services.background_tasks.chart_generator.get_chart_data') as mock_get_data:
                mock_get_data.return_value = None  # No data yet
                
                # Make request
                response = self.client.get(f'/api/chart-generator-progress/{self.portfolio.id}')
                data = json.loads(response.data)
                
                # Verify response
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                self.assertEqual(data['status'], 'generating')
                self.assertEqual(data['progress']['percent_complete'], 50)
                
                # Verify mock calls
                mock_get_progress.assert_called_once()
                mock_get_data.assert_called_once_with(self.portfolio.id)
    
    def test_chart_generator_progress_endpoint_with_data(self):
        """Test the chart-generator-progress endpoint with completed data"""
        # Mock chart_generator.get_progress
        with patch('app.services.background_tasks.chart_generator.get_progress') as mock_get_progress:
            mock_get_progress.return_value = {
                'status': 'completed',
                'portfolio_id': self.portfolio.id
            }
            
            # Mock chart_generator.get_chart_data
            with patch('app.services.background_tasks.chart_generator.get_chart_data') as mock_get_data:
                chart_data = {
                    'dates': ['2025-06-23', '2025-06-24', '2025-06-25'],
                    'portfolio_values': [3000.0, 3050.0, 3100.0],
                    'voo_values': [2900.0, 2950.0, 3000.0],
                    'qqq_values': [2800.0, 2850.0, 2900.0]
                }
                mock_get_data.return_value = chart_data
                
                # Make request
                response = self.client.get(f'/api/chart-generator-progress/{self.portfolio.id}')
                data = json.loads(response.data)
                
                # Verify response
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                self.assertEqual(data['status'], 'completed')
                self.assertEqual(data['chart_data'], chart_data)
                
                # Verify mock calls
                mock_get_progress.assert_called_once()
                mock_get_data.assert_called_once_with(self.portfolio.id)

if __name__ == '__main__':
    unittest.main()
