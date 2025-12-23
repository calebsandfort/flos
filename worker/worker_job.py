import sys
import os
import time
import json
import re
import datetime
from datetime import timezone
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select

# Add project root and api directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

api_root = os.path.join(project_root, 'api')
if api_root not in sys.path:
    sys.path.insert(0, api_root)

# Load .env file manually to ensure DATABASE_URL is set before app.database import
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    print(f"Loading environment from {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key.strip() not in os.environ:
                    os.environ[key.strip()] = value.strip()

try:
    # Import from common (requires project_root in sys.path)
    from common.models import StatusReport
    from common.database import SessionLocal
    # Import from worker (requires project_root in sys.path)
    from worker.data.unstructured_notams import mock_legacy_notams
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        # Check if already datetime object (e.g. from pandas)
        if isinstance(dt_str, datetime.datetime):
             return dt_str.replace(tzinfo=timezone.utc) if dt_str.tzinfo is None else dt_str
        
        # Handle "Z" suffix if present
        if dt_str.endswith('Z'):
             dt_str = dt_str[:-1] + '+00:00'
        return datetime.datetime.fromisoformat(dt_str)
    except ValueError:
        return None

def parse_csv_datetime(dt_str):
    if not dt_str or pd.isna(dt_str):
        return None
    try:
        # Format "12/17/25 14:00" -> UTC
        dt = datetime.datetime.strptime(dt_str, "%m/%d/%y %H:%M")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def parse_notam_effective_time(time_str):
    # Format "YYMMDDHHMM"
    if not time_str or len(time_str) < 10:
        return None
    try:
        dt = datetime.datetime.strptime(time_str[:10], "%y%m%d%H%M")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def process_runway_json(file_path):
    print(f"Processing JSON: {file_path}")
    results = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        for item in data:
            facility_id = item.get('facility_icao')
            status_type = item.get('report_type')
            
            # Combine status and closure reason
            status = item.get('status', '')
            reason = item.get('closure_reason', '')
            raw_notam_text = f"{status}"
            if reason:
                 raw_notam_text += f" - {reason}"
                 
            start_time = parse_iso_datetime(item.get('time_active_utc'))
            end_time = parse_iso_datetime(item.get('estimated_reopen_utc'))
            
            if facility_id and status_type and start_time:
                results.append({
                    'facility_id': facility_id,
                    'status_type': status_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'raw_notam_text': raw_notam_text
                })
    except Exception as e:
        print(f"Error processing JSON: {e}")
        
    return results

def process_outage_csv(file_path):
    print(f"Processing CSV: {file_path}")
    results = []
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            facility_id = row.get('FACILITY')
            status_type = row.get('OUTAGE_TYPE')
            raw_notam_text = row.get('DETAILS')
            
            start_time = parse_csv_datetime(row.get('TIME_LOST'))
            end_time = parse_csv_datetime(row.get('EST_REPAIR'))
            
            if facility_id and status_type and start_time:
                results.append({
                    'facility_id': facility_id,
                    'status_type': status_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'raw_notam_text': raw_notam_text
                })
    except Exception as e:
        print(f"Error processing CSV: {e}")
        
    return results

def process_text_notams(notams_list):
    print(f"Processing {len(notams_list)} text NOTAMs")
    results = []
    
    # Regex patterns
    facility_pattern = r'\(([A-Z]{3,4})\)'
    effective_pattern = r'EFFECTIVE:\s*([0-9]{10})-([0-9A-Z]*)'
    
    for notam_text in notams_list:
        clean_text = notam_text.strip()
        
        # Extract Facility
        fac_match = re.search(facility_pattern, clean_text)
        facility_id = fac_match.group(1) if fac_match else None
        
        # Extract Times
        start_time = None
        end_time = None
        eff_match = re.search(effective_pattern, clean_text)
        
        if eff_match:
            start_str = eff_match.group(1)
            end_str = eff_match.group(2)
            
            start_time = parse_notam_effective_time(start_str)
            
            if end_str and end_str.isdigit() and len(end_str) >= 10:
                end_time = parse_notam_effective_time(end_str)
            elif end_str in ['UFN', 'PERM']:
                end_time = None
        
        status_type = "NOTAM"
        
        if facility_id and start_time:
             results.append({
                'facility_id': facility_id,
                'status_type': status_type,
                'start_time': start_time,
                'end_time': end_time,
                'raw_notam_text': clean_text
            })
            
    return results

def ingest_data():
    all_records = []
    
    # Define file paths
    # Assuming script is run from project root, but file paths are relative to this script or consistent
    # The requirement says "Reads worker/data/runway_data.json" etc.
    # So we'll construct absolute paths based on this script's location
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    
    runway_file = os.path.join(data_dir, 'runway_data.json')
    outage_file = os.path.join(data_dir, 'outage_log.csv')
    
    # Process inputs
    all_records.extend(process_runway_json(runway_file))
    all_records.extend(process_outage_csv(outage_file))
    all_records.extend(process_text_notams(mock_legacy_notams))
    
    print(f"Total records to ingest: {len(all_records)}")
    
    db = SessionLocal()
    count_added = 0
    count_updated = 0
    
    try:
        for record in all_records:
            # Check for existing record
            stmt = select(StatusReport).where(
                StatusReport.facility_id == record['facility_id'],
                StatusReport.status_type == record['status_type'],
                StatusReport.start_time == record['start_time']
            )
            existing = db.execute(stmt).scalar_one_or_none()
            
            if existing:
                # Update
                existing.end_time = record['end_time']
                existing.raw_notam_text = record['raw_notam_text']
                existing.last_updated = datetime.datetime.now(timezone.utc)
                count_updated += 1
            else:
                # Insert
                new_report = StatusReport(
                    facility_id=record['facility_id'],
                    status_type=record['status_type'],
                    start_time=record['start_time'],
                    end_time=record['end_time'],
                    raw_notam_text=record['raw_notam_text']
                )
                db.add(new_report)
                count_added += 1
        
        db.commit()
        print(f"Ingestion Complete: {count_added} records added, {count_updated} records updated")
        
    except Exception as e:
        db.rollback()
        print(f"Error during database ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting Worker Service...")
    while True:
        print(f"Running ingestion job at {datetime.datetime.now(timezone.utc)}")
        ingest_data()
        print("Sleeping for 60 seconds...")
        time.sleep(60)
