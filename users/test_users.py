import pytest
from fastapi.testclient import TestClient
from main import app
import sqlite3
import os

# Initialize test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_teardown():
    yield
    # Teardown - remove test data if needed
    conn = sqlite3.connect("test_app.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email='test_user@example.com'")
    conn.commit()
    conn.close()

@pytest.fixture(autouse=True)
def wipe_cookies():
    client.cookies.clear()

def test_register_page(setup_teardown):
    response = client.get("/users/register")
    assert response.status_code == 200
    assert "Register" in response.text

def test_login_page():
    response = client.get("/users/login")
    assert response.status_code == 200
    assert "Login" in response.text

def test_register_user():
    response = client.post(
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
    assert response.status_code == 303
    assert response.headers["location"] == "/users/login?msg=Registered+successfully"

def test_login_user():
    response = client.post(
        "/users/login",
        data={
            "email": "test_user@example.com",
            "password": "testpassword"
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/users/index"
    assert "user_session" in response.cookies

def test_index_page_unauthorized():
    client.cookies.clear()
    response = client.get("/users/index", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/users/login"

def test_index_page_authorized():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    response = client.get("/users/index")
    assert response.status_code == 200
    assert "Test User" in response.text

def test_api_get_user():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    conn = sqlite3.connect("test_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email='test_user@example.com'")
    user_id = cursor.fetchone()[0]
    conn.close()

    response = client.get(f"/users/api/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_user@example.com"

def test_api_edit_user():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    conn = sqlite3.connect("test_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email='test_user@example.com'")
    user_id = cursor.fetchone()[0]
    conn.close()

    response = client.post(
        f"/users/api/edit/{user_id}",
        json={
            "fullname": "Test User Updated",
            "email": "test_user@example.com",
            "mobile": "0987654321",
            "gender": "Other",
            "city": "Updated City"
        }
    )
    assert response.status_code == 200

def test_add_user_page_authorized():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    response = client.get("/users/add")
    assert response.status_code == 200
    assert "Add New User" in response.text

def test_api_delete_user():
    client.post("/users/login", data={"email": "test_user@example.com", "password": "testpassword"})
    conn = sqlite3.connect("test_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email='test_user@example.com'")
    user_id = cursor.fetchone()[0]
    conn.close()

    response = client.delete(f"/users/api/delete/{user_id}")
    assert response.status_code == 200
