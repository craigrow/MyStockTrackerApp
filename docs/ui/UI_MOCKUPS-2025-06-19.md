# MyStockTrackerApp - Mobile UI Wireframes

## Overview

These wireframes present a mobile-first design for the MyStockTrackerApp, with particular focus on the core functionality identified in Phase 1. The designs prioritize the portfolio performance chart while ensuring intuitive navigation and data entry. All screens are optimized for mobile devices first, with responsive design considerations for desktop viewing.

## Key Design Principles

1. **Mobile-First Approach**: All screens are designed for mobile devices as the primary use case
2. **Performance Optimization**: Minimal JavaScript and efficient rendering for Heroku free tier
3. **Progressive Loading**: Critical content (portfolio performance) loads first
4. **Touch-Friendly Interface**: Larger touch targets for mobile interaction
5. **Accessibility**: Clear visual hierarchy and readable text

## Screen 1: Dashboard / Portfolio Performance (Home Screen)

```
┌─────────────────────────────┐
│ MyStockTracker       ☰   👤 │
├─────────────────────────────┤
│ Current Portfolio: Main     ▼│
├─────────────────────────────┤
│ Portfolio Performance       │
│                             │
│ [Line Chart: Portfolio vs   │
│  VOO and QQQ over time]     │
│                             │
│                             │
│                             │
├─────────────────────────────┤
│ Today's Performance:        │
│ Portfolio: +1.2%            │
│ vs S&P 500: +0.3% (beating) │
│ vs NASDAQ: -0.1% (beating)  │
├─────────────────────────────┤
│ [Key Stats/Summary Cards]   │
│ Total Value: $10,245        │
│ Total Gain: $1,245 (13.8%)  │
│ vs Market: +3.2%            │
├─────────────────────────────┤
│ [Recent Transactions]       │
│ AAPL - Buy - 06/10/25       │
│ TSLA - Dividend - 06/05/25  │
├─────────────────────────────┤
│ [Navigation Bar]            │
│ 📊 Home  📋 Stocks  ➕ Add   │
└─────────────────────────────┘
```

### Features:
- **Portfolio Selector**: Dropdown to switch between different portfolios
- **Performance Chart**: Focal point showing portfolio vs ETF performance
- **Quick Stats**: Today's performance and comparison to indices
- **Summary Cards**: Total value, gains, and market comparison
- **Recent Activity**: Latest transactions for quick reference
- **Navigation Bar**: Access to main app sections

## Screen 2: Add Transaction Screen

```
┌─────────────────────────────┐
│ Add Transaction      ✕      │
├─────────────────────────────┤
│ Transaction Type:           │
│ ○ Purchase  ○ Sale          │
│ ○ Dividend                  │
├─────────────────────────────┤
│ Stock Symbol:               │
│ ┌───────────────────────┐   │
│ │ AAPL                  │   │
│ └───────────────────────┘   │
│                             │
│ Date:                       │
│ ┌───────────────────────┐   │
│ │ 06/15/2025           │   │
│ └───────────────────────┘   │
│                             │
│ FOR PURCHASE/SALE:          │
│ Price Per Share:            │
│ ┌───────────────────────┐   │
│ │ $185.25              │   │
│ └───────────────────────┘   │
│                             │
│ Number of Shares:           │
│ ┌───────────────────────┐   │
│ │ 10.253                │   │
│ └───────────────────────┘   │
│                             │
│ FOR DIVIDEND:               │
│ Total Dividend Amount:      │
│ ┌───────────────────────┐   │
│ │ $25.50               │   │
│ └───────────────────────┘   │
├─────────────────────────────┤
│ Total Value: $1,852.50      │
├─────────────────────────────┤
│        [Save Transaction]   │
└─────────────────────────────┘
```

### Features:
- **Transaction Type Selection**: Radio buttons for Purchase, Sale, or Dividend
- **Dynamic Form Fields**: Fields change based on transaction type
- **Symbol Input**: Stock ticker symbol entry (could include autocomplete)
- **Date Picker**: Intuitive date selection
- **Automatic Calculation**: Total value calculated from inputs
- **Clear Action Button**: Prominent save button

## Screen 3: Stock List / Portfolio Details

```
┌─────────────────────────────┐
│ Portfolio: Main      ☰   🔍 │
├─────────────────────────────┤
│ Filter: All Stocks     ▼    │
├─────────────────────────────┤
│ Sort By: Performance    ▼   │
├─────────────────────────────┤
│ [Stock List Table]          │
│                             │
│ AAPL                        │
│ $185.25 | +15.5% | +5.2%*   │
│ 10 shares | $1,852          │
├─────────────────────────────┤
│ MSFT                        │
│ $335.75 | +22.3% | +12.0%*  │
│ 5 shares | $1,678           │
├─────────────────────────────┤
│ TSLA                        │
│ $215.50 | -5.2% | -15.5%*   │
│ 8 shares | $1,724           │
├─────────────────────────────┤
│ AMZN                        │
│ $145.30 | +8.7% | -1.6%*    │
│ 12 shares | $1,743          │
├─────────────────────────────┤
│ * Performance vs S&P 500    │
├─────────────────────────────┤
│ [Navigation Bar]            │
│ 📊 Home  📋 Stocks  ➕ Add   │
└─────────────────────────────┘
```

### Features:
- **Filtering Options**: Filter stocks by various criteria
- **Sorting Options**: Sort by performance, value, alphabetical, etc.
- **Stock Entry Format**: 
  - Stock symbol prominently displayed
  - Current price and percentage gain/loss (color-coded)
  - Performance vs index (marked with asterisk)
  - Holdings information (shares and value)
- **Visual Indicators**: Green for winners, red for losers

## Screen 4: Stock Detail View

```
┌─────────────────────────────┐
│ Stock: AAPL         ◀    ⋮  │
├─────────────────────────────┤
│ Apple Inc.                  │
│ $185.25 (+1.25 today)       │
├─────────────────────────────┤
│ [Transaction History]       │
│                             │
│ PURCHASE - 06/10/2025       │
│ 5 shares @ $180.50          │
│ Value: $902.50              │
│ Performance: +2.6%          │
│ vs S&P 500: +1.8%           │
├─────────────────────────────┤
│ PURCHASE - 05/15/2025       │
│ 5 shares @ $175.25          │
│ Value: $876.25              │
│ Performance: +5.7%          │
│ vs S&P 500: +2.5%           │
├─────────────────────────────┤
│ DIVIDEND - 05/02/2025       │
│ Amount: $12.25              │
├─────────────────────────────┤
│ Total Position:             │
│ 10 shares                   │
│ Cost Basis: $1,778.75       │
│ Current Value: $1,852.50    │
│ Total Gain: +4.1%           │
│ vs S&P 500: +2.1%           │
├─────────────────────────────┤
│ [Add Transaction] [Sell]    │
└─────────────────────────────┘
```

### Features:
- **Stock Overview**: Symbol, company name, current price
- **Transaction History**: List of all transactions for this stock
- **Performance Metrics**: For each transaction and overall position
- **Comparison to Index**: How each purchase performs vs the benchmark
- **Quick Actions**: Add transaction or sell buttons

## Screen 5: Navigation Drawer

```
┌─────────────────────────────┐
│ ✕     MyStockTracker        │
├─────────────────────────────┤
│ 👤 User Profile             │
├─────────────────────────────┤
│ 📊 Dashboard                │
├─────────────────────────────┤
│ 📂 Portfolios               │
│  ├─ Main Portfolio          │
│  ├─ Retirement              │
│  ├─ Speculative             │
│  └─ [+ Add Portfolio]       │
├─────────────────────────────┤
│ 📈 Performance Charts       │
├─────────────────────────────┤
│ 📊 Investment Heatmaps      │
├─────────────────────────────┤
│ 🔄 Compare with ETFs        │
├─────────────────────────────┤
│ 📥 Import CSV               │
├─────────────────────────────┤
│ 💾 Export Data              │
├─────────────────────────────┤
│ ⚙️ Settings                 │
├─────────────────────────────┤
│ 📋 Activity Log             │
├─────────────────────────────┤
│ ℹ️ About                    │
└─────────────────────────────┘
```

### Features:
- **Portfolio Access**: Quick access to different portfolios
- **Navigation Links**: Direct access to all major app sections
- **Add Portfolio**: Option to create new portfolios
- **Utility Functions**: Export, settings, logs

## Screen 6: Performance Details / Advanced Visualizations

```
┌─────────────────────────────┐
│ Performance Charts   ◀      │
├─────────────────────────────┤
│ Portfolio: Main     ▼       │
├─────────────────────────────┤
│ [Tab Navigation]            │
│ Chart | Table | Heatmap     │
├─────────────────────────────┤
│ [Investment & Gains Chart]  │
│ [Stacked bar chart showing  │
│  investment and gains]      │
│                             │
│                             │
│                             │
├─────────────────────────────┤
│ Time Period:                │
│ 1D | 1W | 1M | 3M | 1Y | All│
├─────────────────────────────┤
│ Comparison:                 │
│ ☑ VOO (S&P 500)            │
│ ☑ QQQ (NASDAQ)             │
├─────────────────────────────┤
│ Performance Metrics:        │
│ Portfolio: +$1,245 (+13.8%) │
│ S&P 500: +10.6%             │
│ NASDAQ: +9.2%               │
│                             │
│ Outperformance: +3.2%       │
└─────────────────────────────┘
```

### Features:
- **Tab Navigation**: Switch between different visualization types
- **Time Period Selection**: Adjust the time range for analysis
- **ETF Selection**: Toggle comparison benchmarks
- **Key Metrics**: Summary of performance statistics

## Screen 7: Logging/Debug Screen

```
┌─────────────────────────────┐
│ Activity Log         ◀      │
├─────────────────────────────┤
│ Log Level: Info       ▼     │
├─────────────────────────────┤
│ [15:45:23] INFO: Loading    │
│ portfolio data              │
├─────────────────────────────┤
│ [15:45:24] INFO: Fetching   │
│ current prices for AAPL,    │
│ MSFT, TSLA, AMZN            │
├─────────────────────────────┤
│ [15:45:25] INFO: Using      │
│ cached price data for VOO,  │
│ QQQ (last updated: 15 min)  │
├─────────────────────────────┤
│ [15:45:26] INFO: Calculating│
│ portfolio performance       │
├─────────────────────────────┤
│ [15:45:26] WARNING: API     │
│ rate limit at 80%           │
├─────────────────────────────┤
│ [15:45:27] INFO: Rendering  │
│ performance chart           │
├─────────────────────────────┤
│ [Refresh] [Clear] [Export]  │
└─────────────────────────────┘
```

### Features:
- **Log Level Filter**: Adjust verbosity of displayed logs
- **Timestamped Entries**: Chronological log of system activities
- **API Status**: Highlights important information like rate limits
- **Log Actions**: Refresh, clear, or export log data

## Screen 8: CSV Import

```
┌─────────────────────────────┐
│ Import Transactions   ◀     │
├─────────────────────────────┤
│ Portfolio: Main     ▼       │
├─────────────────────────────┤
│ Portfolio Status:           │
│ 12 existing transactions    │
├─────────────────────────────┤
│ Import your transaction     │
│ history from a CSV file     │
├─────────────────────────────┤
│ 📄 Select CSV File          │
│ ┌───────────────────────┐   │
│ │ No file selected      │   │
│ └───────────────────────┘   │
│                             │
│ 📋 Required Format:         │
│ - transaction_type          │
│   (buy,sell,dividend)       │
│ - ticker                    │
│ - date (YYYY-MM-DD)         │
│ - price_per_share           │
│   (for buy/sell)            │
│ - shares (for buy/sell)     │
│ - amount (for dividend)     │
├─────────────────────────────┤
│ [Download Template]         │
├─────────────────────────────┤
│ Duplicate Handling:         │
│ ○ Skip duplicates           │
│ ○ Override existing data    │
│ ○ Review duplicates         │
│                             │
│ Duplicate Detection:        │
│ ☑ Same ticker & date        │
│ ☑ Same shares/amount        │
│ ☐ Exact price match         │
├─────────────────────────────┤
│ Options:                    │
│ ☑ Validate before import    │
│ ☑ Show import summary       │
├─────────────────────────────┤
│ [       Import Data       ] │
├─────────────────────────────┤
│ * Duplicates are determined │
│   based on transaction type,│
│   ticker, date, and amount  │
└─────────────────────────────┘
```

### Features:
- **File Selection**: Simple interface to upload CSV file
- **Format Instructions**: Clear guidance on required CSV format
- **Template Download**: Option to download a CSV template
- **Import Options**: Configurable import settings- **Existing Transaction Warning**: Clear warning when importing to a portfolio with existing data
- **Import Mode Selection**: Options to append transactions or replace all existing transactions
- **Clear Instructions**: Help text to ensure successful import

## Responsive Design Considerations

These wireframes are designed for mobile-first implementation, but will adapt to larger screens with the following considerations:

1. **Tablet Layout**: 
   - Two-column layout for dashboard and detail screens
   - Side-by-side visualization options
   - Expanded table views with more columns visible

2. **Desktop Layout**:
   - Multi-column dashboard with all key visualizations visible
   - Persistent navigation sidebar instead of bottom navigation
   - Expanded tables with full information visible without scrolling

3. **Progressive Enhancement**:
   - Additional visualization details on larger screens
   - More interactive elements when not constrained by mobile

## Implementation Notes

1. **Priority Loading**:
   - Dashboard with portfolio performance chart should load first
   - Other visualizations can load progressively
   
2. **Interaction Design**:
   - All touch targets minimum 44x44px for mobile accessibility
   - Swipe gestures for navigating between related screens
   
3. **Performance Optimization**:
   - Lazy-load visualizations not visible in the viewport
   - Use efficient rendering techniques to minimize resource usage

4. **Logging Integration**:
   - Activity log visible to user for transparency
   - Highlights API call status and caching information