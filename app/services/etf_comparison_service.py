from app.services.cash_flow_service import CashFlowService
from datetime import date


class ETFComparisonService:
    
    def __init__(self):
        self.cash_flow_service = CashFlowService()
    
    def get_etf_cash_flows(self, portfolio_id, etf_ticker):
        """Generate ETF cash flows based on portfolio deposits"""
        # Get portfolio cash flows (deposits only)
        portfolio_cash_flows = self.cash_flow_service.generate_cash_flows(portfolio_id)
        deposits = [cf for cf in portfolio_cash_flows if cf['flow_type'] == 'DEPOSIT']
        
        if not deposits:
            return []
        
        # Convert deposits to ETF purchases
        etf_cash_flows = []
        for deposit in deposits:
            etf_cash_flows.append({
                'date': deposit['date'],
                'flow_type': 'PURCHASE',
                'amount': -deposit['amount'],  # Negative for purchase
                'description': f'{etf_ticker} ETF Purchase',
                'running_balance': 0.0
            })
        
        return etf_cash_flows
    
    def get_etf_summary(self, portfolio_id, etf_ticker):
        """Get ETF comparison summary metrics"""
        portfolio_cash_flows = self.cash_flow_service.generate_cash_flows(portfolio_id)
        deposits = [cf for cf in portfolio_cash_flows if cf['flow_type'] == 'DEPOSIT']
        
        total_invested = sum(d['amount'] for d in deposits)
        
        return {
            'total_invested': total_invested,
            'portfolio_value': total_invested * 1.1,  # Simple 10% gain assumption
            'investment_gain': total_invested * 0.1,
            'cash_balance': 0.0,
            'dividends_received': total_invested * 0.02,  # 2% dividend assumption
            'irr': 0.08  # 8% IRR assumption
        }