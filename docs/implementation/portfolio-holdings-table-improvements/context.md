# Portfolio Holdings Table Improvements - Context

## Project Structure
- **Repository Root**: `/Users/craigrow/craigrow_code/MyStockTrackerApp_Q`
- **Branch**: devQ (confirmed)
- **Framework**: Flask with SQLAlchemy, Bootstrap 5 frontend
- **Database**: PostgreSQL (production), SQLite (development)

## Task Overview
Improve the Current Portfolio Holdings table on the Dashboard with:

1. **Sortable Columns**: Click headers to sort by any column
2. **Column Validation**: Validate and relabel '%' column to 'Gain/Loss %'
3. **VOO Performance**: Add column showing VOO performance with same investment/dates
4. **QQQ Performance**: Add column showing QQQ performance with same investment/dates  
5. **Number Formatting**: Format all numbers with commas for 1000+
6. **Top Holdings Highlighting**: Shade top 50% holdings (by portfolio value) in light grey

## Current Implementation
- Dashboard template: `app/templates/dashboard.html`
- Holdings data populated via Flask route
- Bootstrap 5 styling with responsive table
- Current columns: Ticker, Shares, Current Price, Market Value, Gain/Loss, %

## Requirements
- Maintain existing functionality
- Add ETF performance comparisons using existing API endpoints
- Implement client-side sorting with JavaScript
- Apply conditional formatting for top holdings
- Ensure responsive design compatibility

## Dependencies
- Existing ETF performance API endpoints
- Bootstrap 5 table components
- JavaScript for sorting functionality
- Flask backend for data calculations