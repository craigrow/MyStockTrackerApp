from app import db
from app.models.cash_flow import IRRCalculation
from app.services.cash_flow_service import CashFlowService
from datetime import date, timedelta
import numpy as np
from scipy.optimize import fsolve
import warnings


class IRRCalculationService:
    
    def calculate_irr(self, cash_flows, current_value):
        """Calculate Internal Rate of Return from investor perspective"""
        if not cash_flows:
            return 0.00
        
        # Calculate net cash flows by date (investor perspective)
        from collections import defaultdict
        net_flows_by_date = defaultdict(float)
        
        for flow in cash_flows:
            flow_date = flow['date'] if isinstance(flow, dict) else flow.date
            flow_amount = flow['amount'] if isinstance(flow, dict) else flow.amount
            flow_type = flow['flow_type'] if isinstance(flow, dict) else flow.flow_type
            
            # From investor perspective:
            # DEPOSIT = money out of pocket (negative)
            # PURCHASE = already accounted for in deposit
            # SALE = money received (positive) 
            # DIVIDEND = money received (positive)
            if flow_type == 'DEPOSIT':
                net_flows_by_date[flow_date] -= flow_amount  # Outflow
            elif flow_type in ['SALE', 'DIVIDEND']:
                net_flows_by_date[flow_date] += flow_amount  # Inflow
            # Skip PURCHASE as it's already accounted for in DEPOSIT
        
        # Add current value as final inflow if positive
        if current_value > 0:
            net_flows_by_date[date.today()] += current_value
        
        # Convert to sorted lists
        sorted_dates = sorted(net_flows_by_date.keys())
        dates = []
        amounts = []
        
        for d in sorted_dates:
            if net_flows_by_date[d] != 0:  # Only include non-zero flows
                dates.append(d)
                amounts.append(net_flows_by_date[d])
        
        if len(amounts) < 2:
            return 0.00
        
        # Check if we have both inflows and outflows
        has_outflow = any(x < 0 for x in amounts)
        has_inflow = any(x > 0 for x in amounts)
        
        if not (has_outflow and has_inflow):
            return 0.00
        
        try:
            # Calculate time periods in years from first date
            start_date = dates[0]
            periods = np.array([(d - start_date).days / 365.25 for d in dates])
            amounts = np.array(amounts)
            
            # Define NPV function for IRR calculation
            def npv_function(rate):
                if rate <= -1:  # Avoid division by zero/negative
                    return float('inf')
                return np.sum(amounts / (1 + rate) ** periods)
            
            # Use scipy to solve for IRR (rate where NPV = 0)
            irr_result = fsolve(npv_function, 0.1)[0]
            
            # Validate result is reasonable (-99% to 1000%)
            if -0.99 <= irr_result <= 10.0:
                return round(irr_result, 4)
            else:
                return 0.00
                
        except Exception:
            return 0.00
    

    
    def save_irr_calculation(self, portfolio_id, irr_value, total_invested, current_value):
        """Save IRR calculation to database"""
        irr_calc = IRRCalculation(
            portfolio_id=portfolio_id,
            irr_value=irr_value,
            total_invested=total_invested,
            current_value=current_value,
            calculation_date=date.today()
        )
        
        db.session.add(irr_calc)
        db.session.commit()
        
        return irr_calc
    
    def get_latest_irr_calculation(self, portfolio_id):
        """Get the most recent IRR calculation for a portfolio"""
        return IRRCalculation.query.filter_by(
            portfolio_id=portfolio_id
        ).order_by(IRRCalculation.calculation_date.desc()).first()
    
    def calculate_portfolio_irr(self, portfolio_id, current_portfolio_value):
        """Calculate and save IRR for a portfolio"""
        # Generate cash flows
        cash_flow_service = CashFlowService()
        cash_flows = cash_flow_service.generate_cash_flows(portfolio_id)
        
        if not cash_flows:
            return None
        
        # Calculate total invested (sum of all deposits)
        total_invested = sum(
            flow['amount'] for flow in cash_flows 
            if flow['flow_type'] == 'DEPOSIT'
        )
        
        # Calculate IRR
        irr_value = self.calculate_irr(cash_flows, current_portfolio_value)
        
        # Save calculation
        return self.save_irr_calculation(
            portfolio_id=portfolio_id,
            irr_value=irr_value,
            total_invested=total_invested,
            current_value=current_portfolio_value
        )
    
    def get_portfolio_summary(self, portfolio_id):
        """Get portfolio cash flow summary with IRR"""
        cash_flow_service = CashFlowService()
        cash_flows = cash_flow_service.generate_cash_flows(portfolio_id)
        
        if not cash_flows:
            return {
                'total_invested': 0.00,
                'total_returned': 0.00,
                'net_cash_flow': 0.00,
                'irr': 0.00,
                'cash_flows': []
            }
        
        # Calculate summary metrics
        total_invested = sum(
            flow['amount'] for flow in cash_flows 
            if flow['flow_type'] == 'DEPOSIT'
        )
        
        # Total returned = current portfolio value + cash received from sales/dividends
        cash_received = sum(
            flow['amount'] for flow in cash_flows 
            if flow['flow_type'] in ['SALE', 'DIVIDEND']
        )
        
        # Get current portfolio value
        from app.services.portfolio_service import PortfolioService
        portfolio_service = PortfolioService()
        current_value = portfolio_service.get_portfolio_current_value(portfolio_id)
        
        total_returned = current_value + cash_received
        net_cash_flow = total_returned - total_invested
        
        # Get latest IRR calculation or calculate new one
        latest_irr = self.get_latest_irr_calculation(portfolio_id)
        if latest_irr:
            irr_value = latest_irr.irr_value
        else:
            # Calculate IRR if none exists
            from app.services.portfolio_service import PortfolioService
            portfolio_service = PortfolioService()
            current_value = portfolio_service.get_portfolio_current_value(portfolio_id)
            irr_value = self.calculate_irr(cash_flows, current_value)
            
            # Save the calculation for future use
            try:
                self.save_irr_calculation(portfolio_id, irr_value, total_invested, current_value)
            except Exception as e:
                print(f"Error saving IRR calculation: {e}")
                db.session.rollback()
        
        return {
            'total_invested': total_invested,
            'total_returned': total_returned,
            'net_cash_flow': net_cash_flow,
            'irr': irr_value,
            'cash_flows': cash_flows
        }