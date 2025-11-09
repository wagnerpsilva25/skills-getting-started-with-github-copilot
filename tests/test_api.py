import sys
import pathlib

# Ensure src is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_remove_flow():
    activity = "Chess Club"
    email = "pytest.user@example.com"

    # Ensure clean state (ignore errors)
    client.delete(f"/activities/{activity}/participants?email={email}")

    # Signup should succeed
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Participant should appear in GET
    r2 = client.get("/activities")
    participants = r2.json()[activity]["participants"]
    assert email in participants

    # Remove participant
    r3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r3.status_code == 200

    # Confirm removed
    r4 = client.get("/activities")
    assert email not in r4.json()[activity]["participants"]


def test_duplicate_signup_fails():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already present in initial data

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 400


def test_remove_nonexistent_participant_fails():
    activity = "Chess Club"
    email = "no-such-user@example.com"

    r = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r.status_code == 400
