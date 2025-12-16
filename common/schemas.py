from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class StatusReportBase(BaseModel):
    facility_id: str
    status_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    raw_notam_text: Optional[str] = None

class StatusReport(StatusReportBase):
    report_id: int
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
