# Database Migration Scripts: Cash Flows Tracking Feature

This document provides the SQL migration scripts needed to implement the database schema for the Cash Flows Tracking feature.

## 1. PostgreSQL Migration Scripts

### 1.1 Create New Tables

```sql
-- Create CashFlow table
CREATE TABLE cash_flows (
    id VARCHAR(36) PRIMARY KEY,
    portfolio_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    flow_type VARCHAR(20) NOT NULL CHECK (flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE_PROCEEDS', 'PURCHASE')),
    amount NUMERIC(10,2) NOT NULL,
    balance_after NUMERIC(10,2) NOT NULL,
    is_inferred BOOLEAN NOT NULL DEFAULT FALSE,
    source_transaction_id VARCHAR(36),
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (source_transaction_id) REFERENCES stock_transactions(id) ON DELETE SET NULL
);

-- Create IRRCalculation table
CREATE TABLE irr_calculations (
    id VARCHAR(36) PRIMARY KEY,
    portfolio_id VARCHAR(36) NOT NULL,
    calculation_date DATE NOT NULL,
    irr_value NUMERIC(10,6) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- Create ETFComparisonPortfolio table
CREATE TABLE etf_comparison_portfolios (
    id VARCHAR(36) PRIMARY KEY,
    user_portfolio_id VARCHAR(36) NOT NULL,
    etf_ticker VARCHAR(10) NOT NULL,
    creation_date DATE NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    latest_irr NUMERIC(10,6),
    total_invested NUMERIC(10,2),
    FOREIGN KEY (user_portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- Create ETFCashFlow table
CREATE TABLE etf_cash_flows (
    id VARCHAR(36) PRIMARY KEY,
    etf_portfolio_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    flow_type VARCHAR(20) NOT NULL CHECK (flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE', 'PURCHASE')),
    amount NUMERIC(10,2) NOT NULL,
    shares NUMERIC(10,4),
    price_per_share NUMERIC(10,2),
    is_dividend_reinvest BOOLEAN NOT NULL DEFAULT FALSE,
    source_user_cashflow_id VARCHAR(36),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etf_portfolio_id) REFERENCES etf_comparison_portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (source_user_cashflow_id) REFERENCES cash_flows(id) ON DELETE SET NULL
);

-- Create ETFDividend table
CREATE TABLE etf_dividends (
    id VARCHAR(36) PRIMARY KEY,
    etf_portfolio_id VARCHAR(36) NOT NULL,
    payment_date DATE NOT NULL,
    amount_per_share NUMERIC(10,4) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    reinvested BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etf_portfolio_id) REFERENCES etf_comparison_portfolios(id) ON DELETE CASCADE
);
```

### 1.2 Modify Existing Tables

```sql
-- Add new fields to Portfolio table
ALTER TABLE portfolios
ADD COLUMN latest_irr NUMERIC(10,6),
ADD COLUMN total_invested NUMERIC(10,2);

-- Add new fields to PortfolioCache table
ALTER TABLE portfolio_cache
ADD COLUMN irr_value NUMERIC(10,6),
ADD COLUMN total_invested NUMERIC(10,2);
```

### 1.3 Create Indexes

```sql
-- Create indexes for CashFlow table
CREATE INDEX ix_cash_flows_portfolio_date ON cash_flows(portfolio_id, date);

-- Create indexes for IRRCalculation table
CREATE INDEX ix_irr_calculations_portfolio_date ON irr_calculations(portfolio_id, calculation_date);

-- Create indexes for ETF tables
CREATE INDEX ix_etf_comparison_portfolios_user_portfolio ON etf_comparison_portfolios(user_portfolio_id);
CREATE INDEX ix_etf_cash_flows_portfolio_date ON etf_cash_flows(etf_portfolio_id, date);
CREATE INDEX ix_etf_cash_flows_source ON etf_cash_flows(source_user_cashflow_id);
CREATE INDEX ix_etf_dividends_portfolio_date ON etf_dividends(etf_portfolio_id, payment_date);
```

## 2. SQLite Migration Scripts (for development/testing)

### 2.1 Create New Tables

```sql
-- Create CashFlow table
CREATE TABLE cash_flows (
    id VARCHAR(36) PRIMARY KEY,
    portfolio_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    flow_type VARCHAR(20) NOT NULL CHECK (flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE_PROCEEDS', 'PURCHASE')),
    amount NUMERIC(10,2) NOT NULL,
    balance_after NUMERIC(10,2) NOT NULL,
    is_inferred BOOLEAN NOT NULL DEFAULT 0,
    source_transaction_id VARCHAR(36),
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (source_transaction_id) REFERENCES stock_transactions(id) ON DELETE SET NULL
);

-- Create IRRCalculation table
CREATE TABLE irr_calculations (
    id VARCHAR(36) PRIMARY KEY,
    portfolio_id VARCHAR(36) NOT NULL,
    calculation_date DATE NOT NULL,
    irr_value NUMERIC(10,6) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- Create ETFComparisonPortfolio table
CREATE TABLE etf_comparison_portfolios (
    id VARCHAR(36) PRIMARY KEY,
    user_portfolio_id VARCHAR(36) NOT NULL,
    etf_ticker VARCHAR(10) NOT NULL,
    creation_date DATE NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    latest_irr NUMERIC(10,6),
    total_invested NUMERIC(10,2),
    FOREIGN KEY (user_portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
);

-- Create ETFCashFlow table
CREATE TABLE etf_cash_flows (
    id VARCHAR(36) PRIMARY KEY,
    etf_portfolio_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    flow_type VARCHAR(20) NOT NULL CHECK (flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE', 'PURCHASE')),
    amount NUMERIC(10,2) NOT NULL,
    shares NUMERIC(10,4),
    price_per_share NUMERIC(10,2),
    is_dividend_reinvest BOOLEAN NOT NULL DEFAULT 0,
    source_user_cashflow_id VARCHAR(36),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etf_portfolio_id) REFERENCES etf_comparison_portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (source_user_cashflow_id) REFERENCES cash_flows(id) ON DELETE SET NULL
);

-- Create ETFDividend table
CREATE TABLE etf_dividends (
    id VARCHAR(36) PRIMARY KEY,
    etf_portfolio_id VARCHAR(36) NOT NULL,
    payment_date DATE NOT NULL,
    amount_per_share NUMERIC(10,4) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    reinvested BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etf_portfolio_id) REFERENCES etf_comparison_portfolios(id) ON DELETE CASCADE
);
```

### 2.2 Modify Existing Tables

```sql
-- Add new fields to Portfolio table
ALTER TABLE portfolios
ADD COLUMN latest_irr NUMERIC(10,6);

ALTER TABLE portfolios
ADD COLUMN total_invested NUMERIC(10,2);

-- Add new fields to PortfolioCache table
ALTER TABLE portfolio_cache
ADD COLUMN irr_value NUMERIC(10,6);

ALTER TABLE portfolio_cache
ADD COLUMN total_invested NUMERIC(10,2);
```

### 2.3 Create Indexes

```sql
-- Create indexes for CashFlow table
CREATE INDEX ix_cash_flows_portfolio_date ON cash_flows(portfolio_id, date);

-- Create indexes for IRRCalculation table
CREATE INDEX ix_irr_calculations_portfolio_date ON irr_calculations(portfolio_id, calculation_date);

-- Create indexes for ETF tables
CREATE INDEX ix_etf_comparison_portfolios_user_portfolio ON etf_comparison_portfolios(user_portfolio_id);
CREATE INDEX ix_etf_cash_flows_portfolio_date ON etf_cash_flows(etf_portfolio_id, date);
CREATE INDEX ix_etf_cash_flows_source ON etf_cash_flows(source_user_cashflow_id);
CREATE INDEX ix_etf_dividends_portfolio_date ON etf_dividends(etf_portfolio_id, payment_date);
```

## 3. Python SQLAlchemy Models

Here are the Python SQLAlchemy model definitions that correspond to the database schema:

```python
import uuid
import datetime
from sqlalchemy import Column, String, Numeric, Date, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app import db

def generate_uuid():
    return str(uuid.uuid4())

class CashFlow(db.Model):
    __tablename__ = 'cash_flows'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    portfolio_id = Column(String(36), ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    flow_type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    is_inferred = Column(Boolean, default=False, nullable=False)
    source_transaction_id = Column(String(36), ForeignKey('stock_transactions.id', ondelete='SET NULL'), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    portfolio = relationship('Portfolio', back_populates='cash_flows')
    source_transaction = relationship('StockTransaction')
    
    __table_args__ = (
        CheckConstraint("flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE_PROCEEDS', 'PURCHASE')"),
    )


class IRRCalculation(db.Model):
    __tablename__ = 'irr_calculations'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    portfolio_id = Column(String(36), ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    calculation_date = Column(Date, nullable=False)
    irr_value = Column(Numeric(10, 6), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    portfolio = relationship('Portfolio', back_populates='irr_calculations')


class ETFComparisonPortfolio(db.Model):
    __tablename__ = 'etf_comparison_portfolios'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_portfolio_id = Column(String(36), ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    etf_ticker = Column(String(10), nullable=False)
    creation_date = Column(Date, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    latest_irr = Column(Numeric(10, 6), nullable=True)
    total_invested = Column(Numeric(10, 2), nullable=True)
    
    user_portfolio = relationship('Portfolio', foreign_keys=[user_portfolio_id])
    etf_cash_flows = relationship('ETFCashFlow', back_populates='etf_portfolio', cascade='all, delete-orphan')
    etf_dividends = relationship('ETFDividend', back_populates='etf_portfolio', cascade='all, delete-orphan')


class ETFCashFlow(db.Model):
    __tablename__ = 'etf_cash_flows'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    etf_portfolio_id = Column(String(36), ForeignKey('etf_comparison_portfolios.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    flow_type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    shares = Column(Numeric(10, 4), nullable=True)
    price_per_share = Column(Numeric(10, 2), nullable=True)
    is_dividend_reinvest = Column(Boolean, default=False, nullable=False)
    source_user_cashflow_id = Column(String(36), ForeignKey('cash_flows.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    etf_portfolio = relationship('ETFComparisonPortfolio', back_populates='etf_cash_flows')
    source_user_cashflow = relationship('CashFlow')
    
    __table_args__ = (
        CheckConstraint("flow_type IN ('DEPOSIT', 'DIVIDEND', 'SALE', 'PURCHASE')"),
    )


class ETFDividend(db.Model):
    __tablename__ = 'etf_dividends'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    etf_portfolio_id = Column(String(36), ForeignKey('etf_comparison_portfolios.id', ondelete='CASCADE'), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount_per_share = Column(Numeric(10, 4), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    reinvested = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    etf_portfolio = relationship('ETFComparisonPortfolio', back_populates='etf_dividends')


# Update existing models with new fields and relationships

# Add to Portfolio model
"""
class Portfolio(db.Model):
    # ... existing fields ...
    
    latest_irr = Column(Numeric(10, 6), nullable=True)
    total_invested = Column(Numeric(10, 2), nullable=True)
    
    # Add these relationships
    cash_flows = relationship('CashFlow', back_populates='portfolio', cascade='all, delete-orphan')
    irr_calculations = relationship('IRRCalculation', back_populates='portfolio', cascade='all, delete-orphan')
    etf_comparison_portfolios = relationship('ETFComparisonPortfolio', 
                                           foreign_keys='ETFComparisonPortfolio.user_portfolio_id',
                                           backref='source_portfolio',
                                           cascade='all, delete-orphan')
"""

# Add to PortfolioCache model
"""
class PortfolioCache(db.Model):
    # ... existing fields ...
    
    irr_value = Column(Numeric(10, 6), nullable=True)
    total_invested = Column(Numeric(10, 2), nullable=True)
"""

# Add to StockTransaction model
"""
class StockTransaction(db.Model):
    # ... existing fields ...
    
    # Add this relationship
    cash_flow = relationship('CashFlow', foreign_keys='CashFlow.source_transaction_id', uselist=False)
"""
```

## 4. Data Migration Procedure

### 4.1 Initial Data Migration Logic

Here's the Python code to populate the cash flow data from existing transactions and dividends:

```python
def migrate_existing_data_to_cash_flows():
    """
    Populates the cash_flows table with data from existing transactions and dividends.
    Should be run after creating the new tables.
    """
    from app.models import Portfolio, StockTransaction, Dividend, CashFlow, CashBalance
    from app.services.irr_calculator import IRRCalculatorService
    from sqlalchemy import desc
    
    # Process each portfolio
    portfolios = Portfolio.query.all()
    for portfolio in portfolios:
        print(f"Processing portfolio: {portfolio.name} ({portfolio.id})")
        
        # Get all transactions and dividends for this portfolio
        transactions = StockTransaction.query.filter_by(portfolio_id=portfolio.id).order_by(StockTransaction.date).all()
        dividends = Dividend.query.filter_by(portfolio_id=portfolio.id).order_by(Dividend.payment_date).all()
        
        # Combine and sort all cash flow events by date
        cash_flow_events = []
        
        for transaction in transactions:
            # For BUY transactions, create a negative cash flow (money leaving the portfolio)
            if transaction.transaction_type == 'BUY':
                cash_flow_events.append({
                    'date': transaction.date,
                    'type': 'PURCHASE',
                    'amount': -transaction.total_value,
                    'source_id': transaction.id,
                    'description': f"Purchase of {transaction.shares} shares of {transaction.ticker} @ ${transaction.price_per_share:.2f}"
                })
            # For SELL transactions, create a positive cash flow (money entering the portfolio)
            else:  # SELL
                cash_flow_events.append({
                    'date': transaction.date,
                    'type': 'SALE_PROCEEDS',
                    'amount': transaction.total_value,
                    'source_id': transaction.id,
                    'description': f"Sale of {transaction.shares} shares of {transaction.ticker} @ ${transaction.price_per_share:.2f}"
                })
        
        for dividend in dividends:
            # For dividends, create a positive cash flow
            cash_flow_events.append({
                'date': dividend.payment_date,
                'type': 'DIVIDEND',
                'amount': dividend.total_amount,
                'source_id': None,
                'description': f"Dividend from {dividend.ticker}"
            })
        
        # Sort all events by date
        cash_flow_events.sort(key=lambda x: x['date'])
        
        # Process events and create cash flow entries
        current_balance = 0.0
        deposit_required = False
        for event in cash_flow_events:
            if event['amount'] < 0 and (current_balance + event['amount'] < 0):
                # Need to add a deposit
                deposit_amount = abs(current_balance + event['amount'])
                deposit = CashFlow(
                    portfolio_id=portfolio.id,
                    date=event['date'],
                    flow_type='DEPOSIT',
                    amount=deposit_amount,
                    balance_after=deposit_amount,
                    is_inferred=True,
                    source_transaction_id=None,
                    description=f"Inferred deposit to cover {event['description']}"
                )
                db.session.add(deposit)
                current_balance += deposit_amount
            
            # Create the cash flow entry
            cash_flow = CashFlow(
                portfolio_id=portfolio.id,
                date=event['date'],
                flow_type=event['type'],
                amount=event['amount'],
                balance_after=current_balance + event['amount'],
                is_inferred=False,
                source_transaction_id=event['source_id'],
                description=event['description']
            )
            db.session.add(cash_flow)
            current_balance += event['amount']
        
        # Update the cash balance
        cash_balance = CashBalance.query.filter_by(portfolio_id=portfolio.id).first()
        if cash_balance:
            cash_balance.balance = current_balance
        else:
            cash_balance = CashBalance(portfolio_id=portfolio.id, balance=current_balance)
            db.session.add(cash_balance)
            
        # Calculate and store IRR
        irr_calculator = IRRCalculatorService()
        irr_value = irr_calculator.calculate_portfolio_irr(portfolio.id)
        
        # Update portfolio with total invested and IRR
        portfolio.total_invested = sum([e['amount'] for e in cash_flow_events if e['type'] == 'DEPOSIT'])
        portfolio.latest_irr = irr_value
        
        # Commit changes for this portfolio
        db.session.commit()
        print(f"Migration completed for portfolio {portfolio.name}")

    print("All portfolios migrated successfully!")
```

### 4.2 ETF Comparison Portfolio Setup

```python
def setup_etf_comparison_portfolios():
    """
    Creates ETF comparison portfolios for each user portfolio.
    """
    from app.models import Portfolio, ETFComparisonPortfolio
    import datetime
    
    # ETFs to track
    etfs = ['VOO', 'QQQ']
    
    # Get all portfolios
    portfolios = Portfolio.query.all()
    
    for portfolio in portfolios:
        print(f"Setting up ETF comparison for portfolio: {portfolio.name}")
        
        # Create comparison portfolio for each ETF
        for etf in etfs:
            etf_portfolio = ETFComparisonPortfolio(
                user_portfolio_id=portfolio.id,
                etf_ticker=etf,
                creation_date=datetime.date.today()
            )
            db.session.add(etf_portfolio)
        
        db.session.commit()
        
    print("ETF comparison portfolios created successfully!")
```

## 5. Running the Migration

To execute this migration in a Flask-SQLAlchemy environment:

1. Create a new migration script in Flask-Migrate (if used):
```bash
flask db migrate -m "Add cash flow tracking tables"
```

2. Review the generated migration script to ensure it matches our schema design

3. Apply the migration:
```bash
flask db upgrade
```

4. Run the data migration scripts:
```python
from app.migrations.cash_flows import migrate_existing_data_to_cash_flows, setup_etf_comparison_portfolios

# Migrate existing transaction and dividend data to cash flows
migrate_existing_data_to_cash_flows()

# Set up ETF comparison portfolios
setup_etf_comparison_portfolios()
```

## 6. Rollback Procedure

If issues are encountered during migration, the following rollback script can be used:

```sql
-- PostgreSQL Rollback Script
DROP TABLE IF EXISTS etf_dividends;
DROP TABLE IF EXISTS etf_cash_flows;
DROP TABLE IF EXISTS etf_comparison_portfolios;
DROP TABLE IF EXISTS irr_calculations;
DROP TABLE IF EXISTS cash_flows;

-- Remove added columns from existing tables
ALTER TABLE portfolios DROP COLUMN IF EXISTS latest_irr;
ALTER TABLE portfolios DROP COLUMN IF EXISTS total_invested;

ALTER TABLE portfolio_cache DROP COLUMN IF EXISTS irr_value;
ALTER TABLE portfolio_cache DROP COLUMN IF EXISTS total_invested;
```

For Flask-Migrate, use:
```bash
flask db downgrade
```