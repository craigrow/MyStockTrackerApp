# Integration Test Phase 1 - Context Document

## Project Structure Analysis

### Technology Stack
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5, Chart.js for visualizations
- **Testing**: pytest with 132 existing tests
- **APIs**: Yahoo Finance (yfinance) for real-time stock data

### Current Test Infrastructure
- **Existing Tests**: 132 comprehensive tests (100% pass rate)
- **Test Categories**: Models, Services, Integration, CSV Import, Performance
- **Test Markers**: `@pytest.mark.fast`, `@pytest.mark.slow`, `@pytest.mark.ui`, `@pytest.mark.api`
- **Test Utilities**: Comprehensive fixtures in `conftest.py`
- **Fast Test Runner**: `run_fast_tests.py` for development workflow

## Requirements Analysis

### Primary Goal
Implement Phase 1 of comprehensive integration test strategy to prevent rollbacks like the recent chart issue and establish foundation for high code velocity.

### Specific Requirements
1. **Critical User Journey Tests**
   - Dashboard loads with working chart in <3 seconds
   - Portfolio creation to chart workflow
   - Chart lines start at same value (regression prevention)
   - Multi-portfolio dashboard handling

2. **Test Infrastructure**
   - Reusable test utilities and data factories
   - Performance baseline validation
   - CI integration for fast tests (<30 seconds)

3. **Performance Baselines**
   - Dashboard load time validation (2-3 seconds)
   - Chart generation performance
   - Interactive chart responsiveness

### Acceptance Criteria
- All critical user journeys have integration tests
- Tests run in <30 seconds for CI integration
- Performance baselines are automatically validated
- Test infrastructure supports future phases
- Tests would have caught the chart rollback issue

## Implementation Paths

### Directory Structure
```
tests/integration/
├── critical_paths/           # Phase 1 focus
│   ├── test_dashboard_chart.py
│   ├── test_portfolio_workflow.py
│   └── test_core_features.py
└── utils/                    # Shared infrastructure
    ├── test_factories.py
    ├── performance_helpers.py
    └── assertion_helpers.py
```

### Integration Points
- **Existing Test Suite**: Extend current pytest infrastructure
- **Flask Test Client**: Use existing client fixtures
- **Database**: Leverage existing test database setup
- **Mocking**: Use existing Yahoo Finance API mocking patterns

## Patterns and Dependencies

### Existing Test Patterns
- **Fixture Usage**: Comprehensive fixtures in `conftest.py`
- **Mocking Strategy**: Yahoo Finance API mocked with `unittest.mock.patch`
- **Database Testing**: Temporary SQLite databases with automatic cleanup
- **AAA Pattern**: Arrange, Act, Assert structure

### Key Dependencies
- **Flask Testing**: Test client and application context
- **SQLAlchemy**: Database operations and transactions
- **Chart.js Integration**: Frontend chart rendering validation
- **Yahoo Finance API**: External data source (mocked in tests)

### Performance Testing Approach
- **Time Measurement**: Use `time.time()` for load time validation
- **Memory Monitoring**: Track memory usage during operations
- **Response Validation**: Verify chart data structure and content

## Implementation Strategy

### Phase 1 Focus Areas
1. **Test Infrastructure Setup**
   - Create reusable test utilities
   - Establish performance measurement helpers
   - Set up data factories for consistent test scenarios

2. **Critical Path Tests**
   - Dashboard load with chart validation
   - Complete user workflow testing
   - Chart regression prevention tests

3. **CI Integration**
   - Fast test execution (<30 seconds)
   - Automated performance baseline validation
   - Clear failure reporting

### Success Metrics
- Tests prevent chart rollback scenario
- Dashboard load time consistently validated
- Test execution time under 30 seconds
- Foundation ready for Phase 2 expansion

## Risk Mitigation
- **Test Isolation**: Each test uses clean database state
- **Mock Reliability**: Consistent API response mocking
- **Performance Variability**: Use reasonable time thresholds
- **Chart Rendering**: Focus on data validation over visual testing