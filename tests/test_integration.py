import pytest
from unittest.mock import patch, Mock
from datetime import datetime, date, timedelta
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.services.data_loader import DataLoader
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app.models.stock import Stock
from app.models.price import PriceHistory
from app import db


class TestPortfolioIntegration:
    """Integration tests for portfolio operations with price service."""
    
    @pytest.fixture
    def portfolio_service(self, app):
        with app.app_context():
            return PortfolioService()
    
    @pytest.fixture
    def price_service(self, app):
        with app.app_context():
            return PriceService()
    


    def test_complete_investment_workflow(self, portfolio_service, price_service, sample_portfolio, app):
        """Test complete workflow: buy stock, receive dividend, calculate performance."""
        with app.app_context():
            # Step 1: Add stock purchase
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Step 2: Add dividend
            dividend = portfolio_service.add_dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date(2023, 3, 15),
                total_amount=25.50
            )
            
            # Step 3: Mock current price
            price_service.cache_price_data("AAPL", date.today(), 160.00, False)
            
            # Step 4: Calculate performance
            with patch.object(price_service, 'get_current_price', return_value=160.00):
                performance = portfolio_service.calculate_transaction_performance(transaction.id)
                
                # Verify performance calculation
                assert performance['gain_loss'] == 100.00  # (160-150) * 10
                assert abs(performance['gain_loss_percentage'] - 6.67) < 0.01
                
                # Verify dividend is included in portfolio value
                portfolio_value = portfolio_service.calculate_portfolio_value(sample_portfolio.id)
                assert portfolio_value == 1600.00  # 10 shares * $160

    def test_portfolio_with_multiple_stocks(self, portfolio_service, price_service, sample_portfolio, app):
        """Test portfolio with multiple stock positions."""
        with app.app_context():
            # Add multiple stock purchases
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="GOOGL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=2500.00,
                shares=2.0
            )
            
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="MSFT",
                transaction_type="BUY",
                date=date(2023, 2, 1),
                price_per_share=250.00,
                shares=8.0
            )
            
            # Mock current prices
            price_service.cache_price_data("AAPL", date.today(), 160.00, False)
            price_service.cache_price_data("GOOGL", date.today(), 2600.00, False)
            price_service.cache_price_data("MSFT", date.today(), 280.00, False)
            
            # Calculate portfolio value
            with patch.object(price_service, 'get_current_price') as mock_price:
                mock_price.side_effect = lambda ticker: {
                    "AAPL": 160.00,
                    "GOOGL": 2600.00,
                    "MSFT": 280.00
                }[ticker]
                
                portfolio_value = portfolio_service.calculate_portfolio_value(sample_portfolio.id)
                expected_value = (10 * 160.00) + (2 * 2600.00) + (8 * 280.00)  # 1600 + 5200 + 2240 = 9040
                assert portfolio_value == expected_value

    def test_buy_and_sell_workflow(self, portfolio_service, price_service, sample_portfolio, app):
        """Test buying and then selling shares."""
        with app.app_context():
            # Buy shares
            buy_transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Sell some shares
            sell_transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date(2023, 6, 1),
                price_per_share=180.00,
                shares=4.0
            )
            
            # Check current holdings
            holdings = portfolio_service.get_current_holdings(sample_portfolio.id)
            assert holdings["AAPL"] == 6.0  # 10 - 4 = 6 shares remaining
            
            # Mock current price and calculate remaining position value
            with patch('app.services.price_service.PriceService') as mock_price_service_class:
                mock_price_service_instance = mock_price_service_class.return_value
                mock_price_service_instance.get_current_price.return_value = 170.00
                
                portfolio_value = portfolio_service.calculate_portfolio_value(sample_portfolio.id)
                assert portfolio_value == 1020.00  # 6 shares * $170

    def test_fractional_shares_integration(self, portfolio_service, price_service, sample_portfolio, app):
        """Test fractional share handling across services."""
        with app.app_context():
            # Buy fractional shares
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.333
            )
            
            # Verify fractional shares are stored correctly
            assert transaction.shares == 10.333
            assert transaction.total_value == 1549.95  # 10.333 * 150
            
            # Calculate value with fractional shares
            with patch('app.services.price_service.PriceService') as mock_price_service_class:
                mock_price_service_instance = mock_price_service_class.return_value
                mock_price_service_instance.get_current_price.return_value = 160.00
                
                portfolio_value = portfolio_service.calculate_portfolio_value(sample_portfolio.id)
                expected_value = 10.333 * 160.00
                assert abs(portfolio_value - expected_value) < 0.01

    def test_dividend_attribution_to_holdings(self, portfolio_service, sample_portfolio, app):
        """Test that dividends are properly attributed to stock holdings."""
        with app.app_context():
            # Buy shares at different times
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 2, 1),
                price_per_share=160.00,
                shares=5.0
            )
            
            # Add dividend after both purchases
            dividend = portfolio_service.add_dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date(2023, 3, 15),
                total_amount=30.00  # $2 per share for 15 shares
            )
            
            # Verify dividend is recorded
            dividends = portfolio_service.get_portfolio_dividends(sample_portfolio.id)
            assert len(dividends) == 1
            assert dividends[0].total_amount == 30.00

    def test_etf_comparison_integration(self, portfolio_service, price_service, sample_portfolio, app):
        """Test ETF comparison functionality."""
        with app.app_context():
            # Add stock purchase
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Add ETF price data for comparison
            investment_date = date(2023, 1, 1)
            current_date = date.today()
            
            # VOO prices
            voo_purchase = PriceHistory(
                ticker="VOO",
                date=investment_date,
                close_price=400.00,
                is_intraday=False,
                price_timestamp=datetime.combine(investment_date, datetime.min.time()),
                last_updated=datetime.utcnow()
            )
            
            voo_current = PriceHistory(
                ticker="VOO",
                date=current_date,
                close_price=420.00,
                is_intraday=False,
                price_timestamp=datetime.combine(current_date, datetime.min.time()),
                last_updated=datetime.utcnow()
            )
            
            db.session.add_all([voo_purchase, voo_current])
            db.session.commit()
            
            # Get ETF comparison
            comparison = price_service.get_etf_comparison_data(
                "VOO", investment_date, 1500.00, current_date
            )
            
            assert comparison['ticker'] == "VOO"
            assert comparison['investment_amount'] == 1500.00
            assert comparison['gain_loss_percentage'] == 5.0  # (420-400)/400 * 100


class TestDataLoaderIntegration:
    """Integration tests for data import/export functionality."""
    
    @pytest.fixture
    def data_loader(self, app):
        with app.app_context():
            return DataLoader()
    
    @pytest.fixture
    def portfolio_service(self, app):
        with app.app_context():
            return PortfolioService()
    


    def test_csv_import_export_roundtrip(self, data_loader, sample_portfolio, app):
        """Test importing data from CSV and then exporting it back."""
        with app.app_context():
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
                sample_portfolio.id, transaction_data
            )
            imported_dividends = data_loader.import_dividends_from_csv(
                sample_portfolio.id, dividend_data
            )
            
            assert imported_transactions == 2
            assert imported_dividends == 1
            
            # Export data
            export_data = data_loader.export_portfolio_to_csv(sample_portfolio.id)
            
            # Verify exported data matches imported data
            assert len(export_data['transactions']) == 2
            assert len(export_data['dividends']) == 1
            
            # Check transaction details
            exported_tickers = [t['ticker'] for t in export_data['transactions']]
            assert 'AAPL' in exported_tickers
            assert 'GOOGL' in exported_tickers
            
            # Check dividend details
            assert export_data['dividends'][0]['ticker'] == 'AAPL'
            assert float(export_data['dividends'][0]['total_amount']) == 25.50

    def test_data_validation_during_import(self, data_loader, sample_portfolio, app):
        """Test that data validation works during CSV import."""
        with app.app_context():
            # Mix of valid and invalid data
            mixed_data = [
                {
                    'Ticker': 'AAPL',
                    'Type': 'BUY',
                    'Date': '2023-01-01',
                    'Price': '150.00',
                    'Shares': '10.0'
                },
                {
                    'Ticker': '',  # Invalid: empty ticker
                    'Type': 'BUY',
                    'Date': '2023-01-02',
                    'Price': '160.00',
                    'Shares': '5.0'
                },
                {
                    'Ticker': 'GOOGL',
                    'Type': 'INVALID',  # Invalid: bad transaction type
                    'Date': '2023-01-03',
                    'Price': '2500.00',
                    'Shares': '2.0'
                }
            ]
            
            # Import should only process valid records
            imported_count = data_loader.import_transactions_from_csv(
                sample_portfolio.id, mixed_data
            )
            
            # Only 1 valid record should be imported
            assert imported_count == 1
            
            # Verify only valid transaction was saved
            transactions = StockTransaction.query.filter_by(
                portfolio_id=sample_portfolio.id
            ).all()
            
            assert len(transactions) == 1
            assert transactions[0].ticker == 'AAPL'


class TestPriceServiceIntegration:
    """Integration tests for price service with caching."""
    
    @pytest.fixture
    def price_service(self, app):
        with app.app_context():
            return PriceService()

    def test_price_caching_workflow(self, price_service, app):
        """Test the complete price caching workflow."""
        with app.app_context():
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

    @patch('yfinance.Ticker')
    def test_api_fallback_when_cache_stale(self, mock_ticker, price_service, app):
        """Test that API is called when cache is stale."""
        with app.app_context():
            ticker = "AAPL"
            test_date = date.today()
            
            # Add stale cache data
            stale_time = datetime.utcnow() - timedelta(hours=2)
            price_history = PriceHistory(
                ticker=ticker,
                date=test_date,
                close_price=140.00,
                is_intraday=True,
                price_timestamp=stale_time,
                last_updated=stale_time
            )
            db.session.add(price_history)
            db.session.commit()
            
            # Mock API response
            mock_hist = Mock()
            mock_hist.empty = False
            mock_hist.__len__ = Mock(return_value=1)
            mock_hist.iloc = Mock()
            mock_hist.iloc.__getitem__ = Mock(return_value={'Close': 155.00})
            
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = mock_hist
            mock_ticker.return_value = mock_ticker_instance
            
            # Should use stale cache by default (optimization)
            current_price = price_service.get_current_price(ticker)
            assert current_price == 140.00
            
            # Should fetch from API when explicitly requested
            current_price = price_service.get_current_price(ticker, use_stale=False)
            assert current_price == 155.00
            
            # Verify cache was updated
            updated_cache = price_service.get_cached_price(ticker, test_date)
            assert updated_cache == 155.00

    def test_historical_data_retrieval(self, price_service, app):
        """Test retrieving historical price data."""
        with app.app_context():
            ticker = "AAPL"
            start_date = date.today() - timedelta(days=5)
            end_date = date.today()
            
            # Add historical price data
            dates = [start_date + timedelta(days=i) for i in range(6)]
            prices = [150.00, 151.00, 149.00, 152.00, 148.00, 153.00]
            
            for d, p in zip(dates, prices):
                price_history = PriceHistory(
                    ticker=ticker,
                    date=d,
                    close_price=p,
                    is_intraday=False,
                    price_timestamp=datetime.combine(d, datetime.min.time()),
                    last_updated=datetime.utcnow()
                )
                db.session.add(price_history)
            db.session.commit()
            
            # Retrieve historical data
            history = price_service.get_price_history(ticker, start_date, end_date)
            
            assert len(history) == 6
            assert all(h.ticker == ticker for h in history)
            assert history[0].date == start_date
            assert history[-1].date == end_date