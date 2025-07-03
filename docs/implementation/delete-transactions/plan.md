# Delete Transactions Feature - Implementation Plan

## Test Strategy

### Test Scenarios
1. **Backend API Tests**
   - Test successful transaction deletion
   - Test deletion of non-existent transaction (404 error)
   - Test deletion without proper permissions
   - Test portfolio recalculation after deletion
   - Test database integrity after deletion

2. **Service Layer Tests**
   - Test delete_transaction method
   - Test portfolio holdings recalculation
   - Test error handling for invalid transaction IDs

3. **Integration Tests**
   - Test complete delete workflow
   - Test UI updates after deletion
   - Test confirmation dialog functionality

4. **Edge Cases**
   - Delete transaction that affects current holdings
   - Delete transaction from portfolio with single transaction
   - Delete transaction with associated dividends

### Test Data Strategy
- Use existing test factories for creating portfolios and transactions
- Mock price service calls for consistent testing
- Test with various transaction types (BUY/SELL)

## Implementation Plan

### Phase 1: Backend Implementation
1. **Add delete endpoint** in `app/views/portfolio.py`
   - Route: `/portfolio/delete-transaction/<transaction_id>`
   - Method: DELETE or POST
   - Return JSON response with success/error status

2. **Add service method** in `app/services/portfolio_service.py`
   - Method: `delete_transaction(transaction_id, portfolio_id)`
   - Validate transaction belongs to portfolio
   - Delete transaction from database
   - Return success/error status

### Phase 2: Frontend Implementation
3. **Update JavaScript** in transactions.html
   - Replace placeholder `deleteTransaction` function
   - Add AJAX call to delete endpoint
   - Handle success/error responses
   - Update UI after successful deletion

4. **Add confirmation modal** (optional enhancement)
   - Bootstrap modal for better UX
   - Show transaction details in confirmation

### Phase 3: Testing & Validation
5. **Implement comprehensive tests**
   - Backend API tests
   - Service layer tests
   - Integration tests

6. **Manual testing**
   - Test delete functionality in browser
   - Verify portfolio calculations update
   - Test error scenarios

## Implementation Checklist
- [ ] Write test cases for delete functionality
- [ ] Add delete_transaction method to PortfolioService
- [ ] Add delete endpoint to portfolio views
- [ ] Update JavaScript deleteTransaction function
- [ ] Add error handling and user feedback
- [ ] Test portfolio recalculation after deletion
- [ ] Validate security (user can only delete own transactions)
- [ ] Test edge cases and error scenarios
- [ ] Manual testing in browser
- [ ] Code review and refactoring

## Security Considerations
- Validate user owns the portfolio containing the transaction
- Use proper HTTP methods (DELETE or POST with CSRF)
- Sanitize transaction ID input
- Return appropriate error codes for unauthorized access

## Performance Considerations
- Minimal impact - single database delete operation
- Portfolio recalculation happens on next page load
- Consider caching invalidation if implemented

## Risk Mitigation
- Confirmation dialog prevents accidental deletions
- Database constraints ensure referential integrity
- Comprehensive error handling for edge cases
- Rollback capability through database transactions