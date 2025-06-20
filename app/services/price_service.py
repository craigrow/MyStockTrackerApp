from app import db
from app.models.price import PriceHistory
from datetime import datetime, date, timedelta
import yfinance as yf


class PriceService:
    
    def get_current_price(self, ticker):
        # First check cache
        cached_price = self.get_cached_price(ticker, date.today())
        if cached_price and self.is_cache_fresh(ticker, date.today()):
            return cached_price
        
        # Fetch from API
        price = self.fetch_from_api(ticker)
        if price:
            self.cache_price_data(ticker, date.today(), price, True)
        
        return price
    
    def get_cached_price(self, ticker, price_date):
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        return price_history.close_price if price_history else None
    
    def is_cache_fresh(self, ticker, price_date):
        price_history = PriceHistory.query.filter_by(
            ticker=ticker, 
            date=price_date
        ).first()
        
        if not price_history:
            return False
        
        # Consider cache fresh if updated within last 5 minutes
        time_diff = datetime.utcnow() - price_history.last_updated
        return time_diff < timedelta(minutes=5)
    
    def fetch_from_api(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty and len(hist) > 0:
                return float(hist.iloc[-1]['Close'])
        except Exception:
            pass
        return None
    
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