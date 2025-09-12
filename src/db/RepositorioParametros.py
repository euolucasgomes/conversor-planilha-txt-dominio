from .conexao import obter_client


class RepositorioParametros:

    def __init__(self):
        self.client = obter_client()
        self.db = self.client['contabilidade']
        self.collection = self.db['parametros']

    def obter_parametro(self, chave):
        documento = self.collection.find_one({"chave": chave})
        return documento["valor"] if documento else None

    def definir_parametro(self, chave, valor):
        self.collection.update_one(
            {"chave": chave},
            {"$set": {"valor": valor}},
            upsert=True
        )
