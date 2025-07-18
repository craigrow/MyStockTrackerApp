#!/usr/bin/env python3

import pytest
from datetime import date
from unittest.mock import Mock, patch
import pandas as pd
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import the fixed service
from app.services.etf_comparison_service import ETFComparisonService

def test_etf_dividend_shares_calculation():
    """Test that dividend calculations use correct share quantities at each date"""
    
    # Create the service
    etf_service = ETFComparisonService()
    
    # Mock the price service
    mock_price_service = Mock()
    mock_price_service.get_cached_price.side_effect = lambda ticker, date_val: {
        ('VOO', date(2022, 5, 20)): 350.0,
        ('VOO', date(2022, 6, 29)): 360.0,
    }.get((ticker, date_val), 370.0)
    mock_price_service.get_current_price.return_value = 380.0
    
    etf_service.price_service = mock_price_service
    
    # Create test data that matches your example
    # Purchase of 0.0177 shares on 5/20/2022
    existing_cash_flows = [
        {
            'date': date(2022, 5, 20),
            'flow_type': 'PURCHASE',
            'amount': -6.195,  # 0.0177 shares * $350 = $6.195
            'description': '0.0177 shares @ $350.00',
            'shares': 0.0177,
            'price_per_share': 350.0,
            'running_balance': 0.0
        }
    ]
    
    # Mock dividend data - $1.43 per share on 6/29/2022
    dividend_data = {
        pd.Timestamp('2022-06-29'): 1.43,
    }
    mock_dividends = pd.Series(dividend_data)
    
    # Mock deposits
    deposits = [
        {'date': date(2022, 5, 20), 'amount': 6.195, 'flow_type': 'DEPOSIT'}
    ]
    
    # Test the calculation
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.dividends = mock_dividends
        
        # Get dividend flows
        dividend_flows = etf_service._get_etf_dividend_flows('VOO', deposits, existing_cash_flows)
        
        # Should have 2 flows: the dividend and the reinvestment
        assert len(dividend_flows) == 2
        
        # Check the dividend flow
        dividend_flow = dividend_flows[0]
        assert dividend_flow['flow_type'] == 'DIVIDEND'
        assert dividend_flow['date'] == date(2022, 6, 29)
        
        # The key check: shares should be 0.0177, not 161.9805
        assert dividend_flow['shares'] == 0.0177
        
        # Amount should be $1.43 * 0.0177 = $0.025311
        expected_amount = 1.43 * 0.0177
        assert round(dividend_flow['amount'], 6) == round(expected_amount, 6)
        
        # Check the reinvestment flow
        reinvest_flow = dividend_flows[1]
        assert reinvest_flow['flow_type'] == 'PURCHASE'
        assert reinvest_flow['date'] == date(2022, 6, 29)
        
        # Reinvested amount should match the dividend amount
        assert abs(reinvest_flow['amount']) == dividend_flow['amount']
        
        # Reinvested shares should be dividend amount / price
        expected_reinvest_shares = dividend_flow['amount'] / 360.0
        assert round(reinvest_flow['shares'], 8) == round(expected_reinvest_shares, 8)

if __name__ == "__main__":
    test_etf_dividend_shares_calculation()
    print("All tests passed!")
