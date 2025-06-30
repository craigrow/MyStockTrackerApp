"""Test factories for integration tests."""
from datetime import date, datetime
from app import db
from app.models.portfolio import Portfolio, StockTransaction
from app.models.stock import Stock
from app.models.price import PriceHistory


class IntegrationTestFactory:
    """Factory for creating integration test data."""
    
    @staticmethod
    def create_portfolio_with_chart_data(user_id="test_user", name="Chart Test Portfolio"):
        """Create portfolio with data that generates valid charts."""
        # Create portfolio
        portfolio = Portfolio(
            name=name,
            description="Portfolio for chart testing",
            user_id=user_id
        )
        db.session.add(portfolio)
        db.session.flush()  # Get ID without committing
        
        # Create stocks
        stocks = [
            Stock(ticker="AAPL", name="Apple Inc.", sector="Technology"),
            Stock(ticker="VOO", name="Vanguard S&P 500 ETF", sector="ETF"),
            Stock(ticker="QQQ", name="Invesco QQQ Trust ETF", sector="ETF")
        ]
        for stock in stocks:
            db.session.merge(stock)  # Use merge to handle existing stocks
        
        # Create transaction on specific date
        purchase_date = date(2023, 1, 15)
        transaction = StockTransaction(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            transaction_type="BUY",
            date=purchase_date,
            price_per_share=150.00,
            shares=10.0,
            total_value=1500.00
        )
        db.session.add(transaction)
        
        # Create price history for chart alignment test
        base_price = 150.00
        for ticker in ["AAPL", "VOO", "QQQ"]:
            price_history = PriceHistory(
                ticker=ticker,
                date=purchase_date,
                close_price=base_price,  # Same starting value for all
                is_intraday=False,
                price_timestamp=datetime.combine(purchase_date, datetime.min.time()),
                last_updated=datetime.utcnow()
            )
            db.session.add(price_history)
        
        db.session.commit()
        return portfolio
    
    @staticmethod
    def create_multi_portfolio_scenario(user_id="test_user"):
        """Create multiple portfolios for testing."""
        portfolios = []
        
        # Portfolio 1: Tech stocks
        portfolio1 = Portfolio(
            name="Tech Portfolio",
            description="Technology stocks",
            user_id=user_id
        )
        db.session.add(portfolio1)
        db.session.flush()
        
        # Add AAPL transaction
        transaction1 = StockTransaction(
            portfolio_id=portfolio1.id,
            ticker="AAPL",
            transaction_type="BUY",
            date=date(2023, 1, 10),
            price_per_share=150.00,
            shares=5.0,
            total_value=750.00
        )
        db.session.add(transaction1)
        portfolios.append(portfolio1)
        
        # Portfolio 2: Mixed stocks
        portfolio2 = Portfolio(
            name="Mixed Portfolio",
            description="Diversified portfolio",
            user_id=user_id
        )
        db.session.add(portfolio2)
        db.session.flush()
        
        # Add GOOGL transaction
        transaction2 = StockTransaction(
            portfolio_id=portfolio2.id,
            ticker="GOOGL",
            transaction_type="BUY",
            date=date(2023, 1, 20),
            price_per_share=2500.00,
            shares=2.0,
            total_value=5000.00
        )
        db.session.add(transaction2)
        portfolios.append(portfolio2)
        
        # Portfolio 3: Small portfolio
        portfolio3 = Portfolio(
            name="Small Portfolio",
            description="Small test portfolio",
            user_id=user_id
        )
        db.session.add(portfolio3)
        db.session.flush()
        
        # Add MSFT transaction
        transaction3 = StockTransaction(
            portfolio_id=portfolio3.id,
            ticker="MSFT",
            transaction_type="BUY",
            date=date(2023, 2, 1),
            price_per_share=300.00,
            shares=3.0,
            total_value=900.00
        )
        db.session.add(transaction3)
        portfolios.append(portfolio3)
        
        db.session.commit()
        return portfolios
    
    @staticmethod
    def create_performance_test_data(user_id="test_user"):
        """Create data optimized for performance testing."""
        portfolio = Portfolio(
            name="Performance Test Portfolio",
            description="Portfolio for performance testing",
            user_id=user_id
        )
        db.session.add(portfolio)
        db.session.flush()
        
        # Create multiple transactions for realistic load
        tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        for i, ticker in enumerate(tickers):
            transaction = StockTransaction(
                portfolio_id=portfolio.id,
                ticker=ticker,
                transaction_type="BUY",
                date=date(2023, 1, 1 + i),
                price_per_share=100.00 + (i * 50),
                shares=10.0 - i,
                total_value=(100.00 + (i * 50)) * (10.0 - i)
            )
            db.session.add(transaction)
        
        db.session.commit()
        return portfolio