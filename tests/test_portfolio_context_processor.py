"""
Tests for portfolio context processor functionality.

This module tests the global portfolio context processor that provides
portfolio data to all templates and handles persistent portfolio selection.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, render_template_string
from app import create_app, db
from app.models.portfolio import Portfolio
from app.context_processors import portfolio_context


class TestPortfolioContextProcessor(unittest.TestCase):
    """Test portfolio context processor functionality."""
    
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
    
    def test_context_processor_provides_portfolios_list(self):
        """Test that context processor provides portfolios list to templates."""
        with self.app.test_request_context():
            context = portfolio_context()
            
            self.assertIn('portfolios', context)
            self.assertEqual(len(context['portfolios']), 2)
            self.assertEqual(context['portfolios'][0].name, 'Test Portfolio 1')
            self.assertEqual(context['portfolios'][1].name, 'Test Portfolio 2')
    
    def test_context_processor_determines_current_portfolio_from_url(self):
        """Test that context processor gets current_portfolio from URL parameter."""
        with self.app.test_request_context(f'/?portfolio_id={self.portfolio2.id}'):
            context = portfolio_context()
            
            self.assertIn('current_portfolio', context)
            self.assertEqual(context['current_portfolio'].id, self.portfolio2.id)
            self.assertEqual(context['current_portfolio'].name, 'Test Portfolio 2')
    
    def test_context_processor_defaults_to_first_portfolio(self):
        """Test that context processor defaults to first portfolio when no selection."""
        with self.app.test_request_context('/'):
            context = portfolio_context()
            
            self.assertIn('current_portfolio', context)
            self.assertEqual(context['current_portfolio'].id, self.portfolio1.id)
            self.assertEqual(context['current_portfolio'].name, 'Test Portfolio 1')
    
    def test_context_processor_handles_invalid_portfolio_id(self):
        """Test that context processor handles invalid portfolio_id gracefully."""
        with self.app.test_request_context('/?portfolio_id=invalid-id'):
            context = portfolio_context()
            
            self.assertIn('current_portfolio', context)
            # Should fall back to first portfolio
            self.assertEqual(context['current_portfolio'].id, self.portfolio1.id)
    
    def test_context_processor_handles_empty_portfolio_list(self):
        """Test that context processor handles empty portfolio list gracefully."""
        # Remove all portfolios
        db.session.query(Portfolio).delete()
        db.session.commit()
        
        with self.app.test_request_context('/'):
            context = portfolio_context()
            
            self.assertIn('portfolios', context)
            self.assertIn('current_portfolio', context)
            self.assertEqual(len(context['portfolios']), 0)
            self.assertIsNone(context['current_portfolio'])
    
    def test_context_processor_registered_with_app(self):
        """Test that context processor is registered with Flask app."""
        # Check that the context processor is registered
        self.assertIn(portfolio_context, self.app.template_context_processors[None])
    
    def test_context_processor_available_in_templates(self):
        """Test that context processor data is available in templates."""
        template = """
        {% if portfolios %}
            <div>{{ portfolios|length }} portfolios</div>
            {% if current_portfolio %}
                <div>Current: {{ current_portfolio.name }}</div>
            {% endif %}
        {% endif %}
        """
        
        with self.app.test_request_context(f'/?portfolio_id={self.portfolio2.id}'):
            rendered = render_template_string(template)
            
            self.assertIn('2 portfolios', rendered)
            self.assertIn('Current: Test Portfolio 2', rendered)
    
    def test_context_processor_maintains_backward_compatibility(self):
        """Test that existing URL patterns still work."""
        # Test dashboard URL with portfolio_id
        response = self.client.get(f'/?portfolio_id={self.portfolio2.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test that the correct portfolio is selected
        html_content = response.get_data(as_text=True)
        self.assertIn('Test Portfolio 2', html_content)


if __name__ == '__main__':
    unittest.main()
