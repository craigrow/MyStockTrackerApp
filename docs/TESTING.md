# Testing Guide for MyStockTrackerApp

This document provides comprehensive guidance for running tests in the MyStockTrackerApp project.

## Quick Start

### Development Testing (Recommended for Local Development)
```bash
# Fast tests only - excludes performance tests
python run_tests.py dev

# Or using pytest directly
python -m pytest -c pytest_dev.ini
```

### Full Test Suite (CI/CD Equivalent)
```bash
# All tests including performance tests
python run_tests.py full

# Or using pytest directly  
python -m pytest -c pytest_ci.ini
```

## Test Categories

Our test suite uses pytest markers to categorize tests:

### **Markers**
- `@pytest.mark.fast` - Unit tests, quick execution
- `@pytest.mark.slow` - Integration tests, longer execution
- `@pytest.mark.performance` - Performance/timing sensitive tests
- `@pytest.mark.ui` - Frontend/UI tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.database` - Database operation tests
- `@pytest.mark.smoke` - Critical path smoke tests

### **Test Types by Performance**

#### Fast Tests (< 1 second each)
- Unit tests for models, services, utilities
- Mock-heavy tests with minimal I/O
- Business logic validation

#### Slow Tests (1-10 seconds each)
- Integration tests with database
- API endpoint tests with real requests
- Multi-component workflow tests

#### Performance Tests (Variable timing)
- Dashboard load time tests
- Chart generation performance
- API response time validation
- **Note**: These tests are environment-sensitive and may fail locally while passing in CI/CD

## Test Execution Options

### Using the Test Runner Script

```bash
# Development mode (excludes performance tests)
python run_tests.py dev

# Fast unit tests only
python run_tests.py fast

# Full test suite (all tests)
python run_tests.py full

# Performance tests only
python run_tests.py performance

# Smoke tests only
python run_tests.py smoke

# CI/CD mode
python run_tests.py ci

# With verbose output
python run_tests.py dev --verbose

# Show slowest test durations
python run_tests.py dev --durations 10
```

### Using Pytest Directly

```bash
# Development tests (no performance tests)
python -m pytest -c pytest_dev.ini

# Full test suite
python -m pytest -c pytest_ci.ini

# Specific markers
python -m pytest -m "fast"
python -m pytest -m "not slow and not performance"
python -m pytest -m "api and not performance"

# Specific test files
python -m pytest tests/test_models.py
python -m pytest tests/integration/

# With timing information
python -m pytest --durations=10

# Parallel execution (if pytest-xdist installed)
python -m pytest -n auto
```

## Performance Test Considerations

### Why Performance Tests May Fail Locally

Performance tests are **environment-sensitive** and may fail on local machines while passing in CI/CD:

1. **Resource Competition**: Local machines run other applications
2. **Network Variability**: Internet connection affects API calls
3. **Hardware Differences**: CPU/memory specs vary between environments
4. **Database Performance**: SQLite performance varies with disk I/O

### CI/CD vs Local Environment

- **GitHub Actions CI/CD**: Dedicated resources, consistent environment
- **Local Development**: Shared resources, variable performance

**Recommendation**: Use development mode (`python run_tests.py dev`) for local development to skip performance tests.

## Test Configuration Files

### pytest_dev.ini
- **Purpose**: Development testing
- **Excludes**: Performance and slow tests
- **Usage**: Daily development workflow
- **Command**: `python -m pytest -c pytest_dev.ini`

### pytest_ci.ini  
- **Purpose**: CI/CD and release testing
- **Includes**: All tests including performance
- **Usage**: Pre-deployment validation
- **Command**: `python -m pytest -c pytest_ci.ini`

### pytest.ini (Default)
- **Purpose**: Standard configuration
- **Includes**: All tests
- **Usage**: Full test suite execution

## Test Organization

```
tests/
├── unit/                          # Fast unit tests
├── integration/                   # Slower integration tests
│   ├── critical_paths/           # Critical functionality tests
│   ├── performance/              # Performance test suites
│   └── edge_cases/               # Edge case scenarios
├── test_*.py                     # Individual test modules
└── utils/                        # Test utilities and helpers
```

## Best Practices

### For Development
1. **Use development mode** for regular testing: `python run_tests.py dev`
2. **Run specific test files** when working on features
3. **Use verbose mode** for debugging: `--verbose`
4. **Check test durations** to identify slow tests: `--durations 10`

### For CI/CD
1. **Always run full test suite** before deployment
2. **Performance tests must pass** in CI/CD environment
3. **100% test pass rate required** for production deployment

### Writing New Tests
1. **Add appropriate markers** to categorize tests
2. **Use `@pytest.mark.performance`** for timing-sensitive tests
3. **Use `@pytest.mark.slow`** for tests taking >1 second
4. **Mock external dependencies** in unit tests
5. **Document test purpose** in docstrings

## Troubleshooting

### Performance Test Failures
If performance tests fail locally but pass in CI/CD:
1. **This is expected behavior** - use development mode
2. **Check system resources** - close other applications
3. **Run individual performance tests** to isolate issues
4. **Focus on functional correctness** in local development

### Common Issues
- **Database locks**: Ensure proper test cleanup
- **Port conflicts**: Check for running Flask instances
- **Import errors**: Verify virtual environment activation
- **Slow tests**: Use development mode to skip them

## Integration with GitHub Actions

Our CI/CD pipeline automatically:
1. **Runs full test suite** (`pytest_ci.ini`)
2. **Requires 100% pass rate** for deployment
3. **Includes performance tests** in validation
4. **Blocks deployment** on test failures

The GitHub Actions environment is optimized for consistent test performance, making it the authoritative environment for performance test validation.

## Summary

- **Development**: `python run_tests.py dev` (fast, no performance tests)
- **Pre-deployment**: `python run_tests.py full` (complete validation)
- **Debugging**: `python run_tests.py dev --verbose --durations 10`
- **CI/CD**: Automatically runs full suite with performance tests

This testing strategy ensures rapid development feedback while maintaining production quality standards.
