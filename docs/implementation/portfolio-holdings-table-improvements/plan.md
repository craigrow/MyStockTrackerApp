# Portfolio Holdings Table Improvements - Implementation Plan

## Analysis Summary

### Current Holdings Table Structure
- **Location**: `app/templates/dashboard.html` (lines ~150-180)
- **Current Columns**: Ticker, Shares, Current Price, Market Value, Gain/Loss, %
- **Data Source**: `get_holdings_with_performance()` in `app/views/main.py`
- **Current "%" Column**: Shows `gain_loss_percentage` (confirmed this is Gain/Loss %)

### Existing ETF Performance Infrastructure
- ✅ ETF performance API endpoint: `/api/etf-performance/<ticker>/<purchase_date>`
- ✅ ETF equivalent calculations: `calculate_current_etf_equivalent()`
- ✅ Historical price data: `get_historical_price()` function
- ✅ Transaction date tracking: Available in portfolio service

## Implementation Strategy

### Phase 1: Backend Enhancements
1. **Extend Holdings Data Structure**
   - Add VOO performance calculation per holding
   - Add QQQ performance calculation per holding
   - Calculate weighted average purchase dates per ticker
   - Add portfolio percentage for highlighting logic

2. **ETF Performance Calculations**
   - Use existing `get_historical_price()` for purchase date prices
   - Calculate performance: `((current_price - purchase_price) / purchase_price) * 100`
   - Handle multiple purchase dates with weighted averages

### Phase 2: Frontend Enhancements
1. **Table Structure Updates**
   - Add "VOO Performance" column
   - Add "QQQ Performance" column  
   - Rename "%" to "Gain/Loss %"
   - Add sortable headers with click handlers

2. **JavaScript Functionality**
   - Implement table sorting by any column
   - Add number formatting with commas
   - Calculate top 50% holdings by market value
   - Apply light grey highlighting to top holdings

### Phase 3: Testing & Validation
1. **Unit Tests**
   - Test ETF performance calculations
   - Test sorting functionality
   - Test number formatting
   - Test highlighting logic

2. **Integration Tests**
   - Test complete holdings table rendering
   - Test API integration
   - Test responsive behavior

## Detailed Implementation Plan

### Backend Changes

#### 1. Update `get_holdings_with_performance()` Function
```python
# Add to each holding dict:
{
    'voo_performance': calculate_etf_performance_for_holding(ticker, transactions, 'VOO'),
    'qqq_performance': calculate_etf_performance_for_holding(ticker, transactions, 'QQQ'),
    'portfolio_percentage': (market_value / total_portfolio_value) * 100
}
```

#### 2. New Helper Function: `calculate_etf_performance_for_holding()`
- Get all transactions for the ticker
- Calculate weighted average purchase date and price
- Get ETF price on weighted average purchase date
- Get current ETF price
- Calculate performance percentage

### Frontend Changes

#### 1. Update HTML Table Structure
```html
<th class="sortable" data-column="ticker">Ticker</th>
<th class="sortable" data-column="shares">Shares</th>
<th class="sortable" data-column="current_price">Current Price</th>
<th class="sortable" data-column="market_value">Market Value</th>
<th class="sortable" data-column="gain_loss">Gain/Loss</th>
<th class="sortable" data-column="gain_loss_percentage">Gain/Loss %</th>
<th class="sortable" data-column="voo_performance">VOO Performance</th>
<th class="sortable" data-column="qqq_performance">QQQ Performance</th>
```

#### 2. JavaScript Sorting Implementation
- Add click handlers to sortable headers
- Implement multi-type sorting (numeric, text, percentage)
- Add sort direction indicators (arrows)
- Maintain sort state

#### 3. Number Formatting
- Format all numbers ≥1000 with commas
- Apply to: Shares, Current Price, Market Value, Gain/Loss
- Preserve existing color coding for gains/losses

#### 4. Top Holdings Highlighting
- Calculate cumulative portfolio percentage
- Identify holdings that make up top 50%
- Apply `bg-light` class to those rows
- Only when sorted by Market Value (default)

## Test Strategy

### Test Scenarios
1. **ETF Performance Accuracy**
   - Single purchase date scenarios
   - Multiple purchase dates (weighted average)
   - Edge cases (same-day purchases, sells)

2. **Sorting Functionality**
   - Sort by each column (ascending/descending)
   - Mixed data types handling
   - Sort state persistence

3. **Number Formatting**
   - Numbers < 1000 (no commas)
   - Numbers ≥ 1000 (with commas)
   - Decimal precision preservation

4. **Highlighting Logic**
   - Top 50% calculation accuracy
   - Highlighting only on default sort
   - Dynamic recalculation on sort change

### Performance Considerations
- ETF performance calculations cached with holdings data
- Minimal additional API calls (reuse existing price data)
- Client-side sorting for responsiveness
- Efficient DOM manipulation for highlighting

## Risk Mitigation
- Graceful degradation if ETF data unavailable
- Fallback to existing table if JavaScript fails
- Preserve existing responsive design
- Maintain backward compatibility with existing tests