"""Critical path tests for dashboard and chart functionality."""
import pytest
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.performance_helpers import PerformanceValidator
from tests.integration.utils.assertion_helpers import ChartAssertions, ResponseAssertions
from tests.integration.utils.mocks import IntegrationTestMocks


@pytest.mark.database
class TestDashboardChart:
    """Critical tests for dashboard and chart functionality that must never break."""
    
    @pytest.mark.performance
    def test_dashboard_loads_with_working_chart(self, app, client):
        """CRITICAL: Dashboard must load with functional chart in <3 seconds.
        
        This test would have prevented the chart rollback issue.
        """
        with app.app_context():
            # Apply performance mocks to avoid slow API calls
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio with chart data
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Act: Load dashboard and measure performance
                result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                
                # Assert: Dashboard loads successfully with chart
                ResponseAssertions.assert_response_success(result['response'])
                ChartAssertions.assert_chart_data_valid(result['response'])
                ChartAssertions.assert_dashboard_elements_present(result['response'].get_data(as_text=True))
                
                # Assert: Performance requirement met
                PerformanceValidator.assert_performance_requirements(
                    result['load_time'], 
                    max_time=3.0, 
                    context="Dashboard load"
                )
                
                # Log performance metrics
                PerformanceValidator.log_performance_metrics(
                    {'dashboard_load_time': result['load_time']},
                    'Dashboard Chart Load Test'
                )
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_chart_lines_start_same_value_regression(self, app, client):
        """REGRESSION: Chart lines must start at same value.
        
        This is the exact test that would have caught the chart rollback bug.
        """
        with app.app_context():
            # Apply performance mocks
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio with specific purchase date
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Act: Get chart data via API
                response = client.get(f'/api/refresh-holdings/{portfolio.id}')
                
                # Assert: API responds successfully
                ResponseAssertions.assert_response_success(response)
                
                # Assert: Chart data is valid and lines would start at same value
                ChartAssertions.assert_chart_lines_start_same_value(response.get_json())
                
                # Additional validation: Check dashboard HTML
                dashboard_response = client.get(f'/?portfolio_id={portfolio.id}')
                ResponseAssertions.assert_response_success(dashboard_response)
                ChartAssertions.assert_chart_lines_start_same_value(
                    dashboard_response.get_data(as_text=True)
                )
            finally:
                for mock in mocks:
                    mock.stop()
    
    @pytest.mark.performance
    def test_chart_api_endpoints_performance(self, app, client):
        """CRITICAL: Chart-related API endpoints perform within requirements."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio for API testing
                portfolio = IntegrationTestFactory.create_performance_test_data()
                
                # Act: Test chart-related API endpoints
                api_results = PerformanceValidator.validate_chart_generation_speed(client, portfolio.id)
                
                # Assert: All API endpoints respond successfully and quickly
                for endpoint, result in api_results.items():
                    if 'error' not in result:
                        ResponseAssertions.assert_response_success(result['response'])
                        assert result['is_fast'], (
                            f"API endpoint {endpoint} took {result['response_time']:.2f}s, "
                            f"exceeding 1.0s requirement"
                        )
                
                # Log API performance metrics
                metrics = {endpoint: result.get('response_time', 0) for endpoint, result in api_results.items()}
                PerformanceValidator.log_performance_metrics(
                    metrics,
                    'Chart API Performance Test'
                )
            finally:
                for mock in mocks:
                    mock.stop()