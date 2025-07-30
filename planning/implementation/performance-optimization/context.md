# Performance Optimization Context

## Project Overview

MyStockTrackerApp is a web application for tracking stock portfolio performance against market indices. It's built with Python Flask, SQLAlchemy, and uses the Yahoo Finance API (yfinance) for real-time stock data.

## Performance Issues

Based on the logs and code analysis, the main performance issue is an H12 timeout error in the Heroku devQ environment. This occurs because:

1. **Sequential API Processing**: The app makes individual API calls for each ticker, which is slow and inefficient.
2. **Excessive API Call Volume**: The app fetches missing historical data for every ticker on every load.
3. **Chart Data Generation on Critical Path**: Historical price fetching happens synchronously during page load.
4. **Cache Inefficiency**: Cache misses are not handled gracefully.
5. **Holdings Calculation Overhead**: Multiple recalculations during a single request.

## Current Implementation

The current implementation has several performance bottlenecks:

1. In `background_tasks.py`, the `_process_queue` method processes tickers sequentially, making individual API calls for each ticker.
2. In `price_service.py`, there are multiple methods for fetching prices, but they're not optimized for batch processing.
3. In `main.py`, the dashboard route loads all data synchronously, including chart data generation which is computationally expensive.

## Planned Improvements

Based on the performance optimization documents, the following improvements are planned:

1. **Batch API Processing**: Implement efficient batch API calls to reduce the number of API requests.
2. **Async Processing**: Use parallel API requests with threading/asyncio for non-blocking operations.
3. **Background Processing**: Move chart data generation off the critical path.
4. **Smart Caching Strategy**: Implement intelligent caching with market-aware behavior.
5. **Graceful Degradation**: Show cached data with staleness indicators and progressive loading of fresh data.

## Implementation Strategy

1. **Optimize `price_service.py`**:
   - Enhance batch processing capabilities
   - Implement parallel fetching with proper error handling
   - Improve caching mechanisms

2. **Optimize `background_tasks.py`**:
   - Implement batch processing for price updates
   - Add proper error handling and retry logic

3. **Optimize `main.py`**:
   - Move chart data generation to background tasks
   - Implement progressive loading for dashboard
   - Optimize holdings calculation

## Success Criteria

- Dashboard load time reduced from 30+ seconds to 2-3 seconds
- API calls reduced from ~19,690 to <100 per dashboard load
- Cache hit rate improved to >95%
- No H12 timeout errors in Heroku

## Technical Approach

1. **Phase 1: Critical Path Optimization**
   - Implement batch API calls using yfinance batch download
   - Add parallel API requests using threading/asyncio
   - Move chart data generation to background tasks

2. **Phase 2: Caching Improvements**
   - Implement smart cache warming
   - Add graceful degradation with staleness indicators

3. **Phase 3: Architecture Improvements**
   - Optimize database queries
   - Implement edge caching for price data

## Implementation Plan

1. Enhance `price_service.py` with improved batch and parallel processing
2. Update `background_tasks.py` to use the enhanced price service
3. Modify `main.py` to use background processing for chart data
4. Add proper error handling and fallback mechanisms
5. Implement progressive loading for the dashboard

This implementation will focus on the critical path optimization (Phase 1) to address the immediate H12 timeout issue.
