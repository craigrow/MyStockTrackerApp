import hashlib
from app import db
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app.models.cash_flow import CashFlow
from app.services.cash_flow_service import CashFlowService


class CashFlowSyncService:
    """Service to ensure cash flows stay synchronized with transaction data"""
    
    def __init__(self):
        self.cash_flow_service = CashFlowService()
    
    def ensure_cash_flows_current(self, portfolio_id):
        """Ensure cash flows are synchronized with current transaction data"""
        if not self.is_cash_flow_data_current(portfolio_id):
            self.regenerate_cash_flows(portfolio_id)
    
    def is_cash_flow_data_current(self, portfolio_id):
        """Check if cash flows match current transaction data using hash comparison"""
        current_hash = self.calculate_source_data_hash(portfolio_id)
        stored_hash = self.get_stored_hash(portfolio_id)
        
        # Also check if cash flows exist at all
        cash_flow_count = CashFlow.query.filter_by(portfolio_id=portfolio_id).count()
        
        return cash_flow_count > 0 and current_hash == stored_hash
    
    def calculate_source_data_hash(self, portfolio_id):
        """Generate hash from all transactions and dividends"""
        # Get all transactions and dividends for this portfolio
        transactions = StockTransaction.query.filter_by(portfolio_id=portfolio_id).order_by(
            StockTransaction.date.asc(), StockTransaction.id.asc()
        ).all()
        
        dividends = Dividend.query.filter_by(portfolio_id=portfolio_id).order_by(
            Dividend.payment_date.asc(), Dividend.id.asc()
        ).all()
        
        # Create hash input string
        hash_input = ""
        
        # Add transaction data
        for t in transactions:
            hash_input += f"T:{t.id}:{t.date}:{t.ticker}:{t.transaction_type}:{t.shares}:{t.total_value}|"
        
        # Add dividend data
        for d in dividends:
            hash_input += f"D:{d.id}:{d.payment_date}:{d.ticker}:{d.total_amount}|"
        
        # Generate SHA-256 hash
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def get_stored_hash(self, portfolio_id):
        """Get the stored hash for this portfolio's cash flows"""
        portfolio = Portfolio.query.get(portfolio_id)
        return portfolio.cash_flow_data_hash if portfolio else None
    
    def store_hash(self, portfolio_id, data_hash):
        """Store the hash for this portfolio's cash flows"""
        portfolio = Portfolio.query.get(portfolio_id)
        if portfolio:
            portfolio.cash_flow_data_hash = data_hash
            db.session.commit()
    
    def regenerate_cash_flows(self, portfolio_id):
        """Regenerate cash flows from current transaction data"""
        try:
            # Generate fresh cash flows
            cash_flows = self.cash_flow_service.generate_cash_flows(portfolio_id)
            
            # Save to database (this clears existing cash flows first)
            self.cash_flow_service.save_cash_flows(portfolio_id, cash_flows)
            
            # Update stored hash
            current_hash = self.calculate_source_data_hash(portfolio_id)
            self.store_hash(portfolio_id, current_hash)
            
            return len(cash_flows)
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_sync_status(self, portfolio_id):
        """Get synchronization status for debugging"""
        current_hash = self.calculate_source_data_hash(portfolio_id)
        stored_hash = self.get_stored_hash(portfolio_id)
        cash_flow_count = CashFlow.query.filter_by(portfolio_id=portfolio_id).count()
        
        transaction_count = StockTransaction.query.filter_by(portfolio_id=portfolio_id).count()
        dividend_count = Dividend.query.filter_by(portfolio_id=portfolio_id).count()
        
        return {
            'is_current': current_hash == stored_hash and cash_flow_count > 0,
            'current_hash': current_hash[:8] + '...',  # First 8 chars for display
            'stored_hash': (stored_hash[:8] + '...') if stored_hash else None,
            'cash_flow_count': cash_flow_count,
            'transaction_count': transaction_count,
            'dividend_count': dividend_count,
            'needs_regeneration': current_hash != stored_hash or cash_flow_count == 0
        }