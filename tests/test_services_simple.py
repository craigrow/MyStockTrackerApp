import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.services.data_loader import DataLoader
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.price import PriceHistory
from app import db


class TestPortfolioService:
    
    def test_create_portfolio(self, app):
        with app.app_context():
            service = PortfolioService()
            portfolio = service.create_portfolio(
                name="New Portfolio",
                description="Test description",
                user_id="test_user"
            )
            
            assert portfolio.name == "New Portfolio"
            assert portfolio.description == "Test description"
            assert portfolio.user_id == "test_user"
            assert portfolio.id is not None

    def test_get_portfolio(self, app):
        with app.app_context():
            service = PortfolioService()
            portfolio = service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            retrieved = service.get_portfolio(portfolio.id)
            
            assert retrieved.id == portfolio.id
            assert retrieved.name == portfolio.name

    def test_add_transaction(self, app):
        with app.app_context():
            service = PortfolioService()
            portfolio = service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            transaction = service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0
            )
            
            assert transaction.ticker == "AAPL"
            assert transaction.transaction_type == "BUY"
            assert transaction.shares == 10.0
            assert transaction.total_value == 1500.00

    def test_add_dividend(self, app):
        with app.app_context():
            service = PortfolioService()
            portfolio = service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            dividend = service.add_dividend(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            
            assert dividend.ticker == "AAPL"
            assert dividend.total_amount == 25.50

    def test_get_current_holdings(self, app):
        with app.app_context():
            service = PortfolioService()
            portfolio = service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            # Add buy transaction
            service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Add sell transaction
            service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date.today(),
                price_per_share=160.00,
                shares=3.0
            )
            
            holdings = service.get_current_holdings(portfolio.id)
            
            assert "AAPL" in holdings
            assert holdings["AAPL"] == 7.0  # 10 - 3 = 7 shares


class TestPriceService:
    
    def test_cache_price_data(self, app):
        with app.app_context():
            service = PriceService()
            service.cache_price_data("AAPL", date.today(), 150.00, False)
            
            cached_price = service.get_cached_price("AAPL", date.today())
            assert cached_price == 150.00

    def test_is_cache_fresh(self, app):
        with app.app_context():
            service = PriceService()
            service.cache_price_data("AAPL", date.today(), 150.00, True)
            
            is_fresh = service.is_cache_fresh("AAPL", date.today())
            assert is_fresh is True

    def test_get_price_history(self, app):
        with app.app_context():
            service = PriceService()
            
            # Add historical prices
            dates = [date.today() - timedelta(days=i) for i in range(3)]
            prices = [150.00, 151.00, 149.00]
            
            for d, p in zip(dates, prices):
                service.cache_price_data("AAPL", d, p, False)
            
            history = service.get_price_history("AAPL", dates[-1], dates[0])
            
            assert len(history) == 3
            assert all(h.ticker == "AAPL" for h in history)


class TestDataLoader:
    
    def test_validate_transaction_data(self, app):
        with app.app_context():
            service = DataLoader()
            
            valid_data = {
                'ticker': 'AAPL',
                'transaction_type': 'BUY',
                'date': '2023-01-01',
                'price_per_share': '150.00',
                'shares': '10.0'
            }
            
            is_valid, errors = service.validate_transaction_data(valid_data)
            assert is_valid is True
            assert len(errors) == 0

    def test_validate_dividend_data(self, app):
        with app.app_context():
            service = DataLoader()
            
            valid_data = {
                'ticker': 'AAPL',
                'payment_date': '2023-01-15',
                'total_amount': '25.50'
            }
            
            is_valid, errors = service.validate_dividend_data(valid_data)
            assert is_valid is True
            assert len(errors) == 0

    def test_import_transactions_from_csv(self, app):
        with app.app_context():
            portfolio_service = PortfolioService()
            data_loader = DataLoader()
            
            portfolio = portfolio_service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            csv_data = [
                {
                    'ticker': 'AAPL',
                    'transaction_type': 'BUY',
                    'date': '2023-01-01',
                    'price_per_share': '150.00',
                    'shares': '10.0'
                }
            ]
            
            imported_count = data_loader.import_transactions_from_csv(
                portfolio.id, csv_data
            )
            
            assert imported_count == 1
            
            transactions = portfolio_service.get_portfolio_transactions(portfolio.id)
            assert len(transactions) == 1
            assert transactions[0].ticker == 'AAPL'