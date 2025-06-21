"""
Cache models for storing computed results.
"""
from app import db
from datetime import datetime
import json


class PortfolioCache(db.Model):
    """Cache for portfolio calculations"""
    __tablename__ = 'portfolio_cache'
    
    id = db.Column(db.String(36), primary_key=True)
    portfolio_id = db.Column(db.String(36), nullable=False)
    cache_type = db.Column(db.String(50), nullable=False)  # 'stats', 'chart_data'
    cache_data = db.Column(db.Text, nullable=False)  # JSON data
    market_date = db.Column(db.Date, nullable=False)  # Market date this cache is for
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def get_data(self):
        """Get cached data as Python object"""
        return json.loads(self.cache_data)
    
    def set_data(self, data):
        """Set cached data from Python object"""
        self.cache_data = json.dumps(data, default=str)