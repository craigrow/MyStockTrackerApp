"""Tests for chart data API endpoint."""
import pytest
from flask import url_for
import json

class TestChartDataAPI:
    """Test chart data API endpoint."""
    
    def test_chart_data_api_endpoint_exists(self, app, client):
        """Test that the chart data API endpoint exists."""
        with app.app_context():
            # Create a test portfolio
            from app.models.portfolio import Portfolio
            from app import db
            
            # Check if test portfolio already exists
            test_portfolio = Portfolio.query.filter_by(name="Test Portfolio").first()
            if not test_portfolio:
                test_portfolio = Portfolio(
                    id="test-portfolio-id",
                    user_id="test-user",
                    name="Test Portfolio",
                    description="Test portfolio for chart API tests"
                )
                db.session.add(test_portfolio)
                db.session.commit()
            
            # Call the chart data API endpoint
            response = client.get(f'/api/chart-data/{test_portfolio.id}')
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Check that the response is JSON
            assert response.content_type == 'application/json'
            
            # Check that the response has the expected structure
            data = response.get_json()
            assert 'dates' in data
            assert 'portfolio_values' in data
            assert 'voo_values' in data
            assert 'qqq_values' in data
    
    def test_chart_data_api_with_empty_portfolio(self, app, client):
        """Test chart data API with an empty portfolio."""
        with app.app_context():
            # Create an empty test portfolio
            from app.models.portfolio import Portfolio
            from app import db
            
            empty_portfolio = Portfolio(
                id="empty-portfolio-id",
                user_id="test-user",
                name="Empty Portfolio",
                description="Empty portfolio for chart API tests"
            )
            db.session.add(empty_portfolio)
            db.session.commit()
            
            # Call the chart data API endpoint
            response = client.get(f'/api/chart-data/{empty_portfolio.id}')
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Check that the response has empty arrays
            data = response.get_json()
            assert len(data['dates']) == 0
            assert len(data['portfolio_values']) == 0
            assert len(data['voo_values']) == 0
            assert len(data['qqq_values']) == 0
    
    def test_progressive_loading_js_exists(self, app, client):
        """Test that the progressive loading JavaScript exists in the dashboard template."""
        with app.app_context():
            # Create a test portfolio to ensure the script block is included
            from app.models.portfolio import Portfolio
            from app import db
            
            # Check if test portfolio already exists
            test_portfolio = Portfolio.query.filter_by(name="Test Portfolio").first()
            if not test_portfolio:
                test_portfolio = Portfolio(
                    id="test-portfolio-id",
                    user_id="test-user",
                    name="Test Portfolio",
                    description="Test portfolio for chart API tests"
                )
                db.session.add(test_portfolio)
                db.session.commit()
            
            # Get the dashboard page with the portfolio_id parameter
            response = client.get(url_for('main.dashboard', portfolio_id=test_portfolio.id))
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Get the HTML content
            html_content = response.get_data(as_text=True)
            
            # Check that chart-related functions exist
            assert "function checkChartProgress(" in html_content
            
            # Check that the function makes an AJAX call to the chart data API
            assert "fetch(`/api/chart-data/" in html_content or "fetch('/api/chart-data/" in html_content