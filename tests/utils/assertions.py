"""Reusable test assertions for behavior-focused testing."""
import re
from bs4 import BeautifulSoup


def assert_response_success(response, expected_status=200):
    """Assert response is successful with expected status."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"


def assert_contains_text(response, text):
    """Assert response contains specific text."""
    assert text.encode() in response.data, f"Response does not contain '{text}'"


def assert_transaction_display(response, expected_transactions):
    """Assert transactions are displayed correctly in UI."""
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Find transaction rows (assuming they have data-ticker attributes)
    transaction_rows = soup.find_all(attrs={"data-ticker": True})
    
    assert len(transaction_rows) >= len(expected_transactions), \
        f"Expected at least {len(expected_transactions)} transactions, found {len(transaction_rows)}"
    
    # Check each expected transaction is displayed
    displayed_tickers = [row.get('data-ticker') for row in transaction_rows]
    for transaction in expected_transactions:
        ticker = transaction.ticker if hasattr(transaction, 'ticker') else transaction['ticker']
        assert ticker in displayed_tickers, f"Transaction for {ticker} not displayed"


def assert_metrics_boxes_present(response):
    """Assert metrics boxes are present in the UI."""
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Look for common metrics box patterns
    metrics_indicators = [
        soup.find_all(class_=re.compile(r'metric|stat|box')),
        soup.find_all(attrs={"data-metric": True}),
        soup.find_all('div', class_=re.compile(r'card|panel'))
    ]
    
    found_metrics = any(indicators for indicators in metrics_indicators)
    assert found_metrics, "No metrics boxes found in response"


def assert_sortable_table(response):
    """Assert table has sortable columns."""
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Look for sortable indicators
    sortable_headers = soup.find_all(attrs={"onclick": re.compile(r'sort')})
    sort_icons = soup.find_all(class_=re.compile(r'sort|fa-sort'))
    
    assert sortable_headers or sort_icons, "No sortable table elements found"


def assert_filter_controls(response, filter_types=None):
    """Assert filter controls are present."""
    if filter_types is None:
        filter_types = ['all', 'buy', 'sell']
    
    soup = BeautifulSoup(response.data, 'html.parser')
    
    for filter_type in filter_types:
        filter_element = soup.find(attrs={"onclick": re.compile(f"setFilter.*{filter_type}")})
        assert filter_element, f"Filter control for '{filter_type}' not found"


def assert_api_response_structure(response_data, required_fields):
    """Assert API response has required structure."""
    assert isinstance(response_data, dict), "Response should be a dictionary"
    
    for field in required_fields:
        assert field in response_data, f"Required field '{field}' missing from response"


def assert_portfolio_data(portfolio, expected_name=None, expected_user_id=None):
    """Assert portfolio has expected data."""
    if expected_name:
        assert portfolio.name == expected_name, f"Expected name '{expected_name}', got '{portfolio.name}'"
    
    if expected_user_id:
        assert portfolio.user_id == expected_user_id, f"Expected user_id '{expected_user_id}', got '{portfolio.user_id}'"
    
    assert portfolio.creation_date is not None, "Portfolio should have creation_date"
    assert portfolio.last_updated is not None, "Portfolio should have last_updated"


def assert_transaction_data(transaction, expected_ticker=None, expected_type=None, expected_shares=None):
    """Assert transaction has expected data."""
    if expected_ticker:
        assert transaction.ticker == expected_ticker, f"Expected ticker '{expected_ticker}', got '{transaction.ticker}'"
    
    if expected_type:
        assert transaction.transaction_type == expected_type, f"Expected type '{expected_type}', got '{transaction.transaction_type}'"
    
    if expected_shares:
        assert transaction.shares == expected_shares, f"Expected shares {expected_shares}, got {transaction.shares}"
    
    assert transaction.price_per_share > 0, "Transaction should have positive price"
    assert transaction.total_value > 0, "Transaction should have positive total value"