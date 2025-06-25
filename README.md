# MyStockTrackerApp
A high-performance web application to track stock portfolio performance against market indices with real-time data and intelligent caching.

## 🚀 Key Features

### Performance & Optimization
- **90% Faster Loading** - Dashboard loads in 2-3 seconds vs 30+ seconds
- **Smart Caching Strategy** - Uses cached data for speed, fresh data when needed
- **Market-Aware Warnings** - Clear indicators when data is stale during market hours
- **On-Demand Refresh** - Manual price updates with "Refresh Prices" button

### Data Integrity
- **CSV Duplicate Detection** - Prevents portfolio value inflation from duplicate imports
- **Comprehensive Validation** - Data validation during CSV imports
- **Transaction History** - Complete audit trail of all portfolio changes

### Portfolio Management
- **Multi-Portfolio Support** - Track multiple investment portfolios
- **Real-Time Performance** - Compare against S&P 500 (VOO) and NASDAQ (QQQ)
- **Daily Change Tracking** - See how your portfolio performs vs market today
- **Dividend Tracking** - Record and track dividend payments
- **Fractional Shares** - Support for fractional share purchases

### User Experience
- **Responsive Design** - Works on desktop and mobile devices
- **Real-Time Activity Log** - See what's happening behind the scenes
- **Visual Performance Charts** - Interactive charts showing portfolio vs market performance
- **Data Freshness Indicators** - Yellow timer icons show when prices may be outdated

## 🎯 Live Demo
[View Live Application](https://mystocktrackerapp-0813547f83cf.herokuapp.com/)

## 📊 Performance Metrics
- **Dashboard Load Time**: 2-3 seconds (90% improvement)
- **Test Coverage**: 132 passing tests
- **Price Data**: 40,000+ cached historical prices
- **Duplicate Prevention**: 100% effective CSV import protection

## 🛠 Technology Stack
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Bootstrap 5, Chart.js for visualizations
- **APIs**: Yahoo Finance (yfinance) for real-time stock data
- **Deployment**: Heroku with automatic deployments
- **Testing**: pytest with 132 comprehensive tests

## 📈 Smart Data Management

### Intelligent Caching
- Cached price data for fast loading
- Automatic cache invalidation during market hours
- Background price updates when needed
- Efficient batch API calls to minimize rate limiting

### Market Awareness
- Detects when US stock market is open/closed
- Different warning messages for market hours vs after hours
- Prioritizes fresh data during trading hours
- Uses cached data for speed when market is closed

### Data Quality
- Duplicate transaction detection and prevention
- Data validation for all CSV imports
- Automatic data type conversion and cleaning
- Error handling with detailed feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (for production)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/craigrow/MyStockTrackerApp.git
cd MyStockTrackerApp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Run the application
flask run
```

### Environment Variables
```bash
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///portfolio.db  # For development
SECRET_KEY=your-secret-key-here
```

## 📊 Usage

### Creating Your First Portfolio
1. Navigate to the dashboard
2. Click "Create Portfolio"
3. Enter portfolio name and description
4. Start adding transactions

### Adding Transactions
- **Manual Entry**: Use the "Add Transaction" form
- **CSV Import**: Upload CSV files with transaction data
- **Supported Formats**: Date, Ticker, Type (BUY/SELL), Shares, Price

### CSV Import Format
```csv
Date,Ticker,Type,Shares,Price
2023-01-15,AAPL,BUY,10,150.25
2023-02-01,MSFT,BUY,5,200.50
```

### Monitoring Performance
- **Dashboard Overview**: See total value, gains/losses, daily changes
- **Holdings Table**: Current positions with real-time prices
- **Performance Chart**: Visual comparison with market indices
- **Activity Log**: Real-time updates on data refreshes

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Coverage Areas
- **Models**: Database schema and relationships
- **Services**: Business logic and calculations
- **API Endpoints**: REST API functionality
- **CSV Import**: Data validation and duplicate detection
- **Integration**: End-to-end workflow testing
- **Performance**: Caching and optimization features

### Current Test Status
- ✅ 132 tests passing
- ✅ 0 failures
- ✅ Comprehensive coverage of all features

## 🔧 API Endpoints

### Portfolio Management
- `GET /` - Dashboard with portfolio overview
- `POST /portfolio/create` - Create new portfolio
- `POST /portfolio/add-transaction` - Add transaction
- `POST /portfolio/import-csv` - Import CSV data

### Real-Time Data
- `GET /api/refresh-holdings/{portfolio_id}` - Refresh holdings data
- `GET /api/refresh-all-prices/{portfolio_id}` - Refresh all prices including ETFs
- `GET /api/price-update-progress` - Get background update status

## 🚀 Deployment

### Heroku Deployment
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-production-secret

# Deploy
git push heroku main

# Initialize database
heroku run flask db upgrade
```

## 📋 Recent Updates

### Performance Optimization (Latest)
- **90% faster dashboard loading** through intelligent caching
- **Smart data freshness detection** with market-aware warnings
- **On-demand price refresh** with "Refresh Prices" button
- **Background price updates** with progress tracking

### Data Integrity Improvements
- **CSV duplicate detection** prevents portfolio value inflation
- **Enhanced validation** for all data imports
- **Comprehensive test coverage** with 132 passing tests

### User Experience Enhancements
- **Real-time activity logging** shows system status
- **Visual data freshness indicators** (yellow timer icons)
- **Market-aware messaging** distinguishes trading hours vs after hours
- **Improved error handling** with detailed feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Follow PEP 8 style guidelines
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance API** for real-time stock data
- **Flask Community** for the excellent web framework
- **Bootstrap** for responsive UI components
- **Chart.js** for beautiful data visualizations

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for investors who want to track their portfolio performance against the market.**
