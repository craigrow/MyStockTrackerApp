# Portfolio Persistence Navigation - Implementation Context

## Task Description
As a user, I want the application to persist the portfolio I'm viewing as I switch between tabs (dashboard, transactions, cash flows, etc.) so that I don't have to change portfolios when I switch tabs, unlike today where I might have to switch portfolios using the selector. Also, I want the selector to be in a consistent location across all of the tabs, preferably in the header, where the tab selectors are today. While we're doing this, let's move the tabs behind a hamburger menu in the top right.

## Project Structure
- **Technology Stack**: Python Flask, SQLAlchemy, Bootstrap 5, Chart.js
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Server-side rendered templates with JavaScript enhancements
- **Testing**: pytest with 225+ comprehensive tests

## Current Architecture Analysis

### Portfolio Selection Pattern
**Current Implementation:**
- All views use `portfolio_id = request.args.get('portfolio_id')` pattern
- Views: main.py (dashboard), portfolio.py (transactions, dividends), cash_flows.py
- Fallback logic: URL param → first available portfolio → None
- Portfolio selector embedded in individual templates (dashboard.html)

### Navigation Structure
**Current base.html:**
- Traditional horizontal navbar with visible tabs
- Tabs: Dashboard, Transactions, Dividends, Cash Flows, Monitoring
- No portfolio context in base template
- Individual pages handle portfolio selection independently

### Template Data Flow
**Current Pattern:**
```python
# Each view follows this pattern:
portfolio_id = request.args.get('portfolio_id')
current_portfolio = portfolio_service.get_portfolio(portfolio_id) if portfolio_id else portfolios[0]
return render_template('template.html', 
                     portfolios=portfolios,
                     current_portfolio=current_portfolio)
```

## Requirements Analysis

### Functional Requirements
1. **Portfolio Persistence**: Selected portfolio persists across all navigation
2. **Header Integration**: Portfolio selector moves to navbar in base.html
3. **Hamburger Menu**: Navigation tabs collapse into hamburger menu
4. **Cross-Tab Context**: No re-selection needed when switching tabs
5. **Backward Compatibility**: URL parameters still work for direct links

### Technical Requirements
1. **localStorage Integration**: Client-side portfolio persistence
2. **Context Processor**: Global portfolio data availability
3. **JavaScript Navigation**: Portfolio-aware navigation functions
4. **Template Refactoring**: Remove individual portfolio selectors
5. **Route Enhancement**: Support persistent portfolio context

### Acceptance Criteria
1. Portfolio selection persists when navigating between tabs
2. Portfolio selector appears consistently in header across all pages
3. Navigation tabs are accessible via hamburger menu
4. Direct URLs with portfolio_id parameter still work
5. First-time users see default portfolio selection
6. All existing functionality remains intact

## Implementation Strategy

### Phase 1: Context Processor
- Create global portfolio context processor
- Ensure all templates have access to portfolios and current_portfolio
- Maintain backward compatibility with existing URL parameters

### Phase 2: Base Template Enhancement
- Move portfolio selector to navbar in base.html
- Implement hamburger menu for navigation tabs
- Add JavaScript for portfolio persistence and navigation

### Phase 3: View Layer Updates
- Enhance portfolio selection logic to check localStorage
- Update all views to support persistent portfolio context
- Remove individual portfolio selectors from templates

### Phase 4: JavaScript Integration
- localStorage-based portfolio persistence
- Portfolio-aware navigation functions
- Automatic portfolio context restoration

## Dependencies
- Flask templating system and context processors
- Bootstrap 5 dropdown and collapse components
- JavaScript localStorage API
- Existing portfolio service layer
- Current route structure and URL patterns

## Risk Considerations
- Breaking existing bookmarks/direct links
- JavaScript disabled scenarios
- Multiple portfolio edge cases
- Template inheritance complexity
