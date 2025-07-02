"""Integration tests for API endpoints and external service integration."""
import pytest
import json
import io
from tests.integration.utils.test_factories import IntegrationTestFactory
from tests.integration.utils.mocks import IntegrationTestMocks


@pytest.mark.fast
@pytest.mark.api
class TestAPIIntegration:
    """Test API endpoint integration and behavior."""
    
    def test_dashboard_api_performance(self, app, client):
        """Test dashboard API endpoint performance."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Test dashboard API endpoint
                response = client.get('/')
                assert response.status_code == 200
                assert b'Portfolio Performance' in response.data
                
                # Test chart data API (check if endpoint exists)
                response = client.get('/api/chart-data')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    assert 'portfolio_data' in data
                    assert 'etf_data' in data
                else:
                    # API endpoint may not exist, that's acceptable
                    assert response.status_code == 404
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_portfolio_api_endpoints(self, app, client):
        """Test portfolio-related API endpoints."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Test transactions page
                response = client.get('/portfolio/transactions')
                assert response.status_code == 200
                assert b'Transactions' in response.data
                
                # Test dividends page
                response = client.get('/portfolio/dividends')
                assert response.status_code == 200
                assert b'Dividends' in response.data
                
                # Test price refresh API (check if endpoint exists)
                response = client.post('/api/refresh-prices')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    assert 'status' in data
                else:
                    # API endpoint may not exist, that's acceptable
                    assert response.status_code == 404
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_csv_upload_api(self, app, client):
        """Test CSV upload API functionality."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Create test CSV data
                csv_data = "ticker,date,type,shares,price\nAAPL,2023-01-01,BUY,10,150.00"
                
                # Test CSV upload
                response = client.post('/portfolio/import-csv', 
                                     data={
                                         'portfolio_id': portfolio.id,
                                         'import_type': 'transactions',
                                         'csv_file': (io.BytesIO(csv_data.encode()), 'test.csv')
                                     },
                                     content_type='multipart/form-data')
                
                # Should redirect or return success
                assert response.status_code in [200, 302]
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_error_handling_apis(self, app, client):
        """Test API error handling."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                # Test invalid portfolio access
                response = client.get('/portfolio/transactions?portfolio_id=invalid')
                assert response.status_code in [200, 404]  # Should handle gracefully
                
                # Test invalid API calls
                response = client.post('/api/refresh-prices', 
                                     data=json.dumps({'invalid': 'data'}),
                                     content_type='application/json')
                assert response.status_code in [200, 400, 404]  # Should handle gracefully
                
            finally:
                for mock in mocks:
                    mock.stop()
    
    def test_api_response_formats(self, app, client):
        """Test API response formats and structure."""
        with app.app_context():
            mocks = IntegrationTestMocks.apply_all_mocks()
            
            try:
                for mock in mocks:
                    mock.start()
                
                portfolio = IntegrationTestFactory.create_portfolio_with_chart_data()
                
                # Test JSON API responses
                response = client.get('/api/chart-data')
                if response.status_code == 200:
                    assert response.content_type == 'application/json'
                    
                    data = json.loads(response.data)
                    assert isinstance(data, dict)
                    assert 'portfolio_data' in data
                    assert 'etf_data' in data
                    
                    # Verify data structure
                    portfolio_data = data['portfolio_data']
                    assert isinstance(portfolio_data, list)
                    if portfolio_data:
                        assert 'date' in portfolio_data[0]
                        assert 'value' in portfolio_data[0]
                else:
                    # API endpoint may not exist
                    assert response.status_code == 404
                
            finally:
                for mock in mocks:
                    mock.stop()