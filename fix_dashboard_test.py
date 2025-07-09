"""
Fix for dashboard caching test - create a class that supports both attribute and dictionary access
"""

class PortfolioStats(dict):
    """Dictionary that also supports attribute access for template compatibility"""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'PortfolioStats' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value

# Test the fix
if __name__ == "__main__":
    # Create test data like the failing test
    stats = PortfolioStats({
        'current_value': 50000,
        'total_gain_loss': 5000,
        'gain_loss_percentage': 10.0,
        'voo_equivalent': 45000,
        'qqq_equivalent': 44000,
        'voo_gain_loss': 4000,
        'qqq_gain_loss': 3500,
        'voo_gain_loss_percentage': 8.9,
        'qqq_gain_loss_percentage': 8.0
    })
    
    # Test both access methods
    print("Dictionary access:", stats['current_value'])  # Should work
    print("Attribute access:", stats.current_value)      # Should also work
    
    # Test template-style formatting
    print(f"Template format: ${stats.current_value:,.2f}")  # Should work without MagicMock error