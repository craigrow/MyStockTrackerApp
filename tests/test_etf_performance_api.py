import pytest
from datetime import date, datetime
from app import create_app, db
from app.models.price import PriceHistory
from app.views.main import get_historical_price


class TestETFPerformanceAPI:
    """Test ETF performance calculations and API endpoints"""
    
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
    
    def test_get_historical_price_cached(self, app):
        """Test getting historical price from cache"""
        with app.app_context():
            # Clear any existing data first
            db.session.query(PriceHistory).filter_by(ticker='VOO', date=date(2025, 6, 17)).delete()
            db.session.commit()
            
            # Add cached price
            price_record = PriceHistory(
                ticker='VOO',
                date=date(2025, 6, 17),
                close_price=549.35,
                is_intraday=False,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            db.session.add(price_record)
            db.session.commit()
            
            # Test retrieval
            price = get_historical_price('VOO', date(2025, 6, 17))
            assert price == 549.35
    
    def test_get_historical_price_missing(self, app):
        """Test getting historical price when not cached"""
        with app.app_context():
            # Should return None for missing price
            price = get_historical_price('NONEXISTENT', date(2025, 1, 1))
            assert price is None
    
    def test_current_price_api_endpoint(self, client, app):
        """Test current price API endpoint"""
        with app.app_context():
            # Add cached price
            price_record = PriceHistory(
                ticker='AAPL',
                date=date.today(),
                close_price=220.50,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            db.session.add(price_record)
            db.session.commit()
            
            response = client.get('/api/current-price/AAPL')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['ticker'] == 'AAPL'
            assert data['success'] is True
            assert data['price'] == 220.50
    
    def test_etf_performance_api_endpoint(self, client, app):
        """Test ETF performance calculation API endpoint"""
        with app.app_context():
            # Add historical price (purchase date)
            purchase_price = PriceHistory(
                ticker='VOO',
                date=date(2025, 6, 17),
                close_price=549.35,
                is_intraday=False,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            db.session.add(purchase_price)
            
            # Add current price
            current_price = PriceHistory(
                ticker='VOO',
                date=date.today(),
                close_price=559.95,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            db.session.add(current_price)
            db.session.commit()
            
            response = client.get('/api/etf-performance/VOO/2025-06-17')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['ticker'] == 'VOO'
            assert data['purchase_date'] == '2025-06-17'
            assert data['purchase_price'] == 549.35
            assert data['current_price'] == 559.95
            assert data['success'] is True
            
            # Calculate expected performance: (559.95 - 549.35) / 549.35 * 100 = 1.93%
            expected_performance = ((559.95 - 549.35) / 549.35) * 100
            assert abs(data['performance'] - expected_performance) < 0.01
    
    def test_etf_performance_missing_data(self, client, app):
        """Test ETF performance API with missing price data"""
        with app.app_context():
            # Use a date far in the past to avoid API calls
            response = client.get('/api/etf-performance/NONEXISTENT/1990-01-01')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['ticker'] == 'NONEXISTENT'
            assert data['performance'] == 0  # Should default to 0 when no data
            assert data['success'] is True
    
    def test_etf_performance_calculation_accuracy(self, client, app):
        """Test specific calculation accuracy for CPNG vs VOO example"""
        with app.app_context():
            # CPNG purchase scenario
            voo_purchase = PriceHistory(
                ticker='VOO',
                date=date(2025, 6, 17),
                close_price=549.35,
                is_intraday=False,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
            voo_current = PriceHistory(
                ticker='VOO',
                date=date.today(),
                close_price=559.95,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
            db.session.add(voo_purchase)
            db.session.add(voo_current)
            db.session.commit()
            
            response = client.get('/api/etf-performance/VOO/2025-06-17')
            data = response.get_json()
            
            # Expected: (559.95 - 549.35) / 549.35 * 100 = 1.9289%
            expected = ((559.95 - 549.35) / 549.35) * 100
            assert abs(data['performance'] - expected) < 0.0001
            assert abs(data['performance'] - 1.9289) < 0.01
    
    def test_invalid_date_format(self, client):
        """Test API with invalid date format"""
        response = client.get('/api/etf-performance/VOO/invalid-date')
        assert response.status_code == 500
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_multiple_etf_performance_calls(self, client, app):
        """Test multiple ETF performance calculations"""
        with app.app_context():
            # Clear existing data first
            db.session.query(PriceHistory).filter_by(ticker='TEST').delete()
            db.session.commit()
            
            # Add test data for multiple dates using TEST ticker to avoid conflicts
            dates_and_prices = [
                (date(2025, 6, 17), 549.35, 559.95),
                (date(2025, 5, 15), 540.00, 559.95),
                (date(2025, 4, 10), 530.00, 559.95)
            ]
            
            # Add current price once
            current_record = PriceHistory(
                ticker='TEST',
                date=date.today(),
                close_price=559.95,
                is_intraday=True,
                price_timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            db.session.add(current_record)
            
            for purchase_date, purchase_price, current_price in dates_and_prices:
                # Add purchase price
                purchase_record = PriceHistory(
                    ticker='TEST',
                    date=purchase_date,
                    close_price=purchase_price,
                    is_intraday=False,
                    price_timestamp=datetime.now(),
                    last_updated=datetime.now()
                )
                db.session.add(purchase_record)
            
            db.session.commit()
            
            # Test each date
            for purchase_date, purchase_price, current_price in dates_and_prices:
                date_str = purchase_date.strftime('%Y-%m-%d')
                response = client.get(f'/api/etf-performance/TEST/{date_str}')
                
                assert response.status_code == 200
                data = response.get_json()
                
                expected_performance = ((current_price - purchase_price) / purchase_price) * 100
                assert abs(data['performance'] - expected_performance) < 0.01
                assert data['success'] is True