from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
import sys
import json

# Agregar el directorio actual al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.database import get_db
from app.utils.csv_processor import process_csv
from app.services.incident_service import create_incident, search_incidents
from app.services.chart_service import generate_state_chart, generate_assigned_chart, generate_timeline_chart

app = Flask(__name__)
CORS(app) 

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Guardar archivo temporalmente
    file_path = os.path.join("temp_upload", file.filename)
    os.makedirs("temp_upload", exist_ok=True)
    file.save(file_path)
    
    try:
        # Procesar CSV
        incidents = process_csv(file_path)
        
        # Guardar en base de datos
        db = next(get_db())
        for incident in incidents:
            # Convertir el objeto a diccionario
            incident_dict = {
                'id': incident.id,
                'work_item_type': incident.work_item_type,
                'title': incident.title,
                'assigned_to': incident.assigned_to,
                'state': incident.state,
                'tags': incident.tags,
                'iteration_path': incident.iteration_path,
                'created_date': incident.created_date
            }
            create_incident(db, incident_dict)
        
        # Limpiar archivo temporal
        os.remove(file_path)
        
        return jsonify({"message": f"Successfully uploaded {len(incidents)} incidents"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET"])
def search():
    try:
        filters = {
            "id": request.args.get("id"),
            "title": request.args.get("title"),
            "state": request.args.get("state"),
            "assigned_to": request.args.get("assigned_to")
        }
        
        db = next(get_db())
        results = search_incidents(db, filters)
        
        return jsonify([{
            "id": incident.id,
            "title": incident.title,
            "state": incident.state,
            "assigned_to": incident.assigned_to,
            "work_item_type": incident.work_item_type,
            "tags": incident.tags,
            "iteration_path": incident.iteration_path,
            "created_date": incident.created_date.isoformat() if incident.created_date else None
        } for incident in results])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/charts/state", methods=["GET"])
def chart_state():
    """Genera gráfico de estados"""
    try:
        filters = {
            "state": request.args.get("state"),
            "assigned_to": request.args.get("assigned_to"),
            "title": request.args.get("title")
        }
        
        db = next(get_db())
        chart_json = generate_state_chart(db, filters)
        chart_data = json.loads(chart_json)
        
        return jsonify(chart_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/charts/assigned", methods=["GET"])
def chart_assigned():
    """Genera gráfico de asignados"""
    try:
        filters = {
            "state": request.args.get("state"),
            "assigned_to": request.args.get("assigned_to"),
            "title": request.args.get("title")
        }
        
        db = next(get_db())
        chart_json = generate_assigned_chart(db, filters)
        chart_data = json.loads(chart_json)
        
        return jsonify(chart_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/charts/timeline", methods=["GET"])
def chart_timeline():
    """Genera gráfico de timeline"""
    try:
        filters = {
            "state": request.args.get("state"),
            "assigned_to": request.args.get("assigned_to"),
            "title": request.args.get("title")
        }
        
        db = next(get_db())
        chart_json = generate_timeline_chart(db, filters)
        
        if chart_json:
            chart_data = json.loads(chart_json)
            return jsonify(chart_data)
        else:
            return jsonify({"message": "No data available for timeline"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/charts/export", methods=["GET"])
def export_chart():
    """Exporta gráfico como imagen"""
    try:
        chart_type = request.args.get("type", "state")
        filters = {
            "state": request.args.get("state"),
            "assigned_to": request.args.get("assigned_to"),
            "title": request.args.get("title")
        }
        
        db = next(get_db())
        
        if chart_type == "state":
            chart_json = generate_state_chart(db, filters)
        elif chart_type == "assigned":
            chart_json = generate_assigned_chart(db, filters)
        elif chart_type == "timeline":
            chart_json = generate_timeline_chart(db, filters)
        else:
            return jsonify({"error": "Invalid chart type"}), 400
        
        return jsonify({"chart_data": json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "TRACKER DONDOCTOR API is running!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)