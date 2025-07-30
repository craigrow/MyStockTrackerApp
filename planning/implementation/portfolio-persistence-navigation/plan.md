# Portfolio Persistence Navigation - Implementation Plan

## Test Strategy

### Test Categories

#### 1. Context Processor Tests
**Test File**: `tests/test_portfolio_context_processor.py`

**Scenarios:**
- Context processor provides portfolios list to all templates
- Context processor determines current_portfolio from URL parameter
- Context processor falls back to localStorage-indicated portfolio
- Context processor defaults to first portfolio when no selection exists
- Context processor handles empty portfolio list gracefully
- Context processor maintains backward compatibility with existing URL patterns

#### 2. Base Template Integration Tests  
**Test File**: `tests/test_base_template_navigation.py`

**Scenarios:**
- Base template renders portfolio selector in navbar
- Portfolio selector displays current portfolio name correctly
- Portfolio dropdown contains all available portfolios
- Hamburger menu contains all navigation items
- Navigation items have correct URLs and icons
- Template handles missing portfolio data gracefully

#### 3. JavaScript Portfolio Persistence Tests
**Test File**: `tests/test_portfolio_persistence_js.py`

**Scenarios:**
- Portfolio selection saves to localStorage
- Navigation functions append portfolio_id to URLs
- Page load restores portfolio from localStorage
- URL parameter overrides localStorage selection
- Portfolio selector updates when selection changes
- Handles missing localStorage gracefully

#### 4. View Integration Tests
**Test File**: `tests/test_persistent_portfolio_views.py`

**Scenarios:**
- Dashboard view respects persistent portfolio selection
- Transactions view maintains portfolio context
- Cash flows view preserves portfolio selection
- Dividends view uses persistent portfolio
- Direct URLs with portfolio_id still work
- Views handle portfolio persistence edge cases

#### 5. End-to-End Navigation Tests
**Test File**: `tests/test_e2e_portfolio_navigation.py`

**Scenarios:**
- User selects portfolio, navigates to different tab, portfolio persists
- User bookmarks page with portfolio_id, returns later, correct portfolio loads
- User switches portfolios, all subsequent navigation uses new portfolio
- Multiple browser tabs maintain independent portfolio selections
- Portfolio persistence works across browser sessions

### Test Data Strategy
- Use test fixtures for multiple portfolios
- Mock localStorage for JavaScript tests
- Create test transactions across different portfolios
- Use Selenium for end-to-end browser testing

## Implementation Plan

### Phase 1: Context Processor Foundation
**Files to Create/Modify:**
- `app/context_processors.py` (new)
- `app/__init__.py` (register context processor)

**Implementation Tasks:**
1. Create portfolio context processor function
2. Implement portfolio selection logic (URL → localStorage → default)
3. Register context processor with Flask app
4. Ensure all templates receive portfolio data

### Phase 2: Base Template Redesign
**Files to Modify:**
- `app/templates/base.html`

**Implementation Tasks:**
1. Move portfolio selector to navbar
2. Implement hamburger menu for navigation
3. Add JavaScript for portfolio persistence
4. Style components with Bootstrap 5

### Phase 3: View Layer Enhancement
**Files to Modify:**
- `app/views/main.py`
- `app/views/portfolio.py` 
- `app/views/cash_flows.py`

**Implementation Tasks:**
1. Update portfolio selection logic in all views
2. Remove redundant portfolio data passing
3. Maintain backward compatibility with URL parameters
4. Add portfolio persistence support

### Phase 4: Template Cleanup
**Files to Modify:**
- `app/templates/dashboard.html`
- `app/templates/portfolio/transactions.html`
- `app/templates/cash_flows.html`
- Other portfolio-specific templates

**Implementation Tasks:**
1. Remove individual portfolio selectors
2. Update portfolio-dependent JavaScript
3. Ensure templates use context processor data
4. Test template rendering with new structure

### Phase 5: JavaScript Integration
**Files to Create/Modify:**
- `app/templates/base.html` (JavaScript section)
- Individual templates (portfolio-specific JS updates)

**Implementation Tasks:**
1. Implement localStorage portfolio persistence
2. Create portfolio-aware navigation functions
3. Add automatic portfolio context restoration
4. Handle edge cases and error scenarios

## Architecture Decisions

### Context Processor Design
- Single context processor for all portfolio-related data
- Centralized portfolio selection logic
- Backward compatibility with existing URL patterns
- Graceful handling of edge cases

### JavaScript Strategy
- localStorage for client-side persistence
- Progressive enhancement (works without JS)
- Automatic URL parameter injection
- Cross-tab portfolio synchronization

### Template Inheritance
- Portfolio selector in base template only
- Individual templates inherit portfolio context
- Consistent navigation across all pages
- Minimal template duplication

## Implementation Checklist

### Context Processor
- [ ] Create context processor function
- [ ] Implement portfolio selection logic
- [ ] Register with Flask application
- [ ] Test portfolio data availability

### Base Template
- [ ] Design navbar with portfolio selector
- [ ] Implement hamburger menu
- [ ] Add portfolio persistence JavaScript
- [ ] Style with Bootstrap components

### View Updates
- [ ] Update dashboard view
- [ ] Update transactions view
- [ ] Update cash flows view
- [ ] Update dividends view
- [ ] Test backward compatibility

### Template Cleanup
- [ ] Remove individual selectors
- [ ] Update JavaScript references
- [ ] Test template rendering
- [ ] Verify portfolio context

### JavaScript Features
- [ ] localStorage persistence
- [ ] Navigation functions
- [ ] Context restoration
- [ ] Error handling

### Testing
- [ ] Unit tests for context processor
- [ ] Template rendering tests
- [ ] JavaScript functionality tests
- [ ] Integration tests
- [ ] End-to-end navigation tests

## Risk Mitigation

### Backward Compatibility
- Maintain URL parameter support
- Graceful degradation without JavaScript
- Preserve existing bookmarks/links

### Performance Considerations
- Minimize additional database queries
- Efficient localStorage usage
- Fast template rendering

### User Experience
- Clear portfolio selection feedback
- Consistent navigation behavior
- Intuitive hamburger menu design
