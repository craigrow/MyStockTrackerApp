"""Test data factories for efficient test setup."""
from datetime import date, datetime
from app.models.portfolio import Portfolio, StockTransaction, Dividend, CashBalance
from app.models.stock import Stock
from app.models.price import PriceHistory
from app import db


class PortfolioFactory:
    """Factory for creating test portfolios with related data."""
    
    @staticmethod
    def create_simple(user_id="test_user", name="Test Portfolio"):
        """Create a simple portfolio without transactions."""
        portfolio = Portfolio(
            name=name,
            description=f"Test portfolio: {name}",
            user_id=user_id
        )
        db.session.add(portfolio)
        db.session.commit()
        return portfolio
    
    @staticmethod
    def create_with_transactions(user_id="test_user", transaction_count=2):
        """Create portfolio with sample transactions."""
        portfolio = PortfolioFactory.create_simple(user_id)
        
        # Add sample transactions
        transactions = [
            StockTransaction(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            ),
            StockTransaction(
                portfolio_id=portfolio.id,
                ticker="GOOGL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=2500.00,
                shares=2.0,
                total_value=5000.00
            )
        ]
        
        for i, transaction in enumerate(transactions[:transaction_count]):
            db.session.add(transaction)
        
        db.session.commit()
        return portfolio
    
    @staticmethod
    def create_with_price_data(user_id="test_user"):
        """Create portfolio with transactions and price history."""
        portfolio = PortfolioFactory.create_with_transactions(user_id)
        
        # Add price history
        prices = [
            PriceHistory(
                ticker="AAPL",
                date=date.today(),
                close_price=160.00,
                is_intraday=False,
                price_timestamp=datetime.now()
            ),
            PriceHistory(
                ticker="GOOGL", 
                date=date.today(),
                close_price=2600.00,
                is_intraday=False,
                price_timestamp=datetime.now()
            )
        ]
        
        for price in prices:
            db.session.add(price)
        
        db.session.commit()
        return portfolio


class StockFactory:
    """Factory for creating test stocks."""
    
    @staticmethod
    def create(ticker="AAPL", name="Apple Inc.", sector="Technology"):
        """Create a stock with default or custom values."""
        stock = Stock(ticker=ticker, name=name, sector=sector)
        db.session.add(stock)
        db.session.commit()
        return stock
    
    @staticmethod
    def create_multiple(tickers=None):
        """Create multiple stocks."""
        if tickers is None:
            tickers = ["AAPL", "GOOGL", "MSFT", "VOO", "QQQ"]
        
        stocks = []
        stock_data = {
            "AAPL": ("Apple Inc.", "Technology"),
            "GOOGL": ("Alphabet Inc.", "Technology"),
            "MSFT": ("Microsoft Corporation", "Technology"),
            "VOO": ("Vanguard S&P 500 ETF", "ETF"),
            "QQQ": ("Invesco QQQ Trust ETF", "ETF")
        }
        
        for ticker in tickers:
            name, sector = stock_data.get(ticker, (f"{ticker} Corp", "Unknown"))
            stock = Stock(ticker=ticker, name=name, sector=sector)
            stocks.append(stock)
            db.session.add(stock)
        
        db.session.commit()
        return stocks


class TransactionFactory:
    """Factory for creating test transactions."""
    
    @staticmethod
    def create_buy(portfolio_id, ticker="AAPL", shares=10.0, price=150.00, transaction_date=None):
        """Create a buy transaction."""
        if transaction_date is None:
            transaction_date = date.today()
        
        transaction = StockTransaction(
            portfolio_id=portfolio_id,
            ticker=ticker,
            transaction_type="BUY",
            date=transaction_date,
            price_per_share=price,
            shares=shares,
            total_value=shares * price
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def create_sell(portfolio_id, ticker="AAPL", shares=5.0, price=160.00, transaction_date=None):
        """Create a sell transaction."""
        if transaction_date is None:
            transaction_date = date.today()
        
        transaction = StockTransaction(
            portfolio_id=portfolio_id,
            ticker=ticker,
            transaction_type="SELL",
            date=transaction_date,
            price_per_share=price,
            shares=shares,
            total_value=shares * price
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction