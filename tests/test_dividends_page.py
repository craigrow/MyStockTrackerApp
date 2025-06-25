"""
Test suite for dividends page functionality.
"""

import pytest
from flask import url_for
from app import create_app, db
from app.models.portfolio import Portfolio, Dividend
from datetime import date


class TestDividendsPage:
    """Test dividends page functionality."""

    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def portfolio_with_dividends(self, app):
        """Create portfolio with sample dividends."""
        with app.app_context():
            portfolio = Portfolio(name="Test Portfolio", user_id="test-user")
            db.session.add(portfolio)
            db.session.commit()
            
            dividends = [
                Dividend(
                    portfolio_id=portfolio.id,
                    ticker="AAPL",
                    payment_date=date(2024, 12, 15),
                    total_amount=25.50
                ),
                Dividend(
                    portfolio_id=portfolio.id,
                    ticker="MSFT",
                    payment_date=date(2024, 11, 20),
                    total_amount=18.75
                ),
                Dividend(
                    portfolio_id=portfolio.id,
                    ticker="AAPL",
                    payment_date=date(2024, 9, 15),
                    total_amount=24.00
                )
            ]
            
            for dividend in dividends:
                db.session.add(dividend)
            
            db.session.commit()
            db.session.refresh(portfolio)
            return portfolio

    def test_dividends_page_loads(self, client, app):
        """Test dividends page loads successfully."""
        with app.app_context():
            portfolio = Portfolio(name="Empty Portfolio", user_id="test-user")
            db.session.add(portfolio)
            db.session.commit()
            
            response = client.get(f'/portfolio/dividends?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            assert b'Dividends' in response.data

    def test_dividends_table_structure(self, client, portfolio_with_dividends):
        """Test dividends table has correct structure."""
        response = client.get(f'/portfolio/dividends?portfolio_id={portfolio_with_dividends.id}')
        
        assert response.status_code == 200
        assert b'<table' in response.data
        assert b'Date' in response.data
        assert b'Ticker' in response.data
        assert b'Amount' in response.data

    def test_dividends_data_display(self, client, portfolio_with_dividends):
        """Test dividends data is displayed correctly."""
        response = client.get(f'/portfolio/dividends?portfolio_id={portfolio_with_dividends.id}')
        response_text = response.data.decode('utf-8')
        
        # Check dividend data appears
        assert 'AAPL' in response_text
        assert 'MSFT' in response_text
        assert '$25.50' in response_text
        assert '$18.75' in response_text
        assert '$24.00' in response_text
        assert '2024-12-15' in response_text
        assert '2024-11-20' in response_text
        assert '2024-09-15' in response_text

    def test_empty_dividends_state(self, client, app):
        """Test empty state when no dividends exist."""
        with app.app_context():
            portfolio = Portfolio(name="Empty Portfolio", user_id="test-user")
            db.session.add(portfolio)
            db.session.commit()
            
            response = client.get(f'/portfolio/dividends?portfolio_id={portfolio.id}')
            response_text = response.data.decode('utf-8')
            
            assert 'No dividends recorded yet' in response_text
            assert 'Add your first dividend' in response_text

    def test_dividends_sorted_by_date(self, client, portfolio_with_dividends):
        """Test dividends are sorted by date (most recent first)."""
        response = client.get(f'/portfolio/dividends?portfolio_id={portfolio_with_dividends.id}')
        response_text = response.data.decode('utf-8')
        
        # Most recent date should appear first
        dec_pos = response_text.find('2024-12-15')
        nov_pos = response_text.find('2024-11-20')
        sep_pos = response_text.find('2024-09-15')
        
        assert dec_pos < nov_pos < sep_pos