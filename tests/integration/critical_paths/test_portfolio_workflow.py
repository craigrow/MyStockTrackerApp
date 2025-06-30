"""Critical path tests for complete portfolio workflows."""
import pytest
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.performance_helpers import PerformanceValidator
from tests.integration.utils.assertion_helpers import ChartAssertions, ResponseAssertions


@pytest.mark.fast
@pytest.mark.database
class TestPortfolioWorkflow:
    """Critical tests for complete user workflows that must never break."""
    
    def test_complete_user_workflow_end_to_end(self, app, client):
        """CRITICAL: Complete workflow from portfolio creation to chart visualization.
        
        This test validates the entire user journey that must always work.
        """
        with app.app_context():
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
    
    def test_portfolio_switching_workflow(self, app, client):
        """CRITICAL: User can switch between portfolios without issues."""
        with app.app_context():
            # Arrange: Create multiple portfolios
            portfolios = IntegrationTestFactory.create_multi_portfolio_scenario()
            
            # Act & Assert: Test switching between portfolios
            load_times = []
            for i, portfolio in enumerate(portfolios):
                # Load each portfolio dashboard
                result = PerformanceValidator.measure_dashboard_load_time(client, portfolio.id)
                
                # Assert: Each portfolio loads successfully
                ResponseAssertions.assert_response_success(result['response'])
                ChartAssertions.assert_chart_data_valid(result['response'])
                
                # Track performance across switches
                load_times.append(result['load_time'])
                
                # Assert: Performance doesn't degrade with switching
                PerformanceValidator.assert_performance_requirements(
                    result['load_time'],
                    max_time=3.0,
                    context=f"Portfolio switch #{i+1} ({portfolio.name})"
                )
            
            # Assert: Performance is consistent across portfolio switches
            avg_load_time = sum(load_times) / len(load_times)
            max_load_time = max(load_times)
            
            assert max_load_time < 3.0, (
                f"Maximum load time {max_load_time:.2f}s exceeds 3.0s requirement"
            )
            
            # Log performance metrics
            PerformanceValidator.log_performance_metrics(
                {
                    'average_load_time': avg_load_time,
                    'max_load_time': max_load_time,
                    'portfolio_count': len(portfolios)
                },
                'Portfolio Switching Workflow'
            )
    
    def test_price_refresh_workflow(self, app, client):
        """CRITICAL: Price refresh workflow maintains chart functionality."""
        with app.app_context():
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
            
            # Step 3: Refresh all prices (including ETFs)
            all_prices_refresh = PerformanceValidator.measure_api_response_time(
                client, f'/api/refresh-all-prices/{portfolio.id}'
            )
            ResponseAssertions.assert_response_success(all_prices_refresh['response'])
            
            # Step 4: Verify dashboard still works after refresh
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
    
    def test_empty_to_populated_portfolio_workflow(self, app, client):
        """CRITICAL: Portfolio workflow from empty state to populated with chart."""
        with app.app_context():
            # Step 1: Create empty portfolio
            from app.models.portfolio import Portfolio
            from app import db
            
            empty_portfolio = Portfolio(
                name="Initially Empty Portfolio",
                description="Portfolio that starts empty",
                user_id="test_user"
            )
            db.session.add(empty_portfolio)
            db.session.commit()
            
            # Step 2: Load empty portfolio dashboard
            empty_result = PerformanceValidator.measure_dashboard_load_time(client, empty_portfolio.id)
            ResponseAssertions.assert_response_success(empty_result['response'])
            ResponseAssertions.assert_no_errors_in_response(empty_result['response'])
            
            # Step 3: Add transaction data (simulating user adding stocks)
            from app.models.portfolio import StockTransaction
            from app.models.stock import Stock
            from datetime import date
            
            # Create stock if it doesn't exist
            stock = Stock(ticker="AAPL", name="Apple Inc.", sector="Technology")
            db.session.merge(stock)
            
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=empty_portfolio.id,
                ticker="AAPL",
                transaction_type="BUY",
                date=date(2023, 1, 15),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Step 4: Load populated portfolio dashboard
            populated_result = PerformanceValidator.measure_dashboard_load_time(client, empty_portfolio.id)
            ResponseAssertions.assert_response_success(populated_result['response'])
            ChartAssertions.assert_chart_data_valid(populated_result['response'])
            
            # Assert: Performance maintained in both states
            PerformanceValidator.assert_performance_requirements(
                empty_result['load_time'],
                max_time=3.0,
                context="Empty portfolio dashboard"
            )
            PerformanceValidator.assert_performance_requirements(
                populated_result['load_time'],
                max_time=3.0,
                context="Populated portfolio dashboard"
            )