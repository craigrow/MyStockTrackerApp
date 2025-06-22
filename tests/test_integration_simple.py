import pytest
from unittest.mock import patch, Mock
from datetime import datetime, date, timedelta
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.services.data_loader import DataLoader
from app.models.price import PriceHistory
from app import db


class TestPortfolioIntegration:
    
    def test_complete_investment_workflow(self, app):
        """Test complete workflow: buy stock, receive dividend, calculate performance."""
        with app.app_context():
            portfolio_service = PortfolioService()
            price_service = PriceService()
            
            # Create portfolio
            portfolio = portfolio_service.create_portfolio(
                name="Integration Test Portfolio", 
                user_id="test_user"
            )
            
            # Add stock purchase
            transaction = portfolio_service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Add dividend
            dividend = portfolio_service.add_dividend(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                payment_date=date(2023, 3, 15),
                total_amount=25.50
            )
            
            # Mock current price
            price_service.cache_price_data("AAPL", date.today(), 160.00, False)
            
            # Calculate performance
            with patch.object(price_service, 'get_current_price', return_value=160.00):
                performance = portfolio_service.calculate_transaction_performance(transaction.id)
                
                assert performance['gain_loss'] == 100.00  # (160-150) * 10
                assert abs(performance['gain_loss_percentage'] - 6.67) < 0.01

    def test_buy_and_sell_workflow(self, app):
        """Test buying and then selling shares."""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            # Create portfolio
            portfolio = portfolio_service.create_portfolio(
                name="Buy/Sell Test Portfolio", 
                user_id="test_user"
            )
            
            # Buy shares
            portfolio_service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Sell some shares
            portfolio_service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date(2023, 6, 1),
                price_per_share=180.00,
                shares=4.0
            )
            
            # Check current holdings
            holdings = portfolio_service.get_current_holdings(portfolio.id)
            assert holdings["AAPL"] == 6.0  # 10 - 4 = 6 shares remaining

    def test_fractional_shares_integration(self, app):
        """Test fractional share handling across services."""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            # Create portfolio
            portfolio = portfolio_service.create_portfolio(
                name="Fractional Test Portfolio", 
                user_id="test_user"
            )
            
            # Buy fractional shares
            transaction = portfolio_service.add_transaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.333
            )
            
            # Verify fractional shares are stored correctly
            assert transaction.shares == 10.333
            assert transaction.total_value == 1549.95  # 10.333 * 150


class TestDataLoaderIntegration:
    
    def test_csv_import_export_roundtrip(self, app):
        """Test importing data from CSV and then exporting it back."""
        with app.app_context():
            portfolio_service = PortfolioService()
            data_loader = DataLoader()
            
            # Create portfolio
            portfolio = portfolio_service.create_portfolio(
                name="CSV Test Portfolio", 
                user_id="test_user"
            )
            
            # Import transaction data
            transaction_data = [
                {
                    'Ticker': 'AAPL',
                    'Type': 'BUY',
                    'Date': '2023-01-01',
                    'Price': '150.00',
                    'Shares': '10.0'
                },
                {
                    'Ticker': 'GOOGL',
                    'Type': 'BUY',
                    'Date': '2023-01-15',
                    'Price': '2500.00',
                    'Shares': '2.0'
                }
            ]
            
            # Import dividend data
            dividend_data = [
                {
                    'Ticker': 'AAPL',
                    'Date': '2023-03-15',
                    'Amount': '25.50'
                }
            ]
            
            # Import data
            imported_transactions = data_loader.import_transactions_from_csv(
                portfolio.id, transaction_data
            )
            imported_dividends = data_loader.import_dividends_from_csv(
                portfolio.id, dividend_data
            )
            
            assert imported_transactions == 2
            assert imported_dividends == 1
            
            # Export data
            export_data = data_loader.export_portfolio_to_csv(portfolio.id)
            
            # Verify exported data matches imported data
            assert len(export_data['transactions']) == 2
            assert len(export_data['dividends']) == 1
            
            # Check transaction details
            exported_tickers = [t['ticker'] for t in export_data['transactions']]
            assert 'AAPL' in exported_tickers
            assert 'GOOGL' in exported_tickers


class TestPriceServiceIntegration:
    
    def test_price_caching_workflow(self, app):
        """Test the complete price caching workflow."""
        with app.app_context():
            price_service = PriceService()
            ticker = "AAPL"
            test_date = date.today()
            test_price = 150.00
            
            # Initially no cached data
            cached_price = price_service.get_cached_price(ticker, test_date)
            assert cached_price is None
            
            # Cache some data
            price_service.cache_price_data(ticker, test_date, test_price, False)
            
            # Now should retrieve from cache
            cached_price = price_service.get_cached_price(ticker, test_date)
            assert cached_price == test_price
            
            # Verify cache freshness
            is_fresh = price_service.is_cache_fresh(ticker, test_date)
            assert is_fresh is True

    def test_historical_data_retrieval(self, app):
        """Test retrieving historical price data."""
        with app.app_context():
            price_service = PriceService()
            ticker = "AAPL"
            start_date = date.today() - timedelta(days=5)
            end_date = date.today()
            
            # Add historical price data
            dates = [start_date + timedelta(days=i) for i in range(6)]
            prices = [150.00, 151.00, 149.00, 152.00, 148.00, 153.00]
            
            for d, p in zip(dates, prices):
                price_service.cache_price_data(ticker, d, p, False)
            
            # Retrieve historical data
            history = price_service.get_price_history(ticker, start_date, end_date)
            
            assert len(history) == 6
            assert all(h.ticker == ticker for h in history)
            assert history[0].date == start_date
            assert history[-1].date == end_date