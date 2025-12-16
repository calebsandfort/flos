import datetime
from common.models import StatusReport

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_read_status_reports_empty(client):
    response = client.get("/api/v1/status/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_status_reports_with_data(client, db_session):
    # Seed data
    report = StatusReport(
        facility_id="KDEN",
        status_type="RUNWAY",
        start_time=datetime.datetime.now(datetime.timezone.utc),
        raw_notam_text="Test Notam"
    )
    db_session.add(report)
    db_session.commit()
    
    response = client.get("/api/v1/status/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["facility_id"] == "KDEN"
    assert data[0]["report_id"] is not None

def test_read_single_status_report(client, db_session):
    # Seed data
    report = StatusReport(
        facility_id="KSFO",
        status_type="COMM",
        start_time=datetime.datetime.now(datetime.timezone.utc)
    )
    db_session.add(report)
    db_session.commit()
    report_id = report.report_id
    
    # Test Existing
    response = client.get(f"/api/v1/status/{report_id}")
    assert response.status_code == 200
    assert response.json()["facility_id"] == "KSFO"

    # Test Non-Existing
    response = client.get(f"/api/v1/status/{report_id + 999}")
    assert response.status_code == 404
