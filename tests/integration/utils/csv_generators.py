"""CSV test data generators for integration tests."""
import csv
import io
from datetime import date, timedelta
from decimal import Decimal


class CSVTestGenerator:
    """Generate realistic CSV test data for import testing."""
    
    @staticmethod
    def create_valid_transactions_csv():
        """Create CSV with valid transaction data."""
        csv_data = [
            ['Date', 'Ticker', 'Type', 'Shares', 'Price'],
            ['2023-01-15', 'AAPL', 'BUY', '10.0', '150.00'],
            ['2023-01-20', 'GOOGL', 'BUY', '2.0', '2500.00'],
            ['2023-02-01', 'MSFT', 'BUY', '5.0', '300.00'],
            ['2023-03-15', 'AAPL', 'SELL', '3.0', '180.00']
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_mixed_valid_invalid_csv():
        """Create CSV with mix of valid and invalid data."""
        csv_data = [
            ['Date', 'Ticker', 'Type', 'Shares', 'Price'],
            ['2023-01-15', 'AAPL', 'BUY', '10.0', '150.00'],  # Valid
            ['invalid-date', 'GOOGL', 'BUY', '2.0', '2500.00'],  # Invalid date
            ['2023-01-20', '', 'BUY', '5.0', '300.00'],  # Missing ticker
            ['2023-02-01', 'MSFT', 'INVALID', '5.0', '300.00'],  # Invalid type
            ['2023-02-15', 'TSLA', 'BUY', 'invalid', '800.00'],  # Invalid shares
            ['2023-03-01', 'AMZN', 'BUY', '1.0', '3000.00']  # Valid
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_duplicate_transactions_csv():
        """Create CSV with duplicate transactions."""
        csv_data = [
            ['Date', 'Ticker', 'Type', 'Shares', 'Price'],
            ['2023-01-15', 'AAPL', 'BUY', '10.0', '150.00'],
            ['2023-01-20', 'GOOGL', 'BUY', '2.0', '2500.00'],
            ['2023-01-15', 'AAPL', 'BUY', '10.0', '150.00'],  # Exact duplicate
            ['2023-02-01', 'MSFT', 'BUY', '5.0', '300.00']
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_large_transactions_csv(num_transactions=100):
        """Create large CSV for performance testing."""
        csv_data = [['Date', 'Ticker', 'Type', 'Shares', 'Price']]
        
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        base_date = date(2023, 1, 1)
        
        for i in range(num_transactions):
            transaction_date = base_date + timedelta(days=i % 365)
            ticker = tickers[i % len(tickers)]
            transaction_type = 'BUY' if i % 4 != 0 else 'SELL'
            shares = str(float(1 + (i % 10)))
            price = str(float(100 + (i % 500)))
            
            csv_data.append([
                transaction_date.strftime('%Y-%m-%d'),
                ticker,
                transaction_type,
                shares,
                price
            ])
        
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_valid_dividends_csv():
        """Create CSV with valid dividend data."""
        csv_data = [
            ['Date', 'Ticker', 'Amount'],
            ['2023-03-15', 'AAPL', '25.50'],
            ['2023-04-20', 'GOOGL', '15.75'],
            ['2023-06-15', 'AAPL', '28.00']
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_mixed_dividends_csv():
        """Create CSV with mix of valid and invalid dividend data."""
        csv_data = [
            ['Date', 'Ticker', 'Amount'],
            ['2023-03-15', 'AAPL', '25.50'],  # Valid
            ['invalid-date', 'GOOGL', '15.75'],  # Invalid date
            ['2023-04-20', '', '20.00'],  # Missing ticker
            ['2023-06-15', 'MSFT', 'invalid'],  # Invalid amount
            ['2023-07-01', 'TSLA', '30.00']  # Valid
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def create_csv_with_errors_in_middle():
        """Create CSV with errors in the middle for partial import testing."""
        csv_data = [
            ['Date', 'Ticker', 'Type', 'Shares', 'Price'],
            ['2023-01-15', 'AAPL', 'BUY', '10.0', '150.00'],  # Valid
            ['2023-01-20', 'GOOGL', 'BUY', '2.0', '2500.00'],  # Valid
            ['2023-01-25', 'MSFT', 'BUY', '5.0', '300.00'],  # Valid
            ['invalid-date', 'ERROR', 'BUY', 'bad', 'data'],  # Error row
            ['2023-02-01', 'AMZN', 'BUY', '1.0', '3000.00'],  # Valid
            ['2023-02-15', 'TSLA', 'BUY', '2.0', '800.00']  # Valid
        ]
        return CSVTestGenerator._create_csv_string(csv_data)
    
    @staticmethod
    def _create_csv_string(data):
        """Convert data array to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        for row in data:
            writer.writerow(row)
        return output.getvalue()
    
    @staticmethod
    def save_csv_to_file(csv_content, filename):
        """Save CSV content to a temporary file."""
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', newline='') as f:
            f.write(csv_content)
        
        return file_path