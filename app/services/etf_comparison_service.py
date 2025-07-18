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
        
        for deposit in deposits:
            # Get ETF price on deposit date
            etf_price = self.price_service.get_cached_price(etf_ticker, deposit['date'])
            if not etf_price:
                # Fallback to current price if historical not available
                etf_price = self.price_service.get_current_price(etf_ticker)
            
            if etf_price:
                shares_purchased = deposit['amount'] / etf_price
                
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
        dividend_flows = self._get_etf_dividend_flows(etf_ticker, deposits, etf_cash_flows)
        etf_cash_flows.extend(dividend_flows)
        
        # Sort by date
        etf_cash_flows.sort(key=lambda x: x['date'])
        
        # Define flow type priority for same-day sorting (dividends, deposits, purchases)
        flow_type_priority = {
            'DIVIDEND': 1,
            'DEPOSIT': 2,
            'PURCHASE': 3,
            'SALE': 4
        }
        
        # Sort by date first, then by flow type priority for same-day transactions
        etf_cash_flows.sort(key=lambda x: (x['date'], flow_type_priority.get(x['flow_type'], 99)))
        
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
                total_shares += flow['shares']
        
        # Get current value
        current_price = self.price_service.get_current_price(etf_ticker)
        current_value = total_shares * current_price if current_price else total_invested
        
        # Get dividend total for display (even though reinvested)
        dividends_received = sum(flow['amount'] for flow in etf_cash_flows 
                               if flow['flow_type'] == 'DIVIDEND' and flow['amount'] > 0)
        
        # Investment gain = current value - total invested - dividends received
        investment_gain = current_value - total_invested - dividends_received
        
        # Calculate proper IRR using ETF cash flows
        irr_value = self.irr_service.calculate_irr(etf_cash_flows, current_value)
        
        return {
            'total_invested': total_invested,
            'portfolio_value': current_value,
            'investment_gain': investment_gain,
            'cash_balance': 0.0,
            'dividends_received': dividends_received,
            'irr': irr_value
        }
    
    def _get_etf_dividend_flows(self, etf_ticker, deposits, existing_cash_flows):
        """Get ETF dividend cash flows using yfinance API"""
        if not deposits:
            return []
        
        try:
            # Get dividend history from yfinance
            etf = yf.Ticker(etf_ticker)
            dividends = etf.dividends
            
            if dividends.empty:
                return []
            
            dividend_flows = []
            start_date = min(d['date'] for d in deposits)
            
            # Filter dividends after first deposit and sort by date
            relevant_dividends = [(div_date.date(), float(div_amount)) 
                                for div_date, div_amount in dividends.items() 
                                if div_date.date() >= start_date]
            relevant_dividends.sort(key=lambda x: x[0])
            
            # Process each dividend date
            for div_date, div_amount in relevant_dividends:
                # Calculate shares held at this dividend date
                shares_on_date = self._calculate_shares_on_date(existing_cash_flows, div_date)
                
                if shares_on_date > 0:
                    total_dividend = div_amount * shares_on_date
                    if total_dividend > 0.01:  # Only include meaningful dividends
                        dividend_flow = {
                            'date': div_date,
                            'flow_type': 'DIVIDEND',
                            'amount': total_dividend,
                            'description': f'${div_amount:.2f} per share',
                            'shares': shares_on_date,  # Use actual shares on dividend date
                            'price_per_share': div_amount,
                            'running_balance': 0.0
                        }
                        dividend_flows.append(dividend_flow)
                        
                        # Add dividend reinvestment
                        div_price = self.price_service.get_cached_price(etf_ticker, div_date)
                        if not div_price:
                            div_price = self.price_service.get_current_price(etf_ticker)
                        
                        if div_price and total_dividend > 0:
                            reinvest_shares = total_dividend / div_price
                            
                            reinvest_flow = {
                                'date': div_date,
                                'flow_type': 'PURCHASE',
                                'amount': -total_dividend,  # Negative for purchase
                                'description': f'{reinvest_shares:.4f} shares @ ${div_price:.2f} (dividend reinvestment)',
                                'shares': reinvest_shares,
                                'price_per_share': div_price,
                                'running_balance': 0.0
                            }
                            dividend_flows.append(reinvest_flow)
            
            return dividend_flows
            
        except Exception as e:
            print(f"Failed to get dividend data for {etf_ticker}: {e}")
            return []
    
    def _calculate_shares_on_date(self, cash_flows, target_date):
        """Calculate shares held on a specific date based on existing cash flows"""
        total_shares = 0.0
        
        # Add up all purchases and reinvestments up to target date
        for flow in cash_flows:
            if flow['date'] <= target_date:
                if flow['flow_type'] == 'PURCHASE':
                    total_shares += flow['shares']
        
        return total_shares
