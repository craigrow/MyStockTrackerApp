import pytest
from datetime import datetime, date
from decimal import Decimal
from app.models.cash_flow import CashFlow, IRRCalculation
from app.models.portfolio import Portfolio
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestCashFlow:
    def test_cash_flow_creation(self, app, sample_portfolio):
        """Test basic CashFlow model creation"""
        with app.app_context():
            cash_flow = CashFlow(
                portfolio_id=sample_portfolio.id,
                date=date(2023, 1, 1),
                flow_type='DEPOSIT',
                amount=1000.00,
                description='Initial deposit',
                running_balance=1000.00
            )
            db.session.add(cash_flow)
            db.session.commit()
            
            assert cash_flow.portfolio_id == sample_portfolio.id
            assert cash_flow.date == date(2023, 1, 1)
            assert cash_flow.flow_type == 'DEPOSIT'
            assert cash_flow.amount == 1000.00
            assert cash_flow.description == 'Initial deposit'
            assert cash_flow.running_balance == 1000.00
            assert cash_flow.created_at is not None

    def test_cash_flow_types(self, app, sample_portfolio):
        """Test all valid cash flow types"""
        with app.app_context():
            flow_types = ['DEPOSIT', 'PURCHASE', 'SALE', 'DIVIDEND']
            
            for flow_type in flow_types:
                cash_flow = CashFlow(
                    portfolio_id=sample_portfolio.id,
                    date=date(2023, 1, 1),
                    flow_type=flow_type,
                    amount=100.00,
                    description=f'Test {flow_type}',
                    running_balance=100.00
                )
                db.session.add(cash_flow)
            
            db.session.commit()
            
            # Verify all types were created
            flows = CashFlow.query.filter_by(portfolio_id=sample_portfolio.id).all()
            created_types = [f.flow_type for f in flows]
            assert set(created_types) == set(flow_types)

    def test_cash_flow_portfolio_relationship(self, app, sample_portfolio):
        """Test portfolio foreign key relationship"""
        with app.app_context():
            cash_flow = CashFlow(
                portfolio_id=sample_portfolio.id,
                date=date(2023, 1, 1),
                flow_type='DEPOSIT',
                amount=1000.00,
                description='Test relationship',
                running_balance=1000.00
            )
            db.session.add(cash_flow)
            db.session.commit()
            
            # Test relationship access
            portfolio = Portfolio.query.get(sample_portfolio.id)
            assert len(portfolio.cash_flows) == 1
            assert portfolio.cash_flows[0].amount == 1000.00

    def test_cash_flow_chronological_ordering(self, app, sample_portfolio):
        """Test cash flows are ordered chronologically"""
        with app.app_context():
            # Create flows in reverse chronological order
            dates = [date(2023, 1, 3), date(2023, 1, 1), date(2023, 1, 2)]
            
            for i, flow_date in enumerate(dates):
                cash_flow = CashFlow(
                    portfolio_id=sample_portfolio.id,
                    date=flow_date,
                    flow_type='DEPOSIT',
                    amount=100.00 * (i + 1),
                    description=f'Flow {i + 1}',
                    running_balance=100.00 * (i + 1)
                )
                db.session.add(cash_flow)
            
            db.session.commit()
            
            # Query with chronological ordering
            flows = CashFlow.query.filter_by(
                portfolio_id=sample_portfolio.id
            ).order_by(CashFlow.date.asc()).all()
            
            # Should be ordered by date ascending
            assert flows[0].date == date(2023, 1, 1)
            assert flows[1].date == date(2023, 1, 2)
            assert flows[2].date == date(2023, 1, 3)


@pytest.mark.fast
@pytest.mark.database
class TestIRRCalculation:
    def test_irr_calculation_creation(self, app, sample_portfolio):
        """Test basic IRRCalculation model creation"""
        with app.app_context():
            irr_calc = IRRCalculation(
                portfolio_id=sample_portfolio.id,
                irr_value=0.1250,
                total_invested=10000.00,
                current_value=11250.00,
                calculation_date=date.today()
            )
            db.session.add(irr_calc)
            db.session.commit()
            
            assert irr_calc.portfolio_id == sample_portfolio.id
            assert irr_calc.irr_value == 0.1250
            assert irr_calc.total_invested == 10000.00
            assert irr_calc.current_value == 11250.00
            assert irr_calc.calculation_date == date.today()
            assert irr_calc.created_at is not None

    def test_irr_calculation_portfolio_relationship(self, app, sample_portfolio):
        """Test portfolio foreign key relationship"""
        with app.app_context():
            irr_calc = IRRCalculation(
                portfolio_id=sample_portfolio.id,
                irr_value=0.0850,
                total_invested=5000.00,
                current_value=5425.00,
                calculation_date=date.today()
            )
            db.session.add(irr_calc)
            db.session.commit()
            
            # Test relationship access
            portfolio = Portfolio.query.get(sample_portfolio.id)
            assert len(portfolio.irr_calculations) == 1
            assert portfolio.irr_calculations[0].irr_value == 0.0850

    def test_irr_calculation_latest_query(self, app, sample_portfolio):
        """Test querying for latest IRR calculation"""
        with app.app_context():
            # Create multiple calculations
            dates = [date(2023, 1, 1), date(2023, 1, 3), date(2023, 1, 2)]
            irr_values = [0.05, 0.08, 0.06]
            
            for calc_date, irr_val in zip(dates, irr_values):
                irr_calc = IRRCalculation(
                    portfolio_id=sample_portfolio.id,
                    irr_value=irr_val,
                    total_invested=1000.00,
                    current_value=1000.00 * (1 + irr_val),
                    calculation_date=calc_date
                )
                db.session.add(irr_calc)
            
            db.session.commit()
            
            # Query for latest calculation
            latest = IRRCalculation.query.filter_by(
                portfolio_id=sample_portfolio.id
            ).order_by(IRRCalculation.calculation_date.desc()).first()
            
            # Should be the most recent date (2023-01-03)
            assert latest.calculation_date == date(2023, 1, 3)
            assert latest.irr_value == 0.08