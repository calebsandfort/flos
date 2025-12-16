from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from common.database import Base

class StatusReport(Base):
    __tablename__ = "status_report"

    report_id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, index=True, nullable=False)
    status_type = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    raw_notam_text = Column(String)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
