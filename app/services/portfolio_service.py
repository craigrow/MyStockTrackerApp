from app import db
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from datetime import datetime, date, timezone
from collections import defaultdict
from app.util.query_cache import query_cache
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PortfolioService:
    
    def create_portfolio(self, name, user_id, description=None):
        portfolio = Portfolio(
            name=name,
            user_id=user_id,
            description=description
        )
        db.session.add(portfolio)
        db.session.commit()
        return portfolio
    
    def get_portfolio(self, portfolio_id):
        return Portfolio.query.get(portfolio_id)
    
    def add_transaction(self, portfolio_id, ticker, transaction_type, date, price_per_share, shares):
        total_value = price_per_share * shares
        transaction = StockTransaction(
            portfolio_id=portfolio_id,
            ticker=ticker,
            transaction_type=transaction_type,
            date=date,
            price_per_share=price_per_share,
            shares=shares,
            total_value=total_value
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def add_dividend(self, portfolio_id, ticker, payment_date, total_amount):
        dividend = Dividend(
            portfolio_id=portfolio_id,
            ticker=ticker,
            payment_date=payment_date,
            total_amount=total_amount
        )
        db.session.add(dividend)
        db.session.commit()
        return dividend
    
    @query_cache(ttl_seconds=60)  # Cache for 1 minute
    def get_portfolio_transactions(self, portfolio_id):
        """Get all transactions for a portfolio with caching"""
        logger.debug(f"Fetching transactions for portfolio {portfolio_id}")
        return StockTransaction.query.filter_by(portfolio_id=portfolio_id).all()
    
    @query_cache(ttl_seconds=60)  # Cache for 1 minute
    def get_portfolio_dividends(self, portfolio_id):
        """Get all dividends for a portfolio with caching"""
        logger.debug(f"Fetching dividends for portfolio {portfolio_id}")
        return Dividend.query.filter_by(portfolio_id=portfolio_id).all()
    
    def calculate_portfolio_value(self, portfolio_id):
        from app.services.price_service import PriceService
        price_service = PriceService()
        
        holdings = self.get_current_holdings(portfolio_id)
        total_value = 0.0
        
        for ticker, shares in holdings.items():
            current_price = price_service.get_current_price(ticker)
            if current_price:
                total_value += shares * current_price
        
        return total_value
    
    def get_portfolio_current_value(self, portfolio_id):
        """Get current portfolio value including cash balance"""
        portfolio_value = self.calculate_portfolio_value(portfolio_id)
        cash_balance = self.get_cash_balance(portfolio_id)
        return portfolio_value + cash_balance
    
    @query_cache(ttl_seconds=60)  # Cache for 1 minute
    def get_current_holdings(self, portfolio_id):
        """Get current holdings for a portfolio with caching"""
        logger.debug(f"Calculating current holdings for portfolio {portfolio_id}")
        transactions = self.get_portfolio_transactions(portfolio_id)
        holdings = defaultdict(float)
        
        for transaction in transactions:
            if transaction.transaction_type == "BUY":
                holdings[transaction.ticker] += transaction.shares
            elif transaction.transaction_type == "SELL":
                holdings[transaction.ticker] -= transaction.shares
        
        # Remove tickers with zero or negative holdings
        return {ticker: shares for ticker, shares in holdings.items() if shares > 0}
    
    def calculate_transaction_performance(self, transaction_id):
        from app.services.price_service import PriceService
        price_service = PriceService()
        
        transaction = StockTransaction.query.get(transaction_id)
        if not transaction:
            return None
        
        current_price = price_service.get_current_price(transaction.ticker)
        if not current_price:
            return None
        
        current_value = transaction.shares * current_price
        gain_loss = current_value - transaction.total_value
        gain_loss_percentage = (gain_loss / transaction.total_value) * 100
        
        return {
            'gain_loss': gain_loss,
            'gain_loss_percentage': gain_loss_percentage,
            'current_value': current_value
        }
    
    def update_cash_balance(self, portfolio_id, balance):
        cash_balance = CashBalance.query.get(portfolio_id)
        if cash_balance:
            cash_balance.balance = balance
            cash_balance.last_updated = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            cash_balance = CashBalance(
                portfolio_id=portfolio_id,
                balance=balance
            )
            db.session.add(cash_balance)
        
        db.session.commit()
        return cash_balance
    
    def get_cash_balance(self, portfolio_id):
        cash_balance = CashBalance.query.get(portfolio_id)
        return cash_balance.balance if cash_balance else 0.0
    
    def get_all_portfolios(self):
        return Portfolio.query.all()
    
    def get_portfolio_current_value(self, portfolio_id):
        """Get current market value of portfolio"""
        from app.services.price_service import PriceService
        price_service = PriceService()
        
        holdings = self.get_current_holdings(portfolio_id)
        total_value = 0.0
        
        for ticker, shares in holdings.items():
            try:
                current_price = price_service.get_current_price(ticker, use_stale=True)
                if current_price:
                    total_value += shares * current_price
            except Exception:
                pass
        
        # Add cash balance
        total_value += self.get_cash_balance(portfolio_id)
        
        return total_value
    
    def delete_transaction(self, transaction_id, portfolio_id):
        """Delete a transaction if it belongs to the specified portfolio"""
        transaction = StockTransaction.query.get(transaction_id)
        
        if not transaction:
            return False
        
        # Verify transaction belongs to the specified portfolio
        if transaction.portfolio_id != portfolio_id:
            return False
        
        try:
            db.session.delete(transaction)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def update_transaction(self, transaction_id, portfolio_id, **kwargs):
        """Update a transaction if it belongs to the specified portfolio"""
        transaction = StockTransaction.query.get(transaction_id)
        
        if not transaction:
            return None
        
        # Verify transaction belongs to the specified portfolio
        if transaction.portfolio_id != portfolio_id:
            return None
        
        try:
            # Update allowed fields
            for field, value in kwargs.items():
                if hasattr(transaction, field):
                    setattr(transaction, field, value)
            
            # Recalculate total_value if price or shares changed
            if 'price_per_share' in kwargs or 'shares' in kwargs:
                transaction.total_value = transaction.price_per_share * transaction.shares
            
            db.session.commit()
            return transaction
        except Exception:
            db.session.rollback()
            return None