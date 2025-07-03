import pytest
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import StockTransaction
from datetime import date
import json


class TestDeleteTransactionService:
    """Test the portfolio service delete_transaction method"""
    
    @pytest.fixture
    def portfolio_service(self, app):
        with app.app_context():
            return PortfolioService()
    
    def test_delete_transaction_success(self, portfolio_service, sample_portfolio, app):
        """Test successful transaction deletion"""
        with app.app_context():
            # Add a transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            transaction_id = transaction.id
            portfolio_id = transaction.portfolio_id
            
            # Verify transaction exists
            existing_transaction = StockTransaction.query.get(transaction_id)
            assert existing_transaction is not None
            
            # Delete transaction
            result = portfolio_service.delete_transaction(transaction_id, portfolio_id)
            
            # Verify deletion
            assert result is True
            deleted_transaction = StockTransaction.query.get(transaction_id)
            assert deleted_transaction is None
    
    def test_delete_nonexistent_transaction(self, portfolio_service, sample_portfolio, app):
        """Test deletion of non-existent transaction"""
        with app.app_context():
            result = portfolio_service.delete_transaction(99999, sample_portfolio.id)
            assert result is False
    
    def test_delete_transaction_wrong_portfolio(self, portfolio_service, sample_portfolio, app):
        """Test deletion with wrong portfolio ID"""
        with app.app_context():
            # Add a transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            # Create another portfolio
            other_portfolio = portfolio_service.create_portfolio(
                name="Other Portfolio",
                user_id="other_user"
            )
            
            # Try to delete transaction with wrong portfolio ID
            result = portfolio_service.delete_transaction(
                transaction.id, 
                other_portfolio.id
            )
            assert result is False
            
            # Verify transaction still exists
            existing_transaction = StockTransaction.query.get(transaction.id)
            assert existing_transaction is not None
    
    def test_holdings_recalculation_after_delete(self, portfolio_service, sample_portfolio, app):
        """Test that holdings are recalculated after transaction deletion"""
        with app.app_context():
            # Add multiple transactions
            buy_transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.0,
                shares=10.0
            )
            
            sell_transaction = portfolio_service.add_transaction(
                portfolio_id=sample_portfolio.id,
                ticker="AAPL",
                transaction_type="SELL",
                date=date(2023, 2, 15),
                price_per_share=160.0,
                shares=5.0
            )
            
            # Check initial holdings
            holdings = portfolio_service.get_current_holdings(sample_portfolio.id)
            assert holdings["AAPL"] == 5.0  # 10 - 5 = 5
            
            # Delete sell transaction
            portfolio_service.delete_transaction(sell_transaction.id, sample_portfolio.id)
            
            # Check updated holdings
            updated_holdings = portfolio_service.get_current_holdings(sample_portfolio.id)
            assert updated_holdings["AAPL"] == 10.0  # Only buy transaction remains


class TestDeleteTransactionAPI:
    """Test the API endpoint for deleting transactions"""
    
    def test_delete_transaction_endpoint_success(self, client, sample_portfolio, app):
        """Test successful deletion via API endpoint"""
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
            
            response = client.delete(f'/portfolio/delete-transaction/{transaction_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'message' in data
            
            # Verify transaction is deleted
            deleted_transaction = StockTransaction.query.get(transaction_id)
            assert deleted_transaction is None
    
    def test_delete_transaction_endpoint_not_found(self, client, app):
        """Test deletion of non-existent transaction via API"""
        with app.app_context():
            response = client.delete('/portfolio/delete-transaction/99999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data
    
    def test_delete_transaction_endpoint_invalid_method(self, client, sample_portfolio, app):
        """Test that only DELETE method is allowed"""
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
            
            response = client.get(f'/portfolio/delete-transaction/{transaction_id}')
            assert response.status_code == 405  # Method Not Allowed