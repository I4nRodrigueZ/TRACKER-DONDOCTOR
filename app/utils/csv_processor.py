import pandas as pd
import numpy as np
from app.models.incident import Incident

def process_csv(file_path):
    # Leer CSV con comillas y commas
    df = pd.read_csv(file_path, quotechar='"', delimiter=',', encoding='utf-8')
    
    # Renombrar columnas para coincidir con nuestro modelo
    column_mapping = {
        "ID": "id",
        "Work Item Type": "work_item_type",
        "Title": "title", 
        "Assigned To": "assigned_to",
        "State": "state",
        "Tags": "tags",
        "Iteration Path": "iteration_path",
        "Changed Date": "created_date"
    }
    
    df = df.rename(columns=column_mapping)
    
    # Reemplazar NaN y NaT por None (para MySQL)
    df = df.replace({np.nan: None, pd.NaT: None})
    
    # Convertir a lista de diccionarios
    incidents_data = df.to_dict(orient='records')
    
    # Crear objetos Incident
    incidents = []
    for data in incidents_data:
        try:
            # Convertir valores NaN a None manualmente
            incident_data = {
                'id': int(data.get("id")) if data.get("id") is not None else None,
                'work_item_type': data.get("work_item_type"),
                'title': data.get("title"),
                'assigned_to': data.get("assigned_to"),
                'state': data.get("state"),
                'tags': data.get("tags"),
                'iteration_path': data.get("iteration_path"),
                'created_date': pd.to_datetime(data.get("created_date")) if data.get("created_date") is not None else None
            }
            
            # Reemplazar cualquier valor NaN que haya quedado
            for key, value in incident_data.items():
                if pd.isna(value):
                    incident_data[key] = None
            
            incident = Incident(**incident_data)
            incidents.append(incident)
            
        except Exception as e:
            print(f"Error procesando fila: {data}, Error: {e}")
            continue
    
    return incidents