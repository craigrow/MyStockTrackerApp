# ETF Dividend Calculation Fix - Context

## Project Structure
- **Project Type**: Python Flask web application
- **Testing Framework**: pytest (275+ comprehensive tests)
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Heroku with GitHub Actions CI/CD
- **Branch**: devR (development branch for AI agent R)

## Requirements
Fix the ETF dividend calculation bug in `ETFComparisonService._get_etf_dividend_flows()` method where:

### Current Problem
- Method uses `total_shares` (final total shares) for ALL dividend calculations
- Should calculate shares held **at each dividend date** instead
- Example: If portfolio has 100 shares today but had 50 shares on 10/1/2024 when $1 dividend was paid:
  - **Current (Wrong)**: Records $100 dividend ($1 × 100 shares)
  - **Correct**: Should record $50 dividend ($1 × 50 shares held on that date)

### Functional Requirements
1. Calculate shares held at each dividend payment date
2. Account for initial purchases up to dividend date
3. Account for previous dividend reinvestments up to dividend date
4. Generate correct dividend cash flows for ETF comparisons
5. Maintain dividend reinvestment functionality

### Acceptance Criteria
- Dividend amounts reflect actual shares held on dividend date
- ETF comparison IRR calculations are accurate
- All existing tests continue to pass
- New tests validate correct dividend calculation

## Implementation Paths
- **Target File**: `app/services/etf_comparison_service.py`
- **Target Method**: `_get_etf_dividend_flows()`
- **Test File**: `tests/test_etf_comparison_service.py`

## Dependencies
- `yfinance` for ETF dividend data
- `PriceService` for historical prices
- `CashFlowService` for portfolio deposits
- `IRRCalculationService` for performance calculations

## Existing Documentation
- Cash flows feature requirements in `docs/cash_flows_feature/`
- Current implementation documented in `docs/CURRENT_IMPLEMENTATION.md`
- Testing strategy in `docs/TESTING_QUICK_REFERENCE.md`

## Patterns
- Follow existing service layer patterns
- Use TDD approach with comprehensive test coverage
- Maintain backward compatibility
- Follow project's error handling conventions