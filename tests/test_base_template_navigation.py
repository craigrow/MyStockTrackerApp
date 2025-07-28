"""
Tests for base template navigation functionality.

This module tests the updated base template with portfolio selector
in the navbar and hamburger menu navigation.
"""

import unittest
from flask import render_template_string
from app import create_app, db
from app.models.portfolio import Portfolio


class TestBaseTemplateNavigation(unittest.TestCase):
    """Test base template navigation functionality."""
    
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
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_base_template_renders_portfolio_selector_in_navbar(self):
        """Test that base template renders portfolio selector in navbar."""
        response = self.client.get(f'/?portfolio_id={self.portfolio1.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for portfolio selector in navbar
        self.assertIn('id="portfolioSelector"', html_content)
        self.assertIn('fas fa-briefcase', html_content)
        self.assertIn('Test Portfolio 1', html_content)
    
    def test_portfolio_selector_displays_current_portfolio_name(self):
        """Test that portfolio selector displays current portfolio name correctly."""
        response = self.client.get(f'/?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check that current portfolio name is displayed
        self.assertIn('id="currentPortfolioName"', html_content)
        self.assertIn('Test Portfolio 2', html_content)
    
    def test_portfolio_dropdown_contains_all_portfolios(self):
        """Test that portfolio dropdown contains all available portfolios."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for portfolio dropdown
        self.assertIn('id="portfolioDropdown"', html_content)
        self.assertIn('Test Portfolio 1', html_content)
        self.assertIn('Test Portfolio 2', html_content)
        self.assertIn('Create New Portfolio', html_content)
    
    def test_hamburger_menu_contains_navigation_items(self):
        """Test that hamburger menu contains all navigation items."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for hamburger menu
        self.assertIn('id="navigationMenu"', html_content)
        self.assertIn('fas fa-bars', html_content)
        
        # Check for navigation items in dropdown
        self.assertIn('fas fa-tachometer-alt', html_content)  # Dashboard
        self.assertIn('fas fa-exchange-alt', html_content)    # Transactions
        self.assertIn('fas fa-coins', html_content)          # Dividends
        self.assertIn('fas fa-chart-line', html_content)     # Cash Flows
        self.assertIn('fas fa-desktop', html_content)        # Monitoring
    
    def test_navigation_items_have_correct_onclick_handlers(self):
        """Test that navigation items have portfolio-aware onclick handlers."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for navigateWithPortfolio function calls
        self.assertIn('navigateWithPortfolio', html_content)
        self.assertIn('onclick="navigateWithPortfolio', html_content)
    
    def test_portfolio_selector_has_onclick_handlers(self):
        """Test that portfolio selector items have correct onclick handlers."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for selectPortfolio function calls
        self.assertIn('selectPortfolio', html_content)
        self.assertIn('onclick="selectPortfolio', html_content)
    
    def test_template_handles_missing_portfolio_data_gracefully(self):
        """Test that template handles missing portfolio data gracefully."""
        # Remove all portfolios
        db.session.query(Portfolio).delete()
        db.session.commit()
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Should still render without errors
        self.assertIn('Select Portfolio', html_content)
        self.assertIn('Create New Portfolio', html_content)
    
    def test_base_template_includes_portfolio_persistence_javascript(self):
        """Test that base template includes portfolio persistence JavaScript."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for JavaScript functions
        self.assertIn('getSelectedPortfolioId', html_content)
        self.assertIn('selectPortfolio', html_content)
        self.assertIn('navigateWithPortfolio', html_content)
        self.assertIn('localStorage', html_content)
    
    def test_navigation_preserves_bootstrap_styling(self):
        """Test that navigation maintains Bootstrap 5 styling."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        
        # Check for Bootstrap classes
        self.assertIn('navbar navbar-expand-lg navbar-dark bg-dark', html_content)
        self.assertIn('btn btn-outline-light dropdown-toggle', html_content)
        self.assertIn('dropdown-menu', html_content)
        self.assertIn('dropdown-item', html_content)


if __name__ == '__main__':
    unittest.main()
