"""Integration tests for dashboard functionality."""
import pytest
from flask import url_for
from bs4 import BeautifulSoup
import re
import json

class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""
    
    def test_dashboard_chart_and_refresh_integration(self, app, client):
        """Test that both chart generation and refresh prices functionality work together."""
        with app.app_context():
            # Create a test portfolio with transactions
            from app.models.portfolio import Portfolio
            from app.models.portfolio import StockTransaction
            from datetime import date, timedelta
            from app import db
            
            # Check if test portfolio already exists
            test_portfolio = Portfolio.query.filter_by(name="Integration Test Portfolio").first()
            if not test_portfolio:
                test_portfolio = Portfolio(
                    id="integration-test-portfolio",
                    user_id="test-user",  # Add user_id to satisfy NOT NULL constraint
                    name="Integration Test Portfolio",
                    description="Integration test portfolio"
                )
                db.session.add(test_portfolio)
                db.session.commit()
            
            # Add some test transactions if none exist
            transactions = StockTransaction.query.filter_by(portfolio_id=test_portfolio.id).all()
            if not transactions:
                today = date.today()
                
                # Add 25 transactions with different tickers (exceeds original 20 threshold)
                for i in range(1, 26):
                    ticker = f"TEST{i}"
                    transaction = StockTransaction(
                        id=f"integration-test-transaction-{i}",
                        portfolio_id=test_portfolio.id,
                        ticker=ticker,
                        transaction_type="BUY",
                        date=today - timedelta(days=30),
                        price_per_share=100.0,
                        shares=1.0,
                        total_value=100.0
                    )
                    db.session.add(transaction)
                
                db.session.commit()
            
            # Get the dashboard page
            response = client.get(url_for('main.dashboard', portfolio_id=test_portfolio.id))
            
            # Check that the response is successful
            assert response.status_code == 200
            
            # Get the HTML content
            html_content = response.get_data(as_text=True)
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check that chart canvas exists
            chart_canvas = soup.find('canvas', id='portfolioChart')
            assert chart_canvas is not None, "Chart canvas should exist"
            
            # Check that chart data is defined in JavaScript
            chart_data_pattern = re.compile(r'const\s+originalChartData\s*=\s*\{[^}]*\}', re.DOTALL)
            chart_data_match = chart_data_pattern.search(html_content)
            assert chart_data_match, "Chart data should be defined in JavaScript"
            
            # Check that updateHoldingsTable function is defined
            update_holdings_pattern = re.compile(r'function\s+updateHoldingsTable\s*\(holdings\)', re.DOTALL)
            update_holdings_match = update_holdings_pattern.search(html_content)
            assert update_holdings_match, "updateHoldingsTable function should be defined"
            
            # Check that refreshPrices function is defined
            refresh_prices_pattern = re.compile(r'function\s+refreshPrices\s*\(\)', re.DOTALL)
            refresh_prices_match = refresh_prices_pattern.search(html_content)
            assert refresh_prices_match, "refreshPrices function should be defined"
            
            # Test the refresh prices API endpoint
            api_response = client.get(f'/api/refresh-all-prices/{test_portfolio.id}')
            assert api_response.status_code == 200
            
            # Check API response structure
            api_data = api_response.get_json()
            assert 'success' in api_data
            assert 'refreshed_count' in api_data
            assert 'total_tickers' in api_data
            assert 'timestamp' in api_data
            
            # Test the refresh holdings API endpoint (which should still return holdings data)
            holdings_response = client.get(f'/api/refresh-holdings/{test_portfolio.id}')
            assert holdings_response.status_code == 200
            
            # Check holdings API response structure
            holdings_data = holdings_response.get_json()
            assert 'success' in holdings_data
            assert 'holdings' in holdings_data
            assert isinstance(holdings_data['holdings'], list)
            
            # Verify that holdings data has the expected structure for updateHoldingsTable
            if holdings_data['holdings']:
                first_holding = holdings_data['holdings'][0]
                required_fields = ['ticker', 'shares', 'current_price', 'market_value', 
                                  'gain_loss', 'gain_loss_percentage', 'portfolio_percentage']
                for field in required_fields:
                    assert field in first_holding, f"Holding should have {field} field"