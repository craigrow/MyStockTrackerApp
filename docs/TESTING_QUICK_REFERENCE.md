# Testing Quick Reference

## New Test Categories

### Markers Available
- `@pytest.mark.fast` - Unit tests, quick execution
- `@pytest.mark.slow` - Integration tests, longer execution  
- `@pytest.mark.ui` - UI/frontend behavior tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.database` - Tests requiring database operations

## Quick Commands

### Development Workflow (Fast Feedback)
```bash
# Run only fast tests (recommended for development)
python -m pytest -m "fast" -v

# Run fast tests in parallel
python -m pytest -m "fast" -n auto

# Skip slow tests (everything except integration tests)
python -m pytest -m "not slow" -v
```

### Full Test Suite
```bash
# Run all tests (CI/deployment)
python -m pytest -v

# Run all tests in parallel
python -m pytest -n auto
```

### Specific Categories
```bash
# Only UI tests
python -m pytest -m "ui" -v

# Only API tests  
python -m pytest -m "api" -v

# Only database tests
python -m pytest -m "database" -v
```

## Fast Test Runner Script

Use the provided script for development:
```bash
python run_fast_tests.py
```

## Development Workflow

1. **During development**: Run `python -m pytest -m "fast"`
2. **Before commit**: Run `python -m pytest -m "not slow"`  
3. **Before push**: Run full suite `python -m pytest`