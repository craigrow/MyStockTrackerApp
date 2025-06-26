# Stock Portfolio Tracker - Implementation Context

## Project Overview
MyStockTrackerApp is a high-performance Flask web application for tracking stock portfolio performance against market indices (S&P 500/VOO and NASDAQ/QQQ). The application has achieved significant performance optimizations (90% faster loading) and comprehensive feature implementation.

## Current Status
- **Branch**: devR (currently active)
- **Production Status**: Live on Heroku with 132 passing tests (100% pass rate)
- **Recent Completion**: Phase 5 Advanced Analytics completed June 24, 2025
- **Performance**: Dashboard loads in 2-3 seconds vs previous 30+ seconds

## Technology Stack
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5, Chart.js
- **APIs**: Yahoo Finance (yfinance)
- **Testing**: pytest (132 comprehensive tests)
- **Deployment**: Heroku with automatic deployments

## Repository Structure & Deployment Strategy
- **Main Branch**: Production-ready code → **PROD Heroku deployment** (CRITICAL: Real users depend on this)
- **devQ Branch**: Development branch for Q agent → devQ Heroku deployment
- **devR Branch**: Development branch for R agent (current) → devR Heroku deployment
- **Deployment Safety**: PROD must remain stable and available at all times

## Key Features Implemented
### ✅ Core Functionality
- Multi-portfolio management
- Transaction and dividend tracking
- Real-time price data integration
- Performance calculations vs market indices
- Interactive visualizations

### ✅ Performance Optimization
- Smart caching strategy with market awareness
- 90% dashboard loading speed improvement
- On-demand refresh capability
- Real-time activity logging

### ✅ Data Integrity
- CSV duplicate detection and prevention
- Enhanced data validation
- Import safety mechanisms
- Comprehensive error handling

### ✅ Advanced Analytics (Phase 5)
- ETF performance comparison functionality
- Time-period matched calculations from purchase dates
- Comprehensive transactions page with sorting/filtering
- vs QQQ and vs VOO performance columns

## Outstanding Feature Gaps (from FEATURE_GAPS.md)
1. Dividends in Recent Activity box
2. Total Dividends Received indicator
3. Error handling for missing stock price data
4. Transaction edit/delete backend functionality (UI placeholders exist)
5. Large CSV import optimization (async processing)
6. Portfolio persistence across views
7. Stock splits integration
8. Custom ETF settings per portfolio
9. Cash flow log with manual inflow/outflow tracking
10. Improved app load experience with cached data display

## Development Guidelines (CRITICAL)
- **Testing**: 100% test pass rate required before promotion
- **Deployment Flow**: devR/devQ → main → PROD Heroku
- **Quality Gates**: 
  1. 100% tests pass in dev branch
  2. Pull from main, 100% tests pass again
  3. Promote to main, 100% tests pass in main
  4. Deploy to PROD Heroku
- **Production Safety**: PROD must NEVER break - real users depend on it
- **Rollback Policy**: If main tests fail, immediate rollback required

## Implementation Paths
- **Models**: `/app/models/` - SQLAlchemy models
- **Services**: `/app/services/` - Business logic
- **Views**: `/app/views/` - Flask routes and controllers
- **Templates**: `/app/templates/` - Jinja2 HTML templates
- **Tests**: `/tests/` - pytest test suite
- **Utilities**: `/app/util/` - Helper functions

## API Endpoints Available
- `/api/refresh-holdings/{portfolio_id}` - Refresh holdings data
- `/api/refresh-all-prices/{portfolio_id}` - Refresh all prices including ETFs
- `/api/price-update-progress` - Background update status
- `/api/current-price/{ticker}` - Get current price for any ticker
- `/api/etf-performance/{ticker}/{purchase_date}` - Calculate ETF performance

## Dependencies and Patterns
- **Database**: SQLAlchemy ORM with relationship management
- **Caching**: Intelligent price data caching with market awareness
- **API Integration**: Yahoo Finance with rate limiting protection
- **Error Handling**: Comprehensive exception management
- **Testing**: Comprehensive test coverage across all layers

## Current Modified Files
- `app/views/main.py` - Modified (needs review)
- `docs/AI_Instructions.md` - New file
- `docs/TESTING_STRATEGY_IMPROVEMENTS.md` - New file
- `q-analysis.md` - New file

## Next Development Focus
Based on the feature gaps and current state, the most impactful next implementations would be:
1. Transaction edit/delete functionality (backend for existing UI)
2. Improved app loading experience with cached data
3. Portfolio persistence across views
4. Large CSV import optimization