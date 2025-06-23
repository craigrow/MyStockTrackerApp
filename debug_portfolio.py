#!/usr/bin/env python3

from app import create_app
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.views.main import calculate_portfolio_stats
from datetime import date

def debug_portfolio():
    app = create_app()
    with app.app_context():
        portfolio_service = PortfolioService()
        price_service = PriceService()
        
        # Get portfolios
        portfolios = portfolio_service.get_all_portfolios()
        print(f"Found {len(portfolios)} portfolios")
        
        if not portfolios:
            print("No portfolios found!")
            return
            
        portfolio = portfolios[0]
        print(f"Portfolio: {portfolio.name} (ID: {portfolio.id})")
        
        # Get basic data
        transactions = portfolio_service.get_portfolio_transactions(portfolio.id)
        dividends = portfolio_service.get_portfolio_dividends(portfolio.id)
        holdings = portfolio_service.get_current_holdings(portfolio.id)
        cash_balance = portfolio_service.get_cash_balance(portfolio.id)
        
        print(f"Transactions: {len(transactions)}")
        print(f"Dividends: {len(dividends)}")
        print(f"Holdings: {len(holdings)} stocks")
        print(f"Cash balance: ${cash_balance}")
        
        # Calculate basic stats
        total_invested = sum(t.total_value for t in transactions if t.transaction_type == 'BUY')
        total_sold = sum(t.total_value for t in transactions if t.transaction_type == 'SELL')
        total_dividends = sum(d.total_amount for d in dividends)
        
        print(f"Total invested: ${total_invested}")
        print(f"Total sold: ${total_sold}")
        print(f"Total dividends: ${total_dividends}")
        print(f"Net invested: ${total_invested - total_sold}")
        
        # Check current portfolio value calculation
        current_value = 0
        print("\nHoldings breakdown:")
        for ticker, shares in holdings.items():
            try:
                current_price = price_service.get_current_price(ticker, use_stale=True)
                if current_price:
                    value = shares * current_price
                    current_value += value
                    print(f"  {ticker}: {shares} shares @ ${current_price} = ${value}")
                else:
                    print(f"  {ticker}: {shares} shares @ NO PRICE")
            except Exception as e:
                print(f"  {ticker}: ERROR - {e}")
        
        current_value += cash_balance
        print(f"\nTotal portfolio value: ${current_value}")
        
        # Try full stats calculation
        try:
            stats = calculate_portfolio_stats(portfolio, portfolio_service, price_service)
            print(f"\nCalculated stats:")
            print(f"  Current value: ${stats.get('current_value', 'ERROR')}")
            print(f"  Total gain/loss: ${stats.get('total_gain_loss', 'ERROR')}")
            print(f"  Portfolio daily change: ${stats.get('portfolio_daily_dollar_change', 'ERROR')}")
            print(f"  VOO daily change: ${stats.get('voo_daily_dollar_change', 'ERROR')}")
            print(f"  QQQ daily change: ${stats.get('qqq_daily_dollar_change', 'ERROR')}")
        except Exception as e:
            print(f"\nStats calculation ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_portfolio()