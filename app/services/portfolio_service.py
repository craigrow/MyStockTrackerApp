from app import db
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from datetime import datetime, date
from collections import defaultdict


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
    
    def get_portfolio_transactions(self, portfolio_id):
        return StockTransaction.query.filter_by(portfolio_id=portfolio_id).all()
    
    def get_portfolio_dividends(self, portfolio_id):
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
    
    def get_current_holdings(self, portfolio_id):
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
            cash_balance.last_updated = datetime.utcnow()
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