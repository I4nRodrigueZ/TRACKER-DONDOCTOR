from sqlalchemy.orm import Session
from app.models.incident import Incident

def create_incident(db: Session, incident_data):
    # Asegurarse de que no hay valores NaN
    cleaned_data = {}
    for key, value in incident_data.items():
        if hasattr(value, 'item'):  # Para pandas NaN
            cleaned_data[key] = value.item() if not pd.isna(value) else None
        else:
            cleaned_data[key] = value
    
    db_incident = Incident(**cleaned_data)
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def get_incidents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Incident).offset(skip).limit(limit).all()

def search_incidents(db: Session, filters: dict):
    query = db.query(Incident)
    
    if filters.get("id"):
        query = query.filter(Incident.id == filters["id"])
    if filters.get("title"):
        query = query.filter(Incident.title.contains(filters["title"]))
    if filters.get("state"):
        query = query.filter(Incident.state == filters["state"])
    if filters.get("assigned_to"):
        query = query.filter(Incident.assigned_to.contains(filters["assigned_to"]))
    
    return query.all()