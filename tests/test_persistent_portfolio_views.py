"""
Tests for persistent portfolio view integration.

This module tests that all views properly integrate with the portfolio
context processor and handle persistent portfolio selection.
"""

import unittest
from app import create_app, db
from app.models.portfolio import Portfolio
from app.models.portfolio import StockTransaction
from datetime import date, timedelta


class TestPersistentPortfolioViews(unittest.TestCase):
    """Test persistent portfolio view integration."""
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test portfolios
        self.portfolio1 = Portfolio(
            name='Test Portfolio 1',
            description='First test portfolio',
            user_id='test_user'
        )
        self.portfolio2 = Portfolio(
            name='Test Portfolio 2',
            description='Second test portfolio',
            user_id='test_user'
        )
        db.session.add(self.portfolio1)
        db.session.add(self.portfolio2)
        db.session.commit()
        
        # Add test transaction
        transaction = StockTransaction(
            portfolio_id=self.portfolio1.id,
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
    
    def test_dashboard_view_uses_context_processor_data(self):
        """Test that dashboard view uses context processor for portfolio data."""
        response = self.client.get(f'/?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Should show correct portfolio from context processor
        self.assertIn('Test Portfolio 2', html_content)
        self.assertIn('portfolioSelector', html_content)
    
    def test_transactions_view_respects_persistent_portfolio(self):
        """Test that transactions view respects persistent portfolio selection."""
        response = self.client.get(f'/portfolio/transactions?portfolio_id={self.portfolio1.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Should show portfolio selector with correct portfolio
        self.assertIn('Test Portfolio 1', html_content)
        self.assertIn('portfolioSelector', html_content)
    
    def test_cash_flows_view_maintains_portfolio_context(self):
        """Test that cash flows view maintains portfolio context."""
        response = self.client.get(f'/cash-flows?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Should show portfolio selector with correct portfolio
        self.assertIn('Test Portfolio 2', html_content)
        self.assertIn('portfolioSelector', html_content)
    
    def test_direct_urls_with_portfolio_id_still_work(self):
        """Test that direct URLs with portfolio_id parameter still work."""
        # Test dashboard
        response = self.client.get(f'/?portfolio_id={self.portfolio1.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test transactions
        response = self.client.get(f'/portfolio/transactions?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test cash flows
        response = self.client.get(f'/cash-flows?portfolio_id={self.portfolio1.id}')
        self.assertEqual(response.status_code, 200)
    
    def test_views_handle_missing_portfolio_id_gracefully(self):
        """Test that views handle missing portfolio_id gracefully."""
        # Should default to first portfolio
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        self.assertIn('Test Portfolio 1', html_content)  # First portfolio
    
    def test_views_handle_invalid_portfolio_id_gracefully(self):
        """Test that views handle invalid portfolio_id gracefully."""
        response = self.client.get('/?portfolio_id=invalid-id')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        # Should fall back to first portfolio
        self.assertIn('Test Portfolio 1', html_content)
    
    def test_all_views_have_consistent_navigation(self):
        """Test that all views have consistent navigation structure."""
        views_to_test = [
            '/',
            '/portfolio/transactions',
            '/cash-flows'
        ]
        
        for view_url in views_to_test:
            with self.subTest(view=view_url):
                response = self.client.get(f'{view_url}?portfolio_id={self.portfolio1.id}')
                self.assertEqual(response.status_code, 200)
                
                html_content = response.get_data(as_text=True)
                
                # Check for consistent navigation elements
                self.assertIn('portfolioSelector', html_content)
                self.assertIn('navigationMenu', html_content)
                self.assertIn('fas fa-bars', html_content)
                self.assertIn('navigateWithPortfolio', html_content)
    
    def test_views_no_longer_pass_redundant_portfolio_data(self):
        """Test that views rely on context processor instead of explicit data passing."""
        # This test verifies that the view functions have been cleaned up
        # to not pass portfolios and current_portfolio explicitly since
        # they're now provided by the context processor
        
        # We'll test this by checking that the templates still work
        # even if the view doesn't pass the data explicitly
        response = self.client.get(f'/?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Portfolio data should still be available via context processor
        self.assertIn('Test Portfolio 2', html_content)
        self.assertIn('portfolioDropdown', html_content)


if __name__ == '__main__':
    unittest.main()
