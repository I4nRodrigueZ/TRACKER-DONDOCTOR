from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    work_item_type = Column(String(255))
    title = Column(String(255))
    assigned_to = Column(String(255))
    state = Column(String(255))
    tags = Column(String(255))
    iteration_path = Column(String(255))
    created_date = Column(DateTime)