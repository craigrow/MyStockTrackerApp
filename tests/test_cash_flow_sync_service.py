import pytest
from datetime import date
from app.services.cash_flow_sync_service import CashFlowSyncService
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app.models.cash_flow import CashFlow
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestCashFlowSyncService:
    def test_hash_calculation_empty_portfolio(self, app, sample_portfolio):
        """Test hash calculation for empty portfolio"""
        with app.app_context():
            sync_service = CashFlowSyncService()
            hash_value = sync_service.calculate_source_data_hash(sample_portfolio.id)
            
            # Empty portfolio should have consistent hash
            assert len(hash_value) == 64  # SHA-256 hex string
            assert hash_value == sync_service.calculate_source_data_hash(sample_portfolio.id)

    def test_hash_changes_with_new_transaction(self, app, sample_portfolio):
        """Test that hash changes when transactions are added"""
        with app.app_context():
            sync_service = CashFlowSyncService()
            
            # Get initial hash
            initial_hash = sync_service.calculate_source_data_hash(sample_portfolio.id)
            
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Hash should change
            new_hash = sync_service.calculate_source_data_hash(sample_portfolio.id)
            assert new_hash != initial_hash

    def test_hash_changes_with_backdated_transaction(self, app, sample_portfolio):
        """Test that hash changes when backdated transactions are added"""
        with app.app_context():
            sync_service = CashFlowSyncService()
            
            # Add initial transaction
            transaction1 = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 15),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction1)
            db.session.commit()
            
            hash_after_first = sync_service.calculate_source_data_hash(sample_portfolio.id)
            
            # Add backdated transaction
            transaction2 = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='MSFT',
                transaction_type='BUY',
                date=date(2023, 1, 5),  # Earlier date
                price_per_share=200.00,
                shares=5.0,
                total_value=1000.00
            )
            db.session.add(transaction2)
            db.session.commit()
            
            # Hash should change even for backdated transaction
            hash_after_backdated = sync_service.calculate_source_data_hash(sample_portfolio.id)
            assert hash_after_backdated != hash_after_first

    def test_is_cash_flow_data_current_no_data(self, app, sample_portfolio):
        """Test current check when no cash flows exist"""
        with app.app_context():
            sync_service = CashFlowSyncService()
            
            # No cash flows exist, should return False
            assert not sync_service.is_cash_flow_data_current(sample_portfolio.id)

    def test_ensure_cash_flows_current_generates_data(self, app, sample_portfolio):
        """Test that ensure_cash_flows_current generates cash flows when needed"""
        with app.app_context():
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            sync_service = CashFlowSyncService()
            
            # Initially no cash flows
            assert CashFlow.query.filter_by(portfolio_id=sample_portfolio.id).count() == 0
            
            # Ensure current should generate cash flows
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            
            # Should now have cash flows
            cash_flows = CashFlow.query.filter_by(portfolio_id=sample_portfolio.id).all()
            assert len(cash_flows) == 2  # Deposit + Purchase

    def test_cash_flows_stay_current_when_unchanged(self, app, sample_portfolio):
        """Test that cash flows are not regenerated when data hasn't changed"""
        with app.app_context():
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            sync_service = CashFlowSyncService()
            
            # Generate initial cash flows
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            initial_count = CashFlow.query.filter_by(portfolio_id=sample_portfolio.id).count()
            
            # Should be current now
            assert sync_service.is_cash_flow_data_current(sample_portfolio.id)
            
            # Calling again should not regenerate
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            final_count = CashFlow.query.filter_by(portfolio_id=sample_portfolio.id).count()
            
            assert final_count == initial_count

    def test_cash_flows_regenerated_when_transaction_modified(self, app, sample_portfolio):
        """Test that cash flows are regenerated when transactions are modified"""
        with app.app_context():
            # Add transaction
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            sync_service = CashFlowSyncService()
            
            # Generate initial cash flows
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            assert sync_service.is_cash_flow_data_current(sample_portfolio.id)
            
            # Modify transaction
            transaction.total_value = 1600.00
            db.session.commit()
            
            # Should no longer be current
            assert not sync_service.is_cash_flow_data_current(sample_portfolio.id)
            
            # Ensure current should regenerate
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            assert sync_service.is_cash_flow_data_current(sample_portfolio.id)

    def test_get_sync_status(self, app, sample_portfolio):
        """Test sync status reporting"""
        with app.app_context():
            sync_service = CashFlowSyncService()
            
            # Initial status - should need regeneration
            status = sync_service.get_sync_status(sample_portfolio.id)
            assert not status['is_current']
            assert status['needs_regeneration']
            assert status['cash_flow_count'] == 0
            assert status['transaction_count'] == 0
            
            # Add transaction and sync
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            sync_service.ensure_cash_flows_current(sample_portfolio.id)
            
            # Status should show current
            status = sync_service.get_sync_status(sample_portfolio.id)
            assert status['is_current']
            assert not status['needs_regeneration']
            assert status['cash_flow_count'] > 0
            assert status['transaction_count'] == 1