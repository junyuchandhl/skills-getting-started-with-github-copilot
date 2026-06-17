import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure repository root is on the import path for src.app
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.app import activities, app  # noqa: E402

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_new_participant():
    new_email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": new_email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    existing_email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_participant():
    participant_email = "john@mergington.edu"
    response = client.delete(
        "/activities/Gym%20Class/participants",
        params={"email": participant_email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from Gym Class"
    assert participant_email not in activities["Gym Class"]["participants"]


def test_unregister_missing_participant_returns_404():
    missing_email = "missing@mergington.edu"
    response = client.delete(
        "/activities/Gym%20Class/participants",
        params={"email": missing_email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
