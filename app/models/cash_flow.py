from app import db
from datetime import datetime
import uuid


class CashFlow(db.Model):
    __tablename__ = 'cash_flows'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    flow_type = db.Column(db.String(20), nullable=False)  # DEPOSIT, PURCHASE, SALE, DIVIDEND
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    running_balance = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_cash_flows_portfolio_date', 'portfolio_id', 'date'),
    )


class IRRCalculation(db.Model):
    __tablename__ = 'irr_calculations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    irr_value = db.Column(db.Float, nullable=False)
    total_invested = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    calculation_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for latest calculation queries
    __table_args__ = (
        db.Index('idx_irr_calculations_portfolio_date', 'portfolio_id', 'calculation_date'),
    )


class ETFComparison(db.Model):
    __tablename__ = 'etf_comparisons'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id'), nullable=False)
    etf_ticker = db.Column(db.String(10), nullable=False)  # VOO or QQQ
    total_invested = db.Column(db.Float, nullable=False, default=0.0)
    current_shares = db.Column(db.Float, nullable=False, default=0.0)
    current_value = db.Column(db.Float, nullable=False, default=0.0)
    irr_value = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    etf_cash_flows = db.relationship('ETFCashFlow', backref='etf_comparison', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_etf_comparisons_portfolio_ticker', 'portfolio_id', 'etf_ticker'),
    )


class ETFCashFlow(db.Model):
    __tablename__ = 'etf_cash_flows'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    etf_comparison_id = db.Column(db.String(36), db.ForeignKey('etf_comparisons.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    flow_type = db.Column(db.String(20), nullable=False)  # DEPOSIT, PURCHASE, DIVIDEND, REINVEST
    amount = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Float, nullable=True)  # Shares bought/sold
    price_per_share = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text)
    running_balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_etf_cash_flows_comparison_date', 'etf_comparison_id', 'date'),
    )