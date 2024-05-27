import time
import hashlib

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

