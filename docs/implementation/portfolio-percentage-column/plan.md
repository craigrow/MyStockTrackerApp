# Portfolio Percentage Column - Implementation Plan

## Test Scenarios

### Unit Tests
1. **Percentage Calculation**
   - Input: Holdings with market values [1000, 500, 250], Total: 1750
   - Expected: [57.14%, 28.57%, 14.29%]

2. **Edge Cases**
   - Zero portfolio value: Should return 0% for all holdings
   - Single holding: Should return 100%
   - Empty holdings: Should handle gracefully

3. **Sorting Logic**
   - Holdings should be sorted by portfolio_percentage descending by default
   - Verify largest percentage appears first

### Integration Tests
1. **Dashboard Rendering**
   - Verify new column appears in holdings table
   - Verify column header is "Portfolio %"
   - Verify percentages display with 2 decimal places

2. **Data Accuracy**
   - Create test portfolio with known values
   - Verify calculated percentages match expected values
   - Verify sorting order is correct

## Implementation Steps

### Step 1: Backend Logic
- Modify `get_holdings_with_performance()` function
- Calculate total portfolio value
- Add `portfolio_percentage` to each holding dictionary
- Sort holdings by portfolio_percentage descending

### Step 2: Frontend Template
- Add new column header to holdings table
- Add portfolio percentage cell with proper formatting
- Ensure responsive design is maintained

### Step 3: Testing
- Write unit tests for calculation logic
- Write integration tests for dashboard rendering
- Verify all existing tests still pass

## Implementation Checklist
- [ ] Write unit tests for percentage calculation
- [ ] Write integration tests for dashboard display
- [ ] Modify `get_holdings_with_performance()` function
- [ ] Update dashboard template
- [ ] Verify sorting functionality
- [ ] Run full test suite
- [ ] Manual testing on dashboard