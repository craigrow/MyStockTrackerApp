from flask import Blueprint, render_template, request, Response
from app.services.portfolio_service import PortfolioService
from app.services.cash_flow_sync_service import CashFlowSyncService
from app.services.cash_flow_service import CashFlowService
from app.services.irr_calculation_service import IRRCalculationService
import csv
import io

cash_flows_blueprint = Blueprint('cash_flows', __name__)

@cash_flows_blueprint.route('/cash-flows')
def cash_flows_page():
    """Cash flows analysis page"""
    portfolio_service = PortfolioService()
    cash_flow_sync_service = CashFlowSyncService()
    cash_flow_service = CashFlowService()
    irr_service = IRRCalculationService()
    
    # Get all portfolios
    portfolios = portfolio_service.get_all_portfolios()
    
    # Get current portfolio (from URL param or first available)
    portfolio_id = request.args.get('portfolio_id')
    current_portfolio = None
    
    if portfolio_id:
        current_portfolio = portfolio_service.get_portfolio(portfolio_id)
    elif portfolios:
        current_portfolio = portfolios[0]
    
    # Initialize data
    cash_flows = []
    portfolio_summary = {}
    sync_status = {}
    
    if current_portfolio:
        # Ensure cash flows are synchronized
        cash_flow_sync_service.ensure_cash_flows_current(current_portfolio.id)
        
        # Get cash flows and summary
        cash_flows = cash_flow_service.get_cash_flows(current_portfolio.id)
        portfolio_summary = irr_service.get_portfolio_summary(current_portfolio.id)
        sync_status = cash_flow_sync_service.get_sync_status(current_portfolio.id)
    
    return render_template('cash_flows.html',
                         portfolios=portfolios,
                         current_portfolio=current_portfolio,
                         cash_flows=cash_flows,
                         portfolio_summary=portfolio_summary,
                         sync_status=sync_status)

@cash_flows_blueprint.route('/cash-flows/export')
def export_cash_flows():
    """Export cash flows to CSV"""
    portfolio_service = PortfolioService()
    cash_flow_service = CashFlowService()
    
    # Get portfolio
    portfolio_id = request.args.get('portfolio_id')
    if not portfolio_id:
        return "Portfolio ID required", 400
    
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if not portfolio:
        return "Portfolio not found", 404
    
    # Get cash flows
    cash_flows = cash_flow_service.get_cash_flows(portfolio_id)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Type', 'Description', 'Amount', 'Running Balance'])
    
    # Write data
    for flow in cash_flows:
        writer.writerow([
            flow.date.strftime('%Y-%m-%d'),
            flow.flow_type,
            flow.description,
            f"{flow.amount:.2f}",
            f"{flow.running_balance:.2f}"
        ])
    
    # Create response
    output.seek(0)
    filename = f"cash_flows_{portfolio.name.replace(' ', '_')}_{portfolio_id[:8]}.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )