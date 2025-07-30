from flask import Blueprint, render_template, request, Response
from app.services.portfolio_service import PortfolioService
from app.services.cash_flow_sync_service import CashFlowSyncService
from app.services.cash_flow_service import CashFlowService
from app.services.irr_calculation_service import IRRCalculationService
from app.services.etf_comparison_service import ETFComparisonService
from datetime import date
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
    voo_irr = 0.0
    qqq_irr = 0.0
    
    if current_portfolio:
        # Get comparison type (portfolio, VOO, or QQQ)
        comparison = request.args.get('comparison', 'portfolio')
        
        # Always calculate VOO and QQQ IRR for display
        etf_service = ETFComparisonService()
        voo_summary = etf_service.get_etf_summary(current_portfolio.id, 'VOO')
        qqq_summary = etf_service.get_etf_summary(current_portfolio.id, 'QQQ')
        voo_irr = voo_summary.get('irr', 0.0)
        qqq_irr = qqq_summary.get('irr', 0.0)
        
        if comparison in ['VOO', 'QQQ']:
            # ETF comparison view - using real service
            cash_flows = etf_service.get_etf_cash_flows(current_portfolio.id, comparison)
            portfolio_summary = etf_service.get_etf_summary(current_portfolio.id, comparison)
            sync_status = {'status': 'complete', 'message': f'{comparison} comparison data loaded'}
        else:
            # Portfolio view
            cash_flow_sync_service.ensure_cash_flows_current(current_portfolio.id)
            cash_flows = cash_flow_service.get_cash_flows(current_portfolio.id)
            portfolio_summary = irr_service.get_portfolio_summary(current_portfolio.id)
            sync_status = cash_flow_sync_service.get_sync_status(current_portfolio.id)
    
    return render_template('cash_flows.html',
                         cash_flows=cash_flows,
                         portfolio_summary=portfolio_summary,
                         sync_status=sync_status,
                         voo_irr=voo_irr,
                         qqq_irr=qqq_irr,
                         comparison=comparison if current_portfolio else 'portfolio')

@cash_flows_blueprint.route('/cash-flows/export')
def export_cash_flows():
    """Export cash flows to CSV with filtering"""
    portfolio_service = PortfolioService()
    cash_flow_service = CashFlowService()
    etf_service = ETFComparisonService()
    
    # Get portfolio
    portfolio_id = request.args.get('portfolio_id')
    if not portfolio_id:
        return "Portfolio ID required", 400
    
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if not portfolio:
        return "Portfolio not found", 404
    
    # Get comparison type and cash flows
    comparison = request.args.get('comparison', 'portfolio')
    if comparison in ['VOO', 'QQQ']:
        cash_flows = etf_service.get_etf_cash_flows(portfolio_id, comparison)
    else:
        cash_flows = cash_flow_service.get_cash_flows(portfolio_id)
    
    # Get filter types
    filter_types = request.args.getlist('types')
    if filter_types:
        cash_flows = [cf for cf in cash_flows if cf.flow_type in filter_types or cf.get('flow_type') in filter_types]
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Type', 'Description', 'Amount', 'Running Balance'])
    
    # Write data
    for flow in cash_flows:
        if hasattr(flow, 'date'):
            # Database object
            writer.writerow([
                flow.date.strftime('%Y-%m-%d'),
                flow.flow_type,
                flow.description,
                f"{flow.amount:.2f}",
                f"{flow.running_balance:.2f}"
            ])
        else:
            # Dictionary object (ETF flows)
            writer.writerow([
                flow['date'].strftime('%Y-%m-%d'),
                flow['flow_type'],
                flow['description'],
                f"{flow['amount']:.2f}",
                f"{flow['running_balance']:.2f}"
            ])
    
    # Create response
    output.seek(0)
    comparison_suffix = f"_{comparison}" if comparison != 'portfolio' else ""
    filename = f"cash_flows_{portfolio.name.replace(' ', '_')}{comparison_suffix}_{portfolio_id[:8]}.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )