from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from common import models, schemas
from common.database import SessionLocal, engine

# Create tables if they don't exist (useful for simple setups, though alembic is preferred)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flos API", version="1.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/status/", response_model=List[schemas.StatusReport])
def read_status_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(models.StatusReport).offset(skip).limit(limit).all()
    return reports

@app.get("/api/v1/status/{report_id}", response_model=schemas.StatusReport)
def read_status_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.StatusReport).filter(models.StatusReport.report_id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Status report not found")
    return report
