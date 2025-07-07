"""
Test suite for Portfolio Holdings Table Improvements
Tests the enhanced holdings table with ETF performance, sorting, and highlighting features.
"""

import pytest
from datetime import date, timedelta, datetime
from app import create_app, db
from app.models.portfolio import Portfolio, StockTransaction
from app.models.price import PriceHistory
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.views.main import get_holdings_with_performance, calculate_etf_performance_for_holding
from tests.utils.factories import PortfolioFactory, TransactionFactory


class TestHoldingsTableImprovements:
    """Test enhanced holdings table functionality"""
    
    def _create_price_history(self, ticker, price_date, price):
        """Helper method to create price history records"""
        price_record = PriceHistory(
            ticker=ticker,
            date=price_date,
            close_price=price,
            is_intraday=False,
            price_timestamp=datetime.now(),
            last_updated=datetime.now()
        )
        db.session.add(price_record)
        db.session.commit()
        return price_record
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def portfolio_service(self, app):
        return PortfolioService()
    
    @pytest.fixture
    def price_service(self, app):
        return PriceService()
    
    def test_holdings_include_etf_performance_data(self, app, portfolio_service, price_service):
        """Test that holdings data includes VOO and QQQ performance calculations"""
        with app.app_context():
            # Create test portfolio and transactions
            portfolio = PortfolioFactory.create_simple(name="Test Portfolio")
            
            # Create transactions with known dates
            purchase_date = date(2024, 1, 15)
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10, 150.0, purchase_date)
            
            # Create price history for AAPL, VOO, and QQQ
            self._create_price_history("AAPL", purchase_date, 150.0)
            self._create_price_history("AAPL", date.today(), 180.0)
            self._create_price_history("VOO", purchase_date, 400.0)
            self._create_price_history("VOO", date.today(), 440.0)
            self._create_price_history("QQQ", purchase_date, 350.0)
            self._create_price_history("QQQ", date.today(), 385.0)
            
            # Get holdings with performance
            holdings = get_holdings_with_performance(portfolio.id, portfolio_service, price_service, use_stale=True)
            
            assert len(holdings) == 1
            holding = holdings[0]
            
            # Verify basic holding data
            assert holding['ticker'] == 'AAPL'
            assert holding['shares'] == 10
            assert holding['current_price'] == 180.0
            assert holding['market_value'] == 1800.0
            
            # Verify ETF performance calculations exist
            assert 'voo_performance' in holding
            assert 'qqq_performance' in holding
            assert 'portfolio_percentage' in holding
            
            # VOO performance: (440 - 400) / 400 * 100 = 10%
            assert abs(holding['voo_performance'] - 10.0) < 0.01
            
            # QQQ performance: (385 - 350) / 350 * 100 = 10%
            assert abs(holding['qqq_performance'] - 10.0) < 0.01
            
            # Portfolio percentage should be 100% for single holding
            assert abs(holding['portfolio_percentage'] - 100.0) < 0.01
    
    def test_dashboard_template_includes_new_columns(self, app, client):
        """Test that dashboard template includes new sortable columns"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Template Test Portfolio")
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10, 150.0, date.today())
            
            # Mock price data
            self._create_price_history("AAPL", date.today(), 160.0)
            self._create_price_history("VOO", date.today(), 400.0)
            self._create_price_history("QQQ", date.today(), 350.0)
            
            response = client.get(f'/dashboard?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            html_content = response.get_data(as_text=True)
            
            # Check for new column headers
            assert 'Gain/Loss %' in html_content
            assert 'VOO Performance' in html_content
            assert 'QQQ Performance' in html_content
            
            # Check for sortable functionality
            assert 'class="sortable"' in html_content
            assert 'data-column="voo_performance"' in html_content
            assert 'data-column="qqq_performance"' in html_content
            
            # Check for sort icons
            assert 'fas fa-sort' in html_content
    
    def test_etf_performance_calculation_works(self, app):
        """Test that ETF performance calculation works with real or cached data"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="ETF Performance Portfolio")
            
            # Create transaction
            purchase_date = date(2024, 1, 15)
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10, 150.0, purchase_date)
            
            transactions = StockTransaction.query.filter_by(
                portfolio_id=portfolio.id, 
                ticker="AAPL"
            ).all()
            
            # ETF performance calculation should work (either from cache or API)
            voo_performance = calculate_etf_performance_for_holding("AAPL", transactions, "VOO")
            qqq_performance = calculate_etf_performance_for_holding("AAPL", transactions, "QQQ")
            
            # Should return numeric values (not necessarily 0)
            assert isinstance(voo_performance, (int, float))
            assert isinstance(qqq_performance, (int, float))
    
    def test_javascript_sorting_functions_present(self, app, client):
        """Test that JavaScript sorting functions are included in template"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="JS Test Portfolio")
            
            response = client.get(f'/dashboard?portfolio_id={portfolio.id}')
            html_content = response.get_data(as_text=True)
            
            # Check for JavaScript functions
            assert 'function sortTable(' in html_content
            assert 'function formatNumber(' in html_content
            assert 'function highlightTopHoldings(' in html_content
            assert 'function updateSortIndicators(' in html_content
            assert 'currentSortColumn' in html_content
            assert 'currentSortDirection' in html_content


class TestETFPerformanceCalculation:
    """Test ETF performance calculation logic specifically"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def _create_price_history(self, ticker, price_date, price):
        """Helper method to create price history records"""
        price_record = PriceHistory(
            ticker=ticker,
            date=price_date,
            close_price=price,
            is_intraday=False,
            price_timestamp=datetime.now(),
            last_updated=datetime.now()
        )
        db.session.add(price_record)
        db.session.commit()
        return price_record
    
    def test_single_purchase_etf_performance(self, app):
        """Test ETF performance calculation for single purchase"""
        with app.app_context():
            portfolio = PortfolioFactory.create_simple(name="Single Purchase")
            
            purchase_date = date(2024, 1, 15)
            TransactionFactory.create_buy(portfolio.id, "AAPL", 10, 150.0, purchase_date)
            
            # VOO: 400 -> 440 = 10% gain
            self._create_price_history("VOO", purchase_date, 400.0)
            self._create_price_history("VOO", date.today(), 440.0)
            
            transactions = StockTransaction.query.filter_by(
                portfolio_id=portfolio.id,
                ticker="AAPL"
            ).all()
            
            performance = calculate_etf_performance_for_holding("AAPL", transactions, "VOO")
            assert abs(performance - 10.0) < 0.01


if __name__ == '__main__':
    pytest.main([__file__])