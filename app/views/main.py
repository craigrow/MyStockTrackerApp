from flask import Blueprint, render_template, request, jsonify
from app.services.portfolio_service import PortfolioService
from app.services.price_service import PriceService
from app.services.background_tasks import background_updater
from collections import defaultdict
from datetime import datetime, date, timedelta
import pandas as pd
from app.models.cache import PortfolioCache
from app import db
import uuid

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/api/price-update-progress')
def price_update_progress():
    """Get current price update progress"""
    progress = background_updater.get_progress()
    return jsonify(progress)

@main_blueprint.route('/api/refresh-holdings/<portfolio_id>')
def refresh_holdings(portfolio_id):
    """Get refreshed holdings data"""
    try:
        portfolio_service = PortfolioService()
        price_service = PriceService()
        
        holdings = get_holdings_with_performance(portfolio_id, portfolio_service, price_service, use_stale=False)
        
        return jsonify({
            'success': True,
            'holdings': holdings,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_blueprint.route('/api/refresh-all-prices/<portfolio_id>')
def refresh_all_prices(portfolio_id):
    """Refresh all prices including holdings and ETFs"""
    try:
        portfolio_service = PortfolioService()
        price_service = PriceService()
        
        # Get all tickers that need refreshing
        holdings = portfolio_service.get_current_holdings(portfolio_id)
        all_tickers = list(holdings.keys()) + ['VOO', 'QQQ']
        
        # Force refresh all prices
        refreshed_count = 0
        for ticker in all_tickers:
            try:
                price_service.get_current_price(ticker, use_stale=False)
                refreshed_count += 1
            except Exception as e:
                print(f"Failed to refresh {ticker}: {e}")
        
        # Get updated holdings data
        updated_holdings = get_holdings_with_performance(portfolio_id, portfolio_service, price_service, use_stale=False)
        
        return jsonify({
            'success': True,
            'refreshed_count': refreshed_count,
            'total_tickers': len(all_tickers),
            'holdings': updated_holdings,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    data_warnings = []
    
    if current_portfolio:
        # Check for stale data and show clear warnings
        holdings = portfolio_service.get_current_holdings(current_portfolio.id)
        stale_holdings = []
        stale_etfs = []
        
        # Check holdings for stale data
        for ticker in holdings.keys():
            freshness = price_service.get_data_freshness(ticker, date.today())
            if freshness is None or freshness > 15:  # More than 15 minutes old
                stale_holdings.append(ticker)
        
        # Check ETFs separately
        for etf in ['VOO', 'QQQ']:
            freshness = price_service.get_data_freshness(etf, date.today())
            if freshness is None or freshness > 15:
                stale_etfs.append(etf)
        
        # Only show warning if holdings have stale data
        if stale_holdings:
            market_open = is_market_open_now()
            if market_open:
                data_warnings.append(f"⚠️ MARKET IS OPEN: Price data for {len(stale_holdings)} holdings is outdated. Prices shown may not reflect current market values.")
            else:
                data_warnings.append(f"ℹ️ Market is closed. Showing last available prices for {len(stale_holdings)} holdings.")
        
        stale_tickers = stale_holdings + stale_etfs  # Keep for button logic
        # Check if we're in testing mode
        import os
        is_testing = os.environ.get('TESTING') == 'True' or 'pytest' in os.environ.get('_', '')
        
        if is_testing:
            # Skip caching during tests to avoid session issues
            portfolio_stats = calculate_portfolio_stats(current_portfolio, portfolio_service, price_service)
            chart_data = generate_chart_data(current_portfolio.id, portfolio_service, price_service)
        else:
            # Use caching in production
            try:
                market_date = get_last_market_date()
                is_market_closed = not is_market_open_now()
                
                # Try to get cached data if market is closed
                portfolio_stats = None
                chart_data = None
                
                if is_market_closed:
                    portfolio_stats = get_cached_portfolio_stats(current_portfolio.id, market_date)
                    chart_data = get_cached_chart_data(current_portfolio.id, market_date)
                
                # Check if cached stats are valid (not zeros)
                if not portfolio_stats or portfolio_stats.get('current_value', 0) == 0:
                    print("[CACHE] Calculating fresh portfolio stats (no cache or zero values)")
                    portfolio_stats = calculate_portfolio_stats(current_portfolio, portfolio_service, price_service)
                    if is_market_closed and portfolio_stats:
                        cache_portfolio_stats(current_portfolio.id, market_date, portfolio_stats)
                else:
                    print("[CACHE] Using cached base stats, calculating fresh daily changes")
                    # Always recalculate daily changes for accuracy
                    daily_changes = calculate_daily_changes(current_portfolio.id, portfolio_service, price_service)
                    portfolio_stats.update(daily_changes)
                
                if not chart_data:
                    print("[CACHE] Calculating fresh chart data")
                    chart_data = generate_chart_data(current_portfolio.id, portfolio_service, price_service)
                    if is_market_closed and chart_data:
                        cache_chart_data(current_portfolio.id, market_date, chart_data)
                else:
                    print("[CACHE] Using cached chart data")
            except Exception as e:
                print(f"[CACHE] Error in caching logic: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to normal calculation
                portfolio_stats = calculate_portfolio_stats(current_portfolio, portfolio_service, price_service)
                chart_data = generate_chart_data(current_portfolio.id, portfolio_service, price_service)
        
        # Get current holdings with performance (use stale data for fast load)
        holdings = get_holdings_with_performance(current_portfolio.id, portfolio_service, price_service, use_stale=True)
        
        # Get recent transactions (last 10)
        recent_transactions = portfolio_service.get_portfolio_transactions(current_portfolio.id)[-10:]
        recent_transactions.reverse()  # Show most recent first
    else:
        chart_data = None
    
    return render_template('dashboard.html',
                         portfolios=portfolios,
                         current_portfolio=current_portfolio,
                         portfolio_stats=portfolio_stats,
                         holdings=holdings,
                         recent_transactions=recent_transactions,
                         chart_data=chart_data,
                         data_warnings=data_warnings,
                         update_progress={'status': 'disabled'},
                         stale_tickers=stale_holdings if 'stale_holdings' in locals() else [])

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
            current_price = price_service.get_current_price(ticker, use_stale=True)
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
    
    # Calculate ETF equivalent values
    voo_equivalent = calculate_current_etf_equivalent(portfolio.id, portfolio_service, price_service, 'VOO')
    qqq_equivalent = calculate_current_etf_equivalent(portfolio.id, portfolio_service, price_service, 'QQQ')
    
    # Calculate ETF gains/losses
    voo_gain_loss = voo_equivalent - net_invested if voo_equivalent else 0
    qqq_gain_loss = qqq_equivalent - net_invested if qqq_equivalent else 0
    
    # Calculate ETF gain/loss percentages
    voo_gain_loss_percentage = (voo_gain_loss / net_invested * 100) if net_invested > 0 else 0
    qqq_gain_loss_percentage = (qqq_gain_loss / net_invested * 100) if net_invested > 0 else 0
    
    # Calculate daily changes
    daily_changes = calculate_daily_changes(portfolio.id, portfolio_service, price_service)
    
    stats = {
        'current_value': current_value,
        'total_invested': net_invested,
        'total_gain_loss': total_gain_loss,
        'gain_loss_percentage': gain_loss_percentage,
        'cash_balance': cash_balance,
        'total_dividends': total_dividends,
        'voo_equivalent': voo_equivalent or 0,
        'qqq_equivalent': qqq_equivalent or 0,
        'voo_gain_loss': voo_gain_loss,
        'qqq_gain_loss': qqq_gain_loss,
        'voo_gain_loss_percentage': voo_gain_loss_percentage,
        'qqq_gain_loss_percentage': qqq_gain_loss_percentage
    }
    
    # Merge daily changes into stats
    stats.update(daily_changes)
    
    return stats

def get_holdings_with_performance(portfolio_id, portfolio_service, price_service, use_stale=False):
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
            current_price = price_service.get_current_price(ticker, use_stale=use_stale) or 0
            market_value = shares * current_price
            
            # Check data freshness for warning
            freshness = price_service.get_data_freshness(ticker, date.today())
            is_stale = freshness is None or freshness > 5
            
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
                'gain_loss_percentage': gain_loss_percentage,
                'data_age_minutes': freshness,
                'is_stale': is_stale
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
                'gain_loss_percentage': 0,
                'data_age_minutes': None,
                'is_stale': True
            })
    
    return holdings_data

def generate_chart_data(portfolio_id, portfolio_service, price_service):
    """Generate chart data for portfolio performance visualization"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    if not transactions:
        return None
    
    # Get date range from first transaction to today
    end_date = date.today()
    start_date = min(t.date for t in transactions)
    
    # Get all unique tickers from transactions
    tickers = list(set(t.ticker for t in transactions))
    etf_tickers = ['VOO', 'QQQ']
    all_tickers = tickers + etf_tickers
    
    # Batch fetch price histories for all tickers
    print(f"[API] Batch fetching price histories for {len(all_tickers)} tickers...")
    price_histories = {}
    for ticker in all_tickers:
        price_histories[ticker] = get_ticker_price_dataframe(ticker, start_date, end_date)
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Calculate values efficiently
    dates = []
    portfolio_values = []
    voo_values = []
    qqq_values = []
    
    # Track cumulative holdings and ETF shares
    cumulative_holdings = {}
    cumulative_voo_shares = 0
    cumulative_qqq_shares = 0
    
    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        # Add any new transactions on this date
        for transaction in transactions:
            if transaction.date == current_date.date():
                if transaction.ticker not in cumulative_holdings:
                    cumulative_holdings[transaction.ticker] = 0
                
                if transaction.transaction_type == 'BUY':
                    cumulative_holdings[transaction.ticker] += transaction.shares
                    # Calculate equivalent ETF shares
                    voo_price = get_price_from_dataframe(price_histories.get('VOO'), date_str)
                    if voo_price:
                        cumulative_voo_shares += transaction.total_value / voo_price
                    
                    qqq_price = get_price_from_dataframe(price_histories.get('QQQ'), date_str)
                    if qqq_price:
                        cumulative_qqq_shares += transaction.total_value / qqq_price
                elif transaction.transaction_type == 'SELL':
                    cumulative_holdings[transaction.ticker] -= transaction.shares
        
        # Calculate portfolio value
        portfolio_value = 0
        for ticker, shares in cumulative_holdings.items():
            if shares > 0:
                price = get_price_from_dataframe(price_histories.get(ticker), date_str)
                if price:
                    portfolio_value += shares * price
        
        # Calculate ETF values
        voo_price = get_price_from_dataframe(price_histories.get('VOO'), date_str)
        voo_value = cumulative_voo_shares * voo_price if voo_price else 0
        
        qqq_price = get_price_from_dataframe(price_histories.get('QQQ'), date_str)
        qqq_value = cumulative_qqq_shares * qqq_price if qqq_price else 0
        
        portfolio_values.append(portfolio_value)
        voo_values.append(voo_value)
        qqq_values.append(qqq_value)
    
    return {
        'dates': dates,
        'portfolio_values': portfolio_values,
        'voo_values': voo_values,
        'qqq_values': qqq_values
    }

def calculate_portfolio_value_on_date(portfolio_id, target_date, portfolio_service, price_service):
    """Calculate portfolio value on a specific date using actual historical prices"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    # Get holdings as of target date
    holdings = defaultdict(float)
    for transaction in transactions:
        if transaction.date <= target_date:
            if transaction.transaction_type == 'BUY':
                holdings[transaction.ticker] += transaction.shares
            elif transaction.transaction_type == 'SELL':
                holdings[transaction.ticker] -= transaction.shares
    
    # Calculate value using actual historical prices
    total_value = 0
    for ticker, shares in holdings.items():
        if shares > 0:
            try:
                # Get historical price for this specific date
                historical_price = get_historical_price(ticker, target_date)
                if historical_price:
                    total_value += shares * historical_price
            except:
                pass
    
    return total_value

def get_ticker_price_dataframe(ticker, start_date, end_date):
    """Get price history as pandas DataFrame with efficient caching"""
    from app.models.price import PriceHistory
    from app import db
    import yfinance as yf
    import time
    
    # Get cached prices
    cached_prices = PriceHistory.query.filter(
        PriceHistory.ticker == ticker,
        PriceHistory.date >= start_date,
        PriceHistory.date <= end_date
    ).all()
    
    # Convert to DataFrame
    if cached_prices:
        cached_df = pd.DataFrame([
            {'Date': p.date.strftime('%Y-%m-%d'), 'Close': p.close_price}
            for p in cached_prices
        ])
        cached_df.set_index('Date', inplace=True)
        print(f"[CACHE] Found {len(cached_prices)} cached prices for {ticker}")
    else:
        cached_df = pd.DataFrame()
    
    # Check for missing dates
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    missing_dates = []
    
    for d in date_range:
        date_str = d.strftime('%Y-%m-%d')
        if cached_df.empty or date_str not in cached_df.index:
            missing_dates.append(d.date())
    
    # Batch fetch missing data
    if missing_dates:
        print(f"[API] Fetching {len(missing_dates)} missing prices for {ticker}")
        try:
            time.sleep(0.2)
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date + timedelta(days=1))
            
            if not hist.empty:
                # Batch insert new prices
                records_added = 0
                for date_idx, row in hist.iterrows():
                    price_date = date_idx.date()
                    if price_date in missing_dates:
                        try:
                            price_record = PriceHistory(
                                ticker=ticker,
                                date=price_date,
                                close_price=float(row['Close']),
                                is_intraday=False,
                                price_timestamp=datetime.now(),
                                last_updated=datetime.now()
                            )
                            db.session.add(price_record)
                            records_added += 1
                        except Exception:
                            pass
                
                try:
                    db.session.commit()
                    print(f"[CACHE] Stored {records_added} new prices for {ticker}")
                except Exception:
                    db.session.rollback()
                
                # Add to DataFrame
                new_df = pd.DataFrame({'Close': hist['Close']})
                new_df.index = new_df.index.strftime('%Y-%m-%d')
                
                if cached_df.empty:
                    cached_df = new_df
                else:
                    cached_df = pd.concat([cached_df, new_df]).sort_index()
        
        except Exception as e:
            print(f"[API] Error fetching {ticker}: {e}")
    
    return cached_df

def get_price_from_dataframe(price_df, date_str):
    """Get price for date from DataFrame, using closest previous if needed"""
    if price_df is None or price_df.empty:
        return None
    
    if date_str in price_df.index:
        price = price_df.loc[date_str, 'Close']
        # Handle case where multiple entries exist for same date
        if isinstance(price, pd.Series):
            return float(price.iloc[0])
        return float(price)
    
    # Find closest previous date
    available_dates = [d for d in price_df.index if d < date_str]
    if available_dates:
        closest_date = max(available_dates)
        price = price_df.loc[closest_date, 'Close']
        if isinstance(price, pd.Series):
            return float(price.iloc[0])
        return float(price)
    
    return None

def get_historical_price(ticker, target_date):
    """Get historical closing price for a ticker on a specific date"""
    from app.models.price import PriceHistory
    from app import db
    import yfinance as yf
    import time
    
    # Check if we have exact date
    cached_price = PriceHistory.query.filter_by(
        ticker=ticker,
        date=target_date
    ).first()
    
    if cached_price:
        return cached_price.close_price
    
    # Try to fetch missing price from API
    try:
        print(f"[API] Fetching missing price for {ticker} on {target_date}")
        time.sleep(0.1)
        stock = yf.Ticker(ticker)
        
        # Get data around the target date
        start_date = target_date - timedelta(days=5)
        end_date = target_date + timedelta(days=1)
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # Find closest date and cache it
            hist_dates = hist.index.date
            closest_date = min(hist_dates, key=lambda x: abs((x - target_date).days))
            price = float(hist.loc[hist.index.date == closest_date]['Close'].iloc[0])
            
            # Cache the price
            try:
                price_record = PriceHistory(
                    ticker=ticker,
                    date=target_date,
                    close_price=price,
                    is_intraday=False,
                    price_timestamp=datetime.now(),
                    last_updated=datetime.now()
                )
                db.session.add(price_record)
                db.session.commit()
                print(f"[CACHE] Stored missing price for {ticker} on {target_date}: ${price:.2f}")
            except Exception:
                db.session.rollback()
            
            return price
    except Exception as e:
        print(f"[API] Error fetching missing price for {ticker} on {target_date}: {e}")
    
    # If API fails, find the most recent previous date
    previous_price = PriceHistory.query.filter(
        PriceHistory.ticker == ticker,
        PriceHistory.date < target_date
    ).order_by(PriceHistory.date.desc()).first()
    
    if previous_price:
        return previous_price.close_price
    
    return None

def calculate_etf_value_on_date(portfolio_id, target_date, etf_ticker, portfolio_service):
    """Calculate what the portfolio investments would be worth if invested in an ETF"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    total_etf_value = 0
    
    for transaction in transactions:
        if transaction.date <= target_date and transaction.transaction_type == 'BUY':
            # Get ETF price on the transaction date
            etf_price_on_buy_date = get_historical_price(etf_ticker, transaction.date)
            # Get ETF price on target date
            etf_price_on_target_date = get_historical_price(etf_ticker, target_date)
            
            if etf_price_on_buy_date and etf_price_on_target_date:
                # Calculate how many ETF shares could have been bought
                etf_shares = transaction.total_value / etf_price_on_buy_date
                # Calculate current value of those ETF shares
                etf_value = etf_shares * etf_price_on_target_date
                total_etf_value += etf_value
    
    return total_etf_value

def calculate_current_etf_equivalent(portfolio_id, portfolio_service, price_service, etf_ticker):
    """Calculate current value of ETF equivalent investment"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    total_etf_shares = 0
    
    for transaction in transactions:
        if transaction.transaction_type == 'BUY':
            # Get ETF price on the transaction date
            etf_price_on_buy_date = get_historical_price(etf_ticker, transaction.date)
            
            if etf_price_on_buy_date:
                # Calculate how many ETF shares could have been bought
                etf_shares = transaction.total_value / etf_price_on_buy_date
                total_etf_shares += etf_shares
    
    # Get current ETF price
    try:
        current_etf_price = price_service.get_current_price(etf_ticker)
        if current_etf_price:
            return total_etf_shares * current_etf_price
    except:
        pass
    
    return 0

def is_market_open_now():
    """Check if US stock market is currently open"""
    from datetime import datetime, time
    import pytz
    
    # Get current time in Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # Market is closed on weekends
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now.time()
    
    return market_open <= current_time <= market_close

def get_last_market_date():
    """Get the last market trading date"""
    today = date.today()
    
    # If today is a weekday, use today (whether market is open or closed)
    if today.weekday() < 5:  # Monday = 0, Friday = 4
        return today
    else:
        # Weekend, go back to Friday
        days_back = today.weekday() - 4  # Friday = 4
        return today - timedelta(days=days_back)

def get_cached_portfolio_stats(portfolio_id, market_date):
    """Get cached portfolio statistics"""
    cache = PortfolioCache.query.filter_by(
        portfolio_id=portfolio_id,
        cache_type='stats',
        market_date=market_date
    ).first()
    
    if cache:
        return cache.get_data()
    return None

def cache_portfolio_stats(portfolio_id, market_date, stats):
    """Cache portfolio statistics"""
    try:
        # Remove existing cache for this date
        PortfolioCache.query.filter_by(
            portfolio_id=portfolio_id,
            cache_type='stats',
            market_date=market_date
        ).delete()
        
        # Create new cache entry
        cache = PortfolioCache(
            id=str(uuid.uuid4()),
            portfolio_id=portfolio_id,
            cache_type='stats',
            market_date=market_date
        )
        cache.set_data(stats)
        
        db.session.add(cache)
        db.session.commit()
    except Exception:
        db.session.rollback()

def get_cached_chart_data(portfolio_id, market_date):
    """Get cached chart data"""
    cache = PortfolioCache.query.filter_by(
        portfolio_id=portfolio_id,
        cache_type='chart_data',
        market_date=market_date
    ).first()
    
    if cache:
        return cache.get_data()
    return None

def cache_chart_data(portfolio_id, market_date, chart_data):
    """Cache chart data"""
    try:
        # Remove existing cache for this date
        PortfolioCache.query.filter_by(
            portfolio_id=portfolio_id,
            cache_type='chart_data',
            market_date=market_date
        ).delete()
        
        # Create new cache entry
        cache = PortfolioCache(
            id=str(uuid.uuid4()),
            portfolio_id=portfolio_id,
            cache_type='chart_data',
            market_date=market_date
        )
        cache.set_data(chart_data)
        
        db.session.add(cache)
        db.session.commit()
    except Exception:
        db.session.rollback()

def calculate_daily_changes(portfolio_id, portfolio_service, price_service):
    """Calculate daily percentage changes for portfolio and ETFs"""
    from app.models.price import PriceHistory
    
    try:
        last_trading_day = get_last_market_date()
        previous_trading_day = get_previous_trading_day(last_trading_day)
        
        print(f"[DAILY] Calculating daily changes for {last_trading_day} vs {previous_trading_day}")
        
        # Calculate ETF daily changes with portfolio equivalent values
        voo_change = calculate_etf_daily_change_for_portfolio('VOO', portfolio_id, portfolio_service, price_service)
        qqq_change = calculate_etf_daily_change_for_portfolio('QQQ', portfolio_id, portfolio_service, price_service)
        
        # Calculate portfolio daily change
        portfolio_change = calculate_portfolio_daily_change(portfolio_id, last_trading_day, previous_trading_day, portfolio_service, price_service)
        
        print(f"[DAILY] Portfolio change: {portfolio_change}")
        print(f"[DAILY] VOO change: {voo_change}")
        print(f"[DAILY] QQQ change: {qqq_change}")
        
        result = {
            'voo_daily_change': voo_change.get('percentage', 0) if isinstance(voo_change, dict) else 0,
            'voo_daily_dollar_change': voo_change.get('dollar', 0) if isinstance(voo_change, dict) else 0,
            'qqq_daily_change': qqq_change.get('percentage', 0) if isinstance(qqq_change, dict) else 0,
            'qqq_daily_dollar_change': qqq_change.get('dollar', 0) if isinstance(qqq_change, dict) else 0,
            'portfolio_daily_change': portfolio_change.get('percentage', 0) if isinstance(portfolio_change, dict) else 0,
            'portfolio_daily_dollar_change': portfolio_change.get('dollar', 0) if isinstance(portfolio_change, dict) else 0
        }
        
        print(f"[DAILY] Final result: {result}")
        return result
        
    except Exception as e:
        print(f"[DAILY] Error calculating daily changes: {e}")
        import traceback
        traceback.print_exc()
        return {
            'voo_daily_change': 0,
            'voo_daily_dollar_change': 0,
            'qqq_daily_change': 0,
            'qqq_daily_dollar_change': 0,
            'portfolio_daily_change': 0,
            'portfolio_daily_dollar_change': 0
        }
    


def calculate_etf_daily_change_for_portfolio(ticker, portfolio_id, portfolio_service, price_service):
    """Calculate daily change for an ETF based on portfolio's equivalent investment"""
    from app.models.price import PriceHistory
    
    try:
        # Get the last two trading days
        last_trading_day = get_last_market_date()
        previous_trading_day = get_previous_trading_day(last_trading_day)
        
        # Get ETF price changes - use cached current prices (may be intraday if available)
        current_price = price_service.get_current_price(ticker, use_stale=True)  # Use cached for speed
        
        # Always use previous day's closing price for comparison
        previous_price_record = PriceHistory.query.filter(
            PriceHistory.ticker == ticker,
            PriceHistory.date < last_trading_day
        ).order_by(PriceHistory.date.desc()).first()
        
        if current_price and previous_price_record:
            previous_price = previous_price_record.close_price
            percentage_change = ((current_price - previous_price) / previous_price) * 100
            
            # Calculate dollar change based on portfolio's equivalent ETF investment
            if ticker == 'VOO':
                etf_equivalent_value = calculate_current_etf_equivalent(portfolio_id, portfolio_service, price_service, 'VOO')
            else:  # QQQ
                etf_equivalent_value = calculate_current_etf_equivalent(portfolio_id, portfolio_service, price_service, 'QQQ')
            
            dollar_change = etf_equivalent_value * (percentage_change / 100)
            

            return {'percentage': percentage_change, 'dollar': dollar_change}
        else:
            return {'percentage': 0, 'dollar': 0}
    except Exception as e:
        print(f"Error calculating daily change for {ticker}: {e}")
    
    return {'percentage': 0, 'dollar': 0}

def calculate_portfolio_daily_change(portfolio_id, today, yesterday, portfolio_service, price_service):
    """Calculate daily percentage and dollar change for the portfolio"""
    try:
        # Get current holdings
        holdings = portfolio_service.get_current_holdings(portfolio_id)
        
        if not holdings:
            return 0
        
        current_value = 0
        yesterday_value = 0
        
        # Get the last two trading days
        last_trading_day = get_last_market_date()
        previous_trading_day = get_previous_trading_day(last_trading_day)
        
        from app.models.price import PriceHistory
        
        # Check if market is open to determine price source
        market_is_open = is_market_open_now()
        
        for ticker, shares in holdings.items():
            # For current value: use cached current prices (may be intraday if market open)
            current_price = price_service.get_current_price(ticker, use_stale=True)  # Use cached for speed
            if current_price:
                current_value += shares * current_price
            
            # For previous value: always use previous day's closing price
            previous_price_record = PriceHistory.query.filter(
                PriceHistory.ticker == ticker,
                PriceHistory.date < last_trading_day
            ).order_by(PriceHistory.date.desc()).first()
            
            if previous_price_record:
                yesterday_value += shares * previous_price_record.close_price
        

        
        if yesterday_value > 0:
            daily_dollar_change = current_value - yesterday_value
            daily_percentage_change = (daily_dollar_change / yesterday_value) * 100
            
            # Update the return dictionary in calculate_daily_changes
            return {
                'percentage': daily_percentage_change,
                'dollar': daily_dollar_change
            }
    except Exception as e:
        print(f"Error calculating portfolio daily change: {e}")
    
    return {'percentage': 0, 'dollar': 0}

def get_previous_trading_day(current_date):
    """Get the previous trading day (skip weekends and holidays)"""
    from app.models.price import PriceHistory
    
    # Find the most recent date before current_date that has price data
    previous_price = PriceHistory.query.filter(
        PriceHistory.date < current_date
    ).order_by(PriceHistory.date.desc()).first()
    
    if previous_price:
        return previous_price.date
    
    # Fallback to simple date calculation if no price data found
    previous_date = current_date - timedelta(days=1)
    while previous_date.weekday() >= 5:
        previous_date -= timedelta(days=1)
    return previous_date
