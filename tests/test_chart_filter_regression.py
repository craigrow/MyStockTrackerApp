"""
Test for chart filter regression fix.

This test verifies that the Portfolio Performance chart correctly
restores user's date period selection after navigation and data updates.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app, db
from app.models.portfolio import Portfolio
from app.models.portfolio import StockTransaction
from datetime import date, timedelta


class TestChartFilterRegression(unittest.TestCase):
    """Test chart filter persistence across navigation and data updates."""
    
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
        
        # Add some test transactions
        transaction = StockTransaction(
            portfolio_id=self.portfolio.id,
            date=date.today() - timedelta(days=30),
            ticker='AAPL',
            transaction_type='BUY',
            shares=10,
            price_per_share=150.0,
            total_value=1500.0
        )
        db.session.add(transaction)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_dashboard_contains_chart_filter_elements(self):
        """Test that dashboard contains the chart period selector elements."""
        response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for period selector buttons
        self.assertIn('name="chartPeriod"', html_content)
        self.assertIn('id="ytd"', html_content)
        self.assertIn('id="last12m"', html_content)
        self.assertIn('id="last5y"', html_content)
        self.assertIn('id="all"', html_content)
        
        # Check for button labels
        self.assertIn('>YTD<', html_content)
        self.assertIn('>12M<', html_content)
        self.assertIn('>5Y<', html_content)
        self.assertIn('>All<', html_content)
    
    def test_dashboard_contains_apply_chart_filters_function(self):
        """Test that the applyChartFilters function is defined in the dashboard."""
        response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check that the applyChartFilters function is defined
        self.assertIn('function applyChartFilters()', html_content)
        
        # Check that it's called after chart updates
        self.assertIn('applyChartFilters();', html_content)
        
        # Check for localStorage interaction
        self.assertIn("localStorage.getItem('chartPeriod')", html_content)
        self.assertIn("localStorage.getItem('chartStartDate')", html_content)
    
    def test_chart_period_functions_exist(self):
        """Test that chart period manipulation functions exist."""
        response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for required functions
        self.assertIn('function setChartPeriod(', html_content)
        self.assertIn('function filterChartByDate(', html_content)
        self.assertIn('function resetChartDate(', html_content)
        
        # Check for localStorage saving
        self.assertIn("localStorage.setItem('chartPeriod'", html_content)
        self.assertIn("localStorage.setItem('chartStartDate'", html_content)
    
    def test_chart_data_api_endpoint_exists(self):
        """Test that the chart data API endpoint exists and returns data."""
        # Mock chart data to avoid actual data generation
        with patch('app.views.main.get_cached_chart_data') as mock_chart_data:
            mock_chart_data.return_value = {
                'dates': ['2024-01-01', '2024-01-02'],
                'portfolio_values': [1000, 1100],
                'voo_values': [500, 550],
                'qqq_values': [400, 440]
            }
            
            response = self.client.get(f'/api/chart-data/{self.portfolio.id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('dates', data)
            self.assertIn('portfolio_values', data)
    
    def test_defensive_programming_in_apply_filters(self):
        """Test that applyChartFilters handles edge cases gracefully."""
        response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for defensive programming
        self.assertIn('if (!originalChartData', html_content)
        self.assertIn('originalChartData.dates.length === 0', html_content)
        self.assertIn('Chart data not ready, skipping filter application', html_content)
    
    def test_activity_logging_for_filter_restoration(self):
        """Test that filter restoration is logged for debugging."""
        response = self.client.get(f'/?portfolio_id={self.portfolio.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for activity logging messages
        self.assertIn('Restored chart period:', html_content)
        self.assertIn('Restored custom chart date:', html_content)
        self.assertIn('No saved chart preferences, showing all data', html_content)


if __name__ == '__main__':
    unittest.main()
