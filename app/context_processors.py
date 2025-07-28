"""
Context processors for making data available to all templates.

This module provides context processors that inject common data
into all template contexts, particularly portfolio-related data.
"""

from flask import request
from app.services.portfolio_service import PortfolioService


def portfolio_context():
    """
    Context processor that provides portfolio data to all templates.
    
    Returns:
        dict: Context containing 'portfolios' and 'current_portfolio'
    """
    portfolio_service = PortfolioService()
    
    # Get all portfolios
    portfolios = portfolio_service.get_all_portfolios()
    
    # Determine current portfolio
    current_portfolio = None
    portfolio_id = request.args.get('portfolio_id')
    
    if portfolio_id:
        # Try to get portfolio from URL parameter
        current_portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    # Fall back to first portfolio if no valid selection
    if not current_portfolio and portfolios:
        current_portfolio = portfolios[0]
    
    return {
        'portfolios': portfolios,
        'current_portfolio': current_portfolio
    }
