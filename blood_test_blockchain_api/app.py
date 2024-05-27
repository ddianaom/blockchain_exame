from flask import Flask, jsonify, request, render_template, redirect
import hashlib 
import time 
from flask_swagger_ui import get_swaggerui_blueprint
from blockchain import Blockchain
import json

app = app = Flask(__name__)

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

blockchain = Blockchain(2)  # Inserir dificuldade

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

# Rotas da URL
@app.route('/api/blockchain', methods=['GET'])
def get_blocks():
    # Exibir todos os blocos da blockchain
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    is_valid = blockchain.is_blockchain_valid()
    return blocks_data

@app.route('/api/patient', methods=['POST'])
def create_patient():
    patient_id = request.json.get('patient_id')
    patient_name = request.json.get('patient_name')
    patient_blood_type = request.json.get('patient_blood_type')

    # TODO: Adicionar verificação se usuário já existe

    # Cria o JSON do usuário
    patient_json = create_user_json(patient_id, patient_name, patient_blood_type)

    # Salvar o valor criado na blockchain
    data = json.dumps(patient_json)
    blockchain.add_block(data)

    return jsonify({"message": "Patient created successfully", "patient": patient_json}), 201

@app.route('/api/patient/<string:index>', methods=['PUT'])
def update_patient(index):
    patient_id = index
    
    patient_name = request.json.get('patient_name')
    patient_blood_type = request.json.get('patient_blood_type')

    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'patient_name' in block_data:
            if block_data['patient_id'] == patient_id:
                # Cria o JSON do usuário
                patient_json = create_user_json(patient_id, patient_name, patient_blood_type)

                # Salvar o valor criado na blockchain
                data = json.dumps(patient_json)
                blockchain.add_block(data)
                
                return jsonify({"message": "Patient updated successfully", "patient": data}), 200
            
    return jsonify({"message": "Patient not found"}), 400

@app.route('/api/patient/<string:index>', methods=['GET'])
def read_patient(index):
    patient_id = index
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'patient_name' in block_data:
            if block_data['patient_id'] == patient_id:
                # Converte a string em JSON
                data = json.dumps(block_data)
                
                return jsonify({"patient": data}), 200
            
    return jsonify({"message": "Patient not found"}), 400

@app.route('/api/patients', methods=['GET'])
def read_all_patients():
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    patients = []

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'patient_name' in block_data:
            # Verificar se o usuário já foi incluído anteriormente na lista, ou seja, se já
            # foi salva uma versão desatualizada do usuário
            for patient in patients:
                if block_data['patient_id'] == patient['patient_id']:
                    patients.remove(patient)
                    break
            
            patients.append(block_data)

    if len(patients) > 0:
        return jsonify({"patients": patients}), 200

    return jsonify({"message": "There is no patients in the blockchain"}), 400

@app.route('/api/patient/exam/', methods=['POST'])
def create_exam():
    exam_id = request.json.get('exam_id')
    patient_id = request.json.get('patient_id')
    hemoglobina = request.json.get('hemoglobina')
    colesterolHDL = request.json.get('colesterolHDL')
    colesterolLDL = request.json.get('colesterolLDL')
    glicose = request.json.get('glicose')
    data = request.json.get('data')

    # Cria o JSON do exame
    exam_json = create_exam_json(exam_id, patient_id, hemoglobina, colesterolHDL, colesterolLDL, glicose, data)

    # Verificação se o paciente solicitado existe
    has_patient = False
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'patient_name' in block_data:
            if block_data['patient_id'] == patient_id:
                has_patient = True

    if has_patient:
        # Salvar o valor criado na blockchain
        data_to_save = json.dumps(exam_json)
        blockchain.add_block(data_to_save)

        return jsonify({"message": "Exam created successfully", "Exam": exam_json}), 201
    else:
        return jsonify({"message": "Patient not found in the blockchain"}), 400

@app.route('/api/patient/exam/<string:index>', methods=['PUT'])
def update_exam(index):
    exam_id = index
    
    patient_id = request.json.get('patient_id')
    hemoglobina = request.json.get('hemoglobina')
    colesterolHDL = request.json.get('colesterolHDL')
    colesterolLDL = request.json.get('colesterolLDL')
    glicose = request.json.get('glicose')
    data = request.json.get('data')

    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'exam_id' in block_data:
            if block_data['exam_id'] == exam_id:
                # Cria o JSON do usuário
                exam_json = create_exam_json(exam_id, patient_id, hemoglobina, colesterolHDL, colesterolLDL, glicose, data)

                # Salvar o valor criado na blockchain
                data = json.dumps(exam_json)
                blockchain.add_block(data)
                
                return jsonify({"message": "Exam updated successfully", "Exam": data}), 200
            
    return jsonify({"message": "Exam not found"}), 400

@app.route('/api/patient/exam/<string:index>', methods=['GET'])
def read_patient_last_exam(index):
    patient_id = index

    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    last_exam = ""

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'exam_id' in block_data:
            if block_data['patient_id'] == patient_id:
                last_exam = block_data

    if last_exam != "":
        return jsonify({"LastExam": last_exam}), 200

    return jsonify({"message": "There is no exams created for this patient"}), 400

@app.route('/api/patient/exams/<string:index>', methods=['GET'])
def read_patient_exams(index):
    patient_id = index

    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    exams = []

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'exam_id' in block_data:
            if block_data['patient_id'] == patient_id:
                # Verificar se o exame já foi incluído anteriormente na lista, ou seja, se já
                # foi salva uma versão desatualizada do exame
                for exam in exams:
                    if block_data['exam_id'] == exam['exam_id']:
                        exams.remove(exam)
                        break
                exams.append(block_data)

    if len(exams) > 0:
        return jsonify({"Exams": exams}), 200

    return jsonify({"message": "There is no exams created for this patient"}), 400

@app.route('/api/patient/exams', methods=['GET'])
def read_all_exams():
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    exams = []

    for block in blocks_data:
        if block['data'] == 'Genesis Block':
            continue

        block_data = json.loads(block['data'])

        if 'exam_id' in block_data:
            # Verificar se o exame já foi incluído anteriormente na lista, ou seja, se já
            # foi salva uma versão desatualizada do exame
            for exam in exams:
                if block_data['exam_id'] == exam['exam_id']:
                    exams.remove(exam)
                    break
            exams.append(block_data)

    if len(exams) > 0:
        return jsonify({"Exams": exams}), 200

    return jsonify({"message": "There is no exams created in the blockchain"}), 400

'''
@app.route('/api/patient', methods=['GET', 'POST'])
def blocks():
    # Adicionar um novo paciente
    if request.method == 'POST':
        data = request.form.get('data')
        blockchain.add_block(data)
        return redirect('/blockchain')
    else:
        return render_template('add_block.html')

@app.route('/add_block', methods=['GET', 'POST'])
def blocks():
    # Adicionar novo bloco
    if request.method == 'POST':
        data = request.form.get('data')
        blockchain.add_block(data)
        return redirect('/blockchain')
    else:
        return render_template('add_block.html')
'''
@app.route('/blockchain/<int:index>', methods=['DELETE'])
def delete_block(index):
    '''
    Não se deve deletar um bloco de uma blockchain, esse método foi inserido para
    validação da função is_blockchain_valid()
    '''
    if blockchain.delete_block(index):
        return jsonify({'message': f'Bloco #{index} foi deletado'}), 200
    else:
        return jsonify({'message': f'Não é possível deletar o bloco #{index}'}), 400

if __name__ == '__main__':
    app.run(debug=True)