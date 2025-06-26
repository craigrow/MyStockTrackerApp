"""Performance optimizations for test execution."""
import pytest
from tests.utils.factories import PortfolioFactory


@pytest.fixture(scope="class")
def class_portfolio_with_data(app):
    """Class-level portfolio fixture for expensive setup operations."""
    with app.app_context():
        portfolio = PortfolioFactory.create_with_price_data()
        yield portfolio
        # Cleanup handled by app fixture


@pytest.fixture(scope="session")
def session_app():
    """Session-level app fixture for maximum reuse."""
    from app import create_app, db
    import tempfile
    import os
    
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    with app.app_context():
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


class TestDataCache:
    """Cache for expensive test data operations."""
    
    _cache = {}
    
    @classmethod
    def get_or_create(cls, key, factory_func):
        """Get cached data or create if not exists."""
        if key not in cls._cache:
            cls._cache[key] = factory_func()
        return cls._cache[key]
    
    @classmethod
    def clear(cls):
        """Clear the cache."""
        cls._cache.clear()