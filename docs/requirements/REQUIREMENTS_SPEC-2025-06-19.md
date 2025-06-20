# MyStockTrackerApp - Requirements Specification

## 1. Project Overview
MyStockTrackerApp is a web application designed to help investors track the performance of their stock purchases against major market indices. Users will be able to manually enter stock purchases, sales, and dividends, organize them into multiple portfolios, and visualize how their investments compare to major market ETFs (VOO for S&P 500, QQQ for NASDAQ).

The application will provide various visualizations and metrics to help users understand:
- How individual stocks perform against the indices
- How entire portfolios perform against the indices
- Distribution of winners and losers in their portfolios
- Portfolio allocation and performance contributions

## 2. User Requirements

### 2.1 User Types
- Initially a single-user application (with future expansion to multi-user)
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
- Bulk import of transactions via CSV file:
  - Support for importing historical purchases, sales, and dividends
  - Standard CSV format with required column headers
  - Data validation before import completion
- Real-time price data retrieval during market hours
- Historical price data storage for performance tracking
- Robust caching of historical price data to minimize API calls

### 3.2 Portfolio Performance Tracking
- Track performance of individual stock transactions (not just aggregate positions)
- Compare individual stocks against selected ETFs (VOO, QQQ)
- Calculate overall portfolio performance
- Compare portfolio performance against the same dollar values invested in ETFs on the same dates
- Track portfolio value over time
- Calculate various performance metrics:
  - Total gain/loss ($ and %)
  - Performance relative to indices
  - Time-based performance metrics (age-based analysis)
- Display portfolio performance for different time periods:
  - vs. the market today
  - vs. the market this week
  - vs. the market this month
  - vs. the market YTD
  - vs. the market past year
  - vs. the market past five years
  - vs. the market all time

### 3.3 Data Visualization Requirements
The application must provide the following visualizations:

1. **Portfolio Performance Chart**
   - Line/area chart showing portfolio performance vs. ETFs (VOO and QQQ)
   - X-axis shows time periods
   - Y-axis shows relative performance
   - Prioritized to load first on the dashboard
   
2. **Investment & Gains Stacked Bar Chart**
   - Three stacked bars representing:
     - User's portfolio
     - VOO (S&P 500 ETF)
     - QQQ (NASDAQ ETF)
   - Each bar shows:
     - Base component: Total money invested
     - Additional component: Gain in value
   - Include dividends in gains component for both portfolio and ETFs

3. **Age-Based Performance Pie Charts**
   - Multiple pie charts categorizing investments by age:
     - Picks less than 1 year old
     - Picks 1-3 years old
     - Picks 4-5 years old
     - Picks older than 5 years
   - Each pie shows proportion of picks beating vs. trailing the index

4. **Performance Distribution Bar Chart**
   - Bar chart showing number of stock picks in different performance categories:
     - Picks trailing the index
     - Picks beating index by less than 100%
     - Picks beating index by 200%
     - Picks beating index by 300%
     - Additional performance brackets as needed for larger gains

5. **Detailed Portfolio Table**
   - Comprehensive table showing all picks with:
     - All user-supplied data:
       - Stock ticker/symbol
       - Purchase date
       - Number of shares purchased
       - Price per share
     - Calculated data:
       - Current value
       - Cost basis
       - Percentage gain/loss
       - ETF gain/loss (for comparison)
       - Performance difference (stock vs ETF)
   - Features:
     - Color coding (green for winners, red for losers)
     - Sortable by any column
     - Filtering capabilities

6. **Investment Distribution Heatmap**
   - Rectangular layout heatmap
   - Each block represents a stock with ticker symbol displayed
   - Block size proportional to amount invested relative to total portfolio
   
7. **Gain Distribution Heatmap**
   - Rectangular layout heatmap
   - Only stocks with positive gains included
   - Each block represents a stock with ticker symbol displayed
   - Block size proportional to each stock's gain (including dividends) as a portion of total portfolio gain

### 3.4 Index Comparison
- Compare stock performance against VOO (for S&P 500) and QQQ (for NASDAQ)
- Track hypothetical growth of equivalent investments in these ETFs
- Calculate performance differences between stocks/portfolio and indices

### 3.5 Logging and Monitoring
- Detailed application logging for debugging purposes
- Log display window visible in the UI showing application activities
- Log API calls, cache usage, and data refresh operations
- User-configurable log level (info, warning, error)

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- Keep Heroku hosting costs as low as possible, prioritizing cost efficiency over performance
- Real-time stock data retrieval during market hours
- Page load times under 2 seconds
- Chart rendering time under 1 second
- Mobile-optimized responsive design
- Prioritize portfolio performance visualization and calculation display for current/most recent day

### 4.2 Usability Requirements
- Mobile-first design (primary use case) with desktop compatibility (secondary use case)
- Intuitive navigation between portfolios
- Clear visualization of performance metrics
- Touch-friendly UI elements for mobile interaction
- Consistent color-coding (green for gains, red for losses)

### 4.3 Security Requirements
- Basic user authentication (for future multi-user expansion)
- Secure storage of user portfolio data

### 4.4 Availability Requirements
- Application available during market hours
- Acceptable downtime during non-market hours for maintenance

## 5. Technical Requirements

### 5.1 Technology Stack
- **Backend**: Python (preferred by user)
- **Visualization Libraries**: Consider Pandas for data processing and visualization
- **Stock Data API**: Yahoo Finance API (free tier)
- **Deployment**: Heroku free tier
- **Source Control**: Personal GitHub repository
- **Development Environment**: Visual Studio Code with Claude Code
- **Database**: Simple implementation suitable for single-user (with future expansion considerations)

### 5.2 External Interfaces
- Yahoo Finance API for stock price data
- ETF price data for VOO and QQQ

### 5.3 Data Requirements
- Storage of user stock purchases
- Storage of stock price history (closing prices only, no high/low/volume data needed)
- Storage of dividends
- Storage of ETF price history
- Multiple portfolio data structures
- Immediate CSV data persistence upon transaction or dividend entry

### 5.4 API Usage Optimization
- Implement robust caching mechanisms for historical price data
- Store timestamp with cached data to determine freshness
- Minimize API calls to prevent hitting rate limits
- Batch API requests when possible to reduce call frequency
- Implement retry mechanisms with exponential backoff for failed API calls

## 6. Constraints and Limitations
- Free tier of Heroku (with app sleeping after 30 minutes of inactivity)
- Free API usage limitations from Yahoo Finance
- Initial implementation for single-user only

## 7. Future Considerations
- Multi-user authentication and authorization
- Additional indices/ETFs for comparison
- Automated imports from brokerage accounts
- Dividend reinvestment modeling

## 8. Implementation Roadmap
### Phase 1: Core Functionality
- Enable the user to enter purchase data and see the portfolio performance chart
- Stock purchase/sale entry
- Dividend entry
- Price data retrieval with caching
- Portfolio vs ETF performance chart
- Basic performance calculations

### Phase 2: Visualization Implementation
- Investment & gains stacked bar chart
- Performance distribution bar chart
- Detailed portfolio table

### Phase 3: Advanced Features
- Age-based performance pie charts
- Investment and gain distribution heatmaps
- Filtering and sorting capabilities
- Enhanced performance metrics

### Phase 4: Future Expansion
- Multi-user support
- Additional indices
- Mobile support enhancements