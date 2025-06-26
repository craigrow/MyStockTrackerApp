"""Consistent mock configurations for external dependencies."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date


@pytest.fixture(autouse=True)
def mock_yfinance():
    """Mock yfinance API calls consistently across all tests."""
    with patch('yfinance.Ticker') as mock_ticker:
        # Create mock ticker instance
        mock_instance = MagicMock()
        mock_ticker.return_value = mock_instance
        
        # Mock price history data
        mock_history = MagicMock()
        mock_history.iloc = MagicMock()
        mock_history.iloc[-1] = {'Close': 150.00}
        mock_instance.history.return_value = mock_history
        
        # Mock current price info
        mock_info = {
            'regularMarketPrice': 150.00,
            'previousClose': 148.00,
            'shortName': 'Apple Inc.'
        }
        mock_instance.info = mock_info
        
        yield mock_ticker


class MockPriceService:
    """Mock price service for consistent price data."""
    
    @staticmethod
    def get_mock_prices():
        """Return consistent mock price data."""
        return {
            'AAPL': 150.00,
            'GOOGL': 2500.00,
            'MSFT': 300.00,
            'VOO': 400.00,
            'QQQ': 350.00
        }
    
    @staticmethod
    def mock_get_current_price(ticker, use_stale=False):
        """Mock current price lookup with use_stale parameter."""
        prices = MockPriceService.get_mock_prices()
        return prices.get(ticker, 100.00)
    
    @staticmethod
    def mock_get_price_history(ticker, start_date, end_date):
        """Mock price history lookup."""
        base_price = MockPriceService.get_mock_prices().get(ticker, 100.00)
        return [
            {
                'date': start_date,
                'close': base_price * 0.95,
                'ticker': ticker
            },
            {
                'date': end_date,
                'close': base_price,
                'ticker': ticker
            }
        ]


@pytest.fixture
def mock_price_service():
    """Fixture for mocking price service methods."""
    with patch('app.services.price_service.PriceService.get_current_price') as mock_current, \
         patch('app.services.price_service.PriceService.get_price_history') as mock_history:
        
        mock_current.side_effect = MockPriceService.mock_get_current_price
        mock_history.side_effect = MockPriceService.mock_get_price_history
        
        yield {
            'current_price': mock_current,
            'price_history': mock_history
        }


@pytest.fixture
def mock_market_hours():
    """Mock market hours detection."""
    with patch('app.util.calculators.is_market_open_now') as mock_market:
        mock_market.return_value = False  # Default to market closed
        yield mock_market


class MockAPIResponses:
    """Mock API response data."""
    
    @staticmethod
    def get_refresh_response(portfolio_id, ticker_count=2):
        """Mock refresh API response."""
        return {
            'success': True,
            'refreshed_count': ticker_count,
            'total_tickers': ticker_count,
            'holdings': [
                {'ticker': 'AAPL', 'current_price': 150.00},
                {'ticker': 'GOOGL', 'current_price': 2500.00}
            ][:ticker_count],
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def get_etf_performance_response(ticker, purchase_date, performance=5.0):
        """Mock ETF performance API response."""
        return {
            'ticker': ticker,
            'purchase_date': purchase_date.strftime('%Y-%m-%d') if isinstance(purchase_date, date) else purchase_date,
            'purchase_price': 400.00,
            'current_price': 420.00,
            'performance': performance,
            'success': True
        }