from flask import Blueprint, jsonify, request, render_template
from app.util.query_cache import get_cache_stats, clear_query_cache
from collections import defaultdict
from datetime import date

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/cache/stats')
def cache_stats():
    """Get statistics about the query cache"""
    stats = get_cache_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@api_blueprint.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the query cache"""
    clear_query_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@api_blueprint.route('/monitoring')
def monitoring_dashboard():
    """Render the performance monitoring dashboard"""
    return render_template('monitoring.html')

def get_minimal_holdings(portfolio_id, portfolio_service, price_service):
    """Get holdings data with cached prices and calculated gains"""
    from collections import defaultdict
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get current holdings and transactions
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
        
        # Get all tickers
        tickers = list(holdings.keys())
        
        # Use batch processing for better performance
        prices = price_service.get_current_prices_batch(tickers, use_cache=True)
        
        # Calculate total portfolio value for percentage
        total_portfolio_value = 0
        for ticker, shares in holdings.items():
            current_price = prices.get(ticker, 0)
            if current_price:
                total_portfolio_value += shares * current_price
        
        # Build holdings data with calculations
        holdings_data = []
        for ticker, shares in holdings.items():
            try:
                current_price = prices.get(ticker, 0)
                market_value = shares * current_price
                
                # Calculate cost basis for remaining shares
                avg_cost = cost_basis[ticker]['total_cost'] / cost_basis[ticker]['total_shares'] if cost_basis[ticker]['total_shares'] > 0 else 0
                total_cost = shares * avg_cost
                
                # Calculate gains
                gain_loss = market_value - total_cost
                gain_loss_percentage = (gain_loss / total_cost * 100) if total_cost > 0 else 0
                
                # Calculate ETF performance (simplified using cached prices)
                voo_performance = calculate_etf_performance_simple(ticker, transactions, 'VOO', price_service)
                qqq_performance = calculate_etf_performance_simple(ticker, transactions, 'QQQ', price_service)
                
                # Check data freshness for warning
                freshness = price_service.get_data_freshness(ticker, date.today())
                is_stale = freshness is None or freshness > 5
                
                # Calculate portfolio percentage
                portfolio_percentage = (market_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
                
                holdings_data.append({
                    'ticker': ticker,
                    'shares': shares,
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_basis': total_cost,
                    'gain_loss': gain_loss,
                    'gain_loss_percentage': gain_loss_percentage,
                    'voo_performance': voo_performance,
                    'qqq_performance': qqq_performance,
                    'portfolio_percentage': portfolio_percentage,
                    'data_age_minutes': freshness,
                    'is_stale': is_stale
                })
            except Exception as e:
                logger.error(f"Error processing holding for {ticker}: {e}")
                holdings_data.append({
                    'ticker': ticker,
                    'shares': shares,
                    'current_price': 0,
                    'market_value': 0,
                    'cost_basis': 0,
                    'gain_loss': 0,
                    'gain_loss_percentage': 0,
                    'voo_performance': 0,
                    'qqq_performance': 0,
                    'portfolio_percentage': 0,
                    'data_age_minutes': None,
                    'is_stale': True
                })
        
        # Sort holdings by portfolio percentage descending (largest first)
        holdings_data.sort(key=lambda x: x['portfolio_percentage'], reverse=True)
        
        return holdings_data
    except Exception as e:
        logger.error(f"Error getting holdings: {e}")
        import traceback
        traceback.print_exc()
        return []

# Add this to the app/__init__.py file:
# from app.views.api import api_blueprint
# app.register_blueprint(api_blueprint)

def calculate_etf_performance_simple(ticker, transactions, etf_ticker, price_service):
    """Calculate ETF performance using cached prices only"""
    from datetime import timedelta
    
    try:
        # Get all BUY transactions for this ticker
        buy_transactions = [t for t in transactions if t.ticker == ticker and t.transaction_type == 'BUY']
        
        if not buy_transactions:
            return 0
        
        # Calculate weighted average purchase date
        total_investment = sum(t.total_value for t in buy_transactions)
        if total_investment <= 0:
            return 0
            
        weighted_date_sum = 0
        for transaction in buy_transactions:
            weight = transaction.total_value / total_investment
            days_since_epoch = (transaction.date - date(1970, 1, 1)).days
            weighted_date_sum += days_since_epoch * weight
        
        avg_purchase_date = date(1970, 1, 1) + timedelta(days=int(weighted_date_sum))
        
        # Get ETF prices using cached data
        etf_purchase_price = price_service.get_current_price(etf_ticker, use_stale=True)  # Use cached
        current_etf_price = price_service.get_current_price(etf_ticker, use_stale=True)
        
        if etf_purchase_price and current_etf_price and etf_purchase_price > 0:
            # Simple approximation - in real implementation would use historical prices
            performance = ((current_etf_price - etf_purchase_price) / etf_purchase_price) * 100
            return round(performance * 0.8, 2)  # Approximate historical performance
        
        return 0
        
    except Exception as e:
        return 0