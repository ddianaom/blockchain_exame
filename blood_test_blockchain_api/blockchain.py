from block import Block
import time

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