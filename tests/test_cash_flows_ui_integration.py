import pytest
from datetime import date
from app.models.portfolio import Portfolio, StockTransaction
from app import db


@pytest.mark.integration
@pytest.mark.database
class TestCashFlowsUIIntegration:
    def test_cash_flows_page_renders_with_data(self, app, client):
        """Test that cash flows page renders correctly with transaction data"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Test cash flows page
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            # Check for key elements
            html = response.get_data(as_text=True)
            assert 'Cash Flows Analysis' in html
            assert 'Total Invested' in html
            assert 'IRR (Annual)' in html
            assert 'Cash Flow History' in html
            assert 'DEPOSIT' in html
            assert 'PURCHASE' in html
            assert '$1,500.00' in html

    def test_cash_flows_page_empty_portfolio(self, app, client):
        """Test cash flows page with empty portfolio"""
        with app.app_context():
            # Create empty portfolio
            portfolio = Portfolio(name='Empty Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Test cash flows page
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            # Check for empty state
            html = response.get_data(as_text=True)
            assert 'Cash Flows Analysis' in html
            assert 'No cash flows found' in html

    def test_navigation_includes_cash_flows_tab(self, app, client):
        """Test that navigation includes Cash Flows tab"""
        with app.app_context():
            # Test dashboard page
            response = client.get('/')
            assert response.status_code == 200
            
            # Check for Cash Flows navigation
            html = response.get_data(as_text=True)
            assert 'Cash Flows' in html
            assert '/cash-flows' in html
            assert 'fa-exchange-alt' in html

    def test_dashboard_includes_cash_flows_button(self, app, client):
        """Test that dashboard includes View Cash Flows button"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Test dashboard with portfolio
            response = client.get(f'/?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            # Check for Cash Flows button
            html = response.get_data(as_text=True)
            assert 'View Cash Flows' in html
            assert 'fa-exchange-alt' in html

    def test_cash_flows_breadcrumb_navigation(self, app, client):
        """Test breadcrumb navigation on cash flows page"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Test cash flows page
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            # Check for breadcrumb
            html = response.get_data(as_text=True)
            assert 'breadcrumb' in html
            assert 'Dashboard' in html
            assert 'Cash Flows' in html