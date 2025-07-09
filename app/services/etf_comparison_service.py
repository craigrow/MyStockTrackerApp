from app.services.cash_flow_service import CashFlowService
from app.services.price_service import PriceService
from datetime import date
import yfinance as yf


class ETFComparisonService:
    
    def __init__(self):
        self.cash_flow_service = CashFlowService()
        self.price_service = PriceService()
    
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
                    'description': f'{etf_ticker} Purchase: {shares_purchased:.4f} shares @ ${etf_price:.2f}',
                    'running_balance': 0.0
                })
        
        # Add dividend cash flows
        dividend_flows = self._get_etf_dividend_flows(etf_ticker, deposits, total_shares)
        etf_cash_flows.extend(dividend_flows)
        
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
        total_shares = 0.0
        
        # Calculate total shares purchased
        for deposit in deposits:
            etf_price = self.price_service.get_cached_price(etf_ticker, deposit['date'])
            if not etf_price:
                etf_price = self.price_service.get_current_price(etf_ticker)
            if etf_price:
                total_shares += deposit['amount'] / etf_price
        
        # Get current value
        current_price = self.price_service.get_current_price(etf_ticker)
        current_value = total_shares * current_price if current_price else total_invested
        
        # Get dividend total
        dividend_flows = self._get_etf_dividend_flows(etf_ticker, deposits, total_shares)
        dividends_received = sum(df['amount'] for df in dividend_flows if df['amount'] > 0)
        
        investment_gain = current_value - total_invested - dividends_received
        
        return {
            'total_invested': total_invested,
            'portfolio_value': current_value,
            'investment_gain': investment_gain,
            'cash_balance': 0.0,
            'dividends_received': dividends_received,
            'irr': self._calculate_simple_irr(total_invested, current_value, dividends_received, deposits)
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
                            'description': f'{etf_ticker} Dividend: ${div_amount:.4f} per share',
                            'running_balance': 0.0
                        })
            
            return dividend_flows
            
        except Exception as e:
            print(f"Failed to get dividend data for {etf_ticker}: {e}")
            return []
    
    def _calculate_simple_irr(self, invested, current_value, dividends, deposits):
        """Calculate simple IRR approximation"""
        if not deposits or invested <= 0:
            return 0.0
        
        # Simple time-weighted return approximation
        total_return = (current_value + dividends - invested) / invested
        
        # Approximate time period in years
        start_date = min(d['date'] for d in deposits)
        years = max(0.1, (date.today() - start_date).days / 365.25)
        
        # Simple annualized return
        return (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0