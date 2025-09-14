from src.db.conexao import obter_client

class RepositorioContasBancarias:           
   
    def __init__(self):
        self.client = obter_client()
        self.db = self.client['contabilidade']
        self.collection = self.db['contas_bancarias']

    def criar_contas_bancarias(self, chave, valor):
        self.collection.insert_one({"numero_conta": chave, "conta_contabil_banco": valor})

    def obter_contas_bancarias(self, chave):
        documento = self.collection.find_one({"numero_conta": chave})
        return documento["conta_contabil_banco"] if documento else None
    
    def atualizar_contas_bancarias(self, chave, valor):
        self.collection.update_one(
            {"numero_conta": chave},
            {"$set": {"conta_contabil_banco": valor}}
        )
    
    def definir_contas_bancarias(self, chave, valor):
        self.collection.update_one(
            {"numero_conta": chave},
            {"$set": {"conta_contabil_banco": valor}},
            upsert=True
        )

    def deletar_contas_bancarias(self, chave):
        self.collection.delete_one({"numero_conta": chave})

    def listar_contas_bancarias(self):
        return list(self.collection.find({}, {"_id": 0}))