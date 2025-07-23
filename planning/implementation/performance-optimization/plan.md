# Performance Optimization Implementation Plan

## Overview

This plan outlines the steps to implement performance optimizations for MyStockTrackerApp to address the H12 timeout error in the Heroku devQ environment. The primary goal is to reduce dashboard load time from 30+ seconds to 2-3 seconds by optimizing API calls, implementing batch processing, and improving caching mechanisms.

## Test Scenarios

### 1. Batch API Processing Tests

1. **Test Case**: `test_batch_fetch_prices`
   - **Input**: List of tickers
   - **Expected Output**: Dictionary of ticker:price_dataframe pairs
   - **Validation**: Verify that all tickers have price data

2. **Test Case**: `test_batch_fetch_current_prices`
   - **Input**: List of tickers
   - **Expected Output**: Dictionary of ticker:current_price pairs
   - **Validation**: Verify that all tickers have current prices

3. **Test Case**: `test_fetch_prices_parallel`
   - **Input**: List of tickers
   - **Expected Output**: Dictionary of ticker:price_dataframe pairs
   - **Validation**: Verify that all tickers have price data and execution time is faster than sequential processing

### 2. Background Processing Tests

1. **Test Case**: `test_background_price_updater_batch_processing`
   - **Input**: Portfolio ID
   - **Expected Output**: Updated price data in database
   - **Validation**: Verify that all tickers in the portfolio have updated prices

2. **Test Case**: `test_background_chart_data_generation`
   - **Input**: Portfolio ID
   - **Expected Output**: Chart data generated in background
   - **Validation**: Verify that chart data is available after background processing completes

### 3. Caching Tests

1. **Test Case**: `test_cache_hit_rate`
   - **Input**: List of tickers
   - **Expected Output**: Cache hit rate > 95%
   - **Validation**: Verify that most price requests are served from cache

2. **Test Case**: `test_cache_staleness_handling`
   - **Input**: Stale cache data
   - **Expected Output**: Proper staleness indicators
   - **Validation**: Verify that stale data is properly identified and handled

### 4. Dashboard Loading Tests

1. **Test Case**: `test_dashboard_load_time`
   - **Input**: Portfolio ID
   - **Expected Output**: Dashboard loads in < 3 seconds
   - **Validation**: Measure time from request to complete response

2. **Test Case**: `test_progressive_loading`
   - **Input**: Portfolio ID
   - **Expected Output**: Initial dashboard loads quickly, followed by progressive data updates
   - **Validation**: Verify that initial load is fast and subsequent data updates occur in background

## Implementation Tasks

### 1. Enhance Price Service

1. **Optimize `batch_fetch_prices` method**:
   - Implement efficient batch processing using yfinance
   - Add proper error handling and retry logic
   - Optimize caching of batch results

2. **Implement `fetch_prices_parallel` method**:
   - Use asyncio and ThreadPoolExecutor for parallel processing
   - Add chunking to avoid overwhelming the API
   - Implement proper error handling and timeout management

3. **Enhance caching mechanisms**:
   - Implement market-aware caching strategy
   - Add cache staleness detection
   - Implement graceful fallback to cached data

### 2. Optimize Background Tasks

1. **Update `BackgroundPriceUpdater` class**:
   - Implement batch processing for price updates
   - Add progress tracking and status reporting
   - Implement proper error handling and retry logic

2. **Implement `BackgroundChartGenerator` class**:
   - Move chart data generation to background tasks
   - Add progress tracking and status reporting
   - Implement caching of generated chart data

### 3. Optimize Dashboard Loading

1. **Update dashboard route**:
   - Implement progressive loading
   - Use cached data for initial load
   - Trigger background updates for fresh data

2. **Optimize holdings calculation**:
   - Reduce redundant calculations
   - Implement caching for expensive calculations
   - Add proper error handling and fallback mechanisms

### 4. Implement API Endpoints for Progressive Loading

1. **Create `/api/dashboard-initial-data` endpoint**:
   - Return minimal data needed for initial dashboard rendering
   - Use cached data whenever possible

2. **Create `/api/dashboard-chart-data` endpoint**:
   - Return chart data asynchronously
   - Use cached data or trigger background generation

3. **Create `/api/dashboard-holdings-data` endpoint**:
   - Return holdings data asynchronously
   - Use cached data or trigger background updates

## Implementation Approach

1. **Phase 1: Critical Path Optimization**
   - Implement batch API processing in `price_service.py`
   - Update `background_tasks.py` to use batch processing
   - Modify dashboard route to use progressive loading

2. **Phase 2: Background Processing**
   - Implement `BackgroundChartGenerator` class
   - Move chart data generation off the critical path
   - Add API endpoints for progressive loading

3. **Phase 3: Caching Improvements**
   - Enhance caching mechanisms in `price_service.py`
   - Implement market-aware caching strategy
   - Add cache staleness detection and handling

## Success Metrics

- Dashboard load time reduced to < 3 seconds
- API calls reduced to < 100 per dashboard load
- Cache hit rate improved to > 95%
- No H12 timeout errors in Heroku

## Rollback Plan

If the performance optimizations cause issues:

1. Revert changes to `price_service.py`
2. Revert changes to `background_tasks.py`
3. Revert changes to `main.py`
4. Deploy the reverted code to restore functionality
