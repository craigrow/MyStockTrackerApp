# Data Model: Cash Flows Tracking Feature

## 1. Overview

This document provides the detailed data model for the Cash Flows Tracking feature, showing both new entities and modifications to existing entities within the MyStockTrackerApp database schema.

## 2. Entity Relationship Diagram

```
┌────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│   Portfolio    │       │  StockTransaction │       │      Dividend     │
├────────────────┤       ├───────────────────┤       ├───────────────────┤
│ id (PK)        │       │ id (PK)           │       │ id (PK)           │
│ name           │◄─────┤│ portfolio_id (FK) │       │ portfolio_id (FK) │◄─────┐
│ description    │       │ ticker            │       │ ticker            │      │
│ user_id        │       │ transaction_type  │       │ payment_date      │      │
│ creation_date  │       │ date              │       │ total_amount      │      │
│ last_updated   │       │ price_per_share   │       └───────────────────┘      │
│ latest_irr*    │       │ shares            │                                  │
│ total_invested*│       │ total_value       │                                  │
└────┬───────────┘       └────┬──────────────┘                                  │
     │                        │                                                 │
     │                        │                                                 │
     │                        │                                                 │
     │                        │                                                 │
     │                        ▼                                                 │
     │           ┌────────────────────────┐                                     │
     │           │      NEW: CashFlow     │                                     │
     │           ├────────────────────────┤                                     │
     └──────────┤│ id (PK)                │                                     │
                 │ portfolio_id (FK)      │◄────────────────────────────────────┘
                 │ date                   │
                 │ flow_type              │
                 │ amount                 │
                 │ balance_after          │
                 │ is_inferred            │
                 │ source_transaction_id  │────┐
                 │ description            │    │
                 │ created_at             │    │
                 │ updated_at             │    │
                 └──────────┬─────────────┘    │
                            │                  │
                            │                  │
                            │                  │
                            ▼                  │
                 ┌────────────────────────┐    │
                 │  NEW: IRRCalculation   │    │
                 ├────────────────────────┤    │
                 │ id (PK)                │    │
                 │ portfolio_id (FK)      │    │
                 │ calculation_date       │    │
                 │ irr_value              │    │
                 │ start_date             │    │
                 │ end_date               │    │
                 │ created_at             │    │
                 └────────────────────────┘    │
                                               │
                                               │
                                               │
                        ┌─────────────────────┐│
                        │    CashBalance      ││
                        ├─────────────────────┤│
                        │ portfolio_id (PK,FK)││
                        │ balance             ││
                        │ last_updated        ││
                        └─────────────────────┘│
                                               │
                                               │
                 ┌───────────────────────┐     │
                 │NEW: ETFComparison     │     │
                 │     Portfolio         │     │
                 ├───────────────────────┤     │
                 │ id (PK)               │     │
                 │ user_portfolio_id (FK)│─────┼─────┐
                 │ etf_ticker            │     │     │
                 │ creation_date         │     │     │
                 │ last_updated          │     │     │
                 │ latest_irr            │     │     │
                 │ total_invested        │     │     │
                 └─────────┬─────────────┘     │     │
                           │                   │     │
                           │                   │     │
                           │                   │     │
                           ▼                   │     │
                 ┌───────────────────────┐     │     │
                 │  NEW: ETFCashFlow     │     │     │
                 ├───────────────────────┤     │     │
                 │ id (PK)               │     │     │
                 │ etf_portfolio_id (FK) │     │     │
                 │ date                  │     │     │
                 │ flow_type             │     │     │
                 │ amount                │     │     │
                 │ shares                │     │     │
                 │ price_per_share       │     │     │
                 │ is_dividend_reinvest  │     │     │
                 │ source_user_cashflow_id───┐ │     │
                 │ created_at            │   │ │     │
                 └───────────┬───────────┘   │ │     │
                             │               │ │     │
                             │               │ │     │
                             ▼               │ │     │
                 ┌───────────────────────┐   │ │     │
                 │  NEW: ETFDividend     │   │ │     │
                 ├───────────────────────┤   │ │     │
                 │ id (PK)               │   │ │     │
                 │ etf_portfolio_id (FK) │   │ │     │
                 │ payment_date          │   │ │     │
                 │ amount_per_share      │   │ │     │
                 │ total_amount          │   │ │     │
                 │ reinvested            │   │ │     │
                 │ created_at            │   │ │     │
                 └───────────────────────┘   │ │     │
                                             │ │     │
                                             │ │     │
                                             │ │     │
                        ┌─────────────────────┐│     │
                        │   PortfolioCache    ││     │
                        ├─────────────────────┤│     │
                        │ id (PK)             ││     │
                        │ portfolio_id (FK)   ││     │
                        │ cache_type          ││     │
                        │ cache_data (JSON)   ││     │
                        │ market_date         ││     │
                        │ created_at          ││     │
                        │ irr_value*          ││     │
                        │ total_invested*     ││     │
                        └─────────────────────┘│     │
                                               │     │
                                               │     │
                                               │     │
                        ┌─────────────────────┐│     │
                        │      Stock          ││     │
                        ├─────────────────────┤│     │
                        │ ticker (PK)         ││     │
                        │ company_name        ││     │
                        │ sector              ││     │
                        │ market_cap          ││     │
                        └─────────────────────┘│     │
                                               │     │
                                               │     │
                                               │     │
                         ┌────────────────────┐│     │
                         │   PriceHistory     ││     │
                         ├────────────────────┤│     │
                         │ ticker + date (PK) ││     │
                         │ close_price        ││     │
                         │ is_intraday        ││     │
                         │ price_timestamp    ││     │
                         │ last_updated       ││     │
                         └────────────────────┘│     │
                                               │     │
                                               │     │
                                               │     │
                                               ▼     │
                        ┌──────────────────────────┐ │
                        │      StockTransaction    │ │
                        │   (Referenced instance)   │ │
                        └──────────────────────────┘ │
                                                     │
                                                     │
                                                     │
                                                     ▼
                         ┌──────────────────────────────┐
                         │         CashFlow             │
                         │   (Referenced instance)      │
                         └──────────────────────────────┘
```

*Note: Fields marked with an asterisk (*) are newly added fields to existing entities.

## 3. Entity Descriptions

### 3.1 New Entities for Portfolio Cash Flows

#### 3.1.1 CashFlow

| Field                | Type          | Description                                           | Constraints              |
|----------------------|---------------|-------------------------------------------------------|--------------------------| 
| id                   | String(36)    | Primary key                                           | PK, NOT NULL             |
| portfolio_id         | String(36)    | Foreign key to Portfolio                              | FK, NOT NULL             |
| date                 | Date          | Date of the cash flow                                 | NOT NULL                 |
| flow_type            | Enum          | Type of cash flow (DEPOSIT, DIVIDEND, SALE_PROCEEDS, PURCHASE) | NOT NULL        |
| amount               | Numeric(10,2) | Amount of cash flow (positive for inflow, negative for outflow) | NOT NULL       |
| balance_after        | Numeric(10,2) | Portfolio cash balance after this flow                | NOT NULL                 |
| is_inferred          | Boolean       | Whether this is an automatically inferred cash flow   | NOT NULL, DEFAULT false  |
| source_transaction_id| String(36)    | Reference to source transaction (if applicable)       | FK to StockTransaction   |
| description          | String(255)   | Description of the cash flow                          | NULL allowed             |
| created_at           | DateTime      | Creation timestamp                                    | NOT NULL                 |
| updated_at           | DateTime      | Last update timestamp                                 | NOT NULL                 |

**Indexes:**
- Primary Key: `id`
- Foreign Keys: `portfolio_id` references `Portfolio.id`
- Foreign Keys: `source_transaction_id` references `StockTransaction.id` 
- Index: `ix_cash_flows_portfolio_date` on (`portfolio_id`, `date`)

#### 3.1.2 IRRCalculation

| Field            | Type          | Description                                  | Constraints      |
|------------------|---------------|----------------------------------------------|------------------|
| id               | String(36)    | Primary key                                  | PK, NOT NULL     |
| portfolio_id     | String(36)    | Foreign key to Portfolio                     | FK, NOT NULL     |
| calculation_date | Date          | Date when IRR was calculated                 | NOT NULL         |
| irr_value        | Numeric(10,6) | Calculated IRR value (as decimal percentage) | NOT NULL         |
| start_date       | Date          | Start date for IRR calculation period        | NOT NULL         |
| end_date         | Date          | End date for IRR calculation period          | NOT NULL         |
| created_at       | DateTime      | Creation timestamp                           | NOT NULL         |

**Indexes:**
- Primary Key: `id`
- Foreign Keys: `portfolio_id` references `Portfolio.id`
- Index: `ix_irr_calculations_portfolio_date` on (`portfolio_id`, `calculation_date`)

### 3.2 Modified Entities

#### 3.2.1 Portfolio

**New Fields Added:**

| Field            | Type          | Description                               | Constraints  |
|------------------|---------------|-------------------------------------------|--------------|
| latest_irr       | Numeric(10,6) | Latest calculated IRR for the portfolio   | NULL allowed |
| total_invested   | Numeric(10,2) | Total amount invested in the portfolio    | NULL allowed |

#### 3.2.2 PortfolioCache

**New Fields Added:**

| Field            | Type          | Description                                   | Constraints  |
|------------------|---------------|-----------------------------------------------|--------------|
| irr_value        | Numeric(10,6) | Cached IRR value for specific calculation     | NULL allowed |
| total_invested   | Numeric(10,2) | Cached total invested amount                  | NULL allowed |

### 3.3 Existing Related Entities

#### 3.3.1 StockTransaction

| Field            | Type          | Description                               | Constraints      |
|------------------|---------------|-------------------------------------------|------------------|
| id               | String(36)    | Primary key                               | PK, NOT NULL     |
| portfolio_id     | String(36)    | Foreign key to Portfolio                  | FK, NOT NULL     |
| ticker           | String        | Stock ticker symbol                       | NOT NULL         |
| transaction_type | Enum          | BUY or SELL                               | NOT NULL         |
| date             | Date          | Transaction date                          | NOT NULL         |
| price_per_share  | Numeric(10,2) | Price per share                           | NOT NULL         |
| shares           | Numeric(10,4) | Number of shares                          | NOT NULL         |
| total_value      | Numeric(10,2) | Total value of the transaction            | NOT NULL         |

#### 3.3.2 Dividend

| Field            | Type          | Description                               | Constraints      |
|------------------|---------------|-------------------------------------------|------------------|
| id               | String(36)    | Primary key                               | PK, NOT NULL     |
| portfolio_id     | String(36)    | Foreign key to Portfolio                  | FK, NOT NULL     |
| ticker           | String        | Stock ticker symbol                       | NOT NULL         |
| payment_date     | Date          | Dividend payment date                     | NOT NULL         |
| total_amount     | Numeric(10,2) | Total dividend amount                     | NOT NULL         |

#### 3.3.3 CashBalance

| Field            | Type          | Description                               | Constraints      |
|------------------|---------------|-------------------------------------------|------------------|
| portfolio_id     | String(36)    | Primary key and foreign key to Portfolio  | PK, FK, NOT NULL |
| balance          | Numeric(10,2) | Current cash balance                      | NOT NULL         |
| last_updated     | DateTime      | Last update timestamp                     | NOT NULL         |

## 4. Relationships

### 4.1 Portfolio Cash Flow Relationships

1. **Portfolio to CashFlow**: One-to-many. A portfolio has many cash flow entries.
   - Portfolio.id → CashFlow.portfolio_id

2. **Portfolio to IRRCalculation**: One-to-many. A portfolio has many IRR calculation records.
   - Portfolio.id → IRRCalculation.portfolio_id

3. **StockTransaction to CashFlow**: One-to-one (optional). A stock transaction may be associated with a cash flow entry.
   - StockTransaction.id → CashFlow.source_transaction_id

4. **Portfolio to StockTransaction**: One-to-many. A portfolio has many stock transactions.
   - Portfolio.id → StockTransaction.portfolio_id

5. **Portfolio to Dividend**: One-to-many. A portfolio has many dividend records.
   - Portfolio.id → Dividend.portfolio_id

6. **Portfolio to CashBalance**: One-to-one. A portfolio has one cash balance record.
   - Portfolio.id → CashBalance.portfolio_id

7. **Portfolio to PortfolioCache**: One-to-many. A portfolio has many cache entries.
   - Portfolio.id → PortfolioCache.portfolio_id

### 4.2 ETF Comparison Relationships

8. **Portfolio to ETFComparisonPortfolio**: One-to-many. A user portfolio can have multiple ETF comparison portfolios (e.g., VOO and QQQ).
   - Portfolio.id → ETFComparisonPortfolio.user_portfolio_id

9. **ETFComparisonPortfolio to ETFCashFlow**: One-to-many. An ETF comparison portfolio has many cash flow entries.
   - ETFComparisonPortfolio.id → ETFCashFlow.etf_portfolio_id

10. **ETFComparisonPortfolio to ETFDividend**: One-to-many. An ETF comparison portfolio has many dividend records.
    - ETFComparisonPortfolio.id → ETFDividend.etf_portfolio_id

11. **CashFlow to ETFCashFlow**: One-to-many. A user portfolio cash flow (typically a deposit) may trigger corresponding cash flows in multiple ETF comparison portfolios.
    - CashFlow.id → ETFCashFlow.source_user_cashflow_id

## 5. Data Integrity Constraints

1. **Cascade Deletion**: When a Portfolio is deleted, all related CashFlow and IRRCalculation records should be deleted (CASCADE).

2. **Foreign Key Integrity**: All foreign key relationships must be maintained.

3. **Non-negative Balance**: The application logic must ensure that CashFlow.balance_after is never negative.

4. **Chronological Ordering**: The application must ensure that cash flows are processed in strict chronological order.

5. **Source Transaction Integrity**: When a StockTransaction is deleted, the associated CashFlow.source_transaction_id should be set to NULL (SET NULL).

## 6. Data Migration Path

The migration path for implementing this data model includes:

1. Add new tables `cash_flows` and `irr_calculations` to the database schema
2. Add new columns to `portfolios` and `portfolio_cache` tables
3. Populate cash flow data from existing transactions and dividends
4. Calculate initial IRR values for existing portfolios

## 7. Database Indexing Strategy

1. **CashFlow Indexing**: 
   - Index on (`portfolio_id`, `date`) to optimize retrieval of cash flows by date for a specific portfolio

2. **IRRCalculation Indexing**:
   - Index on (`portfolio_id`, `calculation_date`) to optimize retrieval of the latest IRR calculation

3. **Efficient Joins**:
   - Ensure all foreign key columns are properly indexed to optimize join operations

## 8. Cache Considerations

The data model supports caching through:

1. Direct storage of calculated values in the Portfolio table for quick access
2. The PortfolioCache table for more detailed and varied cached data
3. Structured JSON storage in PortfolioCache.cache_data for flexible caching needs