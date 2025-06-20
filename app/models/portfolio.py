from app import db
from datetime import datetime
import uuid


class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('StockTransaction', backref='portfolio', lazy=True)
    dividends = db.relationship('Dividend', backref='portfolio', lazy=True)
    cash_balance = db.relationship('CashBalance', backref='portfolio', uselist=False)


class StockTransaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    date = db.Column(db.Date, nullable=False)
    price_per_share = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)


class Dividend(db.Model):
    __tablename__ = 'dividends'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)


class CashBalance(db.Model):
    __tablename__ = 'cash_balances'
    
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)