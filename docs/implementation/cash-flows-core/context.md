# Cash Flows Core Implementation - Context

## Project Overview

MyStockTrackerApp is a high-performance web application for tracking stock portfolio performance against market indices. Built with Python Flask, SQLAlchemy, PostgreSQL/SQLite, Bootstrap 5, and Chart.js.

## Task Description

Implement Core Cash Flow System with IRR calculations - Phase 1 of cash flows feature (no ETF comparisons).

## Existing Documentation

### Key Project Files
- **README.md**: Project overview, technology stack, testing approach (233 tests)
- **DEPLOYMENT_GUIDE.md**: Automated deployment with GitHub Actions
- **Cash Flows Feature Docs**: Complete specification in `/docs/cash_flows_feature/`
  - REQUIREMENTS_SPEC-2025-07-08.md
  - CASHFLOW_REQUIREMENTS-2025-07-08.md  
  - CASHFLOW_HLD-2025-07-08.md
  - CASHFLOW_DATA_MODEL-2025-07-08.md
  - DATABASE_MIGRATION-2025-07-08.md

### Technology Stack
- **Backend**: Python 3.12 + Flask + SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5 + Chart.js + Vanilla JavaScript
- **APIs**: Yahoo Finance (yfinance) for stock data
- **Testing**: pytest with 233 comprehensive tests
- **Deployment**: Heroku with GitHub Actions CI/CD

### Project Structure
```
MyStockTrackerApp_R/
├── app/
│   ├── models/          # Database models
│   ├── services/        # Business logic services  
│   ├── views/           # Route handlers
│   ├── templates/       # Jinja2 HTML templates
│   └── util/            # Utility functions
├── tests/               # Test suite (233 tests)
├── docs/                # Documentation
└── scripts/             # Deployment scripts
```

## Requirements Summary

### Core Functionality
1. **Cash Flow Tracking**: Track all portfolio cash movements (deposits, purchases, sales, dividends)
2. **Inferred Deposits**: Automatically infer cash deposits when purchases would create negative balances
3. **IRR Calculation**: Calculate Internal Rate of Return using Newton-Raphson method
4. **Cash Flows Tab**: New UI tab to display cash flows table and summary metrics
5. **Data Migration**: Populate cash flows from existing transactions/dividends

### Key Constraints
- **No ETF Comparisons**: Phase 1 focuses on portfolio cash flows only
- **No Breaking Changes**: Isolated implementation, existing functionality unchanged
- **100% Test Coverage**: All 233 existing tests must continue passing
- **Real Users**: Production stability is critical

### Cash Flow Logic
- Start with $0 cash balance
- Process transactions chronologically
- Infer deposits (rounded to penny) when purchases would create negative balance
- One deposit per day for multiple same-day purchases
- Never show negative cash balance

## Implementation Paths

### Database Models
- **CashFlow**: New model for tracking cash movements
- **IRRCalculation**: New model for storing IRR calculations
- **Portfolio**: Add latest_irr and total_invested fields

### Services
- **CashFlowService**: Core business logic for cash flow tracking
- **IRRCalculationService**: IRR calculation using scipy
- **Migration Service**: Populate cash flows from existing data

### UI Components
- **Cash Flows Tab**: New tab in existing navigation
- **Cash Flow Table**: Chronological display of all cash movements
- **Summary Cards**: Total Invested, Current Value, IRR

### Integration Points
- Existing Portfolio and Transaction models
- Existing PortfolioService for data access
- Existing UI patterns and Bootstrap styling
- Existing test framework and patterns

## Dependencies

### External Libraries
- **scipy**: For IRR calculation (Newton-Raphson method)
- **yfinance**: Already used for stock data (confirmed ETF dividend support)

### Internal Dependencies
- Portfolio, StockTransaction, Dividend models
- PortfolioService for data access
- Existing database migration framework
- Bootstrap 5 UI components

## Existing Architecture Analysis

### Database Models
- **Portfolio**: Core model with UUID primary key, relationships to transactions/dividends
- **StockTransaction**: BUY/SELL transactions with fractional share support
- **Dividend**: Dividend payments linked to portfolios
- **CashBalance**: Current cash balance per portfolio (will be replaced by cash flows)
- **PriceHistory**: Cached historical prices with composite key (ticker, date)
- **PortfolioCache**: JSON-based caching system for performance optimization

### Service Architecture
- **PortfolioService**: Core business logic for portfolio operations
- **PriceService**: Price fetching and caching (yfinance integration)
- **BackgroundTasks**: Asynchronous processing for price updates
- Services follow dependency injection pattern with app context

### UI Architecture
- **Bootstrap 5**: Responsive design with navbar navigation
- **Chart.js**: Interactive performance charts
- **Flask Templates**: Jinja2 with base template inheritance
- **Navigation**: Dashboard, Transactions, Dividends tabs (will add Cash Flows)

### Testing Architecture
- **pytest**: 233 tests with comprehensive fixtures
- **Markers**: @pytest.mark.fast, @pytest.mark.database, @pytest.mark.slow
- **Fixtures**: sample_portfolio, sample_transaction, sample_dividend
- **Test Structure**: unit/, integration/, ui/ directories
- **Database**: SQLite for testing with temporary files

### Key Patterns
- **UUID Primary Keys**: All models use string UUIDs
- **Decimal Precision**: Financial calculations use float (will need to consider precision)
- **Relationship Patterns**: Foreign keys with backref relationships
- **Error Handling**: Try/catch with graceful degradation
- **Caching Strategy**: Market-aware caching with freshness indicators

## Development Notes

- **DEVELOPMENT.md**: Not found - using project conventions from README.md
- **Testing Framework**: pytest with 233 existing tests
- **Build Commands**: `python -m pytest tests/` for testing
- **Database**: Flask-SQLAlchemy with migrations
- **Branch**: Working on devR, deploying to mystocktrackerapp-devr environment