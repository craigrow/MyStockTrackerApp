from app.services.cash_flow_service import CashFlowService
from app.services.price_service import PriceService
from app.services.irr_calculation_service import IRRCalculationService
from datetime import date
import yfinance as yf


class ETFComparisonService:
    
    def __init__(self):
        self.cash_flow_service = CashFlowService()
        self.price_service = PriceService()
        self.irr_service = IRRCalculationService()
    
    def get_etf_cash_flows(self, portfolio_id, etf_ticker):
        """Generate ETF cash flows based on portfolio deposits with real prices"""
        # Get portfolio cash flows (deposits only)
        portfolio_cash_flows = self.cash_flow_service.generate_cash_flows(portfolio_id)
        deposits = [cf for cf in portfolio_cash_flows if cf['flow_type'] == 'DEPOSIT']
        
        if not deposits:
            return []
        
        # Convert deposits to ETF purchases with real prices
        etf_cash_flows = []
        total_shares = 0.0
        
        for deposit in deposits:
            # Get ETF price on deposit date
            etf_price = self.price_service.get_cached_price(etf_ticker, deposit['date'])
            if not etf_price:
                # Fallback to current price if historical not available
                etf_price = self.price_service.get_current_price(etf_ticker)
            
            if etf_price:
                shares_purchased = deposit['amount'] / etf_price
                total_shares += shares_purchased
                
                etf_cash_flows.append({
                    'date': deposit['date'],
                    'flow_type': 'PURCHASE',
                    'amount': -deposit['amount'],
                    'description': f'{shares_purchased:.4f} shares @ ${etf_price:.2f}',
                    'shares': shares_purchased,
                    'price_per_share': etf_price,
                    'running_balance': 0.0
                })
        
        # Add dividend cash flows with reinvestment
        dividend_flows = self._get_etf_dividend_flows(etf_ticker, deposits, total_shares)
        for div_flow in dividend_flows:
            # Add dividend payment with per-share info
            div_per_share = div_flow['amount'] / total_shares if total_shares > 0 else 0
            div_flow['shares'] = total_shares
            div_flow['price_per_share'] = div_per_share
            etf_cash_flows.append(div_flow)
            
            # Add immediate reinvestment
            div_price = self.price_service.get_cached_price(etf_ticker, div_flow['date'])
            if not div_price:
                div_price = self.price_service.get_current_price(etf_ticker)
            
            if div_price and div_flow['amount'] > 0:
                reinvest_shares = div_flow['amount'] / div_price
                total_shares += reinvest_shares
                
                etf_cash_flows.append({
                    'date': div_flow['date'],
                    'flow_type': 'PURCHASE',
                    'amount': -div_flow['amount'],  # Negative for purchase
                    'description': f'{reinvest_shares:.4f} shares @ ${div_price:.2f} (dividend reinvestment)',
                    'shares': reinvest_shares,
                    'price_per_share': div_price,
                    'running_balance': 0.0
                })
        
        # Sort by date
        etf_cash_flows.sort(key=lambda x: x['date'])
        
        return etf_cash_flows
    
    def get_etf_summary(self, portfolio_id, etf_ticker):
        """Get ETF comparison summary metrics with real prices"""
        portfolio_cash_flows = self.cash_flow_service.generate_cash_flows(portfolio_id)
        deposits = [cf for cf in portfolio_cash_flows if cf['flow_type'] == 'DEPOSIT']
        
        if not deposits:
            return {
                'total_invested': 0.0,
                'portfolio_value': 0.0,
                'investment_gain': 0.0,
                'cash_balance': 0.0,
                'dividends_received': 0.0,
                'irr': 0.0
            }
        
        total_invested = sum(d['amount'] for d in deposits)
        
        # Calculate total shares including reinvestment by getting actual cash flows
        etf_cash_flows = self.get_etf_cash_flows(portfolio_id, etf_ticker)
        total_shares = 0.0
        
        # Sum up all share purchases (initial + reinvested)
        for flow in etf_cash_flows:
            if flow['flow_type'] == 'PURCHASE':
                # Extract shares from description
                desc = flow['description']
                if 'shares @' in desc:
                    shares_str = desc.split(' shares @')[0]
                    try:
                        shares = float(shares_str)
                        total_shares += shares
                    except ValueError:
                        pass
        
        # Get current value
        current_price = self.price_service.get_current_price(etf_ticker)
        current_value = total_shares * current_price if current_price else total_invested
        
        # Get dividend total for display (even though reinvested)
        dividend_flows = self._get_etf_dividend_flows(etf_ticker, deposits, total_shares)
        dividends_received = sum(df['amount'] for df in dividend_flows if df['amount'] > 0)
        
        # Investment gain = current value - total invested - dividends received
        investment_gain = current_value - total_invested - dividends_received
        
        # Calculate proper IRR using ETF cash flows
        etf_cash_flows = self.get_etf_cash_flows(portfolio_id, etf_ticker)
        irr_value = self.irr_service.calculate_irr(etf_cash_flows, current_value)
        
        return {
            'total_invested': total_invested,
            'portfolio_value': current_value,
            'investment_gain': investment_gain,
            'cash_balance': 0.0,
            'dividends_received': dividends_received,
            'irr': irr_value
        }
    
    def _get_etf_dividend_flows(self, etf_ticker, deposits, total_shares):
        """Get ETF dividend cash flows using yfinance API"""
        if not deposits or total_shares <= 0:
            return []
        
        try:
            # Get dividend history from yfinance
            etf = yf.Ticker(etf_ticker)
            dividends = etf.dividends
            
            if dividends.empty:
                return []
            
            dividend_flows = []
            start_date = min(d['date'] for d in deposits)
            
            # Filter dividends after first deposit
            for div_date, div_amount in dividends.items():
                if div_date.date() >= start_date:
                    total_dividend = float(div_amount) * total_shares
                    if total_dividend > 0.01:  # Only include meaningful dividends
                        dividend_flows.append({
                            'date': div_date.date(),
                            'flow_type': 'DIVIDEND',
                            'amount': total_dividend,
                            'description': f'${div_amount:.2f} per share',
                            'running_balance': 0.0
                        })
            
            return dividend_flows
            
        except Exception as e:
            print(f"Failed to get dividend data for {etf_ticker}: {e}")
            return []
    
