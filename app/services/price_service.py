from app import db
from app.models.price import PriceHistory
from datetime import datetime, date, timedelta
import yfinance as yf


class PriceService:
    
    def get_current_price(self, ticker, use_stale=True):
        """Get current price with option to use stale data"""
        from datetime import date
        
        # First check cache
        cached_price = self.get_cached_price(ticker, date.today())
        if cached_price and self.is_cache_fresh(ticker, date.today()):
            return cached_price
        
        # If we allow stale data and have cached price, return it
        if use_stale and cached_price:
            return cached_price
        
        # Fetch from API with timeout
        price = self.fetch_from_api(ticker, timeout=10)
        if price:
            self.cache_price_data(ticker, date.today(), price, True)
            return price
        
        # Fallback to cached price if API fails
        return cached_price
    
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
        time_diff = datetime.utcnow() - price_history.last_updated
        return time_diff < timedelta(minutes=freshness_minutes)
    
    def get_data_freshness(self, ticker, price_date):
        """Get how old the cached data is in minutes"""
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        
        if not price_history or not price_history.last_updated:
            return None
        
        time_diff = datetime.utcnow() - price_history.last_updated
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
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        
        if price_history:
            price_history.close_price = price
            price_history.is_intraday = is_intraday
            price_history.price_timestamp = datetime.utcnow()
            price_history.last_updated = datetime.utcnow()
        else:
            price_history = PriceHistory(
                ticker=ticker,
                date=price_date,
                close_price=price,
                is_intraday=is_intraday,
                price_timestamp=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.session.add(price_history)
        
        db.session.commit()
    
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