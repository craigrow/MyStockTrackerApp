import threading
import time
from datetime import datetime, timedelta
from app.services.price_service import PriceService
from app.services.portfolio_service import PortfolioService
from app import db

class BackgroundPriceUpdater:
    def __init__(self):
        self.price_service = PriceService()
        self.portfolio_service = PortfolioService()
        self.update_queue = []
        self.is_running = False
        self.progress = {'current': 0, 'total': 0, 'status': 'idle'}
    
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
                'stale_data': self._check_stale_data(tickers)
            }
            
            if not self.is_running:
                threading.Thread(target=self._process_queue, daemon=True).start()
                
        except Exception as e:
            print(f"Error queuing price updates: {e}")
    
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
    
    def _process_queue(self):
        """Process the price update queue in background"""
        self.is_running = True
        self.progress['status'] = 'updating'
        
        try:
            for i, ticker in enumerate(self.update_queue):
                self.progress['current'] = i + 1
                
                # Fetch current price with timeout
                try:
                    price = self.price_service.fetch_from_api(ticker)
                    if price:
                        from datetime import date
                        self.price_service.cache_price_data(ticker, date.today(), price, True)
                        print(f"Updated {ticker}: ${price:.2f}")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"Failed to update {ticker}: {e}")
                    continue
            
            self.progress['status'] = 'completed'
            self.progress['last_updated'] = datetime.utcnow()
            
        except Exception as e:
            print(f"Error processing price queue: {e}")
            self.progress['status'] = 'error'
        finally:
            self.is_running = False
    
    def get_progress(self):
        """Get current update progress"""
        return self.progress.copy()

# Global instance
background_updater = BackgroundPriceUpdater()