import pytest
from fastapi.testclient import TestClient
from main import app
import sqlite3
import os

from users.test_users import setup_teardown as users_setup_teardown # Make sure the user exists first in case order gets changed, although tests should be independent

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_teardown():
    # Setup - ensure test user is there for session authentication
    client.post(
        "/users/register",
        data={
            "fullname": "Test User",
            "email": "test_user@example.com",
            "mobile": "1234567890",
            "password": "testpassword",
            "gender": "Other",
            "city": "Test City"
        },
        follow_redirects=False
    )

    yield
    # Teardown - remove test data if needed
    conn = sqlite3.connect("test_app.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE email='test_employee@example.com'")
    cursor.execute("DELETE FROM users WHERE email='test_user@example.com'")
    conn.commit()
    conn.close()

@pytest.fixture(autouse=True)
def wipe_cookies():
    client.cookies.clear()

def test_add_employee_authorized(setup_teardown):
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    response = client.post(
        "/employees/add",
        data={
            "fullname": "Test Employee",
            "email": "test_employee@example.com",
            "mobile": "1234567890",
            "department": "Engineering",
            "designation": "Software Engineer",
            "city": "Test City"
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/employees/index?msg=Employee+added+successfully"

def test_employees_index():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    response = client.get("/employees/index")
    assert response.status_code == 200
    assert "Test Employee" in response.text

def test_api_edit_employee():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    conn = sqlite3.connect("test_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id FROM employees WHERE email='test_employee@example.com'")
    emp_id = cursor.fetchone()[0]
    conn.close()

    response = client.post(
        f"/employees/api/edit/{emp_id}",
        json={
            "fullname": "Test Employee Updated",
            "email": "test_employee@example.com",
            "mobile": "0987654321",
            "department": "Engineering Updated",
            "designation": "Software Engineer",
            "city": "Updated City"
        }
    )
    assert response.status_code == 200

def test_api_delete_employee():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    conn = sqlite3.connect("test_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id FROM employees WHERE email='test_employee@example.com'")
    emp_id = cursor.fetchone()[0]
    conn.close()

    response = client.delete(f"/employees/api/delete/{emp_id}")
    assert response.status_code == 200
