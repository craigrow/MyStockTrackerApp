"""
Query Cache Decorator

This module provides a decorator for caching expensive database queries.
The cache is an in-memory dictionary with TTL (time-to-live) support.
"""

import functools
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global cache dictionary
_query_cache = {}

def query_cache(ttl_seconds=300):
    """
    Decorator for caching expensive database queries.
    
    Args:
        ttl_seconds (int): Time-to-live in seconds for cached results
        
    Returns:
        Decorated function that uses cache for results
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Check if result is in cache and not expired
            if cache_key in _query_cache:
                result, expiry = _query_cache[cache_key]
                if expiry > datetime.now():
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
                else:
                    # Remove expired entry
                    logger.debug(f"Cache expired for {func.__name__}")
                    del _query_cache[cache_key]
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Only cache if execution time is significant (> 0.1 seconds)
            if execution_time > 0.1:
                expiry = datetime.now() + timedelta(seconds=ttl_seconds)
                _query_cache[cache_key] = (result, expiry)
                logger.debug(f"Cached result for {func.__name__} (execution time: {execution_time:.2f}s)")
            
            return result
        return wrapper
    return decorator

def clear_query_cache():
    """Clear the entire query cache"""
    global _query_cache
    cache_size = len(_query_cache)
    _query_cache = {}
    logger.info(f"Cleared query cache ({cache_size} entries)")
    
def get_cache_stats():
    """Get statistics about the query cache"""
    now = datetime.now()
    total_entries = len(_query_cache)
    active_entries = sum(1 for _, expiry in _query_cache.values() if expiry > now)
    expired_entries = total_entries - active_entries
    
    return {
        'total_entries': total_entries,
        'active_entries': active_entries,
        'expired_entries': expired_entries
    }
