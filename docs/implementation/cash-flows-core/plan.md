# Cash Flows Core Implementation - Plan

## Test Strategy

### Database Model Tests

#### CashFlow Model Tests
- **test_cash_flow_creation**: Basic model creation with all required fields
- **test_cash_flow_types**: Validate all cash flow types (DEPOSIT, PURCHASE, SALE, DIVIDEND)
- **test_cash_flow_relationships**: Portfolio foreign key relationship
- **test_cash_flow_chronological_ordering**: Date-based ordering
- **test_cash_flow_balance_calculation**: Running balance calculations

#### IRRCalculation Model Tests  
- **test_irr_calculation_creation**: Basic model creation
- **test_irr_calculation_portfolio_relationship**: Portfolio foreign key
- **test_irr_calculation_caching**: Cache invalidation logic

### Service Layer Tests

#### CashFlowService Tests
- **test_generate_cash_flows_empty_portfolio**: Handle portfolio with no transactions
- **test_generate_cash_flows_simple_purchase**: Single purchase with inferred deposit
- **test_generate_cash_flows_multiple_same_day**: Multiple purchases on same day (one deposit)
- **test_generate_cash_flows_with_sales**: Purchase and sale transactions
- **test_generate_cash_flows_with_dividends**: Include dividend payments
- **test_inferred_deposit_calculation**: Exact amount calculation (rounded to penny)
- **test_no_negative_balances**: Ensure balance never goes negative
- **test_chronological_processing**: Transactions processed in date order

#### IRRCalculationService Tests
- **test_irr_calculation_simple**: Basic IRR calculation with known result
- **test_irr_calculation_no_cash_flows**: Handle empty cash flows
- **test_irr_calculation_single_deposit**: Handle single deposit scenario
- **test_irr_calculation_complex**: Multiple deposits and returns
- **test_irr_calculation_caching**: Cache results for performance

### Integration Tests

#### Data Migration Tests
- **test_migrate_existing_portfolio**: Populate cash flows from existing transactions
- **test_migrate_duplicate_detection**: Report but continue on duplicates
- **test_migrate_data_validation**: Handle invalid transaction data
- **test_migrate_large_portfolio**: Performance with many transactions

#### UI Integration Tests
- **test_cash_flows_tab_rendering**: New tab displays correctly
- **test_cash_flows_table_data**: Table shows correct cash flow data
- **test_cash_flows_summary_metrics**: Summary cards display IRR and totals
- **test_cash_flows_navigation**: Tab navigation works correctly

## Implementation Strategy

### Phase 1: Database Models ✅
1. Create CashFlow model with all required fields
2. Create IRRCalculation model for caching
3. Add Portfolio model extensions (cash_flows, irr_calculations relationships)
4. Comprehensive test coverage (22 tests)

### Phase 2: Service Layer ✅
1. Implement CashFlowService with core business logic
2. Implement IRRCalculationService with scipy integration
3. All tests passing (255 total tests)

### Phase 3: Data Synchronization (Next Session)
1. Create database schema migration (table creation only)
2. Implement hash-based data synchronization service
3. Add page-level integration (dashboard and cash flows routes)
4. Handle edge cases (backdated transactions, modifications, deletions)

### Phase 4: UI Components
1. Add Cash Flows tab to navigation
2. Create cash flows table template
3. Add summary metrics cards with IRR display
4. Implement route handlers

### Phase 5: Integration & Testing
1. End-to-end testing with real portfolio data
2. Performance testing with large datasets
3. User acceptance testing

## Technical Decisions

### IRR Calculation Method
- **Library**: scipy.optimize for Newton-Raphson method
- **Fallback**: Simple approximation if scipy fails
- **Precision**: Round to 4 decimal places (0.01% precision)

### Cash Flow Generation Logic
- **Starting Balance**: Always $0.00
- **Inferred Deposits**: Exact amount needed, rounded to penny
- **Same-Day Grouping**: One deposit per day for multiple purchases
- **Chronological Order**: Process all transactions by date ascending

### Database Schema
- **UUID Primary Keys**: Consistent with existing models
- **Foreign Keys**: Portfolio relationship with cascade delete
- **Indexes**: Date and portfolio_id for performance
- **Constraints**: Non-null validations, positive amounts

### Caching Strategy
- **IRR Results**: Cache per portfolio with date-based invalidation
- **Cash Flows**: Regenerate on transaction changes
- **Performance**: Batch operations for large portfolios

## Risk Mitigation

### Data Migration Risks
- **Backup Strategy**: Document existing data before migration
- **Rollback Plan**: Keep existing calculations running in parallel
- **Validation**: Compare results with current performance metrics

### Performance Risks
- **Large Portfolios**: Batch processing for portfolios with 1000+ transactions
- **IRR Calculation**: Timeout handling for complex scenarios
- **Database Load**: Efficient queries with proper indexing

### Integration Risks
- **UI Compatibility**: Follow existing Bootstrap patterns
- **Navigation**: Maintain existing user experience
- **Testing**: Comprehensive test coverage before deployment