"""Performance measurement utilities for integration tests."""
import time
from contextlib import contextmanager


class PerformanceValidator:
    """Utilities for measuring and validating performance."""
    
    @staticmethod
    @contextmanager
    def measure_time():
        """Context manager to measure execution time."""
        start_time = time.time()
        yield lambda: time.time() - start_time
        
    @staticmethod
    def measure_dashboard_load_time(client, portfolio_id=None):
        """Measure dashboard load time and validate performance."""
        url = f"/?portfolio_id={portfolio_id}" if portfolio_id else "/"
        
        with PerformanceValidator.measure_time() as get_time:
            response = client.get(url)
        
        load_time = get_time()
        
        return {
            'response': response,
            'load_time': load_time,
            'meets_requirement': load_time < 3.0  # 3 second requirement
        }
    
    @staticmethod
    def measure_api_response_time(client, endpoint):
        """Measure API endpoint response time."""
        with PerformanceValidator.measure_time() as get_time:
            response = client.get(endpoint)
        
        response_time = get_time()
        
        return {
            'response': response,
            'response_time': response_time,
            'is_fast': response_time < 1.0  # 1 second for API calls
        }
    
    @staticmethod
    def validate_chart_generation_speed(client, portfolio_id):
        """Validate chart data generation performance."""
        # Test chart data endpoint if it exists
        chart_endpoints = [
            f"/api/refresh-holdings/{portfolio_id}",
            f"/api/refresh-all-prices/{portfolio_id}"
        ]
        
        results = {}
        for endpoint in chart_endpoints:
            try:
                result = PerformanceValidator.measure_api_response_time(client, endpoint)
                results[endpoint] = result
            except Exception as e:
                results[endpoint] = {'error': str(e)}
        
        return results
    
    @staticmethod
    def assert_performance_requirements(load_time, max_time=3.0, context="operation"):
        """Assert that performance meets requirements."""
        assert load_time < max_time, (
            f"{context} took {load_time:.2f}s, exceeding {max_time}s requirement. "
            f"This indicates a performance regression."
        )
    
    @staticmethod
    def log_performance_metrics(metrics, test_name):
        """Log performance metrics for monitoring."""
        print(f"\n=== Performance Metrics for {test_name} ===")
        for key, value in metrics.items():
            if isinstance(value, dict) and 'load_time' in value:
                print(f"{key}: {value['load_time']:.3f}s")
            elif isinstance(value, (int, float)):
                print(f"{key}: {value:.3f}s")
        print("=" * (len(test_name) + 35))