from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.portfolio_service import PortfolioService

portfolio_blueprint = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio_blueprint.route('/create')
def create():
    return render_template('portfolio/create.html')

@portfolio_blueprint.route('/transactions')
def transactions():
    return render_template('portfolio/transactions.html')

@portfolio_blueprint.route('/dividends')
def dividends():
    return render_template('portfolio/dividends.html')

@portfolio_blueprint.route('/add-transaction')
def add_transaction():
    return render_template('portfolio/add_transaction.html')

@portfolio_blueprint.route('/add-dividend')
def add_dividend():
    return render_template('portfolio/add_dividend.html')

@portfolio_blueprint.route('/import-csv')
def import_csv():
    return render_template('portfolio/import_csv.html')

@portfolio_blueprint.route('/export-csv')
def export_csv():
    return "CSV Export - Coming Soon"