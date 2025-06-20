# MyStockTrackerApp - Implementation Plan

## 1. Overview

This implementation plan outlines the approach for developing the MyStockTrackerApp, with particular focus on Phase 1 (core functionality). The plan includes project setup, development priorities, implementation sequences, and deployment processes. The goal is to deliver a working application that satisfies the requirements while optimizing for the Heroku free tier constraints.

## 2. Development Environment Setup

### 2.1 Local Development Environment

#### Required Tools
- **Python 3.9+**: Core programming language
- **Visual Studio Code**: Primary IDE
- **Claude Code**: AI assistant for code generation and debugging
- **Git**: Version control system
- **GitHub**: Repository hosting
- **SQLite**: Local database

#### Environment Setup Steps
1. **Create a GitHub repository**: `MyStockTrackerApp`
2. **Create a local Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install core dependencies**:
   ```bash
   pip install flask flask-sqlalchemy pandas requests yfinance gunicorn
   pip install pytest pytest-flask  # For testing
   pip install python-dotenv  # For environment variables
   ```
4. **Configure VS Code with Claude Code extension**:
   - Install Claude Code extension
   - Set up project-specific settings for Python linting and formatting

### 2.2 Project Structure

```
MyStockTrackerApp/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Configuration settings
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   ├── portfolio.py      # Portfolio models
│   │   ├── stock.py          # Stock and transaction models
│   │   └── price.py          # Price history models
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── portfolio_service.py
│   │   ├── price_service.py
│   │   └── data_loader.py    # CSV import/export
│   ├── static/               # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── portfolio/
│   │   └── transactions/
│   ├── views/                # Route handlers
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes
│   │   ├── portfolio.py      # Portfolio routes
│   │   └── api.py            # API routes
│   └── util/                 # Utility functions
│       ├── __init__.py
│       ├── validators.py     # Input validation
│       └── calculators.py    # Financial calculations
├── docs/                     # Design documentation
│   ├── requirements/         # Requirements specifications
│   ├── design/               # Design documents
│   │   ├── high_level_design.md
│   │   ├── price_service_design.md
│   │   ├── portfolio_service_design.md
│   │   └── data_model_diagram.md
│   ├── ui/                   # UI mockups and wireframes
│   │   └── ui_mockups.md
│   └── implementation/       # Implementation plans
│       └── implementation_plan.md
├── migrations/               # Database migrations
├── tests/                    # Test cases
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures
│   ├── test_models.py        # Model tests
│   ├── test_services.py      # Service tests
│   └── test_views.py         # Route tests
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## 3. Development Phases and Milestones

### Phase 1: Core Functionality (8-10 weeks)

#### Milestone 1: Project Setup and Data Model (Week 1-2)
- Set up development environment
- Create GitHub repository
- Implement database models
- Create database migration scripts
- Implement basic portfolio CRUD operations
- Set up test framework

#### Milestone 2: Price Service Implementation (Week 3-4)
- Implement Yahoo Finance API client
- Create price caching mechanism
- Implement cache invalidation policies
- Create price history storage
- Set up logging for API calls

#### Milestone 3: Portfolio Service Implementation (Week 4-5)
- Implement transaction management
- Set up cash balance tracking
- Create dividend handling
- Implement performance calculators
- Develop transaction import/export

#### Milestone 4: Core UI Implementation (Week 6-7)
- Create base templates and layout
- Implement dashboard view
- Create transaction entry forms
- Implement portfolio selector
- Set up activity log display

#### Milestone 5: CSV Import and Primary Visualization (Week 8-10)
- Implement CSV import functionality
- Develop portfolio performance chart
- Implement basic data tables
- Create transaction history displays
- Finalize Phase 1 features

### Phase 2: Visualization Implementation (Future)

#### Milestone 1: Additional Visualizations
- Implement investment & gains stacked bar chart
- Create performance distribution bar chart
- Develop detailed portfolio table with sorting/filtering

#### Milestone 2: Data Table Enhancements
- Add advanced filtering
- Implement multi-column sorting
- Create bulk edit functionality

### Phase 3: Advanced Features (Future)

#### Milestone 1: Advanced Visualizations
- Implement age-based performance pie charts
- Create investment distribution heatmap
- Develop gain distribution heatmap

#### Milestone 2: Enhanced Analytics
- Add advanced performance metrics
- Implement custom time period analysis
- Create performance report generation

## 4. Phase 1 Implementation Priorities

### 4.1 Critical Path Components

1. **Database Models and Schema**: Foundation for all data operations
2. **Price Service**: Critical for performance calculations and visualizations
3. **Portfolio Service**: Core business logic
4. **Dashboard UI**: Main user interface
5. **CSV Import**: Key functionality for user adoption

### 4.2 Task Breakdown for Phase 1

#### Week 1: Project Setup
- [x] Create GitHub repository
- [ ] Set up project structure
- [ ] Configure development environment
- [ ] Create initial README documentation
- [ ] Set up test framework

#### Week 2: Data Models
- [ ] Implement User model
- [ ] Implement Portfolio model
- [ ] Implement StockTransaction model
- [ ] Implement Dividend model
- [ ] Implement Stock and ETF models
- [ ] Implement PriceHistory model
- [ ] Create database initialization scripts
- [ ] Write model unit tests

#### Week 3: Price Service - Part 1
- [ ] Implement Yahoo Finance API client
- [ ] Create price data retrieval functions
- [ ] Implement ticker validation
- [ ] Create price cache mechanism
- [ ] Write tests for API client

#### Week 4: Price Service - Part 2
- [ ] Implement cache invalidation policies
- [ ] Create batch request optimization
- [ ] Implement retry handler with exponential backoff
- [ ] Add logging for API calls and cache operations
- [ ] Create data validator for price data
- [ ] Write tests for caching and optimization

#### Week 4-5: Portfolio Service - Part 1
- [ ] Implement portfolio CRUD operations
- [ ] Create transaction management functions
- [ ] Implement dividend handling
- [ ] Create cash balance tracking
- [ ] Write tests for portfolio operations

#### Week 5-6: Portfolio Service - Part 2
- [ ] Implement performance calculation algorithms
- [ ] Create ETF comparison functionality
- [ ] Implement age-based performance metrics
- [ ] Set up visualization data preparation
- [ ] Write tests for performance calculations

#### Week 6-7: Core UI - Part 1
- [ ] Create base templates and layout
- [ ] Implement responsive design framework
- [ ] Create navigation components
- [ ] Implement portfolio selector
- [ ] Create dashboard view structure

#### Week 7-8: Core UI - Part 2
- [ ] Implement transaction forms
- [ ] Create portfolio list views
- [ ] Implement stock detail views
- [ ] Create activity log display
- [ ] Add form validation

#### Week 8-9: CSV Import and Export
- [ ] Design CSV format
- [ ] Implement CSV parser
- [ ] Create validation for imported data
- [ ] Implement duplicate detection
- [ ] Create import UI
- [ ] Add export functionality
- [ ] Write tests for import/export

#### Week 9-10: Primary Visualization
- [ ] Implement Chart.js integration
- [ ] Create portfolio performance chart
- [ ] Add time period selection
- [ ] Implement ETF comparison toggle
- [ ] Create transaction table views
- [ ] Write tests for visualization components

#### Week 10: Integration and Polish
- [ ] Final integration testing
- [ ] Performance optimization
- [ ] Bug fixing
- [ ] Documentation
- [ ] Prepare for deployment

## 5. Implementation Approach for Key Components

### 5.1 Price Service Implementation

The Price Service is critical for accurate performance tracking and will be implemented with careful attention to API rate limits:

1. **Yahoo Finance API Client**:
   - Implement using the `yfinance` library
   - Add rate limiting awareness
   - Create a clean interface for price queries

2. **Caching Mechanism**:
   - Implement SQLite-based price storage
   - Create tiered freshness policies
   - Implement cache invalidation logic

3. **Error Handling**:
   - Implement exponential backoff for retries
   - Create circuit breaker for API failures
   - Add fallback to cached data when API is unavailable

#### Code Sample: Cache Manager
```python
class CacheManager:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def get_price(self, ticker, date=None):
        """Get price from cache if available and fresh enough"""
        if date is None:  # Current price
            return self._get_current_price(ticker)
        else:
            return self._get_historical_price(ticker, date)
    
    def _get_current_price(self, ticker):
        # Check cache for recent price
        current_time = datetime.now()
        market_hours = self._is_market_hours(current_time)
        
        # Define freshness threshold based on market hours
        if market_hours:
            threshold = current_time - timedelta(minutes=5)  # 5 min during market
        else:
            threshold = current_time - timedelta(minutes=30)  # 30 min after hours
        
        # Query the database for recent price
        query = """
            SELECT close_price, price_timestamp, is_intraday
            FROM PriceCache
            WHERE ticker = ? AND last_updated > ?
            ORDER BY price_timestamp DESC
            LIMIT 1
        """
        result = self.db.execute(query, (ticker, threshold.isoformat())).fetchone()
        
        if result:
            return {
                'ticker': ticker,
                'price': result['close_price'],
                'timestamp': result['price_timestamp'],
                'is_intraday': result['is_intraday'],
                'from_cache': True
            }
        return None
```

### 5.2 Portfolio Service Implementation

The Portfolio Service manages user portfolios and calculates performance metrics:

1. **Transaction Management**:
   - Implement CRUD operations for transactions
   - Support fractional shares
   - Track cash balance changes

2. **Performance Calculator**:
   - Implement IRR calculation for stock performance
   - Create ETF comparison calculations
   - Support different time periods

3. **CSV Import/Export**:
   - Create parser for CSV files
   - Implement validation and duplicate detection
   - Support different import modes

#### Code Sample: Performance Calculator
```python
class PerformanceCalculator:
    def __init__(self, price_service):
        self.price_service = price_service
        
    def calculate_transaction_performance(self, transaction, current_date=None):
        """Calculate performance for a single transaction"""
        if current_date is None:
            current_date = datetime.now().date()
            
        # Get current price
        current_price = self.price_service.get_price(transaction.ticker)
        
        # Calculate gain/loss
        current_value = transaction.shares * current_price['price']
        cost_basis = transaction.shares * transaction.price_per_share
        gain_loss = current_value - cost_basis
        percent_change = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        # Calculate ETF performance for comparison
        etf_performance = self._calculate_etf_comparison(
            transaction.ticker, 
            transaction.date,
            current_date,
            cost_basis
        )
        
        return {
            'transaction_id': transaction.id,
            'ticker': transaction.ticker,
            'shares': transaction.shares,
            'cost_basis': cost_basis,
            'current_value': current_value,
            'gain_loss': gain_loss,
            'percent_change': percent_change,
            'vs_sp500': percent_change - etf_performance['voo_percent'],
            'vs_nasdaq': percent_change - etf_performance['qqq_percent'],
            'etf_performance': etf_performance
        }
```

### 5.3 User Interface Implementation

The UI will be implemented with a mobile-first approach:

1. **Flask Templates**:
   - Create base templates with responsive design
   - Implement Jinja2 for server-side rendering
   - Create partial templates for reusable components

2. **JavaScript Functionality**:
   - Use minimal JavaScript for interactivity
   - Implement Chart.js for visualizations
   - Create form validation and dynamic updates

3. **Progressive Enhancement**:
   - Ensure core functionality works without JavaScript
   - Add enhanced features when JavaScript is available

#### Code Sample: Portfolio Performance Chart
```javascript
function initPortfolioChart(chartData) {
    const ctx = document.getElementById('portfolioPerformanceChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.dates,
            datasets: [
                {
                    label: 'Portfolio',
                    data: chartData.portfolio_values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'S&P 500 (VOO)',
                    data: chartData.voo_values,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'NASDAQ (QQQ)',
                    data: chartData.qqq_values,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'USD'
                            }).format(context.raw);
                            return label;
                        }
                    }
                }
            }
        }
    });
    return chart;
}
```

## 6. Testing Strategy

### 6.1 Testing Levels

1. **Unit Tests**:
   - Test individual functions and methods
   - Focus on business logic and calculations
   - Use pytest for testing framework

2. **Integration Tests**:
   - Test interaction between components
   - Verify database operations
   - Test API client with mocked responses

3. **UI Tests**:
   - Test template rendering
   - Verify form submissions
   - Test user flows

### 6.2 Test Implementation

#### Setting Up Test Database

```python
@pytest.fixture
def app():
    app = create_app('testing')
    
    # Create test database and tables
    with app.app_context():
        db.create_all()
        
    yield app
    
    # Clean up after test
    with app.app_context():
        db.drop_all()
```

#### Sample Test Cases

```python
def test_price_cache(app):
    """Test price caching functionality"""
    with app.app_context():
        cache_manager = CacheManager(db.session)
        
        # Test adding price to cache
        cache_manager.add_price('AAPL', date.today(), 150.0)
        
        # Test retrieving from cache
        cached_price = cache_manager.get_price('AAPL')
        assert cached_price is not None
        assert cached_price['price'] == 150.0
        assert cached_price['from_cache'] is True

def test_portfolio_performance(app):
    """Test portfolio performance calculation"""
    with app.app_context():
        # Setup test data
        user = User(username='testuser')
        db.session.add(user)
        
        portfolio = Portfolio(user_id=user.id, name='Test Portfolio')
        db.session.add(portfolio)
        
        transaction = StockTransaction(
            portfolio_id=portfolio.id,
            ticker='AAPL',
            transaction_type='BUY',
            date=date.today() - timedelta(days=30),
            price_per_share=140.0,
            shares=10.0,
            total_value=1400.0
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Mock price service
        price_service = MagicMock()
        price_service.get_price.return_value = {'price': 150.0, 'timestamp': datetime.now()}
        
        # Calculate performance
        calculator = PerformanceCalculator(price_service)
        performance = calculator.calculate_portfolio_performance(portfolio.id)
        
        # Verify results
        assert performance['total_gain_percent'] == pytest.approx(7.14, 0.01)
        assert performance['current_value'] == 1500.0
```

## 7. Deployment Strategy

### 7.1 Heroku Setup

1. **Create Heroku App**:
   ```bash
   heroku create mystocktrackerapp
   ```

2. **Configure Environment Variables**:
   ```bash
   heroku config:set FLASK_APP=run.py
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   ```

3. **Setup Database**:
   - Use SQLite for initial deployment (Heroku's ephemeral filesystem requires special handling)
   - Implement regular CSV backups to preserve data

4. **Deployment Process**:
   ```bash
   git push heroku main
   ```

5. **Run Database Migrations**:
   ```bash
   heroku run flask db upgrade
   ```

### 7.2 Post-Deployment Setup

1. **Verify Application**:
   - Check all routes and functionality
   - Verify API integration
   - Test with real data

2. **Monitor Resources**:
   - Track dyno hours usage
   - Monitor API call frequency
   - Check for performance issues

3. **Schedule Maintenance Tasks**:
   - Setup backup process
   - Configure dyno wakeup to prevent sleeping (if needed)

## 8. Key Challenges and Mitigations

### 8.1 Yahoo Finance API Rate Limits

**Challenge**: Yahoo Finance API has unpublished rate limits that can change.

**Mitigation**:
- Implement aggressive caching
- Use exponential backoff for retries
- Batch requests where possible
- Monitor and log API usage patterns

### 8.2 Heroku Free Tier Limitations

**Challenge**: Heroku free tier has limitations including dyno sleeping after 30 minutes of inactivity.

**Mitigation**:
- Optimize cold start performance
- Implement regular CSV backups
- Create clear user messaging about app wake-up time
- Consider scheduled pings to prevent sleeping during market hours

### 8.3 Database Performance

**Challenge**: SQLite has limitations for concurrent access and larger datasets.

**Mitigation**:
- Implement efficient queries
- Use appropriate indexes
- Cache frequently accessed data
- Implement pagination for large datasets
- Monitor database size and performance

## 9. Conclusion

This implementation plan outlines a structured approach to developing the MyStockTrackerApp, with a particular focus on Phase 1 core functionality. By following the milestones and task breakdown, the development will progress in a logical sequence that enables early validation of critical components like the Price Service and Portfolio Service before completing the user interface.

The plan emphasizes:
- A mobile-first design approach
- Efficient use of the Heroku free tier
- Careful management of Yahoo Finance API rate limits
- Support for fractional shares throughout the application
- CSV import/export functionality
- Comprehensive testing strategy

After completing Phase 1, users will be able to track stock purchases, sales, and dividends across multiple portfolios, visualize portfolio performance against market ETFs, and import historical transaction data via CSV.