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
    """Get minimal holdings data for fast initial loading"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get current holdings
        holdings = portfolio_service.get_current_holdings(portfolio_id)
        
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
        
        # Build minimal holdings data
        holdings_data = []
        for ticker, shares in holdings.items():
            try:
                current_price = prices.get(ticker, 0)
                market_value = shares * current_price
                
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
                    'cost_basis': 0,  # Will be calculated in detailed view
                    'gain_loss': 0,   # Will be calculated in detailed view
                    'gain_loss_percentage': 0,  # Will be calculated in detailed view
                    'voo_performance': 0,  # Will be calculated in detailed view
                    'qqq_performance': 0,  # Will be calculated in detailed view
                    'portfolio_percentage': portfolio_percentage,
                    'data_age_minutes': freshness,
                    'is_stale': is_stale
                })
            except Exception as e:
                logger.error(f"Error processing minimal holding for {ticker}: {e}")
                # Add a placeholder for the ticker
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
        logger.error(f"Error getting minimal holdings: {e}")
        import traceback
        traceback.print_exc()
        return []

# Add this to the app/__init__.py file:
# from app.views.api import api_blueprint
# app.register_blueprint(api_blueprint)
