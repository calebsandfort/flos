import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Set env for testing (though we will override db session)
os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from common.database import Base
from common import models
from api.app.main import app, get_db

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Add dummy data
    report1 = models.StatusReport(
        facility_id="TEST",
        status_type="API_TEST",
        start_time=datetime.now(),
        raw_notam_text="Test Notam 1"
    )
    db.add(report1)
    db.commit()
    db.refresh(report1)
    db.close()
    return report1

def test_read_status_reports():
    setup_data()
    response = client.get("/api/v1/status/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["facility_id"] == "TEST"
    print("GET /api/v1/status/ PASSED")

def test_read_status_report_detail():
    report = setup_data() # This resets DB, so we get ID 1
    # We need to know the ID. Since we dropped tables, it should be 1.
    # But let's fetch list first to be sure
    list_resp = client.get("/api/v1/status/")
    rid = list_resp.json()[0]["report_id"]
    
    response = client.get(f"/api/v1/status/{rid}")
    assert response.status_code == 200
    assert response.json()["facility_id"] == "TEST"
    print(f"GET /api/v1/status/{rid} PASSED")
    
    # fail case
    response = client.get(f"/api/v1/status/9999")
    assert response.status_code == 404
    print("GET /api/v1/status/9999 (404) PASSED")

if __name__ == "__main__":
    try:
        print("Running API Tests...")
        test_read_status_reports()
        test_read_status_report_detail()
        print("ALL TESTS PASSED")
        # Cleanup
        if os.path.exists("test_api.db"):
            os.remove("test_api.db")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
