import threading
import time
import asyncio
import logging
from datetime import datetime, timedelta
from app.services.price_service import PriceService
from app.services.portfolio_service import PortfolioService
from app import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundPriceUpdater:
    def __init__(self):
        self.price_service = PriceService()
        self.portfolio_service = PortfolioService()
        self.update_queue = []
        self.is_running = False
        self.progress = {'current': 0, 'total': 0, 'status': 'idle'}
        self.use_parallel = True  # Set to True to use parallel processing
        self.batch_size = 20  # Optimal batch size for yfinance
        self.max_workers = 4  # Maximum number of parallel workers
    
    def queue_portfolio_price_updates(self, portfolio_id):
        """Queue price updates for a portfolio's holdings"""
        try:
            holdings = self.portfolio_service.get_current_holdings(portfolio_id)
            tickers = list(holdings.keys()) + ['VOO', 'QQQ']  # Include ETFs
            
            self.update_queue = list(set(tickers))  # Remove duplicates
            self.progress = {
                'current': 0, 
                'total': len(self.update_queue),
                'status': 'queued',
                'last_updated': None,
                'stale_data': self._check_stale_data(tickers),
                'portfolio_id': portfolio_id,
                'queue_time': datetime.utcnow()
            }
            
            if not self.is_running:
                if self.use_parallel:
                    # Use asyncio for parallel processing
                    threading.Thread(target=self._run_async_process_queue, daemon=True).start()
                else:
                    # Use batch processing
                    threading.Thread(target=self._process_queue_batch, daemon=True).start()
                
            return True
        except Exception as e:
            logger.error(f"Error queuing price updates: {e}")
            return False
    
    def _check_stale_data(self, tickers):
        """Check if any ticker has stale data (>5 minutes old)"""
        from app.models.price import PriceHistory
        from datetime import date
        
        stale_tickers = []
        for ticker in tickers:
            price_record = PriceHistory.query.filter_by(
                ticker=ticker, 
                date=date.today()
            ).first()
            
            if not price_record:
                stale_tickers.append(ticker)
            elif price_record.last_updated:
                time_diff = datetime.utcnow() - price_record.last_updated
                if time_diff > timedelta(minutes=5):
                    stale_tickers.append(ticker)
        
        return stale_tickers
    
    def _run_async_process_queue(self):
        """Run the async process queue in a separate thread"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async function
            loop.run_until_complete(self._process_queue_parallel())
            loop.close()
        except Exception as e:
            logger.error(f"Error in async process queue: {e}")
            self.progress['status'] = 'error'
            self.progress['error'] = str(e)
            self.is_running = False
    
    async def _process_queue_parallel(self):
        """Process the price update queue in background using parallel processing"""
        self.is_running = True
        self.progress['status'] = 'updating'
        start_time = datetime.utcnow()
        
        try:
            from datetime import date
            today = date.today()
            
            # Use parallel processing for better performance
            prices = await self.price_service.fetch_current_prices_parallel(
                self.update_queue,
                max_workers=self.max_workers,
                chunk_size=self.batch_size
            )
            
            # Cache the results
            self.price_service.batch_cache_price_data(prices, today, True)
            
            # Count updated prices
            updated_count = sum(1 for p in prices.values() if p is not None)
            
            self.progress['current'] = len(self.update_queue)
            self.progress['status'] = 'completed'
            self.progress['last_updated'] = datetime.utcnow()
            self.progress['updated_count'] = updated_count
            self.progress['execution_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Price update completed: {updated_count}/{len(self.update_queue)} prices updated in {self.progress['execution_time']:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error processing price queue: {e}")
            self.progress['status'] = 'error'
            self.progress['error'] = str(e)
            self.progress['error_time'] = datetime.utcnow()
        finally:
            self.is_running = False
    
    def _process_queue_batch(self):
        """Process the price update queue in background using batch processing"""
        self.is_running = True
        self.progress['status'] = 'updating'
        start_time = datetime.utcnow()
        
        try:
            from datetime import date
            today = date.today()
            
            # Process tickers in batches for better performance
            batch_size = self.batch_size
            total_updated = 0
            failed_tickers = []
            
            for i in range(0, len(self.update_queue), batch_size):
                batch = self.update_queue[i:i+batch_size]
                self.progress['current'] = i + len(batch)
                
                try:
                    # Use batch processing for better performance
                    prices = self.price_service.batch_fetch_current_prices(batch)
                    
                    # Cache the results
                    self.price_service.batch_cache_price_data(prices, today, True)
                    
                    # Count updated prices and track failures
                    batch_updated = 0
                    for ticker, price in prices.items():
                        if price is not None:
                            batch_updated += 1
                        else:
                            failed_tickers.append(ticker)
                    
                    total_updated += batch_updated
                    
                    logger.info(f"Updated batch {i//batch_size + 1}: {batch_updated}/{len(batch)} prices")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Failed to update batch {i//batch_size + 1}: {e}")
                    failed_tickers.extend(batch)
                    continue
            
            # Try to fetch any failed tickers individually
            if failed_tickers:
                logger.info(f"Retrying {len(failed_tickers)} failed tickers individually")
                retry_count = 0
                
                for ticker in failed_tickers:
                    try:
                        price = self.price_service.fetch_from_api(ticker, timeout=5)
                        if price:
                            self.price_service.cache_price_data(ticker, today, price, True)
                            total_updated += 1
                            retry_count += 1
                        time.sleep(0.2)  # Small delay between retries
                    except Exception:
                        pass
                
                logger.info(f"Retry results: {retry_count}/{len(failed_tickers)} tickers updated")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.progress['status'] = 'completed'
            self.progress['last_updated'] = datetime.utcnow()
            self.progress['updated_count'] = total_updated
            self.progress['execution_time'] = execution_time
            self.progress['failed_count'] = len(failed_tickers) - (retry_count if 'retry_count' in locals() else 0)
            
            logger.info(f"Price update completed: {total_updated}/{len(self.update_queue)} prices updated in {execution_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error processing price queue: {e}")
            self.progress['status'] = 'error'
            self.progress['error'] = str(e)
            self.progress['error_time'] = datetime.utcnow()
        finally:
            self.is_running = False
    
    def get_progress(self):
        """Get current update progress"""
        return self.progress.copy()


class BackgroundChartGenerator:
    def __init__(self):
        self.price_service = PriceService()
        self.portfolio_service = PortfolioService()
        self.is_running = False
        self.progress = {'status': 'idle', 'portfolio_id': None}
        self.chart_data = {}
        self.max_cache_age_hours = 24  # Cache chart data for 24 hours
    
    def generate_chart_data(self, portfolio_id):
        """Queue chart data generation for a portfolio"""
        if self.is_running:
            logger.info(f"Chart generation already in progress for portfolio {self.progress.get('portfolio_id')}")
            return False
        
        # Check if we already have fresh chart data in memory
        if portfolio_id in self.chart_data:
            if self.progress.get('portfolio_id') == portfolio_id and self.progress.get('status') == 'completed':
                start_time = self.progress.get('start_time')
                if start_time:
                    age_hours = (datetime.utcnow() - start_time).total_seconds() / 3600
                    if age_hours < self.max_cache_age_hours:
                        logger.info(f"Using cached chart data for portfolio {portfolio_id} (age: {age_hours:.1f} hours)")
                        return True
        
        # Check if we have cached chart data in the database
        from app.views.main import get_cached_chart_data, get_last_market_date
        market_date = get_last_market_date()
        cached_data = get_cached_chart_data(portfolio_id, market_date)
        
        if cached_data:
            logger.info(f"Using database cached chart data for portfolio {portfolio_id}")
            self.chart_data[portfolio_id] = cached_data
            self.progress = {
                'status': 'completed',
                'portfolio_id': portfolio_id,
                'start_time': datetime.utcnow() - timedelta(minutes=1),  # Pretend it just finished
                'completion_time': datetime.utcnow(),
                'source': 'database_cache'
            }
            return True
        
        # No cached data, generate new chart data
        self.progress = {
            'status': 'queued',
            'portfolio_id': portfolio_id,
            'start_time': datetime.utcnow(),
            'percent_complete': 0
        }
        
        threading.Thread(target=self._generate_chart_data, args=(portfolio_id,), daemon=True).start()
        return True
    
    def _generate_chart_data(self, portfolio_id):
        """Generate chart data in background with progress tracking"""
        self.is_running = True
        self.progress['status'] = 'generating'
        
        try:
            # Import here to avoid circular imports
            from app.views.main import generate_chart_data
            
            # Track start time for performance monitoring
            start_time = datetime.utcnow()
            self.progress['generation_started'] = start_time
            
            # Generate chart data
            chart_data = generate_chart_data(portfolio_id, self.portfolio_service, self.price_service)
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Cache the chart data
            self._cache_chart_data(portfolio_id, chart_data)
            
            self.progress['status'] = 'completed'
            self.progress['completion_time'] = datetime.utcnow()
            self.progress['generation_time_seconds'] = generation_time
            self.chart_data[portfolio_id] = chart_data
            
            logger.info(f"Chart data generation completed for portfolio {portfolio_id} in {generation_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            import traceback
            traceback.print_exc()
            self.progress['status'] = 'error'
            self.progress['error'] = str(e)
            self.progress['error_time'] = datetime.utcnow()
            
            # Try to generate minimal chart data as fallback
            try:
                minimal_chart_data = self._generate_minimal_chart_data(portfolio_id)
                self.chart_data[portfolio_id] = minimal_chart_data
                self.progress['status'] = 'completed_with_fallback'
                logger.info(f"Generated minimal fallback chart data for portfolio {portfolio_id}")
            except Exception as fallback_error:
                logger.error(f"Error generating fallback chart data: {fallback_error}")
        finally:
            self.is_running = False
    
    def _generate_minimal_chart_data(self, portfolio_id):
        """Generate minimal chart data as fallback when full generation fails"""
        try:
            # Get transactions to determine date range
            transactions = self.portfolio_service.get_portfolio_transactions(portfolio_id)
            
            if not transactions:
                return {
                    'dates': [],
                    'portfolio_values': [],
                    'voo_values': [],
                    'qqq_values': []
                }
            
            # Get date range from first transaction to today
            end_date = date.today()
            start_date = min(t.date for t in transactions)
            
            # Generate simplified date range (weekly points instead of daily)
            from datetime import timedelta
            import pandas as pd
            
            # Create weekly date points
            date_range = []
            current = start_date
            while current <= end_date:
                date_range.append(current)
                current += timedelta(days=7)  # Weekly points
            
            # Ensure today is included
            if end_date not in date_range:
                date_range.append(end_date)
            
            # Format dates as strings
            dates = [d.strftime('%Y-%m-%d') for d in date_range]
            
            # Create placeholder values (linear growth)
            portfolio_values = []
            voo_values = []
            qqq_values = []
            
            # Get current portfolio value
            current_value = 0
            holdings = self.portfolio_service.get_current_holdings(portfolio_id)
            
            for ticker, shares in holdings.items():
                current_price = self.price_service.get_current_price(ticker, use_stale=True)
                if current_price:
                    current_value += shares * current_price
            
            # Create linear progression from 0 to current value
            for i in range(len(dates)):
                factor = i / (len(dates) - 1) if len(dates) > 1 else 0
                portfolio_values.append(current_value * factor)
                voo_values.append(current_value * factor * 0.9)  # Slightly underperform
                qqq_values.append(current_value * factor * 1.1)  # Slightly outperform
            
            return {
                'dates': dates,
                'portfolio_values': portfolio_values,
                'voo_values': voo_values,
                'qqq_values': qqq_values,
                'is_fallback': True
            }
        except Exception as e:
            logger.error(f"Error generating minimal chart data: {e}")
            # Return empty chart data
            return {
                'dates': [],
                'portfolio_values': [],
                'voo_values': [],
                'qqq_values': [],
                'is_fallback': True,
                'error': str(e)
            }
    
    def _cache_chart_data(self, portfolio_id, chart_data):
        """Cache chart data in the database"""
        try:
            from app.models.cache import PortfolioCache
            import uuid
            from datetime import date
            
            # Get the last market date
            from app.views.main import get_last_market_date
            market_date = get_last_market_date()
            
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
            
            logger.info(f"Chart data cached for portfolio {portfolio_id}")
            
        except Exception as e:
            logger.error(f"Error caching chart data: {e}")
            db.session.rollback()
    
    def get_progress(self):
        """Get current chart generation progress"""
        return self.progress.copy()
    
    def get_chart_data(self, portfolio_id):
        """Get generated chart data for a portfolio"""
        return self.chart_data.get(portfolio_id)


# Global instances
background_updater = BackgroundPriceUpdater()
chart_generator = BackgroundChartGenerator()
