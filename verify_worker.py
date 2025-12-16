import os
import sys

# Set SQLite DB URL for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_worker.db"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import worker_job to trigger sys.path setup for 'app' and load logic
    import worker.worker_job as job
    from common.database import engine, Base, SessionLocal
    from common.models import StatusReport
    
    # Create tables
    print("Creating tables in SQLite...")
    Base.metadata.create_all(bind=engine)
    
    # Run ingestion
    print("Running ingestion...")
    job.ingest_data()
    
    # Verify
    db = SessionLocal()
    count = db.query(StatusReport).count()
    print(f"Verification: Found {count} records in database.")
    
    # Detailed check
    r = db.query(StatusReport).first()
    if r:
        print(f"Sample Record: {r.facility_id} - {r.status_type} - {r.raw_notam_text}")
    
    if count > 0:
        print("SUCCESS: Ingestion verified.")
    else:
        print("FAILURE: No records found.")
        
except Exception as e:
    print(f"Verification Failed: {e}")
    import traceback
    traceback.print_exc()
