import plotly.express as px
import plotly.io as pio
import pandas as pd
from sqlalchemy.orm import Session
from app.models.incident import Incident

def generate_bar_chart(data, x_axis, y_axis, title):
    """Genera gráfico de barras"""
    fig = px.bar(data, x=x_axis, y=y_axis, title=title, color=x_axis)
    return pio.to_json(fig)

def generate_pie_chart(data, values, names, title):
    """Genera gráfico de pie"""
    fig = px.pie(data, values=values, names=names, title=title)
    return pio.to_json(fig)

def get_chart_data(db: Session, filters: dict):
    """Obtiene datos para gráficos basado en filtros"""
    query = db.query(Incident)
    
    # Aplicar filtros
    if filters.get("state"):
        query = query.filter(Incident.state == filters["state"])
    if filters.get("assigned_to"):
        query = query.filter(Incident.assigned_to.contains(filters["assigned_to"]))
    if filters.get("title"):
        query = query.filter(Incident.title.contains(filters["title"]))
    
    results = query.all()
    
    # Convertir a DataFrame para fácil manipulación
    data = [{
        'id': incident.id,
        'work_item_type': incident.work_item_type,
        'title': incident.title,
        'assigned_to': incident.assigned_to,
        'state': incident.state,
        'tags': incident.tags,
        'iteration_path': incident.iteration_path,
        'created_date': incident.created_date
    } for incident in results]
    
    return pd.DataFrame(data)

def generate_state_chart(db: Session, filters: dict):
    """Genera gráfico de estados"""
    df = get_chart_data(db, filters)
    state_counts = df['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'count']
    
    return generate_bar_chart(state_counts, 'state', 'count', 'Incidentes por Estado')

def generate_assigned_chart(db: Session, filters: dict):
    """Genera gráfico de asignados"""
    df = get_chart_data(db, filters)
    assigned_counts = df['assigned_to'].value_counts().reset_index()
    assigned_counts.columns = ['assigned_to', 'count']
    
    return generate_pie_chart(assigned_counts, 'count', 'assigned_to', 'Incidentes por Asignado')

def generate_timeline_chart(db: Session, filters: dict):
    """Genera gráfico de timeline"""
    df = get_chart_data(db, filters)
    
    if df.empty:
        return None
        
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['date'] = df['created_date'].dt.date
    timeline_data = df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(timeline_data, x='date', y='count', title='Incidentes por Fecha')
    return pio.to_json(fig)