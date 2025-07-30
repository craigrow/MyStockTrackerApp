from app import db
from app.models.price import PriceHistory
from datetime import datetime, date, timedelta, timezone
import yfinance as yf
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time
import logging
import random
from flask import has_app_context, current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceService:
    
    def __init__(self):
        self.cache_freshness_minutes = 5  # Consider cache fresh if updated within this time
        self.max_retries = 3  # Maximum number of retries for API calls
        self.retry_delay = 1  # Delay between retries in seconds
        self.batch_size = 20  # Optimal batch size for yfinance
        self.max_workers = 4  # Maximum number of parallel workers
    
    def get_current_price(self, ticker, use_stale=True):
        """Get current price with option to use stale data"""
        from datetime import date
        
        # First check cache
        cached_price = self.get_cached_price(ticker, date.today())
        if cached_price:
            return cached_price
        
        # For dashboard loading, we'll skip API calls and just use the most recent price
        if use_stale:
            # Try to get the most recent price from the database
            most_recent = PriceHistory.query.filter_by(ticker=ticker).order_by(PriceHistory.date.desc()).first()
            if most_recent:
                return most_recent.close_price
        
        # Only fetch from API if explicitly requested (not for dashboard loading)
        if not use_stale:
            # Fetch from API with timeout and retry
            price = self.fetch_from_api_with_retry(ticker, timeout=10)
            if price:
                self.cache_price_data(ticker, date.today(), price, True)
                return price
        
        # Return None if no price is available
        return None
    
    def get_cached_price(self, ticker, price_date):
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        return price_history.close_price if price_history else None
    
    def is_cache_fresh(self, ticker, price_date, freshness_minutes=5):
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        
        if not price_history or not price_history.last_updated:
            return False
        
        # Consider cache fresh if updated within specified minutes
        time_diff = datetime.now(timezone.utc).replace(tzinfo=None) - price_history.last_updated
        return time_diff < timedelta(minutes=freshness_minutes)
    
    def get_data_freshness(self, ticker, price_date):
        """Get how old the cached data is in minutes"""
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        
        if not price_history or not price_history.last_updated:
            return None
        
        time_diff = datetime.now(timezone.utc).replace(tzinfo=None) - price_history.last_updated
        return int(time_diff.total_seconds() / 60)
    
    def fetch_from_api(self, ticker, timeout=10):
        try:
            import threading
            import time
            
            result = {'price': None, 'error': None}
            
            def fetch_price():
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1d")
                    if not hist.empty and len(hist) > 0:
                        result['price'] = float(hist.iloc[-1]['Close'])
                except Exception as e:
                    result['error'] = str(e)
            
            # Use threading for timeout (cross-platform)
            thread = threading.Thread(target=fetch_price)
            thread.daemon = True
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive():
                logger.warning(f"API call timed out for {ticker}")
                return None
            
            if result['error']:
                logger.warning(f"API fetch failed for {ticker}: {result['error']}")
                return None
                
            return result['price']
                
        except Exception as e:
            logger.error(f"API fetch failed for {ticker}: {e}")
            return None
    
    def batch_fetch_current_prices(self, tickers, timeout=30):
        """Fetch current prices for multiple tickers with timeout"""
        if not tickers:
            return {}
            
        logger.info(f"Batch fetching current prices for {len(tickers)} tickers")
        prices = {}
        try:
            import threading
            
            result = {'data': None, 'error': None}
            
            def fetch_batch():
                try:
                    # Use yfinance download for batch processing
                    data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
                    result['data'] = data
                except Exception as e:
                    result['error'] = str(e)
            
            # Use threading for timeout
            thread = threading.Thread(target=fetch_batch)
            thread.daemon = True
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive() or result['error']:
                logger.warning(f"Batch fetch failed or timed out: {result.get('error', 'timeout')}")
                # Fallback to individual fetches with smaller batches
                return self._fallback_batch_fetch(tickers)
            else:
                data = result['data']
                for ticker in tickers:
                    try:
                        if len(tickers) == 1:
                            close_price = data['Close'].iloc[-1]
                        else:
                            close_price = data[ticker]['Close'].iloc[-1]
                        prices[ticker] = float(close_price)
                    except (KeyError, IndexError) as e:
                        logger.warning(f"Could not extract price for {ticker}: {e}")
                        prices[ticker] = None
                
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            # Fallback to smaller batches
            return self._fallback_batch_fetch(tickers)
        
        return prices
    
    def _fallback_batch_fetch(self, tickers, batch_size=5):
        """Fallback to smaller batches when large batch fails with improved error handling"""
        logger.info(f"Using fallback batch fetch with batch size {batch_size}")
        prices = {}
        
        # Process tickers in smaller batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            try:
                # Small delay to avoid rate limiting with jitter
                time.sleep(0.2 + random.uniform(0, 0.3))
                
                # Use yfinance download for batch processing
                data = yf.download(batch, period="1d", group_by='ticker', progress=False)
                
                for ticker in batch:
                    try:
                        if len(batch) == 1:
                            close_price = data['Close'].iloc[-1]
                        else:
                            close_price = data[ticker]['Close'].iloc[-1]
                        prices[ticker] = float(close_price)
                    except (KeyError, IndexError):
                        prices[ticker] = None
            except Exception as e:
                logger.error(f"Fallback batch fetch failed for batch {i//batch_size + 1}: {e}")
                # If even small batch fails, try individual fetches
                for ticker in batch:
                    prices[ticker] = self.fetch_from_api_with_retry(ticker, timeout=5)
        
        return prices
    
    def cache_price_data(self, ticker, price_date, price, is_intraday):
        # Skip caching if price is None, NaN, or invalid
        if price is None or (isinstance(price, float) and (pd.isna(price) or pd.isnull(price))):
            return
        
        try:
            price_history = PriceHistory.query.filter_by(
                ticker=ticker, 
                date=price_date
            ).first()
            
            if price_history:
                price_history.close_price = price
                price_history.is_intraday = is_intraday
                price_history.price_timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
                price_history.last_updated = datetime.now(timezone.utc).replace(tzinfo=None)
            else:
                price_history = PriceHistory(
                    ticker=ticker,
                    date=price_date,
                    close_price=price,
                    is_intraday=is_intraday,
                    price_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                    last_updated=datetime.now(timezone.utc).replace(tzinfo=None)
                )
                db.session.add(price_history)
            
            db.session.commit()
        except Exception as e:
            logger.error(f"Error caching price data for {ticker}: {e}")
            db.session.rollback()
    
    def batch_cache_price_data(self, prices_dict, price_date, is_intraday=True):
        """Cache multiple prices at once for better performance with improved error handling"""
        if not prices_dict:
            return
            
        logger.info(f"Batch caching {len(prices_dict)} prices")
        
        # Try to perform the operation directly first
        try:
            self._do_batch_cache(prices_dict, price_date, is_intraday)
        except RuntimeError as e:
            if "Working outside of application context" in str(e):
                # If we're outside app context, try to get one
                try:
                    from flask import current_app
                    with current_app.app_context():
                        self._do_batch_cache(prices_dict, price_date, is_intraday)
                except RuntimeError:
                    # If current_app is not available, we're likely in a test or background context
                    # Just log the error and continue
                    logger.error(f"Cannot cache prices - no application context available: {e}")
            else:
                raise
    
    def _do_batch_cache(self, prices_dict, price_date, is_intraday):
        """Internal method to perform the actual caching with app context"""
        
        try:
            # Get existing price records for these tickers on this date
            tickers = list(prices_dict.keys())
            
            # Process in batches to avoid memory issues with large datasets
            batch_size = 500  # Optimal batch size for database operations
            all_updated = 0
            all_created = 0
            
            for i in range(0, len(tickers), batch_size):
                batch_tickers = tickers[i:i+batch_size]
                
                existing_records = PriceHistory.query.filter(
                    PriceHistory.ticker.in_(batch_tickers),
                    PriceHistory.date == price_date
                ).all()
                
                # Create a lookup dictionary for faster access
                existing_dict = {record.ticker: record for record in existing_records}
                
                # Update existing records and prepare new ones
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                new_records = []
                updated = 0
                created = 0
                
                for ticker in batch_tickers:
                    price = prices_dict.get(ticker)
                    # Skip None, NaN, or invalid prices
                    if price is None or (isinstance(price, float) and (pd.isna(price) or pd.isnull(price))):
                        continue
                        
                    if ticker in existing_dict:
                        # Update existing record
                        record = existing_dict[ticker]
                        record.close_price = price
                        record.is_intraday = is_intraday
                        record.price_timestamp = now
                        record.last_updated = now
                        updated += 1
                    else:
                        # Create new record
                        new_record = PriceHistory(
                            ticker=ticker,
                            date=price_date,
                            close_price=price,
                            is_intraday=is_intraday,
                            price_timestamp=now,
                            last_updated=now
                        )
                        new_records.append(new_record)
                        created += 1
                
                # Add all new records at once
                if new_records:
                    db.session.add_all(new_records)
                    
                # Commit changes for this batch
                try:
                    db.session.commit()
                    all_updated += updated
                    all_created += created
                    logger.info(f"Batch {i//batch_size + 1}: Updated {updated}, created {created} price records")
                except Exception as e:
                    logger.error(f"Error committing batch {i//batch_size + 1}: {e}")
                    db.session.rollback()
            
            logger.info(f"Successfully cached {all_updated + all_created} prices (updated: {all_updated}, created: {all_created})")
            
        except Exception as e:
            logger.error(f"Error in batch_cache_price_data: {e}")
            db.session.rollback()
    
    def get_price_history(self, ticker, start_date, end_date):
        return PriceHistory.query.filter(
            PriceHistory.ticker == ticker,
            PriceHistory.date >= start_date,
            PriceHistory.date <= end_date
        ).order_by(PriceHistory.date).all()
    
    def get_etf_comparison_data(self, etf_ticker, investment_date, investment_amount, current_date=None):
        if current_date is None:
            current_date = date.today()
        
        purchase_price = self.get_cached_price(etf_ticker, investment_date)
        current_price = self.get_cached_price(etf_ticker, current_date)
        
        if not purchase_price or not current_price:
            return None
        
        shares_purchased = investment_amount / purchase_price
        current_value = shares_purchased * current_price
        gain_loss = current_value - investment_amount
        gain_loss_percentage = (gain_loss / investment_amount) * 100
        
        return {
            'ticker': etf_ticker,
            'investment_date': investment_date,
            'investment_amount': investment_amount,
            'purchase_price': purchase_price,
            'shares_purchased': shares_purchased,
            'current_price': current_price,
            'current_value': current_value,
            'gain_loss': gain_loss,
            'gain_loss_percentage': gain_loss_percentage
        }
        
    def batch_fetch_prices(self, tickers, period=None, start_date=None, end_date=None):
        """
        Fetches historical price data for multiple tickers in a single batch request
        Returns a dictionary of {ticker: price_dataframe}
        """
        if not tickers:
            return {}
        
        logger.info(f"Batch fetching prices for {len(tickers)} tickers")
        
        try:
            # Use yfinance batch download capability
            data = yf.download(
                tickers=" ".join(tickers),
                period=period,
                start=start_date,
                end=end_date,
                group_by='ticker',
                auto_adjust=True,
                progress=False,
                threads=True
            )
            
            # Initialize result dictionary
            result = {}
            
            # Handle single ticker case (yfinance returns different structure)
            if len(tickers) == 1:
                ticker = tickers[0]
                if not data.empty:
                    result[ticker] = data
                return result
            
            # Handle multiple tickers case
            if hasattr(data.columns, 'levels') and len(data.columns.levels) > 0:
                for ticker in tickers:
                    if ticker in data.columns.levels[0]:
                        ticker_data = data[ticker].copy()
                        if not ticker_data.empty:
                            result[ticker] = ticker_data
            else:
                logger.warning(f"Batch fetch failed: 'RangeIndex' object has no attribute 'levels'")
                # Fallback to smaller batches
                return self._fallback_batch_fetch_historical(tickers, period, start_date, end_date)
            
            return result
            
        except Exception as e:
            logger.error(f"Batch fetch failed: {e}")
            # Fallback to smaller batches
            return self._fallback_batch_fetch_historical(tickers, period, start_date, end_date)
    
    def _fallback_batch_fetch_historical(self, tickers, period=None, start_date=None, end_date=None, batch_size=5):
        """Fallback to smaller batches when large batch fails for historical data with improved error handling"""
        logger.info(f"Using fallback batch fetch for historical data with batch size {batch_size}")
        result = {}
        
        # Process tickers in smaller batches
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            try:
                # Small delay to avoid rate limiting with jitter
                time.sleep(0.2 + random.uniform(0, 0.3))
                
                # Use yfinance download for batch processing
                data = yf.download(
                    " ".join(batch),
                    period=period,
                    start=start_date,
                    end=end_date,
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False,
                    threads=True
                )
                
                # Handle single ticker case
                if len(batch) == 1:
                    ticker = batch[0]
                    if not data.empty:
                        result[ticker] = data
                    continue
                
                # Handle multiple tickers case
                if hasattr(data.columns, 'levels') and len(data.columns.levels) > 0:
                    for ticker in batch:
                        if ticker in data.columns.levels[0]:
                            ticker_data = data[ticker].copy()
                            if not ticker_data.empty:
                                result[ticker] = ticker_data
                
            except Exception as e:
                logger.error(f"Fallback batch fetch failed for batch {i//batch_size + 1}: {e}")
                # Try individual fetches as last resort
                for ticker in batch:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period=period, start=start_date, end=end_date)
                        if not hist.empty:
                            result[ticker] = hist
                    except Exception as e2:
                        logger.error(f"Individual fetch failed for {ticker}: {e2}")
        
        return result
    
    def get_current_prices_batch(self, tickers, use_cache=True):
        """
        Get current prices for multiple tickers with intelligent caching
        Returns a dictionary of {ticker: current_price}
        """
        if not tickers:
            return {}
            
        logger.info(f"Getting current prices for {len(tickers)} tickers (use_cache={use_cache})")
        
        prices = {}
        today = date.today()
        
        # If using cache, check for fresh cached prices first
        if use_cache:
            fresh_tickers = {}
            stale_tickers = []
            
            for ticker in tickers:
                cached_price = self.get_cached_price(ticker, today)
                if cached_price and self.is_cache_fresh(ticker, today):
                    prices[ticker] = cached_price
                    fresh_tickers[ticker] = True
                else:
                    stale_tickers.append(ticker)
            
            logger.info(f"Cache hit: {len(fresh_tickers)}, Cache miss: {len(stale_tickers)}")
            
            # Only fetch prices for tickers with stale or no cache
            if stale_tickers:
                # Use optimized batch fetch
                batch_prices = self.batch_fetch_current_prices(stale_tickers)
                
                # Cache the new prices
                self.batch_cache_price_data(batch_prices, today, True)
                
                # Update the prices dictionary
                prices.update(batch_prices)
        else:
            # Not using cache, fetch all prices from API
            batch_prices = self.batch_fetch_current_prices(tickers)
            
            # Cache the new prices
            self.batch_cache_price_data(batch_prices, today, True)
            
            # Update the prices dictionary
            prices.update(batch_prices)
        
        return prices
    
    async def fetch_prices_parallel(self, tickers, max_workers=4, chunk_size=20):
        """
        Fetch prices for multiple tickers in parallel using asyncio
        Returns a dictionary of {ticker: price_dataframe}
        """
        if not tickers:
            return {}
        
        logger.info(f"Fetching prices in parallel for {len(tickers)} tickers")
        
        # Split tickers into chunks to avoid overwhelming the API
        chunks = [tickers[i:i+chunk_size] for i in range(0, len(tickers), chunk_size)]
        
        # Create tasks for each chunk
        loop = asyncio.get_event_loop()
        tasks = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for chunk in chunks:
                task = loop.run_in_executor(
                    executor,
                    self.batch_fetch_prices,
                    chunk
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
        
        # Merge results from all chunks
        merged_results = {}
        for result in results:
            merged_results.update(result)
        
        return merged_results
    
    async def fetch_current_prices_parallel(self, tickers, max_workers=None, chunk_size=None):
        """
        Fetch current prices for multiple tickers in parallel with improved error handling
        Returns a dictionary of {ticker: current_price}
        """
        if not tickers:
            return {}
        
        if max_workers is None:
            max_workers = self.max_workers
            
        if chunk_size is None:
            chunk_size = self.batch_size
            
        logger.info(f"Fetching current prices in parallel for {len(tickers)} tickers (workers={max_workers}, chunk_size={chunk_size})")
        
        # Split tickers into chunks to avoid overwhelming the API
        chunks = [tickers[i:i+chunk_size] for i in range(0, len(tickers), chunk_size)]
        
        # Create tasks for each chunk
        loop = asyncio.get_event_loop()
        tasks = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i, chunk in enumerate(chunks):
                # Add small delay between chunks to avoid rate limiting
                if i > 0:
                    await asyncio.sleep(0.2)
                    
                task = loop.run_in_executor(
                    executor,
                    self.batch_fetch_current_prices,
                    chunk
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results from all chunks, handling exceptions
        merged_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error in chunk {i}: {result}")
                # Try to fetch this chunk again with fallback method
                chunk = chunks[i]
                try:
                    fallback_result = self._fallback_batch_fetch(chunk)
                    merged_results.update(fallback_result)
                except Exception as e:
                    logger.error(f"Fallback fetch failed for chunk {i}: {e}")
            else:
                merged_results.update(result)
        
        # Cache the results
        self.batch_cache_price_data(merged_results, date.today(), True)
        
        return merged_results
    def fetch_from_api_with_retry(self, ticker, timeout=10):
        """Fetch price from API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                price = self.fetch_from_api(ticker, timeout)
                if price:
                    return price
                
                # If price is None but no exception, wait and retry
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.warning(f"API fetch attempt {attempt+1} failed for {ticker}: {e}")
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        # All retries failed
        logger.error(f"All {self.max_retries} API fetch attempts failed for {ticker}")
        return None
    def get_market_aware_cache_freshness(self):
        """Get cache freshness threshold based on market hours"""
        # Check if market is open
        from app.views.main import is_market_open_now
        market_open = is_market_open_now()
        
        if market_open:
            # During market hours, cache should be fresher
            return 5  # 5 minutes
        else:
            # After hours, cache can be staler
            return 60  # 60 minutes
    
    def invalidate_stale_cache(self, portfolio_id):
        """Invalidate stale cache for a portfolio's holdings"""
        from app.services.portfolio_service import PortfolioService
        portfolio_service = PortfolioService()
        
        # Get holdings
        holdings = portfolio_service.get_current_holdings(portfolio_id)
        tickers = list(holdings.keys()) + ['VOO', 'QQQ']  # Include ETFs
        
        # Get market-aware freshness threshold
        freshness_minutes = self.get_market_aware_cache_freshness()
        
        # Check each ticker for staleness
        stale_tickers = []
        for ticker in tickers:
            if not self.is_cache_fresh(ticker, date.today(), freshness_minutes):
                stale_tickers.append(ticker)
        
        return stale_tickers
