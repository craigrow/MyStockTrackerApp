import pytest
from datetime import date
from app.services.irr_calculation_service import IRRCalculationService
from app.services.cash_flow_service import CashFlowService
from app.models.portfolio import Portfolio, StockTransaction
from app.models.cash_flow import IRRCalculation
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestIRRCalculationService:
    def test_irr_calculation_simple(self, app, sample_portfolio):
        """Test basic IRR calculation with known result"""
        with app.app_context():
            # Create simple scenario: invest $1000, get back $1100 after 1 year
            # Expected IRR ≈ 10%
            transactions = [
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=100.00,
                    shares=10.0,
                    total_value=1000.00
                ),
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='SELL',
                    date=date(2024, 1, 1),
                    price_per_share=110.00,
                    shares=10.0,
                    total_value=1100.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            # Generate cash flows
            cash_flow_service = CashFlowService()
            cash_flows = cash_flow_service.generate_cash_flows(sample_portfolio.id)
            
            # Calculate IRR
            irr_service = IRRCalculationService()
            irr_result = irr_service.calculate_irr(cash_flows, current_value=0.00)
            
            # Should be approximately 10% (0.10)
            assert abs(irr_result - 0.10) < 0.01

    def test_irr_calculation_no_cash_flows(self, app, sample_portfolio):
        """Test IRR calculation with empty cash flows"""
        with app.app_context():
            irr_service = IRRCalculationService()
            irr_result = irr_service.calculate_irr([], current_value=0.00)
            
            # Should return 0 for empty portfolio
            assert irr_result == 0.00

    def test_irr_calculation_single_deposit(self, app, sample_portfolio):
        """Test IRR calculation with only deposits (no returns)"""
        with app.app_context():
            # Create transaction with no sale
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=100.00,
                shares=10.0,
                total_value=1000.00
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Generate cash flows
            cash_flow_service = CashFlowService()
            cash_flows = cash_flow_service.generate_cash_flows(sample_portfolio.id)
            
            # Calculate IRR with current value same as invested
            irr_service = IRRCalculationService()
            irr_result = irr_service.calculate_irr(cash_flows, current_value=1000.00)
            
            # Should be 0% (no gain/loss)
            assert abs(irr_result - 0.00) < 0.01

    def test_irr_calculation_complex(self, app, sample_portfolio):
        """Test IRR calculation with multiple deposits and returns"""
        with app.app_context():
            # Create complex scenario with multiple transactions
            transactions = [
                # Initial investment
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=100.00,
                    shares=10.0,
                    total_value=1000.00
                ),
                # Additional investment 6 months later
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 7, 1),
                    price_per_share=110.00,
                    shares=5.0,
                    total_value=550.00
                ),
                # Partial sale after 1 year
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='SELL',
                    date=date(2024, 1, 1),
                    price_per_share=120.00,
                    shares=8.0,
                    total_value=960.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            # Generate cash flows
            cash_flow_service = CashFlowService()
            cash_flows = cash_flow_service.generate_cash_flows(sample_portfolio.id)
            
            # Calculate IRR with remaining position value
            remaining_value = 7 * 120.00  # 7 shares at $120
            irr_service = IRRCalculationService()
            irr_result = irr_service.calculate_irr(cash_flows, current_value=remaining_value)
            
            # Should be positive (portfolio gained value)
            assert irr_result > 0.00

    def test_save_irr_calculation(self, app, sample_portfolio):
        """Test saving IRR calculation to database"""
        with app.app_context():
            irr_service = IRRCalculationService()
            
            # Save IRR calculation
            saved_calc = irr_service.save_irr_calculation(
                portfolio_id=sample_portfolio.id,
                irr_value=0.1250,
                total_invested=10000.00,
                current_value=11250.00
            )
            
            assert saved_calc.portfolio_id == sample_portfolio.id
            assert saved_calc.irr_value == 0.1250
            assert saved_calc.total_invested == 10000.00
            assert saved_calc.current_value == 11250.00
            assert saved_calc.calculation_date == date.today()

    def test_get_latest_irr_calculation(self, app, sample_portfolio):
        """Test retrieving latest IRR calculation"""
        with app.app_context():
            irr_service = IRRCalculationService()
            
            # Create multiple calculations
            calc1 = irr_service.save_irr_calculation(
                portfolio_id=sample_portfolio.id,
                irr_value=0.08,
                total_invested=1000.00,
                current_value=1080.00
            )
            
            calc2 = irr_service.save_irr_calculation(
                portfolio_id=sample_portfolio.id,
                irr_value=0.12,
                total_invested=1000.00,
                current_value=1120.00
            )
            
            # Get latest calculation
            latest = irr_service.get_latest_irr_calculation(sample_portfolio.id)
            
            # Should be the most recent one
            assert latest.id == calc2.id
            assert latest.irr_value == 0.12

    def test_calculate_portfolio_irr(self, app, sample_portfolio):
        """Test end-to-end portfolio IRR calculation"""
        with app.app_context():
            # Create portfolio with transactions
            transactions = [
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=100.00,
                    shares=10.0,
                    total_value=1000.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            irr_service = IRRCalculationService()
            
            # Calculate and save portfolio IRR
            irr_result = irr_service.calculate_portfolio_irr(
                portfolio_id=sample_portfolio.id,
                current_portfolio_value=1150.00
            )
            
            # Should return IRR calculation object
            assert irr_result is not None
            assert irr_result.portfolio_id == sample_portfolio.id
            assert irr_result.total_invested == 1000.00
            assert irr_result.current_value == 1150.00
            assert irr_result.irr_value > 0.00  # Should be positive

    def test_irr_calculation_error_handling(self, app, sample_portfolio):
        """Test IRR calculation handles edge cases gracefully"""
        with app.app_context():
            irr_service = IRRCalculationService()
            
            # Test with invalid cash flows (all same sign)
            invalid_flows = [
                {'date': date(2023, 1, 1), 'amount': 1000.00, 'flow_type': 'DEPOSIT'},
                {'date': date(2023, 6, 1), 'amount': 500.00, 'flow_type': 'DEPOSIT'}
            ]
            
            irr_result = irr_service.calculate_irr(invalid_flows, current_value=0.00)
            
            # Should handle gracefully and return 0
            assert irr_result == 0.00