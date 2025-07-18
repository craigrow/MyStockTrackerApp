# High-Level Design: Cash Flows Tracking Feature

## 1. Introduction

### 1.1 Purpose
This document outlines the high-level design for the Cash Flows Tracking feature of MyStockTrackerApp. It provides a technical blueprint for implementing the requirements specified in the Cash Flows Tracking Requirements document.

### 1.2 Scope
This design covers:
- System architecture for the Cash Flows Tracking feature
- Data models for cash flow tracking and IRR calculation
- UI components for the new Cash Flows tab
- Service layer design for cash flow processing
- Integration approach with existing application components
- Performance optimization strategies

### 1.3 References
- Cash Flows Tracking Requirements document
- MyStockTrackerApp Current Implementation Documentation
- Existing application architecture and database schema

## 2. System Architecture

### 2.1 Architecture Overview

The Cash Flows Tracking feature will be implemented as an extension of the existing MyStockTrackerApp architecture, following the same design patterns and technology stack. The feature will introduce new components while leveraging existing services and data models.

#### 2.1.1 High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      MyStockTrackerApp                          │
│                                                                 │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐   ┌──────────┐ │
│  │ Dashboard │    │Transactions│    │ Dividends │   │  NEW:    │ │
│  │    Tab    │    │    Tab     │    │    Tab    │   │Cash Flows│ │
│  └───────────┘    └───────────┘    └───────────┘   │   Tab    │ │
│        │               │                │          └──────────┘ │
│        │               │                │               │       │
│        └───────────────┼────────────────┼───────────────┘       │
│                        │                │                       │
│                        ▼                ▼                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Application Services                    │    │
│  │                                                          │    │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐    │    │
│  │  │ Portfolio  │  │   Price    │  │    NEW:         │    │    │
│  │  │  Service   │  │  Service   │  │ Cash Flow       │    │    │
│  │  └────────────┘  └────────────┘  │   Service       │    │    │
│  │        │               │         └─────────────────┘    │    │
│  │        │               │                │               │    │
│  │        └───────────────┼────────────────┘               │    │
│  │                        │                                │    │
│  │                        ▼                                │    │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐    │    │
│  │  │ Data       │  │ Background │  │     NEW:        │    │    │
│  │  │ Loader     │  │   Tasks    │  │  IRR Calculator │    │    │
│  │  └────────────┘  └────────────┘  └─────────────────┘    │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Data Access Layer                      │    │
│  │                                                          │    │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐    │    │
│  │  │ Portfolio  │  │ Transaction │  │     NEW:        │    │    │
│  │  │   Model    │  │   Model    │  │  Cash Flow      │    │    │
│  │  └────────────┘  └────────────┘  │    Model        │    │    │
│  │                                  └─────────────────┘    │    │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐    │    │
│  │  │ Dividend   │  │    Price   │  │     NEW:        │    │    │
│  │  │   Model    │  │   History  │  │  IRR Calculation│    │    │
│  │  └────────────┘  └────────────┘  │     Model       │    │    │
│  │                                  └─────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      Database                            │    │
│  │  (PostgreSQL - Production, SQLite - Development)         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration with Existing Components

The Cash Flows Tracking feature will integrate with these existing components:

1. **Portfolio Service**
   - Extend to incorporate cash flow tracking and IRR calculations
   - Leverage existing portfolio data for historical cash flow generation

2. **Transaction Model**
   - Use as a source for generating cash flow entries
   - Create cash flow entries on transaction creation/modification

3. **Dividend Model**
   - Use as a source for generating dividend cash flow entries
   - Create cash flow entries on dividend recording

4. **DataLoader**
   - Extend to validate cash flow data integrity during import operations
   - Update to ensure cash balance consistency when importing transactions

5. **Background Tasks**
   - Integrate cash flow processing and IRR calculations with existing background task framework
   - Implement proper progress tracking for cash flow processing tasks

## 3. Data Model Design

### 3.1 New Data Entities

#### 3.1.1 CashFlow

```python
class CashFlow(db.Model):
    __tablename__ = 'cash_flows'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    flow_type = db.Column(db.Enum('DEPOSIT', 'DIVIDEND', 'SALE_PROCEEDS', 'PURCHASE', name='cash_flow_type'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    balance_after = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    is_inferred = db.Column(db.Boolean, default=False, nullable=False)
    source_transaction_id = db.Column(db.String(36), db.ForeignKey('stock_transactions.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = db.relationship('Portfolio', back_populates='cash_flows')
    source_transaction = db.relationship('StockTransaction', backref=db.backref('resulting_cash_flow', uselist=False))
    
    # Indexes
    __table_args__ = (
        db.Index('ix_cash_flows_portfolio_date', 'portfolio_id', 'date'),
    )
```

#### 3.1.2 IRRCalculation

```python
class IRRCalculation(db.Model):
    __tablename__ = 'irr_calculations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    calculation_date = db.Column(db.Date, nullable=False)
    irr_value = db.Column(db.Numeric(precision=10, scale=6), nullable=False)  # Store as decimal percentage
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = db.relationship('Portfolio', backref=db.backref('irr_calculations', order_by='IRRCalculation.calculation_date.desc()'))
    
    # Indexes
    __table_args__ = (
        db.Index('ix_irr_calculations_portfolio_date', 'portfolio_id', 'calculation_date'),
    )
```

### 3.2 Modified Data Entities

#### 3.2.1 Portfolio

```python
# Add the following to the existing Portfolio model:
cash_flows = db.relationship('CashFlow', back_populates='portfolio', order_by='CashFlow.date')
latest_irr = db.Column(db.Numeric(precision=10, scale=6), nullable=True)  # Store latest IRR calculation
total_invested = db.Column(db.Numeric(precision=10, scale=2), nullable=True)  # Store total invested amount
```

#### 3.2.2 PortfolioCache

```python
# Add the following fields to the PortfolioCache model:
irr_value = db.Column(db.Numeric(precision=10, scale=6), nullable=True)
total_invested = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
```

### 3.3 Database Migration Strategy

A database migration script will be created to:

1. Create the new `cash_flows` and `irr_calculations` tables
2. Add the new columns to the `portfolios` and `portfolio_cache` tables
3. Populate the `cash_flows` table with historical data based on existing transactions and dividends
4. Calculate initial IRR values for existing portfolios

## 4. Service Layer Design

### 4.1 CashFlowService

This new service will handle the core business logic for cash flow tracking:

```python
class CashFlowService:
    def get_portfolio_cash_flows(self, portfolio_id, start_date=None, end_date=None):
        """Retrieve all cash flows for a portfolio within a date range."""
        pass
        
    def create_cash_flow(self, portfolio_id, date, flow_type, amount, description=None, 
                         source_transaction_id=None, is_inferred=False):
        """Create a new cash flow entry."""
        pass
        
    def generate_cash_flows_from_transaction(self, transaction):
        """Generate appropriate cash flows from a stock transaction."""
        pass
        
    def generate_cash_flows_from_dividend(self, dividend):
        """Generate cash flow from a dividend payment."""
        pass
        
    def infer_deposits_for_portfolio(self, portfolio_id):
        """Find and create inferred deposits for transactions that would create negative balances."""
        pass
        
    def recalculate_cash_balances(self, portfolio_id):
        """Recalculate all cash balances chronologically to ensure consistency."""
        pass
        
    def get_total_invested(self, portfolio_id):
        """Calculate total amount invested in the portfolio."""
        pass
        
    def check_cash_flow_integrity(self, portfolio_id):
        """Verify all transactions have corresponding cash flows and balances are consistent."""
        pass
```

### 4.2 IRRCalculationService

This new service will handle IRR calculations:

```python
class IRRCalculationService:
    def calculate_portfolio_irr(self, portfolio_id, end_date=None):
        """Calculate IRR for a portfolio up to the specified date."""
        pass
        
    def calculate_etf_comparison_irr(self, portfolio_id, ticker, end_date=None):
        """Calculate IRR for a hypothetical investment in an ETF with matching cash deposits."""
        pass
        
    def get_latest_irr(self, portfolio_id):
        """Get the most recent IRR calculation for a portfolio."""
        pass
        
    def store_irr_calculation(self, portfolio_id, irr_value, start_date, end_date):
        """Store an IRR calculation result."""
        pass
        
    def _calculate_irr(self, cash_flows):
        """Internal method to calculate IRR from a list of cash flows."""
        pass
        
    def _generate_etf_cash_flows(self, portfolio_cash_flows, ticker):
        """Generate hypothetical ETF cash flows based on portfolio deposits."""
        pass
```

### 4.3 Integration with Existing Services

#### 4.3.1 PortfolioService Extensions

```python
# Add the following methods to the existing PortfolioService

def update_portfolio_after_transaction(self, transaction):
    """Update portfolio after a transaction, including cash flow generation."""
    # Existing logic...
    
    # Add new logic for cash flow tracking
    cash_flow_service = CashFlowService()
    cash_flow_service.generate_cash_flows_from_transaction(transaction)
    
    # Recalculate IRR
    irr_service = IRRCalculationService()
    irr_service.calculate_portfolio_irr(transaction.portfolio_id)
    
    return portfolio

def update_portfolio_after_dividend(self, dividend):
    """Update portfolio after dividend recording, including cash flow generation."""
    # Existing logic...
    
    # Add new logic for cash flow tracking
    cash_flow_service = CashFlowService()
    cash_flow_service.generate_cash_flows_from_dividend(dividend)
    
    # Recalculate IRR
    irr_service = IRRCalculationService()
    irr_service.calculate_portfolio_irr(dividend.portfolio_id)
    
    return portfolio
```

#### 4.3.2 DataLoader Extensions

```python
# Add the following methods to the existing DataLoader

def validate_cash_flow_integrity_after_import(self, portfolio_id):
    """Ensure cash flow integrity after bulk import operations."""
    cash_flow_service = CashFlowService()
    return cash_flow_service.check_cash_flow_integrity(portfolio_id)
```

### 4.4 Background Task Integration

```python
# Add the following to the existing BackgroundTasks service

def process_cash_flows_for_portfolio(self, portfolio_id):
    """Background task to process cash flows for a portfolio."""
    self.update_progress("Starting cash flow processing", 0)
    
    # Step 1: Validate all transactions have cash flows
    self.update_progress("Validating transaction cash flows", 20)
    cash_flow_service = CashFlowService()
    missing_transactions = cash_flow_service.check_cash_flow_integrity(portfolio_id)
    
    # Step 2: Generate any missing cash flows
    self.update_progress("Generating missing cash flows", 40)
    for transaction in missing_transactions:
        cash_flow_service.generate_cash_flows_from_transaction(transaction)
    
    # Step 3: Infer deposits where needed
    self.update_progress("Inferring deposits", 60)
    cash_flow_service.infer_deposits_for_portfolio(portfolio_id)
    
    # Step 4: Recalculate cash balances
    self.update_progress("Recalculating cash balances", 80)
    cash_flow_service.recalculate_cash_balances(portfolio_id)
    
    # Step 5: Calculate IRR
    self.update_progress("Calculating IRR", 90)
    irr_service = IRRCalculationService()
    irr_service.calculate_portfolio_irr(portfolio_id)
    
    self.update_progress("Cash flow processing complete", 100)
    return True
```

## 5. UI Design

### 5.1 Cash Flows Tab

The Cash Flows tab will follow the design patterns established in the existing application, using Bootstrap 5 for responsive layout and styling.

#### 5.1.1 Tab Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Cash Flows                                                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Summary Metrics Container                   │    │
│  │                                                          │    │
│  │  Total Amount Invested: $XX,XXX.XX                       │    │
│  │  Current Portfolio Value: $XX,XXX.XX                     │    │
│  │  IRR: XX.XX%                                             │    │
│  │                                                          │    │
│  │  Portfolio: [Portfolio Dropdown] Compare: [VOO] [QQQ]    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Cash Flows Table                            │    │
│  │                                                          │    │
│  │  Date       | Type       | Amount     | Balance  | Desc. │    │
│  │  -----------|------------|------------|----------|-------|    │
│  │  2025-07-01 | DEPOSIT    | $1,000.00  | $1,000.00| Init. │    │
│  │  2025-07-01 | PURCHASE   | -$950.00   |    $50.00| AAPL  │    │
│  │  2025-07-15 | DIVIDEND   |    $5.00   |    $55.00| AAPL  │    │
│  │  2025-08-01 | DEPOSIT    | $2,000.00  | $2,055.00| Infer.│    │
│  │  2025-08-01 | PURCHASE   | -$1,900.00 |   $155.00| MSFT  │    │
│  │  ...        | ...        | ...        | ...      | ...   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.1.2 Summary Metrics Component

The Summary Metrics component will display:

1. **Total Amount Invested**: Sum of all cash deposits into the portfolio
2. **Current Portfolio Value**: Current market value of all holdings plus cash balance
3. **IRR**: Internal Rate of Return calculated based on all cash flows

The component will also include controls for:

1. **Portfolio Selection**: Dropdown to select which portfolio to view (if multiple)
2. **Comparison Selection**: Toggle buttons to switch between portfolio, VOO, and QQQ views

#### 5.1.3 Cash Flows Table Component

The Cash Flows table will display cash flows in chronological order with the following features:

1. **Date Ordering**: All entries sorted chronologically by date
2. **Column Layout**: Date, Type, Amount, Balance, Description
3. **Visual Grouping**: Related transactions (e.g., deposit and purchase) will have matching background shading
4. **Formatting**:
   - Positive amounts (inflows) displayed in green
   - Negative amounts (outflows) displayed in red
   - Inferred deposits marked with an indicator in the description

### 5.2 HTML Templates

#### 5.2.1 Cash Flows Tab Template

```html
{% extends "base.html" %}
{% block content %}
<div class="container-fluid">
  <!-- Summary Metrics Card -->
  <div class="card mb-3">
    <div class="card-body">
      <div class="row">
        <div class="col-md-4">
          <h5>Total Amount Invested</h5>
          <h3>${{ '{:,.2f}'.format(total_invested) }}</h3>
        </div>
        <div class="col-md-4">
          <h5>Current Portfolio Value</h5>
          <h3>${{ '{:,.2f}'.format(current_value) }}</h3>
        </div>
        <div class="col-md-4">
          <h5>IRR</h5>
          <h3>{{ '{:.2f}%'.format(irr * 100) }}</h3>
        </div>
      </div>
      
      <div class="row mt-3">
        <div class="col-md-6">
          <label for="portfolio-select">Portfolio:</label>
          <select id="portfolio-select" class="form-select">
            {% for p in portfolios %}
              <option value="{{ p.id }}" {% if p.id == current_portfolio.id %}selected{% endif %}>{{ p.name }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-6">
          <label>Compare:</label>
          <div class="btn-group" role="group">
            <input type="radio" class="btn-check" name="comparison" id="portfolio-radio" value="portfolio" checked>
            <label class="btn btn-outline-primary" for="portfolio-radio">Portfolio</label>
            
            <input type="radio" class="btn-check" name="comparison" id="voo-radio" value="VOO">
            <label class="btn btn-outline-primary" for="voo-radio">VOO</label>
            
            <input type="radio" class="btn-check" name="comparison" id="qqq-radio" value="QQQ">
            <label class="btn btn-outline-primary" for="qqq-radio">QQQ</label>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Cash Flows Table Card -->
  <div class="card">
    <div class="card-body">
      <h5 class="card-title">Cash Flows</h5>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Balance</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {% for flow in cash_flows %}
            <tr class="{{ 'related-transaction' if flow.is_inferred or flow.related_to_inferred }}">
              <td>{{ flow.date.strftime('%Y-%m-%d') }}</td>
              <td>{{ flow.flow_type }}</td>
              <td class="{{ 'text-success' if flow.amount > 0 else 'text-danger' }}">
                ${{ '{:,.2f}'.format(flow.amount) }}
              </td>
              <td>${{ '{:,.2f}'.format(flow.balance_after) }}</td>
              <td>{{ flow.description }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  // Portfolio selection change handler
  $('#portfolio-select').change(function() {
    const portfolioId = $(this).val();
    const comparison = $('input[name="comparison"]:checked').val();
    window.location.href = `/cash-flows/${portfolioId}?comparison=${comparison}`;
  });
  
  // Comparison selection change handler
  $('input[name="comparison"]').change(function() {
    const portfolioId = $('#portfolio-select').val();
    const comparison = $(this).val();
    window.location.href = `/cash-flows/${portfolioId}?comparison=${comparison}`;
  });
</script>
{% endblock %}
```

## 6. Controller Design

### 6.1 Cash Flows Routes

```python
@app.route('/cash-flows')
@app.route('/cash-flows/<portfolio_id>')
def cash_flows(portfolio_id=None):
    """Display cash flows for a portfolio."""
    # Get all portfolios for the dropdown
    portfolios = Portfolio.query.all()
    
    # If no portfolio_id is specified, use the first one
    if not portfolio_id and portfolios:
        portfolio_id = portfolios[0].id
    
    # Get the comparison parameter (portfolio, VOO, or QQQ)
    comparison = request.args.get('comparison', 'portfolio')
    
    # Get the current portfolio
    current_portfolio = Portfolio.query.get(portfolio_id) if portfolio_id else None
    
    if not current_portfolio:
        flash('No portfolio found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Initialize services
    cash_flow_service = CashFlowService()
    irr_service = IRRCalculationService()
    
    # Get metrics based on comparison type
    if comparison == 'VOO':
        cash_flows = cash_flow_service.get_etf_comparison_cash_flows(portfolio_id, 'VOO')
        irr = irr_service.calculate_etf_comparison_irr(portfolio_id, 'VOO')
        total_invested = cash_flow_service.get_total_invested(portfolio_id)
        current_value = cash_flow_service.get_etf_comparison_current_value(portfolio_id, 'VOO')
    elif comparison == 'QQQ':
        cash_flows = cash_flow_service.get_etf_comparison_cash_flows(portfolio_id, 'QQQ')
        irr = irr_service.calculate_etf_comparison_irr(portfolio_id, 'QQQ')
        total_invested = cash_flow_service.get_total_invested(portfolio_id)
        current_value = cash_flow_service.get_etf_comparison_current_value(portfolio_id, 'QQQ')
    else:  # portfolio
        cash_flows = cash_flow_service.get_portfolio_cash_flows(portfolio_id)
        irr = irr_service.get_latest_irr(portfolio_id)
        total_invested = cash_flow_service.get_total_invested(portfolio_id)
        current_value = current_portfolio.get_current_value()
    
    # Mark related transactions for visual grouping
    mark_related_transactions(cash_flows)
    
    return render_template(
        'cash_flows.html',
        portfolios=portfolios,
        current_portfolio=current_portfolio,
        cash_flows=cash_flows,
        total_invested=total_invested,
        current_value=current_value,
        irr=irr,
        comparison=comparison
    )

def mark_related_transactions(cash_flows):
    """Mark related transactions for visual grouping."""
    inferred_deposits = {cf.id: cf.date for cf in cash_flows if cf.is_inferred}
    
    for cf in cash_flows:
        if not cf.is_inferred and cf.flow_type == 'PURCHASE':
            # Check if there's an inferred deposit on the same date
            for deposit_id, deposit_date in inferred_deposits.items():
                if deposit_date == cf.date:
                    cf.related_to_inferred = True
                    break
```

### 6.2 API Routes for Real-time Updates

```python
@app.route('/api/cash-flows/refresh/<portfolio_id>', methods=['POST'])
def refresh_cash_flows(portfolio_id):
    """API endpoint to refresh cash flows for a portfolio."""
    try:
        # Start background task to process cash flows
        background_tasks = BackgroundTasks()
        task_id = background_tasks.process_cash_flows_for_portfolio(portfolio_id)
        return jsonify({
            'status': 'success', 
            'message': 'Cash flow processing started',
            'task_id': task_id
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/cash-flows/progress/<task_id>', methods=['GET'])
def cash_flows_progress(task_id):
    """API endpoint to check progress of cash flow processing task."""
    background_tasks = BackgroundTasks()
    progress = background_tasks.get_task_progress(task_id)
    return jsonify(progress), 200
```

## 7. Algorithm Design

### 7.1 IRR Calculation Algorithm

The Internal Rate of Return (IRR) will be calculated using the Newton-Raphson method, which is a standard approach for IRR calculations:

```python
def calculate_irr(cash_flows, max_iterations=100, precision=0.000001):
    """
    Calculate the Internal Rate of Return (IRR) for a series of cash flows.
    
    Args:
        cash_flows: List of tuples (date, amount) where date is a datetime.date
                    and amount is a decimal (negative for outflows, positive for inflows)
        max_iterations: Maximum number of iterations for the Newton-Raphson method
        precision: Required precision for the result
        
    Returns:
        IRR as a decimal (e.g., 0.0534 for 5.34%)
    """
    # Sort cash flows by date
    cash_flows = sorted(cash_flows, key=lambda x: x[0])
    
    # Convert dates to days from first cash flow
    base_date = cash_flows[0][0]
    time_cash_flows = [(float((cf_date - base_date).days) / 365.0, amount) 
                       for cf_date, amount in cash_flows]
    
    # Initial guess for IRR (start with 10%)
    guess = 0.1
    
    # Newton-Raphson method to find IRR
    for _ in range(max_iterations):
        # Calculate net present value and its derivative at current guess
        npv = sum(amount / ((1 + guess) ** time) for time, amount in time_cash_flows)
        
        # If NPV is close enough to zero, we found IRR
        if abs(npv) < precision:
            return guess
        
        # Calculate derivative of NPV with respect to rate
        npv_prime = sum(-time * amount / ((1 + guess) ** (time + 1)) 
                        for time, amount in time_cash_flows)
        
        # Avoid division by zero
        if npv_prime == 0:
            return None
        
        # Update guess using Newton-Raphson formula
        new_guess = guess - npv / npv_prime
        
        # If new guess is within precision, return it
        if abs(new_guess - guess) < precision:
            return new_guess
        
        guess = new_guess
    
    # If no convergence after max iterations, return the best guess
    return guess
```

### 7.2 Inferred Deposits Algorithm

This algorithm will detect situations where purchases would create negative cash balances and infer deposits:

```python
def infer_deposits(portfolio_id):
    """
    Analyze cash flows and infer deposits where needed to prevent negative balances.
    
    Args:
        portfolio_id: ID of the portfolio to analyze
        
    Returns:
        List of inferred deposit cash flows that were created
    """
    # Get all cash flows for the portfolio ordered by date
    cash_flows = CashFlow.query.filter_by(portfolio_id=portfolio_id).order_by(CashFlow.date).all()
    
    # Track running balance and inferred deposits
    running_balance = 0
    inferred_deposits = []
    
    # Process cash flows in chronological order
    for cf in cash_flows:
        # Calculate new balance after this cash flow
        new_balance = running_balance + cf.amount
        
        # If new balance would be negative, infer a deposit
        if new_balance < 0 and cf.flow_type == 'PURCHASE':
            deposit_amount = abs(new_balance)
            
            # Create inferred deposit with same date
            inferred_deposit = CashFlow(
                portfolio_id=portfolio_id,
                date=cf.date,
                flow_type='DEPOSIT',
                amount=deposit_amount,
                balance_after=deposit_amount,  # Will be updated later
                is_inferred=True,
                description='Inferred deposit for purchase',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(inferred_deposit)
            inferred_deposits.append(inferred_deposit)
            
            # Update running balance with inferred deposit
            running_balance += deposit_amount
        
        # Update running balance
        running_balance = new_balance
        
        # Update stored balance
        cf.balance_after = running_balance
    
    # Commit changes to database
    db.session.commit()
    
    return inferred_deposits
```

### 7.3 ETF Comparison Algorithm

This algorithm generates hypothetical cash flows for ETF comparisons:

```python
def generate_etf_comparison_cash_flows(portfolio_id, etf_ticker):
    """
    Generate hypothetical cash flows for ETF comparison.
    
    Args:
        portfolio_id: ID of the portfolio to compare
        etf_ticker: Ticker symbol of the ETF (e.g., 'VOO', 'QQQ')
        
    Returns:
        List of hypothetical cash flows for the ETF investment
    """
    # Get all deposit cash flows from the portfolio
    deposits = CashFlow.query.filter_by(
        portfolio_id=portfolio_id, 
        flow_type='DEPOSIT'
    ).order_by(CashFlow.date).all()
    
    # Get the price history service
    price_service = PriceService()
    
    # Initialize ETF cash flows and position
    etf_cash_flows = []
    etf_shares = 0
    
    # Process each deposit as a purchase of the ETF
    for deposit in deposits:
        # Get ETF price on deposit date
        etf_price = price_service.get_price_on_date(etf_ticker, deposit.date)
        
        if etf_price:
            # Calculate shares purchased
            shares_purchased = deposit.amount / etf_price
            etf_shares += shares_purchased
            
            # Add as outflow (purchase)
            etf_cash_flows.append({
                'date': deposit.date,
                'flow_type': 'PURCHASE',
                'amount': -deposit.amount,
                'description': f'ETF Purchase: {shares_purchased:.4f} shares @ ${etf_price:.2f}'
            })
    
    # Get ETF dividend history
    etf_dividends = price_service.get_dividend_history(etf_ticker)
    
    # Process each dividend payment
    for div_date, div_amount in etf_dividends:
        # Calculate dividend based on shares held on dividend date
        shares_on_date = sum(
            d.amount / price_service.get_price_on_date(etf_ticker, d.date)
            for d in deposits if d.date <= div_date
        )
        
        dividend_payment = shares_on_date * div_amount
        
        # Add dividend as inflow
        etf_cash_flows.append({
            'date': div_date,
            'flow_type': 'DIVIDEND',
            'amount': dividend_payment,
            'description': f'ETF Dividend: ${div_amount:.4f} per share'
        })
        
        # Use dividend to purchase more shares (reinvestment)
        reinvest_price = price_service.get_price_on_date(etf_ticker, div_date)
        if reinvest_price:
            shares_purchased = dividend_payment / reinvest_price
            etf_shares += shares_purchased
            
            # Add reinvestment as outflow
            etf_cash_flows.append({
                'date': div_date,
                'flow_type': 'PURCHASE',
                'amount': -dividend_payment,
                'description': f'Dividend Reinvestment: {shares_purchased:.4f} shares @ ${reinvest_price:.2f}'
            })
    
    # Add final valuation as inflow (current value)
    current_date = datetime.now().date()
    current_price = price_service.get_current_price(etf_ticker)
    current_value = etf_shares * current_price
    
    etf_cash_flows.append({
        'date': current_date,
        'flow_type': 'VALUATION',
        'amount': current_value,
        'description': f'Current Value: {etf_shares:.4f} shares @ ${current_price:.2f}'
    })
    
    # Sort all cash flows by date
    etf_cash_flows.sort(key=lambda cf: cf['date'])
    
    return etf_cash_flows
```

## 8. Caching Strategy

### 8.1 Cache Design

The Cash Flows feature will leverage the existing PortfolioCache model with extensions for the new metrics:

```python
def cache_cash_flow_metrics(portfolio_id):
    """Cache calculated cash flow metrics for a portfolio."""
    # Get services
    cash_flow_service = CashFlowService()
    irr_service = IRRCalculationService()
    
    # Calculate metrics
    total_invested = cash_flow_service.get_total_invested(portfolio_id)
    irr = irr_service.get_latest_irr(portfolio_id)
    
    # Create or update cache entry
    cache_entry = PortfolioCache.query.filter_by(
        portfolio_id=portfolio_id,
        cache_type='CASH_FLOW_METRICS'
    ).first()
    
    if not cache_entry:
        cache_entry = PortfolioCache(
            portfolio_id=portfolio_id,
            cache_type='CASH_FLOW_METRICS',
            market_date=datetime.now().date()
        )
    
    # Update cache data
    cache_entry.cache_data = json.dumps({
        'total_invested': str(total_invested),
        'irr': str(irr),
        'calculation_date': datetime.now().isoformat()
    })
    
    # Update portfolio model as well for quick access
    portfolio = Portfolio.query.get(portfolio_id)
    portfolio.total_invested = total_invested
    portfolio.latest_irr = irr
    
    # Save changes
    db.session.add(cache_entry)
    db.session.commit()
    
    return cache_entry
```

### 8.2 Cache Invalidation Strategy

```python
def should_invalidate_cache(portfolio_id):
    """Check if cache should be invalidated."""
    cache_entry = PortfolioCache.query.filter_by(
        portfolio_id=portfolio_id,
        cache_type='CASH_FLOW_METRICS'
    ).first()
    
    if not cache_entry:
        return True
    
    # Check if cache is older than 24 hours
    cache_data = json.loads(cache_entry.cache_data)
    calculation_date = datetime.fromisoformat(cache_data['calculation_date'])
    age_hours = (datetime.now() - calculation_date).total_seconds() / 3600
    
    if age_hours > 24:
        return True
    
    # Check if there are new transactions or dividends since cache was created
    latest_transaction = StockTransaction.query.filter_by(portfolio_id=portfolio_id).order_by(
        StockTransaction.updated_at.desc()).first()
    latest_dividend = Dividend.query.filter_by(portfolio_id=portfolio_id).order_by(
        Dividend.created_at.desc()).first()
    
    if (latest_transaction and latest_transaction.updated_at > calculation_date) or \
       (latest_dividend and latest_dividend.created_at > calculation_date):
        return True
    
    return False
```

## 9. Error Handling Strategy

### 9.1 Common Error Scenarios

1. **Missing Price Data**:
   - Handle cases where ETF price data is unavailable for certain dates
   - Fall back to nearest available price or interpolate between available prices

2. **IRR Calculation Failures**:
   - Handle non-convergence in IRR algorithm
   - Provide graceful fallbacks for edge cases (e.g., all negative flows)

3. **Data Integrity Issues**:
   - Handle inconsistencies between transactions and cash flows
   - Provide self-healing mechanisms to restore data consistency

### 9.2 Error Handling Implementation

```python
def safe_calculate_irr(cash_flows, max_retries=3):
    """
    Safely calculate IRR with fallbacks for common error cases.
    
    Args:
        cash_flows: List of cash flow tuples (date, amount)
        max_retries: Maximum number of retry attempts with different initial guesses
        
    Returns:
        IRR value or None if calculation fails
    """
    # Initial guesses to try if first attempt fails
    initial_guesses = [0.1, 0.05, 0.2, 0.01, 0.5]
    
    # Check if cash flows are valid for IRR calculation
    if not cash_flows or len(cash_flows) < 2:
        log_error("Not enough cash flows for IRR calculation")
        return None
    
    # Check if there's at least one positive and one negative flow
    has_positive = any(amount > 0 for _, amount in cash_flows)
    has_negative = any(amount < 0 for _, amount in cash_flows)
    
    if not (has_positive and has_negative):
        log_error("IRR calculation requires both positive and negative cash flows")
        return None
    
    # Try with different initial guesses
    for i, guess in enumerate(initial_guesses[:max_retries]):
        try:
            irr = calculate_irr(cash_flows, initial_guess=guess)
            if irr is not None:
                return irr
        except Exception as e:
            log_error(f"IRR calculation failed on attempt {i+1}: {str(e)}")
    
    # If all attempts fail, log error and return None
    log_error("IRR calculation failed after multiple attempts")
    return None
```

## 10. Testing Strategy

### 10.1 Unit Testing

Key components to test include:

1. **CashFlowService**:
   - Test cash flow creation from transactions
   - Test inferred deposit detection
   - Test cash balance recalculation
   - Test total invested calculation

2. **IRRCalculationService**:
   - Test IRR calculation with various cash flow patterns
   - Test edge cases (all deposits, no sales, etc.)
   - Test ETF comparison calculations

3. **Data Integrity**:
   - Test transaction-to-cash-flow mapping
   - Test dividend-to-cash-flow mapping
   - Test balance consistency checks

### 10.2 Integration Testing

Key integration points to test include:

1. **Transaction Creation Flow**:
   - Verify cash flows are created when transactions are added
   - Verify cash balances are updated correctly

2. **CSV Import**:
   - Test bulk import with cash flow generation
   - Test inferred deposit creation for imported transactions

3. **Real-time Updates**:
   - Test IRR updates after transaction additions
   - Test performance metrics updates across the application

### 10.3 Test Data Generation

Create comprehensive test portfolios covering:

1. Simple portfolio with few transactions
2. Complex portfolio with many transactions over time
3. Portfolio with same-day transactions requiring ordering
4. Portfolio requiring inferred deposits
5. Portfolio with dividend reinvestment

## 11. Implementation Plan

### 11.1 Development Phases

#### Phase 1: Foundation
1. Database schema updates and migrations
2. Core CashFlow and IRRCalculation models
3. Basic CashFlowService implementation
4. Unit tests for core functionality

#### Phase 2: Integration
1. Transaction and dividend integration with cash flow tracking
2. Cash balance maintenance and inferred deposit logic
3. IRR calculation implementation
4. Integration tests

#### Phase 3: UI Implementation
1. Cash Flows tab UI development
2. Summary metrics display
3. Cash flow table with visual grouping
4. UI tests

#### Phase 4: ETF Comparison
1. ETF dividend data integration
2. ETF comparison cash flow generation
3. View switching implementation
4. Comparison tests

#### Phase 5: Optimization
1. Caching implementation
2. Performance optimization
3. Background processing
4. Load testing

### 11.2 Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1: Foundation | 1 week | Database schema, Core models, Base services |
| 2: Integration | 1 week | Transaction hooks, Balance logic, IRR calculations |
| 3: UI Implementation | 1 week | Cash Flows tab, Table display, Summary metrics |
| 4: ETF Comparison | 1 week | ETF data integration, Comparison views |
| 5: Optimization | 1 week | Caching, Performance improvements |

### 11.3 Validation Period

After implementing the Cash Flows Tracking feature, a validation period will be required to ensure the accuracy of IRR calculations before they replace the current performance metrics. This will involve:

1. Running both calculation methods in parallel
2. Comparing results across different portfolio types
3. Validating with test portfolios with known IRR values
4. Addressing any discrepancies before switching to IRR as the primary metric

## 12. Conclusion

This high-level design document outlines the technical approach for implementing the Cash Flows Tracking feature for MyStockTrackerApp. The design focuses on:

1. Accurate tracking of all portfolio cash flows
2. Implementation of IRR as a performance metric
3. Comparison with ETF benchmarks using consistent methodology
4. Performance optimization through intelligent caching
5. Integration with the existing application architecture

The implementation will follow the phased approach outlined in this document, with thorough testing at each stage to ensure accuracy and reliability. Once validated, the IRR calculations will provide users with a more accurate measure of portfolio performance that accounts for all cash flows and timing of investments.