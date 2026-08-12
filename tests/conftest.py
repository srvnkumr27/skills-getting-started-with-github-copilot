"""
Pytest configuration and fixtures for FastAPI tests.
Provides TestClient, clean activities state, and test constants.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Store the original activities state at module load time
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making HTTP requests to the app.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Auto-use fixture that resets the app's activities to clean state before each test.
    This runs automatically for every test function and ensures clean state.
    """
    # Clear and repopulate activities with original clean state
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Cleanup after test (ensure clean state for next test)
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


# Test constants for reuse across test functions
SAMPLE_EMAIL = "test@mergington.edu"
SAMPLE_EMAIL_2 = "test2@mergington.edu"
SAMPLE_ACTIVITY = "Chess Club"
INVALID_ACTIVITY = "Nonexistent Activity"
