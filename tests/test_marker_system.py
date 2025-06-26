"""Test the pytest marker system for test categorization."""
import pytest


@pytest.mark.fast
def test_marker_system_fast():
    """Test that fast marker works correctly."""
    assert True


@pytest.mark.slow
def test_marker_system_slow():
    """Test that slow marker works correctly."""
    assert True


@pytest.mark.ui
def test_marker_system_ui():
    """Test that ui marker works correctly."""
    assert True


@pytest.mark.api
def test_marker_system_api():
    """Test that api marker works correctly."""
    assert True


@pytest.mark.database
def test_marker_system_database():
    """Test that database marker works correctly."""
    assert True


def test_marker_system_unmarked():
    """Test that unmarked tests still work."""
    assert True