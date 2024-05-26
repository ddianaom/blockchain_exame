from flask import Flask, jsonify, request, render_template, redirect
import hashlib 
import time 
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

class Block:
    def __init__(self, index, timestamp, previous_hash, data):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        txt = str(self.index) + str(self.timestamp) + self.previous_hash + self.data + str(self.nonce)
        return hashlib.sha256(txt.encode('utf-8')).hexdigest()

    def proof_of_work(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __str__(self):
        return f"Block #{self.index} [previousHash : {self.previous_hash}, timestamp : {time.ctime(self.timestamp)}, data : {self.data}, hash : {self.hash}]"


class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.blocks = []
        genesis_block = Block(0, time.time(), "0", "Genesis Block")
        genesis_block.proof_of_work(self.difficulty)
        self.blocks.append(genesis_block)

    def latest_block(self):
        return self.blocks[-1]

    def add_block(self, data):
        latest_block = self.latest_block()
        new_block = Block(latest_block.index + 1, time.time(), latest_block.hash, data)
        new_block.proof_of_work(self.difficulty)
        self.blocks.append(new_block)

    def is_first_block_valid(self):
        first_block = self.blocks[0]
        if first_block.index != 0:
            return False
        if first_block.previous_hash != "0":
            return False
        if first_block.hash != first_block.calculate_hash():
            return False
        return True

    def is_valid_new_block(self, new_block, previous_block):
        if previous_block.index + 1 != new_block.index:
            return False
        if new_block.previous_hash != previous_block.hash:
            return False
        if new_block.hash != new_block.calculate_hash():
            return False
        return True

    def is_blockchain_valid(self):
        if not self.is_first_block_valid():
            return False
        for i in range(1, len(self.blocks)):
            if not self.is_valid_new_block(self.blocks[i], self.blocks[i - 1]):
                return False
        return True
    
    def delete_block(self, index):
        if index < 1 or index >= len(self.blocks):
            return False  # Não pode deletar o bloco gênesis ou um bloco que não existe
        del self.blocks[index]
        for i in range(index, len(self.blocks)):
            self.blocks[i].index -= 1  # Atualiza os índices dos blocos subsequentes
        return True
    

blockchain = Blockchain(4)  # Difficulty set to 4 for proof of work

SWAGGER_URL = '/api/docs'  # URL para expor a documentação Swagger UI (sem o arquivo .json)
API_URL = '/static/swagger.json'  # Rota para o arquivo .json da API

# Configuração do Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Endpoint da Swagger UI
    API_URL,
    config={  # Configuração da Swagger UI
        'app_name': "Blockchain API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/resultado', methods=['GET'])
def get_blocks():
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    is_valid = blockchain.is_blockchain_valid()
    return render_template('blocks.html', blocks=blocks_data, is_valid=is_valid, time=time)

@app.route('/blocks', methods=['GET', 'POST'])
def blocks():
    if request.method == 'POST':
        data = request.form.get('data')
        blockchain.add_block(data)
        return redirect('/resultado')
    else:
        return render_template('add_block.html')
    
@app.route('/blocks/<int:index>', methods=['DELETE'])
def delete_block(index):
    if blockchain.delete_block(index):
        return jsonify({'message': f'Block #{index} has been deleted'}), 200
    else:
        return jsonify({'message': f'Cannot delete block #{index}'}), 400


if __name__ == '__main__':
    app.run(debug=True)
