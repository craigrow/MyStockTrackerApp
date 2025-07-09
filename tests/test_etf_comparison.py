import pytest
from datetime import date
from app.models.portfolio import Portfolio, StockTransaction
from app.services.cash_flow_service import CashFlowService
from app import db


class TestETFComparison:
    
    def test_cash_flows_page_supports_voo_comparison(self, app, client):
        """Test that cash flows page supports VOO comparison view with actual ETF data"""
        with app.app_context():
            # Create portfolio with transaction
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
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
            
            # Test VOO comparison view
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}&comparison=VOO')
            assert response.status_code == 200
            
            html = response.get_data(as_text=True)
            assert 'VOO' in html
            # Should show ETF purchase instead of stock purchase
            assert 'Purchase' in html or 'PURCHASE' in html
            # Should show ETF-specific cash flows with real price details
            assert 'shares @' in html or '$ per share' in html
    
    def test_cash_flows_page_supports_qqq_comparison(self, app, client):
        """Test that cash flows page supports QQQ comparison view"""
        with app.app_context():
            # Create portfolio with transaction
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
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
            
            # Test QQQ comparison view
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}&comparison=QQQ')
            assert response.status_code == 200
            
            html = response.get_data(as_text=True)
            assert 'QQQ' in html
            assert 'comparison' in html
    
    def test_cash_flows_template_has_comparison_toggle(self, app, client):
        """Test that cash flows template includes Portfolio/VOO/QQQ toggle buttons"""
        with app.app_context():
            # Create portfolio
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Test default portfolio view
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}')
            assert response.status_code == 200
            
            html = response.get_data(as_text=True)
            assert 'portfolio-radio' in html
            assert 'voo-radio' in html  
            assert 'qqq-radio' in html
            assert 'Portfolio</label>' in html
            assert 'VOO</label>' in html
            assert 'QQQ</label>' in html
    
    def test_etf_comparison_uses_portfolio_deposits(self, app, client):
        """Test that ETF comparison uses actual portfolio deposit amounts"""
        with app.app_context():
            # Create portfolio with multiple transactions
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Add transactions that require deposits
            transaction1 = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            transaction2 = StockTransaction(
                portfolio_id=portfolio.id,
                ticker='MSFT',
                transaction_type='BUY',
                date=date(2023, 2, 1),
                price_per_share=200.00,
                shares=5.0,
                total_value=1000.00
            )
            db.session.add_all([transaction1, transaction2])
            db.session.commit()
            
            # Test VOO comparison uses portfolio deposit amounts
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}&comparison=VOO')
            assert response.status_code == 200
            
            html = response.get_data(as_text=True)
            # Should show multiple ETF purchases based on portfolio deposits
            assert 'VOO' in html
            # Should show amounts that match portfolio investment pattern
            assert '$' in html
    
    def test_etf_comparison_uses_real_prices(self, app, client):
        """Test that ETF comparison uses real price data when available"""
        with app.app_context():
            from app.models.price import PriceHistory
            from datetime import datetime
            
            # Create portfolio with transaction
            portfolio = Portfolio(name='Test Portfolio', user_id='test')
            db.session.add(portfolio)
            db.session.commit()
            
            # Add a transaction
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
            
            # Add VOO price data for the transaction date
            voo_price = PriceHistory(
                ticker='VOO',
                date=date(2023, 1, 1),
                close_price=350.00,
                is_intraday=False,
                price_timestamp=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.session.add(voo_price)
            db.session.commit()
            
            # Test VOO comparison uses real price
            response = client.get(f'/cash-flows?portfolio_id={portfolio.id}&comparison=VOO')
            assert response.status_code == 200
            
            html = response.get_data(as_text=True)
            # Should show real price calculation (1500/350 = 4.2857 shares)
            assert 'VOO' in html
            assert '4.2857' in html or '4.29' in html  # Share calculation
            assert '$350.00' in html  # Real price used