import pytest
import datetime
import pandas as pd
from unittest.mock import patch, mock_open
import json

from worker.worker_job import (
    parse_iso_datetime,
    parse_csv_datetime,
    parse_notam_effective_time,
    process_runway_json,
    process_outage_csv,
    process_text_notams
)

# --- Helper Tests ---

def test_parse_iso_datetime():
    # Test Z suffix
    dt = parse_iso_datetime("2025-12-17T14:00:00Z")
    assert dt is not None
    assert dt.year == 2025
    assert dt.tzinfo == datetime.timezone.utc

    # Test None
    assert parse_iso_datetime(None) is None
    
    # Test Invalid
    assert parse_iso_datetime("invalid") is None

def test_parse_csv_datetime():
    # Test valid format MM/DD/YY HH:MM
    dt = parse_csv_datetime("12/17/25 14:00")
    assert dt is not None
    assert dt.year == 2025
    assert dt.hour == 14
    assert dt.tzinfo == datetime.timezone.utc

    # Test None/NaN
    assert parse_csv_datetime(None) is None
    assert parse_csv_datetime(float('nan')) is None

def test_parse_notam_effective_time():
    # Test YYMMDDHHMM
    dt = parse_notam_effective_time("2512171400")
    assert dt is not None
    assert dt.year == 2025
    assert dt.month == 12
    assert dt.tzinfo == datetime.timezone.utc

# --- Parser Tests ---

def test_process_runway_json():
    mock_data = [
        {
            "facility_icao": "KDEN",
            "report_type": "RUNWAY",
            "status": "CLOSED",
            "closure_reason": "CONSTRUCTION",
            "time_active_utc": "2025-12-17T14:00:00Z",
            "estimated_reopen_utc": "2025-12-18T14:00:00Z"
        }
    ]
    json_str = json.dumps(mock_data)
    
    with patch("builtins.open", mock_open(read_data=json_str)):
        results = process_runway_json("dummy_path.json")
        
    assert len(results) == 1
    item = results[0]
    assert item['facility_id'] == "KDEN"
    assert item['status_type'] == "RUNWAY"
    assert "CLOSED - CONSTRUCTION" in item['raw_notam_text']
    assert item['start_time'].year == 2025

def test_process_outage_csv():
    data = {
        'FACILITY': ['KJFK'],
        'OUTAGE_TYPE': ['COMM'],
        'DETAILS': ['Radio failure'],
        'TIME_LOST': ['12/17/25 10:00'],
        'EST_REPAIR': ['12/17/25 12:00']
    }
    df = pd.DataFrame(data)
    
    with patch("pandas.read_csv", return_value=df):
        results = process_outage_csv("dummy_path.csv")
        
    assert len(results) == 1
    item = results[0]
    assert item['facility_id'] == "KJFK"
    assert item['status_type'] == "COMM"
    assert item['start_time'].day == 17

def test_process_text_notams():
    notams = [
        "!FDC 1/1234 (KSFO) ... EFFECTIVE: 2512171400-2512181400 ...",
        "!FDC 1/5678 (KLAX) ... EFFECTIVE: 2512171400-PERM ..."
    ]
    
    results = process_text_notams(notams)
    
    assert len(results) == 2
    
    # Check KSFO
    ksfo = next(r for r in results if r['facility_id'] == 'KSFO')
    assert ksfo['status_type'] == 'NOTAM'
    assert ksfo['start_time'].year == 2025
    assert ksfo['end_time'] is not None
    
    # Check KLAX
    klax = next(r for r in results if r['facility_id'] == 'KLAX')
    assert klax['end_time'] is None  # PERM
