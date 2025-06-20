from app import db
from datetime import datetime


class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    ticker = db.Column(db.String(10), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    close_price = db.Column(db.Float, nullable=False)
    is_intraday = db.Column(db.Boolean, nullable=False, default=False)
    price_timestamp = db.Column(db.DateTime, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)