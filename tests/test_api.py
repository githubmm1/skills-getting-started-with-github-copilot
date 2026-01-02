import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Check that we get a dictionary with activities
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_root_redirect():
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers.get("location", "")


def test_signup_success():
    """Test successful signup for an activity"""
    # First, get the initial participants count
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data["Chess Club"]["participants"])

    # Sign up a new student
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    updated_data = response.json()
    final_participants = len(updated_data["Chess Club"]["participants"])
    assert final_participants == initial_participants + 1
    assert "test@example.com" in updated_data["Chess Club"]["participants"]


def test_signup_duplicate():
    """Test signing up when already signed up"""
    # Sign up first time
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 200

    # Try to sign up again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity():
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonExistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First sign up
    client.post("/activities/Programming%20Class/signup?email=unregister@example.com")

    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = len(initial_data["Programming Class"]["participants"])

    # Unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]
    assert "Programming Class" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    final_participants = len(updated_data["Programming Class"]["participants"])
    assert final_participants == initial_participants - 1
    assert "unregister@example.com" not in updated_data["Programming Class"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering when not signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity():
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]