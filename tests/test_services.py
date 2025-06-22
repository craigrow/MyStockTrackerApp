import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.services.data_loader import DataLoader
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.stock import Stock
from app.models.price import PriceHistory
from app import db


class TestPortfolioService:
    @pytest.fixture
    def portfolio_service(self, app):
        with app.app_context():
            return PortfolioService()

    def test_create_portfolio(self, portfolio_service, app):
        with app.app_context():
            portfolio = portfolio_service.create_portfolio(
                name="New Portfolio",
                description="Test description",
                user_id="test_user"
            )
            
            assert portfolio.name == "New Portfolio"
            assert portfolio.description == "Test description"
            assert portfolio.user_id == "test_user"
            assert portfolio.id is not None

    def test_get_portfolio(self, portfolio_service, app):
        with app.app_context():
            # Create portfolio within the test
            portfolio = portfolio_service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            retrieved = portfolio_service.get_portfolio(portfolio.id)
            
            assert retrieved.id == portfolio.id
            assert retrieved.name == portfolio.name

    def test_get_portfolio_not_found(self, portfolio_service, app):
        with app.app_context():
            result = portfolio_service.get_portfolio("nonexistent_id")
            assert result is None

    def test_add_transaction(self, portfolio_service, app):
        with app.app_context():
            portfolio = portfolio_service.create_portfolio(
                name="Test Portfolio",
                user_id="test_user"
            )
            
            transaction = portfolio_service.add_transaction(
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

    def test_add_fractional_transaction(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=0.5
            )
            
            assert transaction.shares == 0.5
            assert transaction.total_value == 75.00

    def test_add_dividend(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            dividend = portfolio_service.add_dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            
            assert dividend.ticker == "AAPL"
            assert dividend.total_amount == 25.50
            assert dividend.payment_date == date.today()

    def test_get_portfolio_transactions(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            # Add some transactions
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0
            )
            
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="GOOGL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=2500.00,
                shares=2.0
            )
            
            transactions = portfolio_service.get_portfolio_transactions(sample_portfolio.id)
            
            assert len(transactions) == 2
            tickers = [t.ticker for t in transactions]
            assert "AAPL" in tickers
            assert "GOOGL" in tickers

    def test_get_portfolio_dividends(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            # Add some dividends
            portfolio_service.add_dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            
            portfolio_service.add_dividend(
                portfolio_id=sample_portfolio.id,
                ticker="MSFT",
                payment_date=date.today(),
                total_amount=15.75
            )
            
            dividends = portfolio_service.get_portfolio_dividends(sample_portfolio.id)
            
            assert len(dividends) == 2
            total_amount = sum(d.total_amount for d in dividends)
            assert total_amount == 41.25

    def test_calculate_portfolio_value(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            # Mock price service
            with patch('app.services.price_service.PriceService') as mock_price_service:
                mock_price_service.return_value.get_current_price.return_value = 160.00
                
                # Add transaction
                portfolio_service.add_transaction(
                    portfolio_id=sample_portfolio.id,
                    ticker="AAPL",
                    transaction_type="BUY",
                    date=date.today(),
                    price_per_share=150.00,
                    shares=10.0
                )
                
                value = portfolio_service.calculate_portfolio_value(sample_portfolio.id)
                
                # 10 shares * $160 current price = $1600
                assert value == 1600.00

    def test_get_current_holdings(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            # Add buy transaction
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0
            )
            
            # Add sell transaction
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date.today(),
                price_per_share=160.00,
                shares=3.0
            )
            
            holdings = portfolio_service.get_current_holdings(sample_portfolio.id)
            
            assert "AAPL" in holdings
            assert holdings["AAPL"] == 7.0  # 10 - 3 = 7 shares

    def test_calculate_transaction_performance(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            with patch('app.services.price_service.PriceService') as mock_price_service:
                mock_price_service.return_value.get_current_price.return_value = 160.00
                
                transaction = portfolio_service.add_transaction(
                    portfolio_id=sample_portfolio.id,
                    ticker="AAPL",
                    transaction_type="BUY",
                    date=date.today(),
                    price_per_share=150.00,
                    shares=10.0
                )
                
                performance = portfolio_service.calculate_transaction_performance(transaction.id)
                
                # Gain: (160 - 150) * 10 = $100
                # Percentage: 100 / 1500 = 6.67%
                assert performance['gain_loss'] == 100.00
                assert abs(performance['gain_loss_percentage'] - 6.67) < 0.01

    def test_update_cash_balance(self, portfolio_service, sample_portfolio, app):
        with app.app_context():
            # Initial cash balance
            portfolio_service.update_cash_balance(sample_portfolio.id, 1000.00)
            
            balance = portfolio_service.get_cash_balance(sample_portfolio.id)
            assert balance == 1000.00
            
            # Update balance
            portfolio_service.update_cash_balance(sample_portfolio.id, 1500.00)
            
            updated_balance = portfolio_service.get_cash_balance(sample_portfolio.id)
            assert updated_balance == 1500.00


class TestPriceService:
    @pytest.fixture
    def price_service(self, app):
        with app.app_context():
            return PriceService()

    def test_get_current_price_from_cache(self, price_service, app):
        with app.app_context():
            # Add price to cache
            price_history = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=True,
                price_timestamp=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.session.add(price_history)
            db.session.commit()
            
            price = price_service.get_current_price("AAPL")
            assert price == 150.00

    @patch('yfinance.Ticker')
    def test_get_current_price_from_api(self, mock_ticker, price_service, app):
        with app.app_context():
            # Mock yfinance response
            mock_hist = Mock()
            mock_hist.empty = False
            mock_hist.__len__ = Mock(return_value=1)
            mock_hist.iloc = Mock()
            mock_hist.iloc.__getitem__ = Mock(return_value={'Close': 155.00})
            
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = mock_hist
            mock_ticker.return_value = mock_ticker_instance
            
            price = price_service.get_current_price("AAPL")
            assert price == 155.00

    def test_get_price_history(self, price_service, app):
        with app.app_context():
            # Add historical prices
            dates = [date.today() - timedelta(days=i) for i in range(5)]
            prices = [150.00, 151.00, 149.00, 152.00, 148.00]
            
            for d, p in zip(dates, prices):
                price_history = PriceHistory(
                    ticker="AAPL",
                    date=d,
                    close_price=p,
                    is_intraday=False,
                    price_timestamp=datetime.combine(d, datetime.min.time()),
                    last_updated=datetime.utcnow()
                )
                db.session.add(price_history)
            db.session.commit()
            
            history = price_service.get_price_history("AAPL", dates[-1], dates[0])
            
            assert len(history) == 5
            assert all(h.ticker == "AAPL" for h in history)

    def test_cache_price_data(self, price_service, app):
        with app.app_context():
            price_service.cache_price_data("AAPL", date.today(), 150.00, False)
            
            cached_price = price_service.get_current_price("AAPL")
            assert cached_price == 150.00

    def test_is_cache_fresh(self, price_service, app):
        with app.app_context():
            # Add fresh price data
            price_history = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=True,
                price_timestamp=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.session.add(price_history)
            db.session.commit()
            
            is_fresh = price_service.is_cache_fresh("AAPL", date.today())
            assert is_fresh is True

    def test_is_cache_stale(self, price_service, app):
        with app.app_context():
            # Add stale price data
            stale_time = datetime.utcnow() - timedelta(hours=2)
            price_history = PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=150.00,
                is_intraday=True,
                price_timestamp=stale_time,
                last_updated=stale_time
            )
            db.session.add(price_history)
            db.session.commit()
            
            is_fresh = price_service.is_cache_fresh("AAPL", date.today())
            assert is_fresh is False

    @patch('yfinance.Ticker')
    def test_fetch_from_api_with_retry(self, mock_ticker, price_service, app):
        with app.app_context():
            # Mock successful response
            mock_hist = Mock()
            mock_hist.empty = False
            mock_hist.__len__ = Mock(return_value=1)
            mock_hist.iloc = Mock()
            mock_hist.iloc.__getitem__ = Mock(return_value={'Close': 155.00})
            
            mock_ticker_instance = Mock()
            mock_ticker_instance.history.return_value = mock_hist
            mock_ticker.return_value = mock_ticker_instance
            
            price = price_service.fetch_from_api("AAPL")
            assert price == 155.00

    def test_get_etf_comparison_data(self, price_service, app):
        with app.app_context():
            # Add ETF price data
            investment_date = date.today() - timedelta(days=30)
            current_date = date.today()
            
            # Purchase price
            purchase_price = PriceHistory(
                ticker="VOO",
                date=investment_date,
                close_price=400.00,
                is_intraday=False,
                price_timestamp=datetime.combine(investment_date, datetime.min.time()),
                last_updated=datetime.utcnow()
            )
            
            # Current price
            current_price = PriceHistory(
                ticker="VOO",
                date=current_date,
                close_price=420.00,
                is_intraday=False,
                price_timestamp=datetime.combine(current_date, datetime.min.time()),
                last_updated=datetime.utcnow()
            )
            
            db.session.add_all([purchase_price, current_price])
            db.session.commit()
            
            comparison = price_service.get_etf_comparison_data(
                "VOO", investment_date, 1000.00, current_date
            )
            
            assert comparison['ticker'] == "VOO"
            assert comparison['investment_amount'] == 1000.00
            assert comparison['purchase_price'] == 400.00
            assert comparison['current_price'] == 420.00
            assert comparison['gain_loss_percentage'] == 5.0  # (420-400)/400 * 100


class TestDataLoader:
    @pytest.fixture
    def data_loader(self, app):
        with app.app_context():
            return DataLoader()

    def test_import_transactions_from_csv(self, data_loader, sample_portfolio, app):
        with app.app_context():
            csv_data = [
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
                    'Date': '2023-01-02',
                    'Price': '2500.00',
                    'Shares': '2.0'
                }
            ]
            
            imported_count = data_loader.import_transactions_from_csv(
                sample_portfolio.id, csv_data
            )
            
            assert imported_count == 2
            
            transactions = StockTransaction.query.filter_by(
                portfolio_id=sample_portfolio.id
            ).all()
            
            assert len(transactions) == 2
            tickers = [t.ticker for t in transactions]
            assert 'AAPL' in tickers
            assert 'GOOGL' in tickers

    def test_import_dividends_from_csv(self, data_loader, sample_portfolio, app):
        with app.app_context():
            csv_data = [
                {
                    'Ticker': 'AAPL',
                    'Date': '2023-01-15',
                    'Amount': '25.50'
                },
                {
                    'Ticker': 'MSFT',
                    'Date': '2023-01-20',
                    'Amount': '15.75'
                }
            ]
            
            imported_count = data_loader.import_dividends_from_csv(
                sample_portfolio.id, csv_data
            )
            
            assert imported_count == 2
            
            dividends = Dividend.query.filter_by(
                portfolio_id=sample_portfolio.id
            ).all()
            
            assert len(dividends) == 2
            total_amount = sum(d.total_amount for d in dividends)
            assert total_amount == 41.25

    def test_export_portfolio_to_csv(self, data_loader, sample_portfolio, app):
        with app.app_context():
            # Add some data to export
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            
            dividend = Dividend(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                payment_date=date.today(),
                total_amount=25.50
            )
            
            db.session.add_all([transaction, dividend])
            db.session.commit()
            
            export_data = data_loader.export_portfolio_to_csv(sample_portfolio.id)
            
            assert 'transactions' in export_data
            assert 'dividends' in export_data
            assert len(export_data['transactions']) == 1
            assert len(export_data['dividends']) == 1

    def test_validate_transaction_data(self, data_loader, app):
        with app.app_context():
            valid_data = {
                'Ticker': 'AAPL',
                'Type': 'BUY',
                'Date': '2023-01-01',
                'Price': '150.00',
                'Shares': '10.0'
            }
            
            is_valid, errors = data_loader.validate_transaction_data(valid_data)
            assert is_valid is True
            assert len(errors) == 0

    def test_validate_invalid_transaction_data(self, data_loader, app):
        with app.app_context():
            invalid_data = {
                'ticker': '',  # Empty ticker
                'transaction_type': 'INVALID',  # Invalid type
                'date': 'invalid-date',  # Invalid date
                'price_per_share': '-150.00',  # Negative price
                'shares': '0'  # Zero shares
            }
            
            is_valid, errors = data_loader.validate_transaction_data(invalid_data)
            assert is_valid is False
            assert len(errors) > 0

    def test_validate_dividend_data(self, data_loader, app):
        with app.app_context():
            valid_data = {
                'Ticker': 'AAPL',
                'Date': '2023-01-15',
                'Amount': '25.50'
            }
            
            is_valid, errors = data_loader.validate_dividend_data(valid_data)
            assert is_valid is True
            assert len(errors) == 0

    def test_backup_to_csv(self, data_loader, sample_portfolio, app):
        with app.app_context():
            # Add some data
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date.today(),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Test backup functionality
            backup_result = data_loader.backup_to_csv(sample_portfolio.id)
            
            assert backup_result is True