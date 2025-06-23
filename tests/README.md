# MyStockTrackerApp Test Suite

This directory contains comprehensive test cases for the MyStockTrackerApp, covering models, services, and integration scenarios.

## Test Structure

### Test Files

- **`test_models.py`** - Unit tests for all data models (Stock, Portfolio, StockTransaction, Dividend, CashBalance, PriceHistory)
- **`test_services.py`** - Unit tests for all service classes (PortfolioService, PriceService, DataLoader)
- **`test_integration.py`** - Integration tests that verify components work together correctly
- **`test_dashboard_caching.py`** - Tests for dashboard caching logic and zero value detection
- **`test_daily_changes_calculation.py`** - Tests for daily performance change calculations
- **`test_api_endpoints.py`** - Tests for REST API endpoints
- **`test_csv_duplicate_detection.py`** - Tests for CSV import duplicate prevention
- **`conftest.py`** - Pytest configuration and shared fixtures

### Test Categories

#### Model Tests (`test_models.py`)
- **Stock Model**: Creation, validation, unique constraints
- **Portfolio Model**: CRUD operations, timestamps, relationships
- **StockTransaction Model**: Buy/sell transactions, fractional shares, validation
- **Dividend Model**: Dividend tracking, portfolio relationships
- **CashBalance Model**: Cash management, updates, relationships
- **PriceHistory Model**: Price caching, composite keys, data integrity

#### Service Tests (`test_services.py`)
- **PortfolioService**: Portfolio management, transaction processing, performance calculations
- **PriceService**: Price retrieval, caching strategies, API integration
- **DataLoader**: CSV import/export, data validation, backup functionality

#### Integration Tests (`test_integration.py`)
- **Portfolio Integration**: Complete investment workflows
- **Price Service Integration**: Caching and API fallback scenarios
- **Data Loader Integration**: End-to-end import/export processes

#### Dashboard Tests (`test_dashboard_caching.py`)
- **Cache Detection**: Zero value detection and recalculation triggers
- **Market Awareness**: Different caching behavior for market open/closed
- **Fresh Calculations**: Validation of cache bypass scenarios

#### Performance Tests (`test_daily_changes_calculation.py`)
- **Daily Changes**: Portfolio and ETF daily performance calculations
- **Error Handling**: Graceful degradation on calculation failures
- **Data Validation**: Invalid response handling

#### API Tests (`test_api_endpoints.py`)
- **Price Refresh**: Manual price update endpoints
- **Holdings Refresh**: Portfolio holdings update functionality

#### Data Integrity Tests (`test_csv_duplicate_detection.py`)
- **Duplicate Prevention**: CSV import duplicate detection
- **Data Protection**: Portfolio value accuracy protection

## Running Tests

### Prerequisites

Make sure you have all required dependencies installed:

```bash
pip install -r requirements.txt
```

### Quick Start

Run all tests:
```bash
python run_tests.py
```

### Test Categories

Run specific test categories:
```bash
# Model tests only
python run_tests.py --category models

# Service tests only
python run_tests.py --category services

# Integration tests only
python run_tests.py --category integration
```

### Verbose Output

Run tests with detailed output:
```bash
python run_tests.py --verbose
```

### Coverage Reports

Run tests with coverage analysis:
```bash
python run_tests.py --coverage
```

This will generate:
- Terminal coverage report
- HTML coverage report in `htmlcov/` directory

### Specific Tests

Run a specific test file:
```bash
python run_tests.py --specific tests/test_models.py
```

Run a specific test class:
```bash
python run_tests.py --specific tests/test_models.py::TestStock
```

Run a specific test method:
```bash
python run_tests.py --specific tests/test_models.py::TestStock::test_stock_creation
```

### Direct Pytest Usage

You can also run pytest directly:

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific file
pytest tests/test_models.py

# With coverage
pytest --cov=app --cov-report=html

# Stop on first failure
pytest -x

# Run tests matching a pattern
pytest -k "test_stock"
```

## Test Fixtures

The test suite uses comprehensive fixtures defined in `conftest.py`:

### Database Fixtures
- `app` - Test Flask application with temporary database
- `client` - Test client for HTTP requests
- `runner` - CLI test runner

### Data Fixtures
- `sample_user_id` - Test user identifier
- `sample_stock` - Sample AAPL stock record
- `sample_etf_stock` - Sample VOO ETF record
- `sample_portfolio` - Test portfolio
- `sample_transaction` - Sample buy transaction
- `sample_dividend` - Sample dividend payment
- `sample_cash_balance` - Sample cash balance
- `sample_price_history` - Sample price data
- `multiple_transactions` - Multiple transaction records
- `multiple_dividends` - Multiple dividend records

## Test Coverage Statistics

**Current Status: 114 tests, 100% pass rate**

- **Model Tests**: 24 tests
- **Service Tests**: 27 tests  
- **Integration Tests**: 17 tests
- **CSV Upload Tests**: 17 tests
- **Daily Performance Tests**: 6 tests
- **Dashboard Caching Tests**: 4 tests
- **Daily Changes Tests**: 3 tests
- **API Endpoint Tests**: 2 tests
- **CSV Duplicate Tests**: 3 tests
- **Simple Tests**: 11 tests

## Test Data

Tests use realistic but controlled data:

### Stock Data
- **AAPL**: Apple Inc. (Technology sector)
- **GOOGL**: Alphabet Inc. 
- **MSFT**: Microsoft Corporation
- **VOO**: Vanguard S&P 500 ETF
- **QQQ**: Invesco QQQ Trust ETF

### Transaction Data
- Buy/sell transactions with fractional share support
- Realistic price ranges and dates
- Various transaction sizes and types

### Price Data
- Historical price data for performance calculations
- Both intraday and closing prices
- Cache freshness scenarios

## Mocking Strategy

The test suite uses mocking for external dependencies:

### Yahoo Finance API
- Mocked using `unittest.mock.patch`
- Simulates various API responses and failures
- Tests retry logic and error handling

### Database Operations
- Uses temporary SQLite databases
- Automatic cleanup after each test
- Isolated test environments

## Best Practices

### Writing New Tests

1. **Use Descriptive Names**: Test method names should clearly describe what is being tested
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **Use Fixtures**: Leverage existing fixtures for common test data
4. **Mock External Dependencies**: Don't make real API calls in tests
5. **Test Edge Cases**: Include tests for error conditions and boundary cases

### Example Test Structure

```python
def test_descriptive_test_name(self, fixture1, fixture2, app):
    """Test description explaining what this test verifies."""
    with app.app_context():
        # Arrange
        setup_data = create_test_data()
        
        # Act
        result = service_method(setup_data)
        
        # Assert
        assert result.expected_property == expected_value
        assert len(result.collection) == expected_count
```

### Test Organization

- Group related tests in classes
- Use descriptive class names (e.g., `TestPortfolioService`)
- Order tests logically (creation, retrieval, updates, deletion)
- Include both positive and negative test cases

## Continuous Integration

These tests are designed to run in CI/CD environments:

- No external dependencies (mocked APIs)
- Temporary databases (no persistent state)
- Deterministic results
- Fast execution times

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the app module is in your Python path
2. **Database Errors**: Check that SQLite is available and writable
3. **Fixture Errors**: Verify fixture dependencies are correctly defined
4. **Mock Errors**: Ensure mock patches target the correct module paths

### Debug Mode

Run tests with Python debugger:
```bash
pytest --pdb
```

This will drop into the debugger on test failures.

### Logging

Enable debug logging during tests by setting environment variables:
```bash
export FLASK_ENV=testing
export LOG_LEVEL=DEBUG
pytest
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all existing tests still pass
3. Add integration tests for new workflows
4. Update this README if adding new test categories
5. Maintain test coverage above 90%

## Performance

The test suite is optimized for speed:

- Uses in-memory SQLite databases
- Minimal test data creation
- Efficient fixture reuse
- Parallel execution support (with pytest-xdist)

Run tests in parallel:
```bash
pip install pytest-xdist
pytest -n auto
```