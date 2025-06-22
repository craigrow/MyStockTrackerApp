# MyStockTrackerApp - Deployment Guide

## Overview

This guide covers how to run MyStockTrackerApp both locally for development and in production on Heroku. The app is designed to work seamlessly in both environments with automatic configuration detection.

## Local Development

### Prerequisites
- Python 3.12+
- Virtual environment (venv)
- Git

### Setup & Running Locally

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/craigrow/MyStockTrackerApp.git
   cd MyStockTrackerApp_Q
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python run.py
   ```
   - App runs on `http://localhost:5001` (port 5001 to avoid macOS AirPlay conflict)
   - Uses SQLite database (`mystocktrackerapp-dev.db`)
   - Debug mode enabled for development
   - Database tables created automatically on first run

### Local Configuration
- **Environment**: DevelopmentConfig
- **Database**: SQLite (`sqlite:///mystocktrackerapp-dev.db`)
- **Debug Mode**: Enabled
- **Port**: 5001 (avoids macOS AirPlay Receiver on port 5000)

### Port 5000 Conflict (macOS)
On macOS, port 5000 is used by AirPlay Receiver. Solutions:
- **Recommended**: Use port 5001 (already configured)
- **Alternative**: Disable AirPlay in System Preferences > General > AirDrop & Handoff

## Heroku Production Deployment

### Prerequisites
- **Heroku CLI**: Download and install from https://devcenter.heroku.com/articles/heroku-cli
- **Heroku Account**: Sign up at https://heroku.com (free tier available)
- **Git Repository**: Your code must be in a git repository with changes committed
- **Credit Card**: Required for PostgreSQL addon (~$5/month for essential-0 plan)

### Deployment Files Required

1. **Procfile**:
   ```
   web: python run.py
   ```

2. **requirements.txt** (includes PostgreSQL support):
   ```
   # ... existing packages ...
   psycopg2-binary==2.9.9
   ```

3. **runtime.txt** (optional, deprecated):
   ```
   python-3.12.7
   ```

### Complete Deployment Steps

1. **Install Heroku CLI and Login**:
   ```bash
   # After installing Heroku CLI from the link above:
   heroku login
   # This will open your browser to authenticate
   ```

2. **Prepare Your Code**:
   ```bash
   # Ensure all changes are committed to git
   git add .
   git commit -m "Ready for Heroku deployment"
   ```

3. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   # Note: App name must be globally unique across all Heroku
   # If name is taken, try: heroku create your-app-name-2024
   # Or let Heroku generate a name: heroku create
   ```

4. **Add PostgreSQL Database** (~$5/month):
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   # This will add ~$5/month to your Heroku bill
   # Free tier doesn't include persistent databases
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set FLASK_ENV=production
   ```

6. **Deploy Your Code**:
   ```bash
   # If your code is on the 'devQ' branch:
   git push heroku devQ:main
   
   # If your code is on the 'main' branch:
   git push heroku main
   ```

7. **Initialize Database**:
   ```bash
   heroku run 'python -c "from app import create_app, db; from app.models.portfolio import Portfolio; app = create_app(); app.app_context().push(); db.create_all(); portfolio = Portfolio(id=\"default-portfolio\", user_id=\"default-user\", name=\"Main Portfolio\", description=\"Default portfolio\"); db.session.add(portfolio); db.session.commit(); print(\"Database setup complete!\")"'
   ```

8. **Verify Deployment**:
   ```bash
   # Check if app is running
   heroku ps
   
   # View your app in browser
   heroku open
   
   # Or visit: https://your-app-name.herokuapp.com
   ```

### Production Configuration
- **Environment**: ProductionConfig
- **Database**: PostgreSQL (via DATABASE_URL)
- **Debug Mode**: Disabled
- **Port**: Dynamic (set by Heroku via PORT environment variable)

## Configuration Details

### Environment Detection
The app automatically detects the environment:

```python
# Local Development
if not FLASK_ENV=production and not HEROKU env var:
    → DevelopmentConfig (SQLite, Debug=True)

# Production (Heroku)
if FLASK_ENV=production or HEROKU env var exists:
    → ProductionConfig (PostgreSQL, Debug=False)

# Testing
if config_name="testing":
    → TestingConfig (SQLite test DB)
```

### Database Configuration

**Local (SQLite)**:
- File: `mystocktrackerapp-dev.db`
- Location: Project root
- Auto-created on startup

**Production (PostgreSQL)**:
- URL: From `DATABASE_URL` environment variable
- Handles both `postgres://` and `postgresql://` URLs
- Persistent across deployments

### Key Differences: Local vs Production

| Aspect | Local Development | Heroku Production |
|--------|------------------|-------------------|
| **Database** | SQLite (file-based) | PostgreSQL (managed) |
| **Port** | 5001 (fixed) | Dynamic (Heroku-assigned) |
| **Debug Mode** | Enabled | Disabled |
| **Host** | 127.0.0.1 (localhost) | 0.0.0.0 (all interfaces) |
| **Environment** | DevelopmentConfig | ProductionConfig |
| **Data Persistence** | Local file | Cloud database |

## Troubleshooting

### Common Local Issues

1. **Port 5000 in use**:
   - Solution: App now uses port 5001 by default
   - Alternative: Disable macOS AirPlay Receiver

2. **Database not found**:
   - Solution: Database auto-created on first run
   - Check: Ensure write permissions in project directory

3. **Module not found**:
   - Solution: Ensure virtual environment is activated
   - Check: `pip install -r requirements.txt`

### Common Heroku Issues

1. **"App name is not available"**:
   - Solution: Choose a different name or let Heroku generate one
   - Try: `heroku create` (auto-generates unique name)

2. **"No such app" error**:
   - Solution: Make sure you're in the correct directory
   - Check: `heroku apps` to see your apps

3. **Internal Server Error**:
   - Check: `heroku logs --tail`
   - Common cause: Database tables not created
   - Solution: Run database initialization command (step 7)

4. **Database connection errors**:
   - Check: PostgreSQL addon is provisioned (`heroku addons`)
   - Verify: `heroku config` shows DATABASE_URL
   - Solution: Ensure FLASK_ENV=production is set

5. **"Permission denied" during git push**:
   - Solution: Make sure you're logged in (`heroku login`)
   - Check: `heroku auth:whoami`

6. **App not starting**:
   - Check: Procfile exists and is correct
   - Verify: requirements.txt includes all dependencies
   - Solution: Check `heroku logs --tail` for specific errors

7. **"Couldn't find that process type" error**:
   - Solution: Ensure Procfile is in root directory
   - Check: Procfile contains `web: python run.py`

## Testing the Deployment

### Local Testing
```bash
# Start the app
python run.py

# Test endpoints
curl http://localhost:5001/
curl http://localhost:5001/portfolio/default-portfolio
```

### Production Testing
```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Open app in browser
heroku open

# Or test with curl
curl https://your-app-name.herokuapp.com/

# Check database connection
heroku run python -c "from app import create_app, db; app = create_app(); print('Database connected successfully!')"
```

## Environment Variables

### Local Development
- No environment variables required
- Uses default development settings

### Heroku Production
- `DATABASE_URL`: Auto-set by PostgreSQL addon
- `FLASK_ENV=production`: Forces production config
- `PORT`: Auto-set by Heroku (dynamic)

## Database Management

### Local Database
- **Location**: `mystocktrackerapp-dev.db` in project root
- **Backup**: Copy the SQLite file
- **Reset**: Delete the file, restart app to recreate

### Production Database
- **Access**: `heroku pg:psql`
- **Backup**: `heroku pg:backups:capture`
- **Reset**: `heroku pg:reset DATABASE_URL --confirm your-app-name`

## Performance Considerations

### Local Development
- SQLite is sufficient for development
- No external dependencies
- Fast startup and testing

### Production
- PostgreSQL handles concurrent users
- Persistent data across deployments
- Automatic backups available
- Scales with Heroku dyno types

## Security Notes

### Local Development
- Debug mode exposes detailed errors
- SQLite file contains all data
- No external network access required

### Production
- Debug mode disabled
- Database credentials managed by Heroku
- HTTPS enforced by Heroku
- Environment variables for sensitive data

## Next Steps

After successful deployment:
1. **Monitor**: Use `heroku logs --tail` to monitor the app
2. **Scale**: Upgrade dyno types as needed
3. **Backup**: Set up regular database backups
4. **Domain**: Add custom domain if needed
5. **SSL**: Configure SSL certificate for custom domains

## Quick Start Checklist

### For Local Development:
- [ ] Python 3.12+ installed
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install requirements
- [ ] Run `python run.py`
- [ ] Visit `http://localhost:5001`

### For Heroku Deployment:
- [ ] Heroku CLI installed and logged in
- [ ] Code committed to git
- [ ] Create Heroku app
- [ ] Add PostgreSQL addon (~$5/month)
- [ ] Set FLASK_ENV=production
- [ ] Deploy with `git push heroku devQ:main`
- [ ] Initialize database
- [ ] Test with `heroku open`

## Summary

MyStockTrackerApp is designed for easy deployment in both environments:
- **Local**: Simple `python run.py` with SQLite (free)
- **Production**: Full PostgreSQL setup on Heroku (~$5/month for database)

The automatic environment detection ensures the app works optimally in each environment without manual configuration changes.

**Total Heroku Cost**: ~$5/month for PostgreSQL essential-0 plan (app dyno is free tier)