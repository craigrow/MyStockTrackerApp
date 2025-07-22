from app import db
from app.models.price import PriceHistory
from datetime import datetime, date, timedelta, timezone
import yfinance as yf
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


class PriceService:
    
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
            # Fetch from API with timeout
            price = self.fetch_from_api(ticker, timeout=10)
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
                print(f"API call timed out for {ticker}")
                return None
            
            if result['error']:
                print(f"API fetch failed for {ticker}: {result['error']}")
                return None
                
            return result['price']
                
        except Exception as e:
            print(f"API fetch failed for {ticker}: {e}")
            return None
    
    def batch_fetch_current_prices(self, tickers, timeout=30):
        """Fetch current prices for multiple tickers with timeout"""
        prices = {}
        try:
            import threading
            
            result = {'data': None, 'error': None}
            
            def fetch_batch():
                try:
                    # Use yfinance download for batch processing
                    import yfinance as yf
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
                print(f"Batch fetch failed or timed out: {result.get('error', 'timeout')}")
                # Fallback to individual fetches
                for ticker in tickers:
                    prices[ticker] = self.fetch_from_api(ticker, timeout=5)
            else:
                data = result['data']
                for ticker in tickers:
                    try:
                        if len(tickers) == 1:
                            close_price = data['Close'].iloc[-1]
                        else:
                            close_price = data[ticker]['Close'].iloc[-1]
                        prices[ticker] = float(close_price)
                    except (KeyError, IndexError):
                        prices[ticker] = None
                
        except Exception as e:
            print(f"Batch fetch failed: {e}")
            # Fallback to individual fetches
            for ticker in tickers:
                prices[ticker] = self.fetch_from_api(ticker, timeout=5)
        
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
            print(f"Error caching price data for {ticker}: {e}")
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
                print(f"Batch fetch failed: 'RangeIndex' object has no attribute 'levels'")
            
            return result
            
        except Exception as e:
            print(f"Batch fetch failed: {e}")
            # Return empty dictionary on error
            return {}
    
    def batch_fetch_current_prices(self, tickers):
        """
        Fetch current prices for multiple tickers in a single batch request
        Returns a dictionary of {ticker: current_price}
        """
        prices = {}
        
        try:
            # Use batch_fetch_prices with period="1d" to get the most recent prices
            data = self.batch_fetch_prices(tickers, period="1d")
            
            # Extract the most recent closing price for each ticker
            for ticker, df in data.items():
                if not df.empty and 'Close' in df.columns:
                    prices[ticker] = float(df['Close'].iloc[-1])
                else:
                    prices[ticker] = None
            
            # For any missing tickers, try to get from cache
            for ticker in tickers:
                if ticker not in prices or prices[ticker] is None:
                    cached_price = self.get_cached_price(ticker, date.today())
                    if cached_price:
                        prices[ticker] = cached_price
            
            return prices
            
        except Exception as e:
            print(f"Batch fetch current prices failed: {e}")
            # Fallback to individual fetches
            for ticker in tickers:
                prices[ticker] = self.get_current_price(ticker, use_stale=True)
            return prices
            
    def get_current_prices_batch(self, tickers, use_cache=False):
        """
        Get current prices for multiple tickers with optional caching
        Returns a dictionary of {ticker: current_price}
        """
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
            
            # Only fetch prices for tickers with stale or no cache
            if stale_tickers:
                api_prices = self.batch_fetch_prices(stale_tickers, period="1d")
                
                for ticker in stale_tickers:
                    if ticker in api_prices and api_prices[ticker] is not None:
                        # Extract price from DataFrame
                        try:
                            df = api_prices[ticker]
                            if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                                price = float(df['Close'].iloc[-1])
                                prices[ticker] = price
                                # Cache the new price
                                self.cache_price_data(ticker, today, price, True)
                            else:
                                # If API returned empty data, use cached price if available
                                cached_price = self.get_cached_price(ticker, today)
                                prices[ticker] = cached_price if cached_price else None
                        except Exception as e:
                            print(f"Error processing price for {ticker}: {e}")
                            # If error, use cached price if available
                            cached_price = self.get_cached_price(ticker, today)
                            prices[ticker] = cached_price if cached_price else None
                    else:
                        # If ticker not in API results, use cached price if available
                        cached_price = self.get_cached_price(ticker, today)
                        prices[ticker] = cached_price if cached_price else None
        else:
            # Not using cache, fetch all prices from API
            api_prices = self.batch_fetch_prices(tickers, period="1d")
            
            for ticker in tickers:
                if ticker in api_prices and api_prices[ticker] is not None:
                    # Extract price from DataFrame
                    try:
                        df = api_prices[ticker]
                        if isinstance(df, pd.DataFrame) and not df.empty and 'Close' in df.columns:
                            price = float(df['Close'].iloc[-1])
                            prices[ticker] = price
                            # Cache the new price
                            self.cache_price_data(ticker, today, price, True)
                        else:
                            prices[ticker] = None
                    except Exception as e:
                        print(f"Error processing price for {ticker}: {e}")
                        prices[ticker] = None
                else:
                    prices[ticker] = None
        
        return prices
    
    async def fetch_prices_parallel(self, tickers, max_workers=4, chunk_size=20):
        """
        Fetch prices for multiple tickers in parallel using asyncio
        Returns a dictionary of {ticker: price_dataframe}
        """
        if not tickers:
            return {}
        
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
    
    async def fetch_current_prices_parallel(self, tickers, max_workers=4, chunk_size=20):
        """
        Fetch current prices for multiple tickers in parallel
        Returns a dictionary of {ticker: current_price}
        """
        # Get price dataframes in parallel
        dataframes = await self.fetch_prices_parallel(tickers, max_workers, chunk_size)
        
        # Extract current prices from dataframes
        prices = {}
        for ticker, df in dataframes.items():
            if not df.empty and 'Close' in df.columns:
                prices[ticker] = float(df['Close'].iloc[-1])
            else:
                # Fallback to cached price if available
                cached_price = self.get_cached_price(ticker, date.today())
                prices[ticker] = cached_price
        
        return prices