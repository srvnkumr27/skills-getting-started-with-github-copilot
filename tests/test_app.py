"""
Comprehensive test suite for the Mergington High School Activities API.
Tests all endpoints with success and error scenarios, state changes, and edge cases.
"""

import pytest
from tests.conftest import SAMPLE_EMAIL, SAMPLE_EMAIL_2, SAMPLE_ACTIVITY, INVALID_ACTIVITY


class TestRootEndpoint:
    """Tests for GET / endpoint - should redirect to static HTML."""
    
    def test_root_redirect(self, client):
        """Root path should redirect to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [307, 308]  # Temporary or permanent redirect
        assert "/static/index.html" in response.headers.get("location", "")


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint - retrieve all activities."""
    
    def test_get_all_activities(self, client):
        """GET /activities should return all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
    
    def test_activities_structure(self, client):
        """Each activity should have correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_chess_club_initial_state(self, client):
        """Chess Club should have 2 initial participants."""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Successfully signup a new participant."""
        response = client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert SAMPLE_EMAIL in data["message"]
        assert SAMPLE_ACTIVITY in data["message"]
    
    def test_signup_participant_added_to_list(self, client):
        """New participant should appear in activities list after signup."""
        # Signup
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        participants = activities[SAMPLE_ACTIVITY]["participants"]
        assert SAMPLE_EMAIL in participants
    
    def test_signup_duplicate_fails(self, client):
        """Attempting to signup twice for same activity should fail."""
        # First signup
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Second signup (duplicate)
        response = client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_not_found(self, client):
        """Signup to nonexistent activity should return 404."""
        response = client.post(
            f"/activities/{INVALID_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_participant_count_increases(self, client):
        """Participant count should increase after signup."""
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[SAMPLE_ACTIVITY]["participants"])
        
        # Signup
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Get new count
        response2 = client.get("/activities")
        new_count = len(response2.json()[SAMPLE_ACTIVITY]["participants"])
        
        assert new_count == initial_count + 1
    
    def test_signup_multiple_different_participants(self, client):
        """Multiple participants can signup for the same activity."""
        # First signup
        response1 = client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        assert response1.status_code == 200
        
        # Second signup (different email)
        response2 = client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL_2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        response3 = client.get("/activities")
        participants = response3.json()[SAMPLE_ACTIVITY]["participants"]
        assert SAMPLE_EMAIL in participants
        assert SAMPLE_EMAIL_2 in participants


class TestRemoveEndpoint:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""
    
    def test_remove_success(self, client):
        """Successfully remove a participant from activity."""
        # Setup: signup first
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Remove participant
        response = client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert SAMPLE_EMAIL in data["message"]
    
    def test_remove_participant_removed_from_list(self, client):
        """Removed participant should not appear in activities list."""
        # Setup: signup first
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Remove
        client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Verify participant is gone
        response = client.get("/activities")
        participants = response.json()[SAMPLE_ACTIVITY]["participants"]
        assert SAMPLE_EMAIL not in participants
    
    def test_remove_activity_not_found(self, client):
        """Remove from nonexistent activity should return 404."""
        response = client.delete(
            f"/activities/{INVALID_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_remove_participant_not_found(self, client):
        """Remove non-existent participant should return 400."""
        response = client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_remove_participant_count_decreases(self, client):
        """Participant count should decrease after removal."""
        # Setup: signup first
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        response1 = client.get("/activities")
        count_after_signup = len(response1.json()[SAMPLE_ACTIVITY]["participants"])
        
        # Remove
        client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        
        response2 = client.get("/activities")
        count_after_removal = len(response2.json()[SAMPLE_ACTIVITY]["participants"])
        
        assert count_after_removal == count_after_signup - 1
    
    def test_remove_then_resignup(self, client):
        """Should be able to re-signup after removal."""
        # Signup
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Remove
        client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Re-signup should succeed
        response = client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        assert response.status_code == 200
        
        # Verify back in list
        response = client.get("/activities")
        participants = response.json()[SAMPLE_ACTIVITY]["participants"]
        assert SAMPLE_EMAIL in participants


class TestCrossEndpointScenarios:
    """Tests for interactions between multiple endpoints."""
    
    def test_signup_then_get_activities_reflects_change(self, client):
        """GET /activities should immediately reflect signup changes."""
        # Signup
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Get activities immediately after
        response = client.get("/activities")
        participants = response.json()[SAMPLE_ACTIVITY]["participants"]
        
        # New participant should be visible
        assert SAMPLE_EMAIL in participants
    
    def test_remove_then_get_activities_reflects_change(self, client):
        """GET /activities should immediately reflect removal changes."""
        # Setup: signup first
        client.post(
            f"/activities/{SAMPLE_ACTIVITY}/signup",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Remove
        client.delete(
            f"/activities/{SAMPLE_ACTIVITY}/remove",
            params={"email": SAMPLE_EMAIL}
        )
        
        # Get activities immediately after
        response = client.get("/activities")
        participants = response.json()[SAMPLE_ACTIVITY]["participants"]
        
        # Removed participant should not be visible
        assert SAMPLE_EMAIL not in participants
    
    def test_multiple_activities_signup_independent(self, client):
        """Signups for different activities should be independent."""
        chess_email = "chess@mergington.edu"
        gym_email = "gym@mergington.edu"
        
        # Signup different emails to different activities
        client.post("/activities/Chess Club/signup", params={"email": chess_email})
        client.post("/activities/Gym Class/signup", params={"email": gym_email})
        
        response = client.get("/activities")
        activities = response.json()
        
        # Verify independent signups
        assert chess_email in activities["Chess Club"]["participants"]
        assert gym_email not in activities["Chess Club"]["participants"]
        assert gym_email in activities["Gym Class"]["participants"]
        assert chess_email not in activities["Gym Class"]["participants"]
