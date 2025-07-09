# Cash Flows Data Synchronization Strategy

## Overview
Instead of one-time data migration, we use on-demand synchronization to ensure cash flows stay current with transaction data. This approach handles all edge cases and maintains data integrity automatically.

## Key Principles

### 1. Page-Level Validation
- **Dashboard route**: Validate cash flows before rendering
- **Cash Flows page route**: Validate cash flows before rendering
- **Any route using cash flow data**: Validate first

### 2. Hash-Based Synchronization
- Compare hash of source data (transactions + dividends) with stored hash
- Regenerate cash flows if hashes don't match
- Handles all modification scenarios

## Edge Cases Handled

### Backdated Transactions
```
Existing: 7/1, 7/7, 7/15
User adds: 7/3 (backdated)
Result: Hash changes, cash flows regenerated
```

### Modified Transactions
```
User edits existing transaction amount/date
Result: Hash changes, cash flows regenerated
```

### Deleted Transactions
```
User removes transaction
Result: Hash changes, cash flows regenerated
```

### New Dividends
```
User adds dividend payment
Result: Hash changes, cash flows regenerated
```

## Implementation Components

### 1. Database Schema Migration
```sql
-- Create tables only (no data population)
CREATE TABLE cash_flows (...);
CREATE TABLE irr_calculations (...);
-- Add hash tracking field to portfolios
ALTER TABLE portfolios ADD COLUMN cash_flow_data_hash VARCHAR(64);
```

### 2. Data Synchronization Service
```python
class CashFlowSyncService:
    def ensure_cash_flows_current(self, portfolio_id):
        """Ensure cash flows are synchronized with transaction data"""
        
        if not self.is_cash_flow_data_current(portfolio_id):
            self.regenerate_cash_flows(portfolio_id)
    
    def is_cash_flow_data_current(self, portfolio_id):
        """Check if cash flows match current transaction data"""
        current_hash = self.calculate_source_data_hash(portfolio_id)
        stored_hash = self.get_stored_hash(portfolio_id)
        return current_hash == stored_hash
    
    def calculate_source_data_hash(self, portfolio_id):
        """Generate hash from all transactions and dividends"""
        # Hash: transaction_id + date + amount + type + dividend data
        # Detects any changes to source data
```

### 3. Page Integration
```python
@main_blueprint.route('/')
def dashboard():
    if current_portfolio:
        # Ensure data is current before using
        sync_service = CashFlowSyncService()
        sync_service.ensure_cash_flows_current(current_portfolio.id)
        
        # Now safe to use cash flow data
        portfolio_stats = calculate_portfolio_stats(...)

@cash_flows_blueprint.route('/cash-flows')
def cash_flows_page():
    # Same pattern for cash flows page
    sync_service.ensure_cash_flows_current(portfolio_id)
    cash_flows = cash_flow_service.get_cash_flows(portfolio_id)
```

## Benefits

### Self-Healing
- Missing cash flow data gets regenerated automatically
- Corrupted data gets detected and fixed
- No manual intervention required

### Always Accurate
- Cash flows always reflect current transaction state
- No risk of stale data
- Handles all user modification scenarios

### Performance Optimized
- Hash comparison is fast (O(1))
- Only regenerates when necessary
- Caches results until data changes

### Maintenance-Free
- No scheduled jobs or manual updates
- No risk of forgetting to update cash flows
- Robust against all data modification patterns

## Next Session Tasks

1. **Create database migration script** (schema only)
2. **Implement CashFlowSyncService** with hash-based validation
3. **Add page-level integration** to dashboard and cash flows routes
4. **Test edge cases** (backdated transactions, modifications, deletions)
5. **Performance validation** with large portfolios

## Risk Mitigation

### Performance
- Hash calculation is lightweight
- Only runs on page load (not every request)
- Cached until data changes

### Data Integrity
- Read-only validation (no destructive operations)
- Can always regenerate from source transactions
- Maintains audit trail of all changes

### Rollback Strategy
- Can disable cash flow features without affecting existing functionality
- Source transaction data remains unchanged
- Easy to revert if issues arise