#!/usr/bin/env python3

# Quick debug script to check IRR calculation details
from app import create_app
from app.services.etf_comparison_service import ETFComparisonService
from datetime import date

app = create_app()

with app.app_context():
    etf_service = ETFComparisonService()
    
    # Get a sample portfolio ID (you'll need to replace this)
    portfolio_id = "your-portfolio-id-here"  # Replace with actual portfolio ID
    
    print("=== VOO Cash Flows ===")
    voo_flows = etf_service.get_etf_cash_flows(portfolio_id, 'VOO')
    for flow in voo_flows:
        print(f"{flow['date']}: {flow['flow_type']} ${flow['amount']:.2f} - {flow['description']}")
    
    print("\n=== QQQ Cash Flows ===")
    qqq_flows = etf_service.get_etf_cash_flows(portfolio_id, 'QQQ')
    for flow in qqq_flows:
        print(f"{flow['date']}: {flow['flow_type']} ${flow['amount']:.2f} - {flow['description']}")
    
    print("\n=== VOO Summary ===")
    voo_summary = etf_service.get_etf_summary(portfolio_id, 'VOO')
    for key, value in voo_summary.items():
        print(f"{key}: {value}")
    
    print("\n=== QQQ Summary ===")
    qqq_summary = etf_service.get_etf_summary(portfolio_id, 'QQQ')
    for key, value in qqq_summary.items():
        print(f"{key}: {value}")