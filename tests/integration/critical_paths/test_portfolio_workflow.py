"""Critical path tests for complete portfolio workflows."""
import pytest
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.performance_helpers import PerformanceValidator
from tests.integration.utils.assertion_helpers import ChartAssertions, ResponseAssertions
from tests.integration.utils.mocks import IntegrationTestMocks


@pytest.mark.fast
@pytest.mark.database
class TestPortfolioWorkflow:
    """Critical tests for complete user workflows that must never break."""
    
    def test_complete_user_workflow_end_to_end(self, app, client):
        """CRITICAL: Complete workflow from portfolio creation to chart visualization.
        
        This test validates the entire user journey that must always work.
        """
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Step 1: Create portfolio (simulating user creation)
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data(
                    name="End-to-End Test Portfolio"
                )
                
                # Step 2: Verify portfolio creation was successful
                assert portfolio.id is not None, "Portfolio should be created with valid ID"
                assert portfolio.name == "End-to-End Test Portfolio", "Portfolio should have correct name"
                
                # Step 3: Load dashboard - this is the critical user journey
                result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                
                # Assert: Dashboard loads successfully
                ResponseAssertions.assert_response_success(result['response'])
                ChartAssertions.assert_chart_data_valid(result['response'])
                
                # Step 4: Verify chart functionality
                html_content = result['response'].get_data(as_text=True)
                ChartAssertions.assert_dashboard_elements_present(html_content)
                ChartAssertions.assert_chart_lines_start_same_value(html_content)
                
                # Step 5: Test price refresh functionality
                refresh_response = client.get(f'/api/refresh-holdings/{portfolio.id}')
                ResponseAssertions.assert_response_success(refresh_response)
                
                # Step 6: Verify updated dashboard still works
                updated_result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                ResponseAssertions.assert_response_success(updated_result['response'])
                
                # Assert: Performance maintained throughout workflow
                PerformanceValidator.assert_performance_requirements(
                    result['load_time'],
                    max_time=3.0,
                    context="Initial dashboard load"
                )
                PerformanceValidator.assert_performance_requirements(
                    updated_result['load_time'],
                    max_time=3.0,
                    context="Dashboard load after refresh"
                )
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_price_refresh_workflow(self, app, client):
        """CRITICAL: Price refresh workflow maintains chart functionality."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Arrange: Create portfolio with price data
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Step 1: Initial dashboard load
                initial_result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                ResponseAssertions.assert_response_success(initial_result['response'])
                
                # Step 2: Refresh holdings prices
                holdings_refresh = PerformanceValidator.measure_api_response_time(
                    client, f'/api/refresh-holdings/{portfolio.id}'
                )
                ResponseAssertions.assert_response_success(holdings_refresh['response'])
                
                # Step 3: Verify dashboard still works after refresh
                post_refresh_result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                ResponseAssertions.assert_response_success(post_refresh_result['response'])
                ChartAssertions.assert_chart_data_valid(post_refresh_result['response'])
                
                # Assert: Chart lines still start at same value after refresh
                ChartAssertions.assert_chart_lines_start_same_value(
                    post_refresh_result['response'].get_data(as_text=True)
                )
                
                # Assert: Performance maintained throughout refresh workflow
                PerformanceValidator.assert_performance_requirements(
                    initial_result['load_time'],
                    max_time=3.0,
                    context="Pre-refresh dashboard load"
                )
                PerformanceValidator.assert_performance_requirements(
                    post_refresh_result['load_time'],
                    max_time=3.0,
                    context="Post-refresh dashboard load"
                )
            finally:
                for mock in mocks:
                    mock.stop()