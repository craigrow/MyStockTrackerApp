import unittest
from app import create_app, db
from app.models.portfolio import Portfolio, StockTransaction
from app.models.price import PriceHistory
from app.views.main import generate_chart_data, get_holdings_with_performance, calculate_etf_performance_for_holding
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from datetime import date, timedelta
import uuid
import os
import pandas as pd

class TestDashboardFixes(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test portfolio
        self.portfolio = Portfolio(
            id=str(uuid.uuid4()),
            name='Test Portfolio',
            description='Test Portfolio Description',
            user_id='test_user'
        )
        db.session.add(self.portfolio)
        
        # Create test transactions
        today = date.today()
        one_month_ago = today - timedelta(days=30)
        
        # Transaction 1: Buy AAPL one month ago
        self.transaction1 = StockTransaction(
            id=str(uuid.uuid4()),
            portfolio_id=self.portfolio.id,
            ticker='AAPL',
            transaction_type='BUY',
            date=one_month_ago,
            price_per_share=150.0,
            shares=10,
            total_value=1500.0
        )
        
        # Transaction 2: Buy MSFT today
        self.transaction2 = StockTransaction(
            id=str(uuid.uuid4()),
            portfolio_id=self.portfolio.id,
            ticker='MSFT',
            transaction_type='BUY',
            date=today,
            price_per_share=300.0,
            shares=5,
            total_value=1500.0
        )
        
        db.session.add(self.transaction1)
        db.session.add(self.transaction2)
        
        # Create test price history
        # AAPL prices
        self.price1 = PriceHistory(
            ticker='AAPL',
            date=one_month_ago,
            close_price=150.0,
            is_intraday=False,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        self.price2 = PriceHistory(
            ticker='AAPL',
            date=today,
            close_price=170.0,
            is_intraday=True,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        # MSFT prices
        self.price3 = PriceHistory(
            ticker='MSFT',
            date=one_month_ago,
            close_price=280.0,
            is_intraday=False,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        self.price4 = PriceHistory(
            ticker='MSFT',
            date=today,
            close_price=300.0,
            is_intraday=True,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        # VOO prices
        self.price5 = PriceHistory(
            ticker='VOO',
            date=one_month_ago,
            close_price=400.0,
            is_intraday=False,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        self.price6 = PriceHistory(
            ticker='VOO',
            date=today,
            close_price=420.0,
            is_intraday=True,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        # QQQ prices
        self.price7 = PriceHistory(
            ticker='QQQ',
            date=one_month_ago,
            close_price=350.0,
            is_intraday=False,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        self.price8 = PriceHistory(
            ticker='QQQ',
            date=today,
            close_price=380.0,
            is_intraday=True,
            price_timestamp=date.today(),
            last_updated=date.today()
        )
        
        db.session.add_all([self.price1, self.price2, self.price3, self.price4, 
                           self.price5, self.price6, self.price7, self.price8])
        
        db.session.commit()
        
        # Initialize services
        self.portfolio_service = PortfolioService()
        self.price_service = PriceService()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_holdings_with_performance(self):
        """Test that get_holdings_with_performance returns correct VOO and QQQ performance values"""
        holdings = get_holdings_with_performance(self.portfolio.id, self.portfolio_service, self.price_service)
        
        # Check that we have the expected holdings
        self.assertEqual(len(holdings), 2)
        
        # Find AAPL holding
        aapl_holding = next((h for h in holdings if h['ticker'] == 'AAPL'), None)
        self.assertIsNotNone(aapl_holding)
        
        # Check that VOO and QQQ performance values are not zero for AAPL (purchased one month ago)
        self.assertNotEqual(aapl_holding['voo_performance'], 0)
        self.assertNotEqual(aapl_holding['qqq_performance'], 0)
        
        # Find MSFT holding
        msft_holding = next((h for h in holdings if h['ticker'] == 'MSFT'), None)
        self.assertIsNotNone(msft_holding)
        
        # For MSFT, we don't check the performance values because it was purchased today
        # and there's no historical performance to calculate
    
    def test_calculate_etf_performance_for_holding(self):
        """Test that calculate_etf_performance_for_holding returns correct values"""
        transactions = self.portfolio_service.get_portfolio_transactions(self.portfolio.id)
        
        # Calculate ETF performance for AAPL
        voo_performance = calculate_etf_performance_for_holding('AAPL', transactions, 'VOO')
        qqq_performance = calculate_etf_performance_for_holding('AAPL', transactions, 'QQQ')
        
        # Check that performance values are calculated correctly
        self.assertNotEqual(voo_performance, 0)
        self.assertNotEqual(qqq_performance, 0)
        
        # Expected VOO performance: (420 - 400) / 400 * 100 = 5%
        self.assertAlmostEqual(voo_performance, 5.0, places=1)
        
        # Expected QQQ performance: (380 - 350) / 350 * 100 = 8.57%
        self.assertAlmostEqual(qqq_performance, 8.57, places=1)
    
    def test_generate_chart_data(self):
        """Test that generate_chart_data returns valid chart data"""
        chart_data = generate_chart_data(self.portfolio.id, self.portfolio_service, self.price_service)
        
        # Check that chart data has the expected structure
        self.assertIn('dates', chart_data)
        self.assertIn('portfolio_values', chart_data)
        self.assertIn('voo_values', chart_data)
        self.assertIn('qqq_values', chart_data)
        
        # Check that arrays are not empty
        self.assertTrue(len(chart_data['dates']) > 0)
        self.assertTrue(len(chart_data['portfolio_values']) > 0)
        self.assertTrue(len(chart_data['voo_values']) > 0)
        self.assertTrue(len(chart_data['qqq_values']) > 0)
        
        # Check that arrays have the same length
        self.assertEqual(len(chart_data['dates']), len(chart_data['portfolio_values']))
        self.assertEqual(len(chart_data['dates']), len(chart_data['voo_values']))
        self.assertEqual(len(chart_data['dates']), len(chart_data['qqq_values']))
        
        # Check that portfolio values are not all zero
        self.assertTrue(any(val > 0 for val in chart_data['portfolio_values']))
        
        # Check that the last portfolio value is correct (AAPL: 10 shares * 170 + MSFT: 5 shares * 300 = 3200)
        self.assertAlmostEqual(chart_data['portfolio_values'][-1], 3200, delta=100)
    
    def test_generate_chart_data_with_missing_prices(self):
        """Test that generate_chart_data handles missing prices gracefully"""
        # Delete some price history to simulate missing data
        PriceHistory.query.filter_by(ticker='AAPL', date=date.today()).delete()
        db.session.commit()
        
        chart_data = generate_chart_data(self.portfolio.id, self.portfolio_service, self.price_service)
        
        # Check that chart data has the expected structure
        self.assertIn('dates', chart_data)
        self.assertIn('portfolio_values', chart_data)
        self.assertIn('voo_values', chart_data)
        self.assertIn('qqq_values', chart_data)
        
        # Check that arrays are not empty
        self.assertTrue(len(chart_data['dates']) > 0)
        self.assertTrue(len(chart_data['portfolio_values']) > 0)
        self.assertTrue(len(chart_data['voo_values']) > 0)
        self.assertTrue(len(chart_data['qqq_values']) > 0)
        
        # Check that arrays have the same length
        self.assertEqual(len(chart_data['dates']), len(chart_data['portfolio_values']))
        self.assertEqual(len(chart_data['dates']), len(chart_data['voo_values']))
        self.assertEqual(len(chart_data['dates']), len(chart_data['qqq_values']))

if __name__ == '__main__':
    unittest.main()
