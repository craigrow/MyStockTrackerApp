from app import db
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app.models.cash_flow import CashFlow
from datetime import date
from collections import defaultdict


class CashFlowService:
    
    def generate_cash_flows(self, portfolio_id):
        """Generate cash flows for a portfolio from transactions and dividends"""
        # Get all transactions and dividends
        transactions = StockTransaction.query.filter_by(portfolio_id=portfolio_id).all()
        dividends = Dividend.query.filter_by(portfolio_id=portfolio_id).all()
        
        if not transactions and not dividends:
            return []
        
        # Combine and sort chronologically
        all_events = []
        
        # Add transactions
        for t in transactions:
            all_events.append({
                'date': t.date,
                'type': 'transaction',
                'data': t
            })
        
        # Add dividends
        for d in dividends:
            all_events.append({
                'date': d.payment_date,
                'type': 'dividend',
                'data': d
            })
        
        # Sort by date
        all_events.sort(key=lambda x: x['date'])
        
        # Generate cash flows
        cash_flows = []
        running_balance = 0.00
        daily_purchases = defaultdict(float)  # Track purchases by date for deposit inference
        
        # First pass: calculate required deposits by date
        temp_balance = 0.00
        for event in all_events:
            if event['type'] == 'transaction':
                transaction = event['data']
                if transaction.transaction_type == 'BUY':
                    # Check if we need a deposit
                    if temp_balance < transaction.total_value:
                        needed = transaction.total_value - temp_balance
                        daily_purchases[transaction.date] += needed
                        temp_balance += needed
                    temp_balance -= transaction.total_value
                elif transaction.transaction_type == 'SELL':
                    temp_balance += transaction.total_value
            elif event['type'] == 'dividend':
                temp_balance += event['data'].total_amount
        
        # Second pass: generate actual cash flows
        for event in all_events:
            event_date = event['date']
            
            # Add inferred deposit if needed for this date
            if event_date in daily_purchases:
                deposit_amount = daily_purchases[event_date]
                running_balance += deposit_amount
                
                cash_flows.append({
                    'date': event_date,
                    'flow_type': 'DEPOSIT',
                    'amount': deposit_amount,
                    'description': 'Inferred deposit',
                    'running_balance': running_balance
                })
                
                # Remove from daily_purchases to avoid duplicate deposits
                del daily_purchases[event_date]
            
            # Process the actual event
            if event['type'] == 'transaction':
                transaction = event['data']
                
                if transaction.transaction_type == 'BUY':
                    running_balance -= transaction.total_value
                    cash_flows.append({
                        'date': transaction.date,
                        'flow_type': 'PURCHASE',
                        'amount': -transaction.total_value,
                        'description': f'Purchase: {transaction.ticker}',
                        'running_balance': running_balance
                    })
                
                elif transaction.transaction_type == 'SELL':
                    running_balance += transaction.total_value
                    cash_flows.append({
                        'date': transaction.date,
                        'flow_type': 'SALE',
                        'amount': transaction.total_value,
                        'description': f'Sale: {transaction.ticker}',
                        'running_balance': running_balance
                    })
            
            elif event['type'] == 'dividend':
                dividend = event['data']
                running_balance += dividend.total_amount
                cash_flows.append({
                    'date': dividend.payment_date,
                    'flow_type': 'DIVIDEND',
                    'amount': dividend.total_amount,
                    'description': f'Dividend: {dividend.ticker}',
                    'running_balance': running_balance
                })
        
        return cash_flows
    
    def save_cash_flows(self, portfolio_id, cash_flows):
        """Save generated cash flows to database"""
        # Clear existing cash flows for this portfolio
        CashFlow.query.filter_by(portfolio_id=portfolio_id).delete()
        
        # Save new cash flows
        for flow_data in cash_flows:
            cash_flow = CashFlow(
                portfolio_id=portfolio_id,
                date=flow_data['date'],
                flow_type=flow_data['flow_type'],
                amount=flow_data['amount'],
                description=flow_data['description'],
                running_balance=flow_data['running_balance']
            )
            db.session.add(cash_flow)
        
        db.session.commit()
        return len(cash_flows)
    
    def get_cash_flows(self, portfolio_id):
        """Get saved cash flows for a portfolio"""
        return CashFlow.query.filter_by(
            portfolio_id=portfolio_id
        ).order_by(CashFlow.date.asc()).all()