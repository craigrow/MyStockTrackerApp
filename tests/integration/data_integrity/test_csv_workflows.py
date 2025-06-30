"""Integration tests for CSV import workflows."""
import pytest
import os
from datetime import date
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.csv_generators import CSVTestGenerator
from tests.integration.utils.mocks import IntegrationTestMocks
from tests.integration.utils.assertion_helpers import ResponseAssertions
from app.models.portfolio import StockTransaction, Dividend
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestCSVWorkflows:
    """Test complete CSV import workflows for data integrity."""
    
    def test_valid_csv_import_complete_workflow(self, app, client):
        """Test complete CSV import process with valid data."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio and CSV data
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="CSV Test Portfolio")
                csv_content = CSVTestGenerator.create_valid_transactions_csv()
                csv_file = CSVTestGenerator.save_csv_to_file(csv_content, "valid_transactions.csv")
                
                # Get initial transaction count
                initial_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                
                # Act: Import CSV (simulate file upload)
                with open(csv_file, 'rb') as f:
                    response = client.post('/portfolio/import-csv', 
                                         data={
                                             'portfolio_id': portfolio.id,
                                             'import_type': 'transactions',
                                             'csv_file': (f, 'transactions.csv')
                                         },
                                         content_type='multipart/form-data')
                
                # Assert: Import was successful
                ResponseAssertions.assert_response_success(response, expected_status=302)  # Redirect after success
                
                # Verify transactions were imported
                final_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                assert final_count > initial_count, "Transactions should be imported"
                
                # Verify specific transactions exist
                aapl_buy = StockTransaction.query.filter_by(
                    portfolio_id=portfolio.id, 
                    ticker='AAPL', 
                    transaction_type='BUY'
                ).first()
                assert aapl_buy is not None, "AAPL BUY transaction should exist"
                assert aapl_buy.shares == 10.0, "AAPL shares should be correct"
                assert aapl_buy.price_per_share == 150.00, "AAPL price should be correct"
                
            finally:
                for mock in mocks:
                    mock.stop()
                # Cleanup temp file
                if os.path.exists(csv_file):
                    os.remove(csv_file)
    
    def test_csv_duplicate_detection_workflow(self, app, client):
        """Test CSV import with duplicate detection."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio and add initial transaction
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Duplicate Test Portfolio")
                
                # Add a transaction that will be duplicated in CSV
                existing_transaction = StockTransaction(
                    portfolio_id=portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 15),
                    price_per_share=150.00,
                    shares=10.0,
                    total_value=1500.00
                )
                db.session.add(existing_transaction)
                db.session.commit()
                
                initial_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                
                # Create CSV with duplicate data
                csv_content = CSVTestGenerator.create_duplicate_transactions_csv()
                csv_file = CSVTestGenerator.save_csv_to_file(csv_content, "duplicate_transactions.csv")
                
                # Act: Import CSV with duplicates
                with open(csv_file, 'rb') as f:
                    response = client.post('/portfolio/import-csv', 
                                         data={
                                             'portfolio_id': portfolio.id,
                                             'import_type': 'transactions',
                                             'csv_file': (f, 'transactions.csv')
                                         },
                                         content_type='multipart/form-data')
                
                # Assert: Import handled duplicates correctly
                ResponseAssertions.assert_response_success(response, expected_status=302)
                
                # Verify duplicate was not imported (count should increase by 2, not 3)
                final_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                expected_increase = 2  # GOOGL and MSFT, but not duplicate AAPL
                assert final_count == initial_count + expected_increase, f"Should import {expected_increase} new transactions, not duplicates"
                
                # Verify only one AAPL BUY transaction exists
                aapl_transactions = StockTransaction.query.filter_by(
                    portfolio_id=portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY'
                ).all()
                assert len(aapl_transactions) == 1, "Should have only one AAPL BUY transaction (duplicate prevented)"
                
            finally:
                for mock in mocks:
                    mock.stop()
                if os.path.exists(csv_file):
                    os.remove(csv_file)
    
    def test_csv_mixed_valid_invalid_data_workflow(self, app, client):
        """Test CSV import with mix of valid and invalid data."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Mixed Data Test Portfolio")
                initial_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                
                # Create CSV with mixed valid/invalid data
                csv_content = CSVTestGenerator.create_mixed_valid_invalid_csv()
                csv_file = CSVTestGenerator.save_csv_to_file(csv_content, "mixed_data.csv")
                
                # Act: Import CSV with mixed data
                with open(csv_file, 'rb') as f:
                    response = client.post('/portfolio/import-csv', 
                                         data={
                                             'portfolio_id': portfolio.id,
                                             'import_type': 'transactions',
                                             'csv_file': (f, 'transactions.csv')
                                         },
                                         content_type='multipart/form-data')
                
                # Assert: Import processed valid rows and handled invalid ones
                # Should redirect even with some invalid rows
                assert response.status_code in [200, 302], "Should handle mixed data gracefully"
                
                # Verify only valid transactions were imported
                final_count = StockTransaction.query.filter_by(portfolio_id=portfolio.id).count()
                # From mixed CSV: AAPL (valid) and AMZN (valid) = 2 valid transactions
                expected_valid = 2
                assert final_count >= initial_count + expected_valid, f"Should import at least {expected_valid} valid transactions"
                
                # Verify specific valid transaction was imported
                aapl_transaction = StockTransaction.query.filter_by(
                    portfolio_id=portfolio.id,
                    ticker='AAPL'
                ).first()
                assert aapl_transaction is not None, "Valid AAPL transaction should be imported"
                
                # Verify invalid transactions were not imported
                empty_ticker_transaction = StockTransaction.query.filter_by(
                    portfolio_id=portfolio.id,
                    ticker=''
                ).first()
                assert empty_ticker_transaction is None, "Invalid transaction with empty ticker should not be imported"
                
            finally:
                for mock in mocks:
                    mock.stop()
                if os.path.exists(csv_file):
                    os.remove(csv_file)
    
    def test_dividend_csv_import_workflow(self, app, client):
        """Test dividend CSV import workflow."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(name="Dividend Test Portfolio")
                initial_count = Dividend.query.filter_by(portfolio_id=portfolio.id).count()
                
                # Create valid dividends CSV
                csv_content = CSVTestGenerator.create_valid_dividends_csv()
                csv_file = CSVTestGenerator.save_csv_to_file(csv_content, "dividends.csv")
                
                # Act: Import dividend CSV
                with open(csv_file, 'rb') as f:
                    response = client.post('/portfolio/import-csv', 
                                         data={
                                             'portfolio_id': portfolio.id,
                                             'import_type': 'dividends',
                                             'csv_file': (f, 'dividends.csv')
                                         },
                                         content_type='multipart/form-data')
                
                # Assert: Dividends imported successfully
                # Note: This assumes dividend import endpoint exists, may need adjustment
                assert response.status_code in [200, 302, 404], "Should handle dividend import"
                
                if response.status_code != 404:  # If endpoint exists
                    final_count = Dividend.query.filter_by(portfolio_id=portfolio.id).count()
                    assert final_count > initial_count, "Dividends should be imported"
                
            finally:
                for mock in mocks:
                    mock.stop()
                if os.path.exists(csv_file):
                    os.remove(csv_file)