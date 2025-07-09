# Requirements Specification: Cash Flows Tracking Feature

## 1. Introduction

### 1.1 Purpose
This document outlines the requirements for the Cash Flows Tracking feature, a new addition to the MyStockTrackerApp. The purpose of this feature is to track all cash flows in and out of investment portfolios, support IRR (Internal Rate of Return) calculations for more accurate performance metrics, and provide transparency into the data used for these calculations.

### 1.2 Scope
The Cash Flows Tracking feature will be implemented as a new dedicated tab in the application without modifying any existing functionality. It will focus on accurately tracking, displaying, and utilizing cash flow data for performance calculations.

### 1.3 Definitions and Acronyms
- **IRR**: Internal Rate of Return - A metric used to estimate the profitability of investments that accounts for all cash flows.
- **Cash Flow**: Movement of money into or out of a portfolio, including deposits, withdrawals, dividends, and proceeds from sales.
- **VOO**: Vanguard S&P 500 ETF - A benchmark ETF tracking the S&P 500 index.
- **QQQ**: Invesco QQQ Trust - A benchmark ETF tracking the NASDAQ-100 index.

## 2. Feature Overview

### 2.1 Feature Description
The Cash Flows Tracking feature will add a new "Cash Flows" tab to the existing MyStockTrackerApp. This tab will display a chronological table of all cash flows affecting the portfolio, along with summary metrics including Total Amount Invested, Current Portfolio Value, and IRR. The feature will also support comparison of portfolio performance against benchmark ETFs (VOO and QQQ) using IRR calculations.

### 2.2 User Benefits
- More accurate performance measurement through IRR calculations
- Transparency into all cash flows used in performance calculations
- Better comparison with market benchmarks using consistent methodology
- Clear tracking of portfolio's cash position over time

### 2.3 Feature Context
This feature extends the existing portfolio tracking capabilities by adding dedicated cash flow tracking and utilizing IRR as a performance metric. The data gathered will eventually replace the current portfolio performance calculation methods across the application.

## 3. Functional Requirements

### 3.1 Cash Flow Types and Tracking

#### 3.1.1 Dividend Cash Flows
- FR1.1: The system shall record manually entered dividends for individual stocks in the user's portfolio
- FR1.2: The system shall automatically retrieve and record dividend payments for ETFs (VOO and QQQ) using the yfinance API or similar
- FR1.3: The system shall include all dividends as cash inflows in the cash flow table

#### 3.1.2 Cash Deposits and Withdrawals
- FR2.1: The system shall automatically infer cash deposits when a stock purchase would result in a negative cash balance
- FR2.2: The system shall create an implicit cash deposit transaction with the same date as the stock purchase to bring the cash balance to zero
- FR2.3: The system shall record these inferred deposits as cash inflows in the cash flow table

#### 3.1.3 Stock Sales Proceeds
- FR3.1: The system shall automatically track proceeds from stock sales as cash inflows
- FR3.2: The system shall update the portfolio's cash balance when stocks are sold
- FR3.3: The system shall record these proceeds as cash inflows in the cash flow table

### 3.2 Cash Flow Display

#### 3.2.1 Cash Flow Table
- FR4.1: The system shall display a table of all cash flows with the following columns:
  - Date (chronological order)
  - Type (cash deposit, proceeds from sale, dividend, purchase)
  - Amount
  - Portfolio Cash Balance
  - Description
- FR4.2: The system shall order the table chronologically by date
- FR4.3: The system shall ensure the Portfolio Cash Balance column never displays a negative value
- FR4.4: The system shall arrange same-day transactions in a logical order to maintain a non-negative cash balance
- FR4.5: The system shall visually connect related transactions by applying distinct color shading to rows containing automatic cash deposits and their triggering purchase transactions

#### 3.2.2 Summary Metrics
- FR5.1: The system shall display Total Amount Invested at the top of the Cash Flows tab
- FR5.2: The system shall display Current Portfolio Value (including cash) at the top of the Cash Flows tab
- FR5.3: The system shall display IRR at the top of the Cash Flows tab

#### 3.2.3 View Switching
- FR6.1: The system shall allow users to switch between viewing the user's stock portfolio and benchmark ETFs (VOO and QQQ)
- FR6.2: The system shall support multiple user portfolios, allowing users to select which portfolio to view

### 3.3 IRR Calculation

#### 3.3.1 Portfolio IRR
- FR7.1: The system shall calculate IRR based on all portfolio cash flows for the entire portfolio lifetime
- FR7.2: The system shall handle all cash flows (dividends, deposits, withdrawals, purchases, sales) in the IRR calculation
- FR7.3: The system shall recalculate IRR immediately when new transactions are added to the portfolio

#### 3.3.2 ETF Comparison IRR
- FR8.1: The system shall match cash deposits in ETF comparisons (assuming same-day investment in the ETF)
- FR8.2: The system shall assume automatic dividend reinvestment for ETFs in comparison calculations
- FR8.3: The system shall calculate IRR for ETF comparisons using the same methodology as for the portfolio

### 3.4 Data Management

#### 3.4.1 Data Persistence
- FR9.1: The system shall persist all cash flow data, including inferred cash flows
- FR9.2: The system shall store data in a way that is accessible to engineers without launching the application
- FR9.3: The system shall implement incremental updates, only calculating new cash flows since the last run

#### 3.4.2 Data Integration
- FR10.1: The system shall import historical transactions from existing portfolio data when the feature is first implemented
- FR10.2: The system shall ensure cash flow entries exist for all user transactions (buys, sells, dividends)
- FR10.3: The system shall verify completeness by cross-checking user entries with cash flow records

#### 3.4.3 Real-time Updates
- FR11.1: The system shall update cash flow records immediately when a user adds a new purchase transaction
- FR11.2: The system shall update cash flow records immediately when a user adds a new sale transaction
- FR11.3: The system shall update cash flow records immediately when a user adds a new dividend transaction
- FR11.4: The system shall recalculate Total Invested, Portfolio Value, and IRR immediately when cash flows are updated

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- NFR1.1: The system shall process background tasks (scanning for new transactions, adding assumed cash deposits, cross-checking with user entries, calculating IRR) at application startup
- NFR1.2: The system shall cache calculated values for performance optimization during user navigation
- NFR1.3: The system shall maintain responsiveness while price updates are happening in the background

### 4.2 Usability Requirements
- NFR2.1: The Cash Flows tab shall follow the same Bootstrap 5 styling as the rest of the application
- NFR2.2: The system shall provide clear visual distinction between different types of cash flows
- NFR2.3: The system shall provide intuitive controls for switching between portfolio and ETF comparison views

### 4.3 Reliability Requirements
- NFR3.1: The system shall maintain data integrity for all cash flow records
- NFR3.2: The system shall detect and prevent duplicate cash flow entries
- NFR3.3: The system shall provide accurate IRR calculations validated against financial standards

### 4.4 Compatibility Requirements
- NFR4.1: The Cash Flows feature shall be compatible with all browsers currently supported by MyStockTrackerApp
- NFR4.2: The Cash Flows feature shall be responsive on both desktop and mobile devices

### 4.5 Data Requirements
- NFR5.1: The system shall store cash flow data in a dedicated database table structure
- NFR5.2: The system shall include clear timestamps for when cash flows were added or calculated
- NFR5.3: The system shall distinguish between explicitly entered and inferred cash flows in the data model

## 5. Data Model

### 5.1 New Data Entities

#### 5.1.1 CashFlow
- **Primary Key**: UUID string
- **Attributes**:
  - portfolio_id: Foreign key to Portfolio
  - date: Date of the cash flow
  - flow_type: Enum (DEPOSIT, DIVIDEND, SALE_PROCEEDS, PURCHASE)
  - amount: Decimal value (positive for inflows, negative for outflows)
  - balance_after: Current cash balance after this transaction
  - is_inferred: Boolean indicating if this is an inferred transaction
  - source_transaction_id: Optional reference to originating transaction
  - description: Text description of the cash flow
  - created_at: Timestamp when record was created
  - updated_at: Timestamp when record was last updated

#### 5.1.2 IRRCalculation
- **Primary Key**: UUID string
- **Attributes**:
  - portfolio_id: Foreign key to Portfolio
  - calculation_date: Date when IRR was calculated
  - irr_value: Calculated IRR value
  - start_date: Start date for calculation period
  - end_date: End date for calculation period
  - created_at: Timestamp when record was created

### 5.2 Modified Data Entities

#### 5.2.1 PortfolioCache
- Add irr_value field to store cached IRR calculation
- Add total_invested field to store total invested amount

## 6. User Interface

### 6.1 Cash Flows Tab
- New tab added to the existing tab navigation alongside Dashboard, Transactions, and Dividends
- Contains the cash flow table and summary metrics

### 6.2 Cash Flow Table
- Chronological listing of all cash flows
- Columns: Date, Type, Amount, Portfolio Cash Balance, Description
- No interactive sorting or filtering

### 6.3 Summary Section
- Located at the top of the Cash Flows tab
- Displays Total Amount Invested, Current Portfolio Value, and IRR
- Includes portfolio/ETF comparison selector

## 7. Future Considerations

### 7.1 Planned Extensions
- IRR calculations will eventually replace current performance metrics across the application
- Future versions may include custom time period selection for IRR calculations
- Potential implementation of additional performance metrics based on cash flow data

### 7.2 Transition Strategy
- Validation period where both calculation methods run in parallel
- Criteria for determining when the new IRR calculations are ready to become the primary performance metrics
- UI updates to reflect IRR as the primary performance metric across the application

## 8. Implementation Notes

### 8.1 Development Approach
- Test-Driven Development (TDD) following current project practices
- Focus on data integrity and calculation accuracy
- Background processing for performance optimization

### 8.2 Integration Points
- Existing portfolio and transaction management components
- Yahoo Finance API for ETF dividend data
- Current performance visualization components

### 8.3 Caching Strategy
- Cache IRR calculations and summary metrics after each update
- Use cached values while background updates are in progress
- Clear cache when new transactions are added

## 9. Testing Requirements

### 9.1 Testing Priorities
- Accuracy of IRR calculations with various cash flow scenarios
- Correct identification and handling of implied cash deposits
- Performance with large transaction histories
- Integration with existing portfolio functionality

### 9.2 Test Data
- Sample portfolios with various transaction patterns
- Historical dividend and price data for benchmark ETFs
- Edge cases with same-day transactions