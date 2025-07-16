# ETF Dividend Calculation Fix - Implementation Plan

## Problem Analysis
The bug is in `_get_etf_dividend_flows()` method at line 139:
```python
total_dividend = float(div_amount) * total_shares  # ❌ WRONG
```

This uses `total_shares` (final total) for ALL dividend calculations, but should calculate shares held at each dividend date.

## Test Scenarios

### Test Case 1: Basic Dividend Calculation
- **Setup**: Portfolio with $1000 deposit on 2024-01-01, VOO dividend of $1.50 on 2024-06-30
- **Expected**: Dividend = $1.50 × (shares purchased with $1000 on 2024-01-01)
- **Current Bug**: Uses total final shares instead of shares on dividend date

### Test Case 2: Multiple Deposits Before Dividend
- **Setup**: 
  - $1000 deposit on 2024-01-01 (buys X shares)
  - $500 deposit on 2024-03-01 (buys Y shares) 
  - VOO dividend on 2024-06-30
- **Expected**: Dividend = $1.50 × (X + Y shares)
- **Current Bug**: Uses total final shares including reinvestments

### Test Case 3: Dividend Reinvestment Impact
- **Setup**:
  - $1000 deposit on 2024-01-01 (buys 100 shares)
  - First dividend on 2024-06-30 ($150, reinvested to buy 10 more shares)
  - Second dividend on 2024-12-30
- **Expected**: 
  - First dividend = $1.50 × 100 shares = $150
  - Second dividend = $1.50 × 110 shares = $165
- **Current Bug**: Uses final total (110 shares) for both dividends

### Test Case 4: Edge Cases
- **Empty deposits**: Should return empty dividend flows
- **No dividends in period**: Should return empty list
- **API failure**: Should handle gracefully and return empty list

## Implementation Strategy

### Step 1: Fix `_get_etf_dividend_flows()` Method
Replace the current logic with date-based share calculation:

1. **Track shares chronologically**: Calculate cumulative shares at each dividend date
2. **Account for purchases**: Include all deposits/purchases up to dividend date
3. **Account for reinvestments**: Include previous dividend reinvestments up to dividend date
4. **Calculate correct dividend**: Use shares held on specific dividend date

### Step 2: Algorithm Design
```
For each dividend date:
  1. Get all deposits before or on dividend date
  2. Calculate shares from deposits (deposit_amount / etf_price_on_deposit_date)
  3. Get all previous dividends before this dividend date
  4. Calculate reinvested shares from previous dividends
  5. Total shares on dividend date = deposit_shares + reinvested_shares
  6. Dividend amount = dividend_per_share × total_shares_on_date
```

### Step 3: Maintain Existing Interface
- Keep method signature unchanged
- Maintain return format for backward compatibility
- Preserve error handling patterns

## Implementation Checklist
- [ ] Write failing tests for all scenarios
- [ ] Implement new `_calculate_shares_on_date()` helper method
- [ ] Update `_get_etf_dividend_flows()` to use date-based calculation
- [ ] Verify all tests pass
- [ ] Run full test suite to ensure no regressions
- [ ] Update any related methods if needed

## Risk Mitigation
- **Backward Compatibility**: Maintain existing method signatures
- **Performance**: Cache price lookups to avoid repeated API calls
- **Error Handling**: Graceful fallbacks for missing price data
- **Testing**: Comprehensive test coverage for edge cases