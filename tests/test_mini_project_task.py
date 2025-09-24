import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mini_project_task import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_get_students_empty(monkeypatch):
    # Mock load_data to return empty dict
    monkeypatch.setattr("mini_project_task.load_data", lambda: {})
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == {}


def test_create_student(monkeypatch):
    # Mock load_data and save_data
    monkeypatch.setattr("mini_project_task.load_data", lambda: {})
    monkeypatch.setattr("mini_project_task.save_data", lambda data: None)

    student_payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 20,
        "department": "CS",
        "CGPA": 3.5
    }

    response = client.post("/create_student", json=student_payload)
    assert response.status_code == 201
    assert response.json()["message"] == "Student created successfully"


def test_get_student_not_found(monkeypatch):
    monkeypatch.setattr("mini_project_task.load_data", lambda: {})
    response = client.get("/student/nonexistent_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_sort_invalid(monkeypatch):
    monkeypatch.setattr("mini_project_task.load_data", lambda: {})
    response = client.get("/sort?sort_by=height&order=asc")
    assert response.status_code == 400
    assert "Sorting by name and age allowed only" in response.json()["detail"]
