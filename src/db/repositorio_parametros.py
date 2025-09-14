from .conexao import obter_client


class RepositorioParametros:

    def __init__(self):
        self.client = obter_client()
        self.db = self.client['contabilidade']
        self.collection = self.db['parametros']

    def criar_parametro(self, chave, valor):
        self.collection.insert_one({"chave": chave, "valor": valor})

    def obter_parametro(self, chave):
        documento = self.collection.find_one({"chave": chave})
        return documento["valor"] if documento else None
    
    def atualizar_parametro(self, chave, valor):
        self.collection.update_one(
            {"chave": chave},
            {"$set": {"valor": valor}}
        )

    def definir_parametro(self, chave, valor):
        self.collection.update_one(
            {"chave": chave},
            {"$set": {"valor": valor}},
            upsert=True
        )

    def deletar_parametro(self, chave):
        self.collection.delete_one({"chave": chave})

    def listar_parametros(self):
        return list(self.collection.find({}, {"_id": 0}))
