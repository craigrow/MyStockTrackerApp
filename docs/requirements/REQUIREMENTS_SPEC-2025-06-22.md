# MyStockTrackerApp - Requirements Specification (Updated)
*Updated: June 22, 2025*

## 1. Project Overview
MyStockTrackerApp is a web application designed to help investors track the performance of their stock purchases against major market indices. Users can manually enter stock purchases, sales, and dividends, organize them into multiple portfolios, and visualize how their investments compare to major market ETFs (VOO for S&P 500, QQQ for NASDAQ).

The application provides various visualizations and metrics to help users understand:
- How individual stocks perform against the indices
- How entire portfolios perform against the indices
- Daily performance comparison vs. market benchmarks
- Portfolio allocation and performance contributions

## 2. User Requirements

### 2.1 User Types
- Single-user application (future expansion to multi-user planned)
- Each user can manage multiple portfolios

### 2.2 Portfolio Management
- Create multiple portfolios within a single user account
- Toggle between different portfolios to view portfolio-specific metrics
- Enter stock purchases manually (ticker symbol, date, price per share, number of shares including fractional shares)
- Enter stock sales manually (same data points as purchases)
- Enter dividends manually (ticker symbol, date, total dividend amount)
- View performance metrics specific to each portfolio
- Cash from stock sales and dividends remains in the portfolio
- When new purchases are made, existing cash is used first before additional funds

## 3. Functional Requirements

### 3.1 Stock Data Management
- Manual entry of stock purchases with the following data:
  - Stock ticker symbol
  - Purchase date
  - Price per share
  - Number of shares purchased
- Manual entry of stock sales with the following data:
  - Stock ticker symbol
  - Sale date
  - Price per share
  - Number of shares sold
- Manual entry of dividends with the following data:
  - Stock ticker symbol
  - Payment date
  - Total dividend amount
- **✅ IMPLEMENTED**: Bulk import of transactions via CSV file:
  - Support for importing historical purchases, sales, and dividends
  - User-friendly CSV format with column headers: Ticker, Type, Date, Price, Shares, Amount
  - Comprehensive data validation with detailed error messages
  - BOM handling for Excel-generated CSV files
  - Intelligent data cleaning (dollar signs, date format conversion)
  - Toggle interface for transaction vs dividend imports
- Real-time price data retrieval during market hours
- Historical price data storage for performance tracking
- **✅ IMPLEMENTED**: Robust caching of historical price data to minimize API calls

### 3.2 Portfolio Performance Tracking
- Track performance of individual stock transactions (not just aggregate positions)
- Compare individual stocks against selected ETFs (VOO, QQQ)
- Calculate overall portfolio performance
- Compare portfolio performance against the same dollar values invested in ETFs on the same dates
- Track portfolio value over time
- Calculate various performance metrics:
  - Total gain/loss ($ and %)
  - Performance relative to indices
  - **✅ IMPLEMENTED**: Daily performance tracking ("Today vs. the Market")
- **✅ IMPLEMENTED**: Display portfolio performance for different time periods:
  - vs. the market today (with automatic holiday handling)
  - Portfolio daily dollar and percentage changes
  - ETF daily performance comparison with portfolio equivalent values

### 3.3 Data Visualization Requirements
The application provides the following visualizations:

1. **✅ IMPLEMENTED**: **Portfolio Performance Chart**
   - Line chart showing portfolio performance vs. ETFs (VOO and QQQ)
   - Interactive time-based visualization
   - Prioritized to load first on the dashboard
   
2. **✅ IMPLEMENTED**: **Dashboard Summary Cards**
   - Portfolio Value: Current total value with ETF equivalent comparisons
   - Total Gain/Loss: Dollar amount and percentage with ETF comparisons
   - **Today vs. the Market**: Daily performance comparison showing:
     - Portfolio daily change ($ and %)
     - VOO daily change ($ and %)
     - QQQ daily change ($ and %)
     - Intelligent trading day detection (handles holidays like Juneteenth)

3. **✅ IMPLEMENTED**: **Detailed Portfolio Table**
   - Comprehensive table showing all holdings with:
     - Stock ticker/symbol
     - Current shares and price
     - Market value and cost basis
     - Gain/loss ($ and %)
   - Color coding (green for winners, red for losers)
   - Real-time price updates

4. **✅ IMPLEMENTED**: **Recent Activity Feed**
   - Display of recent transactions
   - Quick access to transaction history

### 3.4 Index Comparison
- **✅ IMPLEMENTED**: Compare stock performance against VOO (for S&P 500) and QQQ (for NASDAQ)
- **✅ IMPLEMENTED**: Track hypothetical growth of equivalent investments in these ETFs
- **✅ IMPLEMENTED**: Calculate performance differences between stocks/portfolio and indices
- **✅ IMPLEMENTED**: Daily performance comparison with portfolio-equivalent ETF values

### 3.5 Logging and Monitoring
- **✅ IMPLEMENTED**: Detailed application logging for debugging purposes
- **✅ IMPLEMENTED**: Log display window visible in the UI showing application activities
- **✅ IMPLEMENTED**: Log API calls, cache usage, and data refresh operations
- **✅ IMPLEMENTED**: Intelligent caching system with market hours detection

### 3.6 CSV Import/Export System
- **✅ IMPLEMENTED**: Comprehensive CSV upload system with:
  - Clean toggle interface for transaction vs dividend imports
  - User-friendly column names (Ticker, Type, Date, Price, Shares, Amount)
  - BOM handling for Excel compatibility
  - Intelligent data cleaning and validation
  - Detailed error reporting with specific failure reasons
  - Support for various date formats and currency symbols
  - Graceful handling of extra columns and missing data

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **✅ IMPLEMENTED**: Intelligent caching system to minimize API calls and improve performance
- **✅ IMPLEMENTED**: Market hours detection for optimal cache usage
- **✅ IMPLEMENTED**: Batch price data fetching for efficiency
- Page load times optimized through caching
- Mobile-optimized responsive design
- **✅ IMPLEMENTED**: Prioritized portfolio performance visualization for current/most recent day

### 4.2 Usability Requirements
- **✅ IMPLEMENTED**: Mobile-first design with desktop compatibility
- **✅ IMPLEMENTED**: Intuitive navigation between portfolios
- **✅ IMPLEMENTED**: Clear visualization of performance metrics
- **✅ IMPLEMENTED**: Consistent color-coding (green for gains, red for losses)
- **✅ IMPLEMENTED**: User-friendly error handling with descriptive messages

### 4.3 Security Requirements
- Basic user authentication (for future multi-user expansion)
- Secure storage of user portfolio data

### 4.4 Availability Requirements
- **✅ IMPLEMENTED**: Application available with intelligent caching during market closures
- **✅ IMPLEMENTED**: Graceful handling of API rate limits and failures

## 5. Technical Requirements

### 5.1 Technology Stack
- **✅ IMPLEMENTED**: **Backend**: Python with Flask framework
- **✅ IMPLEMENTED**: **Database**: SQLAlchemy with SQLite
- **✅ IMPLEMENTED**: **Visualization**: Chart.js for interactive charts
- **✅ IMPLEMENTED**: **Stock Data API**: Yahoo Finance API (yfinance library)
- **✅ IMPLEMENTED**: **Frontend**: Bootstrap for responsive design
- **Deployment**: Heroku (planned)
- **✅ IMPLEMENTED**: **Source Control**: GitHub repository
- **✅ IMPLEMENTED**: **Testing**: Comprehensive pytest test suite (100% pass rate)

### 5.2 External Interfaces
- **✅ IMPLEMENTED**: Yahoo Finance API for stock price data
- **✅ IMPLEMENTED**: ETF price data for VOO and QQQ with intelligent caching

### 5.3 Data Requirements
- **✅ IMPLEMENTED**: Storage of user stock purchases, sales, and dividends
- **✅ IMPLEMENTED**: Storage of stock price history with timestamps
- **✅ IMPLEMENTED**: Multiple portfolio data structures
- **✅ IMPLEMENTED**: Intelligent price caching with market date awareness
- **✅ IMPLEMENTED**: CSV data import with comprehensive validation

### 5.4 API Usage Optimization
- **✅ IMPLEMENTED**: Robust caching mechanisms for historical price data
- **✅ IMPLEMENTED**: Timestamp-based cache freshness determination
- **✅ IMPLEMENTED**: Batch API requests to reduce call frequency
- **✅ IMPLEMENTED**: Market hours detection for optimal caching
- **✅ IMPLEMENTED**: Graceful handling of API failures and rate limits

## 6. Constraints and Limitations
- Free API usage limitations from Yahoo Finance
- Initial implementation for single-user only
- Heroku deployment considerations (planned)

## 7. Future Considerations
- Multi-user authentication and authorization
- Additional indices/ETFs for comparison
- Automated imports from brokerage accounts
- Dividend reinvestment modeling
- Advanced visualization features (heatmaps, age-based analysis)

## 8. Implementation Status

### ✅ Phase 1: Core Functionality (COMPLETED)
- ✅ Stock purchase/sale entry with comprehensive forms
- ✅ Dividend entry with validation
- ✅ Price data retrieval with intelligent caching
- ✅ Portfolio vs ETF performance chart
- ✅ Advanced performance calculations
- ✅ Daily performance tracking ("Today vs. the Market")
- ✅ Comprehensive CSV import system
- ✅ 100% test coverage with robust test suite

### 🔄 Phase 2: Advanced Visualizations (PARTIALLY IMPLEMENTED)
- ✅ Dashboard summary cards with ETF comparisons
- ✅ Detailed portfolio holdings table
- ✅ Recent activity feed
- 🔄 Investment & gains stacked bar chart (planned)
- 🔄 Performance distribution analysis (planned)

### 📋 Phase 3: Enhanced Features (PLANNED)
- Age-based performance analysis
- Investment and gain distribution heatmaps
- Advanced filtering and sorting capabilities
- Enhanced performance metrics

### 📋 Phase 4: Future Expansion (PLANNED)
- Multi-user support
- Additional indices
- Mobile app considerations
- Advanced analytics features

## 9. Quality Assurance

### ✅ Testing Implementation
- **✅ IMPLEMENTED**: Comprehensive test suite with 100% pass rate
- **✅ IMPLEMENTED**: Model tests (24/24 passing)
- **✅ IMPLEMENTED**: Service tests (27/27 passing)
- **✅ IMPLEMENTED**: Integration tests (11/11 passing)
- **✅ IMPLEMENTED**: CSV upload tests (17/17 passing)
- **✅ IMPLEMENTED**: Daily performance tests (6/6 passing)
- **✅ IMPLEMENTED**: Total: 85+ tests with comprehensive coverage

### ✅ Error Handling
- **✅ IMPLEMENTED**: Comprehensive input validation
- **✅ IMPLEMENTED**: Graceful API failure handling
- **✅ IMPLEMENTED**: User-friendly error messages
- **✅ IMPLEMENTED**: Detailed logging for debugging
- **✅ IMPLEMENTED**: CSV import error reporting with specific failure reasons

## 10. Recent Major Enhancements

### Daily Performance Tracking System
- **Market Intelligence**: Automatic detection of trading days vs holidays
- **Portfolio Comparison**: Real-time comparison with ETF equivalents
- **Smart Caching**: Optimized performance with market-aware caching
- **User Experience**: Clean, informative display of daily performance metrics

### CSV Import System
- **User-Friendly Design**: Intuitive toggle interface for different import types
- **Robust Validation**: Comprehensive error checking with detailed feedback
- **Excel Compatibility**: BOM handling and intelligent data cleaning
- **Production Ready**: Extensive test coverage for all edge cases

This updated specification reflects the current state of the application with significant enhancements in daily performance tracking, CSV import functionality, and overall system robustness.