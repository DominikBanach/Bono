from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL: 
    raise ConnectionError

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EventDefinition(Base):
    __tablename__ = "event_definitions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    logs = relationship("EventLog", back_populates="definition")


class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(Integer, primary_key=True, index=True)
    event_def_id = Column(Integer, ForeignKey("event_definitions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    definition = relationship("EventDefinition", back_populates="logs")


class EventDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class EventDefinitionOut(EventDefinitionCreate):
    id: int
    class Config:
        from_attributes = True


class EventLogCreate(BaseModel):
    event_type_name: str
    timestamp: Optional[datetime] = None


class EventLogOut(BaseModel):
    id: int
    event_type: str
    timestamp: datetime
    class Config:
        from_attributes = True


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Tracker")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/event-definitions/", response_model=EventDefinitionOut)
def create_definition(definition: EventDefinitionCreate, db: Session = Depends(get_db)):
    db_def = db.query(EventDefinition).filter(EventDefinition.name == definition.name.upper()).first()
    if db_def:
        raise HTTPException(status_code=400, detail="Definition already exists.")
    
    new_def = EventDefinition(name=definition.name.upper(), description=definition.description)
    db.add(new_def)
    db.commit()
    db.refresh(new_def)
    return new_def


@app.get("/event-definitions/", response_model=List[EventDefinitionOut])
def get_definitions(db: Session = Depends(get_db)):
    return db.query(EventDefinition).all()


@app.post("/events/", response_model=EventLogOut)
def log_event(event_data: EventLogCreate, db: Session = Depends(get_db)):
    event_def = db.query(EventDefinition).filter(EventDefinition.name == event_data.event_type_name.upper()).first()
    if not event_def:
        raise HTTPException(status_code=404, detail=f'There is no {event_data.event_type_name.upper()} event definition.')
    
    if event_data.timestamp:
        event_time = event_data.timestamp
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
    else:
        event_time = datetime.now(timezone.utc)

    new_log = EventLog(
        event_def_id=event_def.id,
        timestamp=event_time
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return {
        "id": new_log.id,
        "event_type": event_def.name,
        "timestamp": new_log.timestamp
    }


@app.get("/events/", response_model=List[EventLogOut])
def get_events(db: Session = Depends(get_db)):
    logs = db.query(EventLog).join(EventDefinition).all()
    return [
        {"id": log.id, "event_type": log.definition.name, "timestamp": log.timestamp}
        for log in logs
    ]
