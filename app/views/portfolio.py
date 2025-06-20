from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.portfolio_service import PortfolioService
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
    return render_template('portfolio/transactions.html')

@portfolio_blueprint.route('/dividends')
def dividends():
    return render_template('portfolio/dividends.html')

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

@portfolio_blueprint.route('/import-csv')
def import_csv():
    return render_template('portfolio/import_csv.html')

@portfolio_blueprint.route('/export-csv')
def export_csv():
    return "CSV Export - Coming Soon"