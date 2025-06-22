import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from app.views.main import calculate_daily_changes, calculate_etf_daily_change_for_portfolio, calculate_portfolio_daily_change
from app.models.price import PriceHistory


class TestDailyPerformance:
    
    @pytest.fixture
    def sample_portfolio_id(self, app, sample_user_id):
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            portfolio_service = PortfolioService()
            portfolio = portfolio_service.create_portfolio(
                name="Daily Performance Test Portfolio",
                user_id=sample_user_id
            )
            return portfolio.id

    @pytest.fixture
    def mock_price_data(self, app):
        """Create mock price data for testing"""
        with app.app_context():
            from app import db
            
            from datetime import datetime
            
            # Create price records for testing
            prices = [
                # VOO prices
                PriceHistory(ticker='VOO', date=date(2025, 6, 20), close_price=547.72, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='VOO', date=date(2025, 6, 18), close_price=549.24, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                # QQQ prices  
                PriceHistory(ticker='QQQ', date=date(2025, 6, 20), close_price=526.83, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='QQQ', date=date(2025, 6, 18), close_price=528.99, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                # Sample stock prices
                PriceHistory(ticker='AAPL', date=date(2025, 6, 20), close_price=220.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='AAPL', date=date(2025, 6, 18), close_price=225.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='MSFT', date=date(2025, 6, 20), close_price=450.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
                PriceHistory(ticker='MSFT', date=date(2025, 6, 18), close_price=455.00, is_intraday=False, price_timestamp=datetime.now(), last_updated=datetime.now()),
            ]
            
            for price in prices:
                db.session.add(price)
            db.session.commit()
            
            yield prices
            
            # Cleanup
            for price in prices:
                db.session.delete(price)
            db.session.commit()

    def test_etf_daily_change_calculation(self, app, mock_price_data, sample_portfolio_id):
        """Test ETF daily change calculation with mock data"""
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            from app.services.price_service import PriceService
            
            portfolio_service = PortfolioService()
            price_service = PriceService()
            
            # Mock the ETF equivalent calculation
            with patch('app.views.main.calculate_current_etf_equivalent') as mock_etf_equiv:
                mock_etf_equiv.return_value = 100000  # $100k equivalent
                
                # Mock the date functions
                with patch('app.views.main.get_last_market_date') as mock_last_date, \
                     patch('app.views.main.get_previous_trading_day') as mock_prev_date:
                    
                    mock_last_date.return_value = date(2025, 6, 20)
                    mock_prev_date.return_value = date(2025, 6, 18)
                    
                    # Test VOO calculation
                    voo_result = calculate_etf_daily_change_for_portfolio('VOO', sample_portfolio_id, portfolio_service, price_service)
                    
                    # VOO: 547.72 vs 549.24 = -1.52 / 549.24 = -0.277% 
                    # On $100k = -$277
                    assert isinstance(voo_result, dict)
                    assert 'percentage' in voo_result
                    assert 'dollar' in voo_result
                    assert abs(voo_result['percentage'] - (-0.277)) < 0.01  # Allow small rounding differences
                    assert abs(voo_result['dollar'] - (-277)) < 5  # Allow small rounding differences

    def test_portfolio_daily_change_calculation(self, app, mock_price_data, sample_portfolio_id):
        """Test portfolio daily change calculation"""
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            from app.services.price_service import PriceService
            
            portfolio_service = PortfolioService()
            price_service = PriceService()
            
            # Add some test transactions
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio_id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 6, 15),
                price_per_share=225.00,
                shares=10
            )
            
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio_id,
                ticker='MSFT',
                transaction_type='BUY',
                date=date(2025, 6, 15),
                price_per_share=455.00,
                shares=5
            )
            
            # Mock the date functions
            with patch('app.views.main.get_last_market_date') as mock_last_date, \
                 patch('app.views.main.get_previous_trading_day') as mock_prev_date:
                
                mock_last_date.return_value = date(2025, 6, 20)
                mock_prev_date.return_value = date(2025, 6, 18)
                
                result = calculate_portfolio_daily_change(
                    sample_portfolio_id, 
                    date(2025, 6, 20), 
                    date(2025, 6, 18), 
                    portfolio_service, 
                    price_service
                )
                
                # Portfolio value on 6/20: AAPL(10 * 220) + MSFT(5 * 450) = 2200 + 2250 = 4450
                # Portfolio value on 6/18: AAPL(10 * 225) + MSFT(5 * 455) = 2250 + 2275 = 4525
                # Change: 4450 - 4525 = -75, percentage: -75/4525 = -1.66%
                
                assert isinstance(result, dict)
                assert 'percentage' in result
                assert 'dollar' in result
                assert abs(result['dollar'] - (-75)) < 1
                assert abs(result['percentage'] - (-1.66)) < 0.1

    def test_calculate_daily_changes_integration(self, app, mock_price_data, sample_portfolio_id):
        """Test the full daily changes calculation integration"""
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            from app.services.price_service import PriceService
            
            portfolio_service = PortfolioService()
            price_service = PriceService()
            
            # Add test transaction
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio_id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 6, 15),
                price_per_share=225.00,
                shares=100
            )
            
            # Mock ETF equivalent calculations
            with patch('app.views.main.calculate_current_etf_equivalent') as mock_etf_equiv:
                mock_etf_equiv.side_effect = lambda pid, ps, prs, ticker: 50000 if ticker == 'VOO' else 45000
                
                # Mock date functions
                with patch('app.views.main.get_last_market_date') as mock_last_date, \
                     patch('app.views.main.get_previous_trading_day') as mock_prev_date:
                    
                    mock_last_date.return_value = date(2025, 6, 20)
                    mock_prev_date.return_value = date(2025, 6, 18)
                    
                    result = calculate_daily_changes(sample_portfolio_id, portfolio_service, price_service)
                    
                    # Verify all required keys are present
                    required_keys = [
                        'voo_daily_change', 'voo_daily_dollar_change',
                        'qqq_daily_change', 'qqq_daily_dollar_change', 
                        'portfolio_daily_change', 'portfolio_daily_dollar_change'
                    ]
                    
                    for key in required_keys:
                        assert key in result, f"Missing key: {key}"
                        assert isinstance(result[key], (int, float)), f"Invalid type for {key}: {type(result[key])}"

    def test_dashboard_stats_include_daily_changes(self, app, mock_price_data, sample_portfolio_id):
        """Test that dashboard portfolio stats include daily changes"""
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            from app.services.price_service import PriceService
            from app.views.main import calculate_portfolio_stats
            
            portfolio_service = PortfolioService()
            price_service = PriceService()
            portfolio = portfolio_service.get_portfolio(sample_portfolio_id)
            
            # Add test transaction
            portfolio_service.add_transaction(
                portfolio_id=sample_portfolio_id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2025, 6, 15),
                price_per_share=225.00,
                shares=10
            )
            
            # Mock dependencies
            with patch('app.views.main.calculate_current_etf_equivalent') as mock_etf_equiv, \
                 patch('app.views.main.get_last_market_date') as mock_last_date, \
                 patch('app.views.main.get_previous_trading_day') as mock_prev_date:
                
                mock_etf_equiv.return_value = 25000
                mock_last_date.return_value = date(2025, 6, 20)
                mock_prev_date.return_value = date(2025, 6, 18)
                
                stats = calculate_portfolio_stats(portfolio, portfolio_service, price_service)
                
                # Verify daily changes are included in stats
                daily_change_keys = [
                    'voo_daily_change', 'voo_daily_dollar_change',
                    'qqq_daily_change', 'qqq_daily_dollar_change',
                    'portfolio_daily_change', 'portfolio_daily_dollar_change'
                ]
                
                for key in daily_change_keys:
                    assert key in stats, f"Daily change key missing from portfolio stats: {key}"

    def test_missing_price_data_handling(self, app, sample_portfolio_id):
        """Test handling when price data is missing"""
        with app.app_context():
            from app.services.portfolio_service import PortfolioService
            from app.services.price_service import PriceService
            
            portfolio_service = PortfolioService()
            price_service = PriceService()
            
            # Mock date functions to return dates with no price data
            with patch('app.views.main.get_last_market_date') as mock_last_date, \
                 patch('app.views.main.get_previous_trading_day') as mock_prev_date:
                
                mock_last_date.return_value = date(2025, 12, 25)  # Christmas - no data
                mock_prev_date.return_value = date(2025, 12, 24)  # Christmas Eve - no data
                
                result = calculate_daily_changes(sample_portfolio_id, portfolio_service, price_service)
                
                # Should return zeros when no price data available
                assert result['voo_daily_change'] == 0
                assert result['voo_daily_dollar_change'] == 0
                assert result['qqq_daily_change'] == 0
                assert result['qqq_daily_dollar_change'] == 0
                assert result['portfolio_daily_change'] == 0
                assert result['portfolio_daily_dollar_change'] == 0

    def test_previous_trading_day_detection(self, app, mock_price_data):
        """Test that previous trading day detection works correctly"""
        with app.app_context():
            from app.views.main import get_previous_trading_day
            
            # Test normal case - should find 6/18 when looking before 6/20
            result = get_previous_trading_day(date(2025, 6, 20))
            assert result == date(2025, 6, 18)
            
            # Test when no price data exists
            result = get_previous_trading_day(date(2025, 1, 1))
            # Should fall back to simple date calculation
            expected = date(2024, 12, 31)
            while expected.weekday() >= 5:  # Skip weekends
                expected -= timedelta(days=1)
            assert result == expected