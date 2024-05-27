from flask import Flask, jsonify, request, render_template, redirect
import hashlib 
import time 
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

class Block:
    def __init__(self, index, timestamp, previous_hash, data):
        '''
        Definição dos valores do bloco
        index: posição do bloco
        timestamp: horário em que o bloco foi criado
        previous_hash: hash do bloco anterior
        data: informações do bloco
        nonce: número usado para encontrar um hash válido
        hash: hash do bloco
        '''
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Cálculo do hash do bloco
        txt = str(self.index) + str(self.timestamp) + self.previous_hash + self.data + str(self.nonce)
        return hashlib.sha256(txt.encode('utf-8')).hexdigest()

    def proof_of_work(self, difficulty):
        # Uso do nonce para achar um hash válido
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __str__(self):
        # Retorna informações do bloco
        return f"Block #{self.index} [previousHash : {self.previous_hash}, timestamp : {time.ctime(self.timestamp)}, data : {self.data}, hash : {self.hash}]"


class Blockchain:
    '''
    Dificuldade: medir nível para mining dos blocos
    Bloco gênesis: primeiro bloco da blockchain
    '''
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.blocks = []
        genesis_block = Block(0, time.time(), "0", "Genesis Block")
        genesis_block.proof_of_work(self.difficulty)
        self.blocks.append(genesis_block) # Adiciona o bloco em seguida do bloco gênesis

    def latest_block(self):
        # Retorna o último bloco
        return self.blocks[-1]

    def add_block(self, data):
        # Adiciona um bloco na blockchain
        latest_block = self.latest_block()
        new_block = Block(latest_block.index + 1, time.time(), latest_block.hash, data)
        new_block.proof_of_work(self.difficulty)
        self.blocks.append(new_block)

    def is_first_block_valid(self):
        # Verifica se o primeiro bloco está correto em relação ao index e o hash
        first_block = self.blocks[0]
        if first_block.index != 0:
            return False
        if first_block.previous_hash != "0":
            return False
        if first_block.hash != first_block.calculate_hash():
            return False
        return True

    def is_valid_new_block(self, new_block, previous_block):
        # Verifica se o novo bloco está de acordo com o bloco anterior
        if previous_block.index + 1 != new_block.index:
            return False
        if new_block.previous_hash != previous_block.hash:
            return False
        if new_block.hash != new_block.calculate_hash():
            return False
        return True

    def is_blockchain_valid(self):
        # Verifica se há alguma inconsistência na blockchain
        if not self.is_first_block_valid():
            return False
        for i in range(1, len(self.blocks)):
            if not self.is_valid_new_block(self.blocks[i], self.blocks[i - 1]):
                return False
        return True
    
    def delete_block(self, index):
        if index < 1 or index >= len(self.blocks):
            # Não pode deletar o bloco gênesis ou um bloco que não existe
            return False
        del self.blocks[index]
        # Atualiza os índices dos blocos subsequentes
        for i in range(index, len(self.blocks)):
            self.blocks[i].index -= 1  
        return True
    

blockchain = Blockchain(4)  # Inserir dificuldade

Blockchain.add_block(blockchain, "HEMOGLOBINA 2")

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

# Rotas da URL
@app.route('/blockchain', methods=['GET'])
def get_blocks():
    # Exibir todos os blocos da blockchain
    blocks_data = [{'index': block.index, 'timestamp': block.timestamp, 'previous_hash': block.previous_hash, 'data': block.data, 'hash': block.hash} for block in blockchain.blocks]
    is_valid = blockchain.is_blockchain_valid()
    return render_template('blockchain.html', blocks=blocks_data, is_valid=is_valid, time=time)

@app.route('/add_block', methods=['GET', 'POST'])
def blocks():
    # Adicionar novo bloco
    if request.method == 'POST':
        data = request.form.get('data')
        blockchain.add_block(data)
        return redirect('/blockchain')
    else:
        return render_template('add_block.html')
    
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
