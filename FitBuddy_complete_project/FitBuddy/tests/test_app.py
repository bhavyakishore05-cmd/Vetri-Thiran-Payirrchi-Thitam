import os
from pathlib import Path
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = "sqlite:///./data/test_fitbuddy.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_module():
    Path("data/test_fitbuddy.db").unlink(missing_ok=True)

def test_home():
    r=client.get("/")
    assert r.status_code==200 and "FitBuddy" in r.text

def test_health():
    r=client.get("/api/health")
    assert r.status_code==200 and r.json()["status"]=="ok"

def test_generate():
    r=client.post("/api/plans",json={"name":"Test User","user_id":"test001","age":20,"weight":60,"goal":"general wellness","intensity":"medium"})
    assert r.status_code==200
    assert "Day 1" in r.json()["workout_plan"]

def test_feedback():
    r=client.post("/api/plans/test001/feedback",json={"feedback":"Add more cardio and keep one recovery day."})
    assert r.status_code==200 and r.json()["updated"] is True

def test_users():
    r=client.get("/api/users")
    assert any(x["user_id"]=="test001" for x in r.json())

def test_delete():
    r=client.delete("/api/users/test001")
    assert r.status_code==200
