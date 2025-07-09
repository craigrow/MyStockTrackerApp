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