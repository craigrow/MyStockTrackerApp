# Portfolio Percentage Column - Implementation Context

## Overview
Add a "Portfolio %" column to the Current Portfolio Holdings table on the Dashboard page. This column will show each holding's percentage of the total portfolio value and will be the default sort order (largest to smallest).

## Requirements
- **Column Title**: "Portfolio %"
- **Calculation**: (Market Value / Total Portfolio Value) * 100
- **Default Sort**: Largest to smallest percentage
- **Display Format**: Percentage with 2 decimal places

## Current Implementation Analysis

### Holdings Table Structure
- Located in: `app/templates/dashboard.html`
- Current columns: Ticker, Shares, Current Price, Market Value, Gain/Loss, %
- Data source: `get_holdings_with_performance()` in `app/views/main.py`

### Data Flow
1. `dashboard()` route calls `get_holdings_with_performance()`
2. Function returns list of holding dictionaries with market_value
3. Template renders table with holdings data
4. Need to calculate total portfolio value for percentage calculation

### Implementation Paths
1. **Backend**: Modify `get_holdings_with_performance()` to include portfolio_percentage
2. **Frontend**: Add new column to holdings table template
3. **Sorting**: Add JavaScript sorting with portfolio_percentage as default

## Dependencies
- Existing holdings calculation logic
- Market value calculations
- Template rendering system
- No new external dependencies required

## Testing Strategy
- Unit tests for percentage calculation logic
- Integration tests for dashboard rendering
- Verify sorting functionality
- Test edge cases (zero portfolio value, single holding)