from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import StockTransaction
from datetime import datetime, date

portfolio_blueprint = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio_blueprint.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Portfolio name is required.', 'error')
                return render_template('portfolio/create.html')
            
            portfolio_service = PortfolioService()
            portfolio = portfolio_service.create_portfolio(
                name=name,
                description=description or None,
                user_id="default_user"  # For now, use a default user
            )
            
            flash(f'Portfolio "{name}" created successfully!', 'success')
            return redirect(url_for('main.dashboard', portfolio_id=portfolio.id))
            
        except Exception as e:
            flash(f'Error creating portfolio: {str(e)}', 'error')
    
    return render_template('portfolio/create.html')

@portfolio_blueprint.route('/transactions')
def transactions():
    portfolio_service = PortfolioService()
    portfolios = portfolio_service.get_all_portfolios()
    
    # Get current portfolio
    portfolio_id = request.args.get('portfolio_id')
    current_portfolio = None
    all_transactions = []
    
    if portfolio_id:
        current_portfolio = portfolio_service.get_portfolio(portfolio_id)
        if current_portfolio:
            all_transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    elif portfolios:
        current_portfolio = portfolios[0]
        all_transactions = portfolio_service.get_portfolio_transactions(current_portfolio.id)
    
    return render_template('portfolio/transactions.html',
                         portfolios=portfolios,
                         current_portfolio=current_portfolio,
                         transactions=all_transactions)

@portfolio_blueprint.route('/dividends')
def dividends():
    portfolio_service = PortfolioService()
    portfolios = portfolio_service.get_all_portfolios()
    
    # Get current portfolio
    portfolio_id = request.args.get('portfolio_id')
    current_portfolio = None
    all_dividends = []
    
    if portfolio_id:
        current_portfolio = portfolio_service.get_portfolio(portfolio_id)
        if current_portfolio:
            all_dividends = portfolio_service.get_portfolio_dividends(portfolio_id)
    elif portfolios:
        current_portfolio = portfolios[0]
        all_dividends = portfolio_service.get_portfolio_dividends(current_portfolio.id)
    
    # Sort dividends by date (most recent first)
    all_dividends.sort(key=lambda d: d.payment_date, reverse=True)
    
    return render_template('portfolio/dividends.html',
                         portfolios=portfolios,
                         current_portfolio=current_portfolio,
                         dividends=all_dividends)

@portfolio_blueprint.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    portfolio_service = PortfolioService()
    portfolios = portfolio_service.get_all_portfolios()
    
    if request.method == 'POST':
        try:
            # Get form data
            portfolio_id = request.form['portfolio_id']
            ticker = request.form['ticker'].upper().strip()
            transaction_type = request.form['transaction_type']
            transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            price_per_share = float(request.form['price_per_share'])
            shares = float(request.form['shares'])
            
            # Validate data
            if not portfolio_id or not ticker or not transaction_type:
                flash('All fields are required.', 'error')
                return render_template('portfolio/add_transaction.html', 
                                     portfolios=portfolios, 
                                     current_portfolio_id=portfolio_id,
                                     today=date.today().isoformat())
            
            if price_per_share <= 0 or shares <= 0:
                flash('Price and shares must be positive numbers.', 'error')
                return render_template('portfolio/add_transaction.html', 
                                     portfolios=portfolios, 
                                     current_portfolio_id=portfolio_id,
                                     today=date.today().isoformat())
            
            # Add transaction
            transaction = portfolio_service.add_transaction(
                portfolio_id=portfolio_id,
                ticker=ticker,
                transaction_type=transaction_type,
                date=transaction_date,
                price_per_share=price_per_share,
                shares=shares
            )
            
            flash(f'Transaction added successfully: {transaction_type} {shares} shares of {ticker}', 'success')
            return redirect(url_for('main.dashboard', portfolio_id=portfolio_id))
            
        except ValueError as e:
            flash('Invalid number format. Please check your inputs.', 'error')
        except Exception as e:
            flash(f'Error adding transaction: {str(e)}', 'error')
    
    # GET request or form error
    current_portfolio_id = request.args.get('portfolio_id')
    return render_template('portfolio/add_transaction.html', 
                         portfolios=portfolios, 
                         current_portfolio_id=current_portfolio_id,
                         today=date.today().isoformat())

@portfolio_blueprint.route('/add-dividend', methods=['GET', 'POST'])
def add_dividend():
    portfolio_service = PortfolioService()
    portfolios = portfolio_service.get_all_portfolios()
    
    if request.method == 'POST':
        try:
            # Get form data
            portfolio_id = request.form['portfolio_id']
            ticker = request.form['ticker'].upper().strip()
            payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
            total_amount = float(request.form['total_amount'])
            
            # Validate data
            if not portfolio_id or not ticker:
                flash('All fields are required.', 'error')
                return render_template('portfolio/add_dividend.html', 
                                     portfolios=portfolios, 
                                     current_portfolio_id=portfolio_id,
                                     today=date.today().isoformat())
            
            if total_amount <= 0:
                flash('Dividend amount must be positive.', 'error')
                return render_template('portfolio/add_dividend.html', 
                                     portfolios=portfolios, 
                                     current_portfolio_id=portfolio_id,
                                     today=date.today().isoformat())
            
            # Add dividend
            dividend = portfolio_service.add_dividend(
                portfolio_id=portfolio_id,
                ticker=ticker,
                payment_date=payment_date,
                total_amount=total_amount
            )
            
            flash(f'Dividend added successfully: ${total_amount:.2f} from {ticker}', 'success')
            return redirect(url_for('main.dashboard', portfolio_id=portfolio_id))
            
        except ValueError as e:
            flash('Invalid number format. Please check your inputs.', 'error')
        except Exception as e:
            flash(f'Error adding dividend: {str(e)}', 'error')
    
    # GET request or form error
    current_portfolio_id = request.args.get('portfolio_id')
    return render_template('portfolio/add_dividend.html', 
                         portfolios=portfolios, 
                         current_portfolio_id=current_portfolio_id,
                         today=date.today().isoformat())

@portfolio_blueprint.route('/import-csv', methods=['GET', 'POST'])
def import_csv():
    portfolio_service = PortfolioService()
    portfolios = portfolio_service.get_all_portfolios()
    
    if request.method == 'POST':
        try:
            portfolio_id = request.form['portfolio_id']
            csv_file = request.files['csv_file']
            import_type = request.form.get('import_type', 'transactions')
            
            if not portfolio_id or not csv_file:
                flash('Portfolio and CSV file are required.', 'error')
                return render_template('portfolio/import_csv.html', portfolios=portfolios)
            
            from app.services.data_loader import DataLoader
            import csv
            import io
            
            # Read CSV content and handle BOM
            csv_content = csv_file.read().decode('utf-8-sig')  # Handles BOM automatically
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            csv_data = list(csv_reader)
            
            data_loader = DataLoader()
            
            if import_type == 'transactions':
                imported_count = data_loader.import_transactions_from_csv(portfolio_id, csv_data)
                if imported_count > 0:
                    flash(f'Successfully imported {imported_count} transactions from CSV file.', 'success')
                else:
                    error_msg = 'No transactions were imported. '
                    if hasattr(data_loader, '_last_import_errors'):
                        error_msg += f'Errors: {" | ".join(data_loader._last_import_errors[:3])}'
                    else:
                        error_msg += 'Please check your CSV format and data.'
                    flash(error_msg, 'warning')
            elif import_type == 'dividends':
                imported_count = data_loader.import_dividends_from_csv(portfolio_id, csv_data)
                if imported_count > 0:
                    flash(f'Successfully imported {imported_count} dividends from CSV file.', 'success')
                else:
                    error_msg = 'No dividends were imported. '
                    if hasattr(data_loader, '_last_import_errors'):
                        error_msg += f'Errors: {" | ".join(data_loader._last_import_errors[:3])}'
                    else:
                        error_msg += 'Please check your CSV format and data.'
                    flash(error_msg, 'warning')
            else:
                flash('Invalid import type.', 'error')
                return render_template('portfolio/import_csv.html', portfolios=portfolios)
            
            return redirect(url_for('main.dashboard', portfolio_id=portfolio_id))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')
    
    current_portfolio_id = request.args.get('portfolio_id')
    return render_template('portfolio/import_csv.html', 
                         portfolios=portfolios,
                         current_portfolio_id=current_portfolio_id)

@portfolio_blueprint.route('/export-csv')
def export_csv():
    return "CSV Export - Coming Soon"

@portfolio_blueprint.route('/delete-transaction/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction via API"""
    try:
        portfolio_service = PortfolioService()
        
        # Get transaction to find portfolio_id
        transaction = StockTransaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        # Delete transaction
        success = portfolio_service.delete_transaction(transaction_id, transaction.portfolio_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Transaction deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete transaction'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error deleting transaction: {str(e)}'
        }), 500