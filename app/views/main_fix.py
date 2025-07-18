def generate_chart_data(portfolio_id, portfolio_service, price_service):
    """Generate chart data for portfolio performance visualization"""
    transactions = portfolio_service.get_portfolio_transactions(portfolio_id)
    
    if not transactions:
        return {
            'dates': [],
            'portfolio_values': [],
            'voo_values': [],
            'qqq_values': []
        }
    
    # Get unique tickers and check if we have too many (performance optimization)
    tickers = list(set(t.ticker for t in transactions))
    print(f"[CHART] Portfolio has {len(tickers)} unique tickers: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
    
    # IMPORTANT: Completely remove the ticker limit check
    # This was causing empty chart data arrays
    
    # Get date range from first transaction to today
    end_date = date.today()
    start_date = min(t.date for t in transactions)
    
    # Get all unique tickers from transactions
    tickers = list(set(t.ticker for t in transactions))
    etf_tickers = ['VOO', 'QQQ']
    all_tickers = tickers + etf_tickers
    
    # Batch fetch price histories for all tickers
    print(f"[API] Batch fetching price histories for {len(all_tickers)} tickers...")
    price_histories = {}
    for ticker in all_tickers:
        price_histories[ticker] = get_ticker_price_dataframe(ticker, start_date, end_date)
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Calculate values efficiently
    dates = []
    portfolio_values = []
    voo_values = []
    qqq_values = []
    
    # Track cumulative holdings and ETF shares
    cumulative_holdings = {}
    cumulative_voo_shares = 0
    cumulative_qqq_shares = 0
    
    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        # Add any new transactions on this date
        for transaction in transactions:
            if transaction.date == current_date.date():
                if transaction.ticker not in cumulative_holdings:
                    cumulative_holdings[transaction.ticker] = 0
                
                if transaction.transaction_type == 'BUY':
                    cumulative_holdings[transaction.ticker] += transaction.shares
                    # Calculate equivalent ETF shares
                    voo_price = get_price_from_dataframe(price_histories.get('VOO'), date_str)
                    if voo_price:
                        cumulative_voo_shares += transaction.total_value / voo_price
                    
                    qqq_price = get_price_from_dataframe(price_histories.get('QQQ'), date_str)
                    if qqq_price:
                        cumulative_qqq_shares += transaction.total_value / qqq_price
                elif transaction.transaction_type == 'SELL':
                    cumulative_holdings[transaction.ticker] -= transaction.shares
        
        # Calculate portfolio value
        portfolio_value = 0
        for ticker, shares in cumulative_holdings.items():
            if shares > 0:
                price = get_price_from_dataframe(price_histories.get(ticker), date_str)
                if price:
                    portfolio_value += shares * price
        
        # Calculate ETF values
        voo_price = get_price_from_dataframe(price_histories.get('VOO'), date_str)
        voo_value = cumulative_voo_shares * voo_price if voo_price else 0
        
        qqq_price = get_price_from_dataframe(price_histories.get('QQQ'), date_str)
        qqq_value = cumulative_qqq_shares * qqq_price if qqq_price else 0
        
        portfolio_values.append(portfolio_value)
        voo_values.append(voo_value)
        qqq_values.append(qqq_value)
    
    return {
        'dates': dates,
        'portfolio_values': portfolio_values,
        'voo_values': voo_values,
        'qqq_values': qqq_values
    }