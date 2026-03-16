import os
import pytest
import sqlite3

# Set this before any application imports occur!
os.environ["TESTING"] = "1"

from db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Attempt to clean up completely before tests begin
    if os.path.exists("test_app.db"):
        os.remove("test_app.db")
        
    init_db()  # Create schemas for test database
    
    yield
    
    # Teardown: delete the test database after the test session completes
    if os.path.exists("test_app.db"):
        os.remove("test_app.db")
