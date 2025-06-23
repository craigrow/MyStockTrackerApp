import pytest
from app.services.data_loader import DataLoader
from app.models.portfolio import StockTransaction, Dividend
from app import db


class TestCSVDuplicateDetection:
    
    @pytest.fixture
    def data_loader(self, app):
        with app.app_context():
            return DataLoader()
    
    @pytest.fixture
    def sample_portfolio_id(self, app, sample_user_id):
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            portfolio_service = PortfolioService()
            portfolio = portfolio_service.create_portfolio(
                name="Duplicate Test Portfolio",
                user_id=sample_user_id
            )
            return portfolio.id

    def test_transaction_duplicate_detection(self, data_loader, sample_portfolio_id, app):
        """Test that duplicate transactions are not imported"""
        with app.app_context():
            csv_data = [
                {'Ticker': 'AAPL', 'Type': 'BUY', 'Date': '2024-01-15', 'Price': '150.25', 'Shares': '10'},
                {'Ticker': 'MSFT', 'Type': 'BUY', 'Date': '2024-01-20', 'Price': '200.50', 'Shares': '5'}
            ]
            
            # First import
            imported_count = data_loader.import_transactions_from_csv(sample_portfolio_id, csv_data)
            assert imported_count == 2
            
            # Second import (same data)
            imported_count = data_loader.import_transactions_from_csv(sample_portfolio_id, csv_data)
            assert imported_count == 0  # No new transactions imported
            
            # Verify only 2 transactions exist
            transactions = StockTransaction.query.filter_by(portfolio_id=sample_portfolio_id).all()
            assert len(transactions) == 2

    def test_dividend_duplicate_detection(self, data_loader, sample_portfolio_id, app):
        """Test that duplicate dividends are not imported"""
        with app.app_context():
            csv_data = [
                {'Ticker': 'AAPL', 'Date': '2024-01-15', 'Amount': '25.50'},
                {'Ticker': 'MSFT', 'Date': '2024-01-20', 'Amount': '15.75'}
            ]
            
            # First import
            imported_count = data_loader.import_dividends_from_csv(sample_portfolio_id, csv_data)
            assert imported_count == 2
            
            # Second import (same data)
            imported_count = data_loader.import_dividends_from_csv(sample_portfolio_id, csv_data)
            assert imported_count == 0  # No new dividends imported
            
            # Verify only 2 dividends exist
            dividends = Dividend.query.filter_by(portfolio_id=sample_portfolio_id).all()
            assert len(dividends) == 2

    def test_partial_duplicate_detection(self, data_loader, sample_portfolio_id, app):
        """Test that only new transactions are imported when some are duplicates"""
        with app.app_context():
            # First batch
            csv_data_1 = [
                {'Ticker': 'AAPL', 'Type': 'BUY', 'Date': '2024-01-15', 'Price': '150.25', 'Shares': '10'},
                {'Ticker': 'MSFT', 'Type': 'BUY', 'Date': '2024-01-20', 'Price': '200.50', 'Shares': '5'}
            ]
            
            imported_count = data_loader.import_transactions_from_csv(sample_portfolio_id, csv_data_1)
            assert imported_count == 2
            
            # Second batch (1 duplicate, 1 new)
            csv_data_2 = [
                {'Ticker': 'AAPL', 'Type': 'BUY', 'Date': '2024-01-15', 'Price': '150.25', 'Shares': '10'},  # Duplicate
                {'Ticker': 'GOOGL', 'Type': 'BUY', 'Date': '2024-01-25', 'Price': '100.00', 'Shares': '3'}   # New
            ]
            
            imported_count = data_loader.import_transactions_from_csv(sample_portfolio_id, csv_data_2)
            assert imported_count == 1  # Only 1 new transaction
            
            # Verify 3 total transactions
            transactions = StockTransaction.query.filter_by(portfolio_id=sample_portfolio_id).all()
            assert len(transactions) == 3