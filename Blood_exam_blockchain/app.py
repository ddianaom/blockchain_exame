from flask import Flask, jsonify, request, render_template, redirect
import hashlib 
import time 
from flask_swagger_ui import get_swaggerui_blueprint
import json
from flask_cors import CORS

app = app = Flask(__name__)
CORS(app)

# Configuração do Swagger UI (Documentação da API)
SWAGGER_URL = '/api/docs'  
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL,
    config={  
        'app_name': "Blockchain API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Funções para converter valores de string para JSON
def create_user_json(patient_id, patient_name, patient_blood_type):
    return {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "patient_blood_type": patient_blood_type
    }

def create_exam_json(exam_id, patient_id, hemoglobina, colesterolHDL, colesterolLDL, glicose, data):
    return {
        "exam_id": exam_id,
        "patient_id": patient_id,
        "hemoglobina": hemoglobina,
        "colesterolHDL": colesterolHDL,
        "colesterolLDL": colesterolLDL,
        "glicose": glicose,
        "data": data
    }

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route('/api/patient')
def create_patient():
    return render_template('add_patient.html')

@app.route('/api/patients')
def read_all_patients():
    return render_template('patients.html')

@app.route('/api/patient/exams')
def read_all_exams():
    return render_template('exams.html')

@app.route('/api/patient/exam/<string:patient_id>')
def read_patient_exams(patient_id):
    return render_template('patient_exam.html', patient_id=patient_id)

@app.route('/api/patient/add_exam/<string:patient_id>')
def create_exam(patient_id):
    return render_template('add_exam.html', patient_id=patient_id)


if __name__ == '__main__':
    app.run(debug=True, port=8000)