from flask import Blueprint, render_template, request
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from collections import defaultdict

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
@main_blueprint.route('/dashboard')
def dashboard():
    portfolio_service = PortfolioService()
    price_service = PriceService()
    
    # Get all portfolios
    portfolios = portfolio_service.get_all_portfolios()
    
    # Get current portfolio (from URL param or first available)
    portfolio_id = request.args.get('portfolio_id')
    current_portfolio = None
    
    if portfolio_id:
        current_portfolio = portfolio_service.get_portfolio(portfolio_id)
    elif portfolios:
        current_portfolio = portfolios[0]
    
    # Initialize data
    portfolio_stats = None
    holdings = []
    recent_transactions = []
    
    if current_portfolio:
        # Get portfolio statistics
        portfolio_stats = calculate_portfolio_stats(current_portfolio, portfolio_service, price_service)
        
        # Get current holdings with performance
        holdings = get_holdings_with_performance(current_portfolio.id, portfolio_service, price_service)
        
        # Get recent transactions (last 10)
        recent_transactions = portfolio_service.get_portfolio_transactions(current_portfolio.id)[-10:]
        recent_transactions.reverse()  # Show most recent first
    
    return render_template('dashboard.html',
                         portfolios=portfolios,
                         current_portfolio=current_portfolio,
                         portfolio_stats=portfolio_stats,
                         holdings=holdings,
                         recent_transactions=recent_transactions)

def calculate_portfolio_stats(portfolio, portfolio_service, price_service):
    """Calculate portfolio statistics"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio.id)
    dividends = portfolio_service.get_portfolio_dividends(portfolio.id)
    cash_balance = portfolio_service.get_cash_balance(portfolio.id)
    
    total_invested = sum(t.total_value for t in transactions if t.transaction_type == 'BUY')
    total_sold = sum(t.total_value for t in transactions if t.transaction_type == 'SELL')
    total_dividends = sum(d.total_amount for d in dividends)
    
    # Calculate current portfolio value
    current_value = 0
    holdings = portfolio_service.get_current_holdings(portfolio.id)
    
    for ticker, shares in holdings.items():
        try:
            current_price = price_service.get_current_price(ticker)
            if current_price:
                current_value += shares * current_price
        except:
            # If price fetch fails, use last known price or skip
            pass
    
    current_value += cash_balance
    
    # Calculate gains
    net_invested = total_invested - total_sold
    total_gain_loss = current_value - net_invested + total_dividends
    gain_loss_percentage = (total_gain_loss / net_invested * 100) if net_invested > 0 else 0
    
    return {
        'current_value': current_value,
        'total_invested': net_invested,
        'total_gain_loss': total_gain_loss,
        'gain_loss_percentage': gain_loss_percentage,
        'cash_balance': cash_balance,
        'total_dividends': total_dividends
    }

def get_holdings_with_performance(portfolio_id, portfolio_service, price_service):
    """Get holdings with current prices and performance"""
    holdings = portfolio_service.get_current_holdings(portfolio_id)
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    # Calculate cost basis for each ticker
    cost_basis = defaultdict(lambda: {'total_cost': 0, 'total_shares': 0})
    
    for transaction in transactions:
        if transaction.transaction_type == 'BUY':
            cost_basis[transaction.ticker]['total_cost'] += transaction.total_value
            cost_basis[transaction.ticker]['total_shares'] += transaction.shares
        elif transaction.transaction_type == 'SELL':
            # Proportionally reduce cost basis
            if cost_basis[transaction.ticker]['total_shares'] > 0:
                cost_per_share = cost_basis[transaction.ticker]['total_cost'] / cost_basis[transaction.ticker]['total_shares']
                cost_basis[transaction.ticker]['total_cost'] -= transaction.shares * cost_per_share
                cost_basis[transaction.ticker]['total_shares'] -= transaction.shares
    
    holdings_data = []
    
    for ticker, shares in holdings.items():
        try:
            current_price = price_service.get_current_price(ticker) or 0
            market_value = shares * current_price
            
            # Calculate cost basis for remaining shares
            avg_cost = cost_basis[ticker]['total_cost'] / cost_basis[ticker]['total_shares'] if cost_basis[ticker]['total_shares'] > 0 else 0
            total_cost = shares * avg_cost
            
            gain_loss = market_value - total_cost
            gain_loss_percentage = (gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            holdings_data.append({
                'ticker': ticker,
                'shares': shares,
                'current_price': current_price,
                'market_value': market_value,
                'cost_basis': total_cost,
                'gain_loss': gain_loss,
                'gain_loss_percentage': gain_loss_percentage
            })
        except:
            # If price fetch fails, show holding without performance data
            holdings_data.append({
                'ticker': ticker,
                'shares': shares,
                'current_price': 0,
                'market_value': 0,
                'cost_basis': 0,
                'gain_loss': 0,
                'gain_loss_percentage': 0
            })
    
    return holdings_data
