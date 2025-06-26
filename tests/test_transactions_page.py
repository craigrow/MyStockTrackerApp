import pytest
from datetime import date, datetime
from app import create_app, db
from app.models.portfolio import Portfolio
from app.models.portfolio import StockTransaction
from app.models.price import PriceHistory
from app.services.portfolio_service import PortfolioService


@pytest.mark.ui
@pytest.mark.slow
class TestTransactionsPage:
    """Test transactions page functionality and performance calculations"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def sample_portfolio(self, app):
        """Create a sample portfolio with transactions"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(
                id='test-portfolio',
                name='Test Portfolio',
                description='Test portfolio for transactions',
                user_id='test-user'
            )
            db.session.add(portfolio)
            
            # Add transactions
            transaction1 = StockTransaction(
                id='trans-1',
                portfolio_id='test-portfolio',
                ticker='CPNG',
                transaction_type='BUY',
                date=date(2025, 6, 17),
                price_per_share=23.81,
                shares=42.0504,
                total_value=1000.92
            )
            
            transaction2 = StockTransaction(
                id='trans-2',
                portfolio_id='test-portfolio',
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 5, 15),
                price_per_share=180.00,
                shares=10.0,
                total_value=1800.00
            )
            
            db.session.add(transaction1)
            db.session.add(transaction2)
            
            # Add price data
            prices = [
                # CPNG prices
                PriceHistory(ticker='CPNG', date=date(2025, 6, 17), close_price=23.81, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='CPNG', date=date.today(), close_price=24.35, is_intraday=True, price_timestamp=datetime.now(), last_updated=datetime.now()),
                
                # AAPL prices
                PriceHistory(ticker='AAPL', date=date(2025, 5, 15), close_price=180.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='AAPL', date=date.today(), close_price=220.50, is_intraday=True, price_timestamp=datetime.now(), last_updated=datetime.now()),
                
                # VOO prices
                PriceHistory(ticker='VOO', date=date(2025, 6, 17), close_price=549.35, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='VOO', date=date(2025, 5, 15), close_price=540.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='VOO', date=date.today(), close_price=559.95, is_intraday=True, price_timestamp=datetime.now(), last_updated=datetime.now()),
                
                # QQQ prices
                PriceHistory(ticker='QQQ', date=date(2025, 6, 17), close_price=450.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='QQQ', date=date(2025, 5, 15), close_price=440.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='QQQ', date=date.today(), close_price=465.00, is_intraday=True, price_timestamp=datetime.now(), last_updated=datetime.now()),
            ]
            
            for price in prices:
                db.session.add(price)
            
            db.session.commit()
            return 'test-portfolio'  # Return ID string instead of object
    
    def test_transactions_page_loads(self, client, sample_portfolio):
        """Test that transactions page loads successfully"""
        response = client.get(f'/portfolio/transactions?portfolio_id={sample_portfolio}')
        assert response.status_code == 200
        assert b'Stock Transactions' in response.data
        assert b'CPNG' in response.data
        assert b'AAPL' in response.data
    
    def test_transactions_page_no_portfolio(self, client):
        """Test transactions page with no portfolio"""
        response = client.get('/portfolio/transactions')
        assert response.status_code == 200
        assert b'No Portfolios Found' in response.data or b'Stock Transactions' in response.data
    
    def test_current_price_api_integration(self, client, sample_portfolio):
        """Test current price API returns correct data"""
        response = client.get('/api/current-price/CPNG')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['ticker'] == 'CPNG'
        assert data['price'] == 24.35
        assert data['success'] is True
    
    def test_etf_performance_cpng_example(self, client, sample_portfolio):
        """Test the specific CPNG vs VOO calculation example"""
        # Test VOO performance from CPNG purchase date
        response = client.get('/api/etf-performance/VOO/2025-06-17')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['ticker'] == 'VOO'
        assert data['purchase_date'] == '2025-06-17'
        assert data['purchase_price'] == 549.35
        assert data['current_price'] == 559.95
        
        # Expected VOO performance: (559.95 - 549.35) / 549.35 * 100 = 1.9289%
        expected_voo_performance = ((559.95 - 549.35) / 549.35) * 100
        assert abs(data['performance'] - expected_voo_performance) < 0.01
        
        # CPNG performance: (24.35 - 23.81) / 23.81 * 100 = 2.2689%
        cpng_performance = ((24.35 - 23.81) / 23.81) * 100
        
        # vs VOO should be: 2.2689% - 1.9289% = 0.34%
        expected_vs_voo = cpng_performance - expected_voo_performance
        assert abs(expected_vs_voo - 0.34) < 0.01
    
    def test_etf_performance_aapl_example(self, client, sample_portfolio):
        """Test ETF performance calculation for AAPL transaction"""
        # Test VOO performance from AAPL purchase date
        response = client.get('/api/etf-performance/VOO/2025-05-15')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['purchase_price'] == 540.00
        assert data['current_price'] == 559.95
        
        # VOO performance: (559.95 - 540.00) / 540.00 * 100 = 3.6944%
        expected_voo_performance = ((559.95 - 540.00) / 540.00) * 100
        assert abs(data['performance'] - expected_voo_performance) < 0.01
        
        # AAPL performance: (220.50 - 180.00) / 180.00 * 100 = 22.5%
        aapl_performance = ((220.50 - 180.00) / 180.00) * 100
        
        # vs VOO should be: 22.5% - 3.6944% = 18.8056%
        expected_vs_voo = aapl_performance - expected_voo_performance
        assert abs(expected_vs_voo - 18.81) < 0.01
    
    def test_transactions_table_structure(self, client, sample_portfolio):
        """Test that transactions table has correct structure"""
        response = client.get(f'/portfolio/transactions?portfolio_id={sample_portfolio}')
        assert response.status_code == 200
        
        # Check for required table headers
        required_headers = [
            b'Date', b'Ticker', b'Type', b'Shares',
            b'Purchase Price', b'Current Price', b'Cost Basis',
            b'Current Value', b'$ Gain/Loss', b'% Gain',
            b'vs QQQ', b'vs VOO', b'Actions'
        ]
        
        for header in required_headers:
            assert header in response.data
    
    def test_transaction_data_attributes(self, client, sample_portfolio):
        """Test that transaction rows have correct data attributes"""
        response = client.get(f'/portfolio/transactions?portfolio_id={sample_portfolio}')
        assert response.status_code == 200
        
        # Check for data attributes needed for JavaScript calculations
        assert b'data-purchase-date="2025-06-17"' in response.data
        assert b'data-purchase-date="2025-05-15"' in response.data
        assert b'data-ticker="CPNG"' in response.data
        assert b'data-ticker="AAPL"' in response.data
    
    def test_quick_filters_present(self, client, sample_portfolio):
        """Test that quick filter buttons are present"""
        response = client.get(f'/portfolio/transactions?portfolio_id={sample_portfolio}')
        assert response.status_code == 200
        
        assert b'Quick Filters' in response.data
        assert b'onclick="setFilter(\'all\')"' in response.data
        assert b'onclick="setFilter(\'buy\')"' in response.data
        assert b'onclick="setFilter(\'sell\')"' in response.data
    
    def test_sortable_columns(self, client, sample_portfolio):
        """Test that columns are sortable"""
        response = client.get(f'/portfolio/transactions?portfolio_id={sample_portfolio}')
        assert response.status_code == 200
        
        # Check for sortable column headers
        assert b'onclick="sortTable(' in response.data
        assert b'cursor: pointer' in response.data
        assert b'fas fa-sort' in response.data
    
    def test_portfolio_service_integration(self, app, sample_portfolio):
        """Test portfolio service returns correct transaction data"""
        with app.app_context():
            portfolio_service = PortfolioService()
            transactions = portfolio_service.get_portfolio_transactions(sample_portfolio)
            
            assert len(transactions) == 2
            
            # Check CPNG transaction
            cpng_transaction = next(t for t in transactions if t.ticker == 'CPNG')
            assert cpng_transaction.price_per_share == 23.81
            assert cpng_transaction.shares == 42.0504
            assert cpng_transaction.total_value == 1000.92
            assert cpng_transaction.date == date(2025, 6, 17)
            
            # Check AAPL transaction
            aapl_transaction = next(t for t in transactions if t.ticker == 'AAPL')
            assert aapl_transaction.price_per_share == 180.00
            assert aapl_transaction.shares == 10.0
            assert aapl_transaction.total_value == 1800.00
            assert aapl_transaction.date == date(2025, 5, 15)