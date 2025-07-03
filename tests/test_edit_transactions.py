import pytest
from datetime import date
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import StockTransaction
from app import db


class TestEditTransactionService:
    """Test the edit transaction service functionality"""
    
    def test_update_transaction_success(self, app, sample_portfolio):
        """Test successful transaction update"""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            # Create a transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            transaction_id = transaction.id
            
            # Update the transaction
            updated_transaction = portfolio_service.update_transaction(
                transaction_id=transaction_id,
                portfolio_id=sample_portfolio.id,
                ticker="MSFT",
                price_per_share=200.0,
                shares=5.0
            )
            
            # Verify update was successful
            assert updated_transaction is not None
            assert updated_transaction.ticker == "MSFT"
            assert updated_transaction.price_per_share == 200.0
            assert updated_transaction.shares == 5.0
            assert updated_transaction.total_value == 1000.0  # 200 * 5
    
    def test_update_transaction_recalculates_total_value(self, app, sample_portfolio):
        """Test that total_value is recalculated when price or shares change"""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            # Create a transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=100.0,
                shares=10.0
            )
            
            # Update only price
            updated_transaction = portfolio_service.update_transaction(
                transaction_id=transaction.id,
                portfolio_id=sample_portfolio.id,
                price_per_share=150.0
            )
            
            assert updated_transaction.total_value == 1500.0  # 150 * 10
            
            # Update only shares
            updated_transaction = portfolio_service.update_transaction(
                transaction_id=transaction.id,
                portfolio_id=sample_portfolio.id,
                shares=20.0
            )
            
            assert updated_transaction.total_value == 3000.0  # 150 * 20
    
    def test_update_nonexistent_transaction(self, app, sample_portfolio):
        """Test updating a transaction that doesn't exist"""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            result = portfolio_service.update_transaction(
                transaction_id="nonexistent-id",
                portfolio_id=sample_portfolio.id,
                ticker="AAPL"
            )
            
            assert result is None
    
    def test_update_transaction_wrong_portfolio(self, app, sample_portfolio):
        """Test updating a transaction with wrong portfolio ID"""
        with app.app_context():
            portfolio_service = PortfolioService()
            
            # Create a transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            # Try to update with wrong portfolio ID
            result = portfolio_service.update_transaction(
                transaction_id=transaction.id,
                portfolio_id="wrong-portfolio-id",
                ticker="MSFT"
            )
            
            assert result is None
            
            # Verify original transaction is unchanged
            original_transaction = StockTransaction.query.get(transaction.id)
            assert original_transaction.ticker == "AAPL"


class TestEditTransactionAPI:
    """Test the edit transaction API endpoints"""
    
    def test_edit_transaction_endpoint_success(self, client, sample_portfolio, app):
        """Test successful transaction edit via API"""
        with app.app_context():
            # Create a transaction
            portfolio_service = PortfolioService()
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            transaction_id = transaction.id
            
            # Update the transaction via API
            response = client.put(f'/portfolio/edit-transaction/{transaction_id}', 
                                json={
                                    'ticker': 'MSFT',
                                    'price_per_share': 200.0,
                                    'shares': 5.0,
                                    'date': '2023-02-01'
                                })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'updated successfully' in data['message']
            
            # Verify the transaction was updated in database
            updated_transaction = StockTransaction.query.get(transaction_id)
            assert updated_transaction.ticker == "MSFT"
            assert updated_transaction.price_per_share == 200.0
            assert updated_transaction.shares == 5.0
            assert updated_transaction.date == date(2023, 2, 1)
    
    def test_edit_transaction_endpoint_not_found(self, client):
        """Test editing a non-existent transaction"""
        response = client.put('/portfolio/edit-transaction/nonexistent-id', 
                            json={'ticker': 'AAPL'})
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error']
    
    def test_edit_transaction_endpoint_invalid_method(self, client, sample_portfolio, app):
        """Test that only PUT method is allowed"""
        with app.app_context():
            # Create a transaction
            portfolio_service = PortfolioService()
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            transaction_id = transaction.id
            
            response = client.get(f'/portfolio/edit-transaction/{transaction_id}')
            assert response.status_code == 405  # Method Not Allowed
    
    def test_edit_transaction_endpoint_invalid_json(self, client, sample_portfolio, app):
        """Test editing with invalid JSON data"""
        with app.app_context():
            # Create a transaction
            portfolio_service = PortfolioService()
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            transaction_id = transaction.id
            
            # Send invalid data
            response = client.put(f'/portfolio/edit-transaction/{transaction_id}', 
                                data="invalid json")
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data