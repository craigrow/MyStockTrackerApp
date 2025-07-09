import pytest
from datetime import date
from app.services.cash_flow_service import CashFlowService
from app.models.portfolio import Portfolio, StockTransaction, Dividend
from app.models.cash_flow import CashFlow
from app import db


@pytest.mark.fast
@pytest.mark.database
class TestCashFlowService:
    def test_generate_cash_flows_empty_portfolio(self, app, sample_portfolio):
        """Test cash flow generation for empty portfolio"""
        with app.app_context():
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            assert cash_flows == []

    def test_generate_cash_flows_simple_purchase(self, app, sample_portfolio):
        """Test cash flow generation with single purchase"""
        with app.app_context():
            # Create a purchase transaction
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
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Should have 2 flows: inferred deposit + purchase
            assert len(cash_flows) == 2
            
            # First flow should be inferred deposit
            deposit = cash_flows[0]
            assert deposit['flow_type'] == 'DEPOSIT'
            assert deposit['amount'] == 1500.00
            assert deposit['date'] == date(2023, 1, 1)
            assert deposit['running_balance'] == 1500.00
            
            # Second flow should be purchase
            purchase = cash_flows[1]
            assert purchase['flow_type'] == 'PURCHASE'
            assert purchase['amount'] == -1500.00
            assert purchase['date'] == date(2023, 1, 1)
            assert purchase['running_balance'] == 0.00

    def test_generate_cash_flows_multiple_same_day(self, app, sample_portfolio):
        """Test multiple purchases on same day create one deposit"""
        with app.app_context():
            # Create two purchases on same day
            transactions = [
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=150.00,
                    shares=10.0,
                    total_value=1500.00
                ),
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='MSFT',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=200.00,
                    shares=5.0,
                    total_value=1000.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Should have 3 flows: 1 deposit + 2 purchases
            assert len(cash_flows) == 3
            
            # First flow should be single deposit for total amount
            deposit = cash_flows[0]
            assert deposit['flow_type'] == 'DEPOSIT'
            assert deposit['amount'] == 2500.00  # 1500 + 1000
            assert deposit['running_balance'] == 2500.00

    def test_generate_cash_flows_with_sales(self, app, sample_portfolio):
        """Test cash flows with purchase and sale transactions"""
        with app.app_context():
            # Create buy then sell
            transactions = [
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=150.00,
                    shares=10.0,
                    total_value=1500.00
                ),
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='SELL',
                    date=date(2023, 6, 1),
                    price_per_share=180.00,
                    shares=5.0,
                    total_value=900.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Should have 3 flows: deposit, purchase, sale
            assert len(cash_flows) == 3
            
            # Sale should add to balance
            sale = cash_flows[2]
            assert sale['flow_type'] == 'SALE'
            assert sale['amount'] == 900.00
            assert sale['running_balance'] == 900.00

    def test_generate_cash_flows_with_dividends(self, app, sample_portfolio):
        """Test cash flows include dividend payments"""
        with app.app_context():
            # Create transaction and dividend
            transaction = StockTransaction(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                transaction_type='BUY',
                date=date(2023, 1, 1),
                price_per_share=150.00,
                shares=10.0,
                total_value=1500.00
            )
            dividend = Dividend(
                portfolio_id=sample_portfolio.id,
                ticker='AAPL',
                payment_date=date(2023, 3, 15),
                total_amount=25.50
            )
            
            db.session.add(transaction)
            db.session.add(dividend)
            db.session.commit()
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Should have 3 flows: deposit, purchase, dividend
            assert len(cash_flows) == 3
            
            # Dividend should be last and add to balance
            dividend_flow = cash_flows[2]
            assert dividend_flow['flow_type'] == 'DIVIDEND'
            assert dividend_flow['amount'] == 25.50
            assert dividend_flow['running_balance'] == 25.50

    def test_no_negative_balances(self, app, sample_portfolio):
        """Test that running balance never goes negative"""
        with app.app_context():
            # Create transaction that would cause negative balance
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
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Check all running balances are non-negative
            for flow in cash_flows:
                assert flow['running_balance'] >= 0.00

    def test_chronological_processing(self, app, sample_portfolio):
        """Test transactions are processed in chronological order"""
        with app.app_context():
            # Create transactions in reverse chronological order
            transactions = [
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='AAPL',
                    transaction_type='BUY',
                    date=date(2023, 1, 3),
                    price_per_share=150.00,
                    shares=5.0,
                    total_value=750.00
                ),
                StockTransaction(
                    portfolio_id=sample_portfolio.id,
                    ticker='MSFT',
                    transaction_type='BUY',
                    date=date(2023, 1, 1),
                    price_per_share=200.00,
                    shares=10.0,
                    total_value=2000.00
                )
            ]
            
            for t in transactions:
                db.session.add(t)
            db.session.commit()
            
            service = CashFlowService()
            cash_flows = service.generate_cash_flows(sample_portfolio.id)
            
            # Should be processed in chronological order
            # First deposit/purchase should be for MSFT (Jan 1)
            assert cash_flows[0]['date'] == date(2023, 1, 1)
            assert cash_flows[1]['description'] == 'Purchase: MSFT'
            
            # Second deposit/purchase should be for AAPL (Jan 3)  
            assert cash_flows[2]['date'] == date(2023, 1, 3)
            assert cash_flows[3]['description'] == 'Purchase: AAPL'