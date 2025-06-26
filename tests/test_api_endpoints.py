import pytest
from unittest.mock import patch


@pytest.mark.api
@pytest.mark.slow
class TestAPIEndpoints:
    
    def test_refresh_all_prices_endpoint(self, client, sample_portfolio, app):
        """Test the refresh all prices API endpoint"""
        with app.app_context():
            with patch('app.services.price_service.PriceService.get_current_price') as mock_price:
                mock_price.return_value = 150.00
                
                response = client.get(f'/api/refresh-all-prices/{sample_portfolio.id}')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert 'refreshed_count' in data
                assert 'total_tickers' in data
                assert 'holdings' in data
                assert 'timestamp' in data

    def test_refresh_holdings_endpoint(self, client, sample_portfolio, app):
        """Test the refresh holdings API endpoint"""
        with app.app_context():
            with patch('app.services.price_service.PriceService.get_current_price') as mock_price:
                mock_price.return_value = 150.00
                
                response = client.get(f'/api/refresh-holdings/{sample_portfolio.id}')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert 'holdings' in data
                assert 'timestamp' in data