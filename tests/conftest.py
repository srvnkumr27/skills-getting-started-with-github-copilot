"""
Pytest configuration and fixtures for FastAPI tests.
Provides TestClient, clean activities state, and test constants.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making HTTP requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def clean_activities():
    """
    Provides a deep copy of the original activities dictionary.
    Ensures each test starts with a clean, known state.
    Prevents test interdependencies caused by state mutations.
    """
    return copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(clean_activities):
    """
    Auto-use fixture that resets the app's activities to clean state before each test.
    This runs automatically for every test function.
    """
    # Clear and repopulate activities with clean state
    activities.clear()
    activities.update(clean_activities)
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(clean_activities)


# Test constants for reuse across test functions
SAMPLE_EMAIL = "test@mergington.edu"
SAMPLE_EMAIL_2 = "test2@mergington.edu"
SAMPLE_ACTIVITY = "Chess Club"
INVALID_ACTIVITY = "Nonexistent Activity"
