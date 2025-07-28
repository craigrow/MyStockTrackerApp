"""Tests for dashboard refresh prices functionality."""
import pytest
from flask import url_for
import re

class TestDashboardRefreshPrices:
    """Test dashboard refresh prices functionality."""
    
    def test_update_holdings_table_function_defined(self, app, client):
        """Test that updateHoldingsTable function is properly defined in the dashboard template."""
        with app.app_context():
            # Create a test portfolio
            from app.models.portfolio import Portfolio
            from app import db
            
            # Check if test portfolio already exists
            test_portfolio = Portfolio.query.filter_by(name="Test Portfolio").first()
            if not test_portfolio:
                test_portfolio = Portfolio(
                    id="test-portfolio-id",
                    user_id="test-user",  # Add user_id to satisfy NOT NULL constraint
                    name="Test Portfolio",
                    description="Test portfolio for dashboard tests"
                )
                db.session.add(test_portfolio)
                db.session.commit()
            
            # Get the dashboard page
            response = client.get(url_for('main.dashboard', portfolio_id=test_portfolio.id))
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Get the HTML content
            html_content = response.get_data(as_text=True)
            
            # Check that updateHoldingsTable function is defined
            assert "function updateHoldingsTable(holdings)" in html_content
            
            # Check that the function is inside a script tag
            script_pattern = re.compile(r'<script>.*?function\s+updateHoldingsTable\s*\(holdings\).*?</script>', re.DOTALL)
            assert script_pattern.search(html_content), "updateHoldingsTable function should be inside a script tag"
            
            # Check that the refresh prices button calls a defined function
            assert 'onclick="refreshPrices()"' in html_content
            assert "function refreshPrices()" in html_content
    
    def test_refresh_prices_api_endpoint(self, app, client):
        """Test that the refresh prices API endpoint works correctly."""
        with app.app_context():
            # Create a test portfolio
            from app.models.portfolio import Portfolio
            from app import db
            
            # Check if test portfolio already exists
            test_portfolio = Portfolio.query.filter_by(name="Test Portfolio").first()
            if not test_portfolio:
                test_portfolio = Portfolio(
                    id="test-portfolio-id",
                    user_id="test-user",  # Add user_id to satisfy NOT NULL constraint
                    name="Test Portfolio",
                    description="Test portfolio for dashboard tests"
                )
                db.session.add(test_portfolio)
                db.session.commit()
            
            # Call the refresh prices API endpoint
            response = client.get(f'/api/refresh-all-prices/{test_portfolio.id}')
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Check that the response is JSON
            assert response.content_type == 'application/json'
            
            # Check that the response has the expected structure
            data = response.get_json()
            assert 'success' in data
            assert 'refreshed_count' in data
            assert 'total_tickers' in data
            assert 'timestamp' in data