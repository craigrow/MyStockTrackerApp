# Dual Agent Testing Strategy

## Overview
Two AI agents will work simultaneously on this project:
- **Agent Q**: Works on `devQ` branch
- **Agent R**: Works on `devR` branch

## Workflow Requirements

### Before Making Changes
```bash
git checkout devQ  # or devR
git pull origin main
python -m pytest tests/ -v  # Ensure clean starting point
```

### After Making Changes
```bash
python -m pytest tests/ -v  # All tests must pass
git pull origin main         # Get latest changes
python -m pytest tests/ -v  # Ensure no merge conflicts
# Only push to main if all tests pass
```

## Test Strategy Guidelines

### 1. Test Isolation
- Keep test changes minimal and feature-specific
- Avoid modifying shared fixtures in `conftest.py` without coordination
- Use descriptive, non-conflicting test file names:
  - `test_feature_q_*.py` for Agent Q features
  - `test_feature_r_*.py` for Agent R features

### 2. Database Schema Changes
- Test model changes carefully - both agents may modify models
- Run full test suite after any model changes
- Consider migration impacts on existing tests

### 3. Mocking Strategy
- Mock external dependencies, not shared internal services
- Keep mocks isolated to specific test files
- Avoid changing core service interfaces

### 4. Shared Code Modifications
- Communicate breaking changes to shared components
- Test thoroughly when modifying:
  - Models (`app/models/`)
  - Services (`app/services/`)
  - Views (`app/views/`)
  - Templates (`app/templates/`)

## Test Suite Status
- **132 tests passing** ✅
- **0 failures** ✅
- **0 errors** ✅
- Comprehensive coverage of all major components

## Risk Mitigation
1. **Pull frequently** from main to catch conflicts early
2. **Atomic commits** - small, focused changes
3. **Full test runs** after every merge from main
4. **Feature branches** for complex changes if needed

## Emergency Procedures
If tests fail after merging from main:
1. Identify conflicting changes
2. Fix conflicts while maintaining test coverage
3. Coordinate with other agent if shared code affected
4. Re-run full test suite before pushing