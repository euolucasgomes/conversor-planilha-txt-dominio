from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from src.db.conexao import obter_client
import re


class RepositorioContasPagas:

    def __init__(self):
        self.client = obter_client()
        self.db = self.client['contabilidade']
        self.collection = self.db['contas_pagas']
        self.collection.create_index(
            [("assintura", 1)],
            unique=True,
            name="uq_assintura"
        )

    def criar_contas_pagas(self, chave: str, valor: dict) -> dict:
        """
        Fail if exists.
        chave = assinatura canônica (ex.: 'RFB|FGTS')
        valor precisa ter: conta_despesa (str)
        opcionais: fornecedor_norm (str), tokens (list[str]), origem (str),        
        """
        if not chave or not isinstance(chave, str):
            raise ValueError("assinatura (chave) inválida")

        conta = valor.get('conta_despesa')
        if not conta or not isinstance(conta, str):
            raise ValueError(
                "campo obrigatório 'conta_despesa' ausente ou inválido")

        # Verificação explícita (mensagem amigável)
        if self.collection.find_one({"assintura": chave}):
            raise ValueError(f"já existe vínculo para assinatura='{chave}'")

        now = datetime.utcnow()
        doc = {
            "assinatura": chave,
            "fornecedor_norm": valor.get('fornecedor_norm'),
            "tokens": valor.get('tokens') or [],
            "conta_despesa": conta,
            "origem": valor.get('origem', 'manual'),
            "stats": {'aplicacoes': 0},
            "created_at": now,
            "updated_at": now,
        }

        try:
            self.collection.insert_one(doc)
        except DuplicateKeyError:
            # Corrida eventual
            raise ValueError(f"assinatura'{chave}' já cadastrada")

        return doc

    def obter_contas_pagas(self, chave: str) -> dict | None:
        """
        Recupera vínculo pela assinatura canônica.
        Ex.: chave = 'RFB|FGTS'
        Retorna o documento completo ou None se não existir.
        """
        if not chave or not isinstance(chave, str):
            raise ValueError("assinatura (chave) inválida")

        return self.collection.find_one({"assinatura": chave})

    def atualizar_contas_pagas(self, chave: str, valor: dict, incrementar_aplicacoes: int = 0) -> dict:
        """
        Atualiza parcialmente o vínculo da assinatura (sem upsert).
        - chave: assinatura canônica (ex.: 'RFB|FGTS')
        - valor: dict com campos a atualizar (whitelist abaixo)
        - incrementar_aplicacoes: se > 0, incrementa stats.aplicacoes
        Retorna o documento arualizado. Lança ValueError se não encontrar.
        """
        if not chave or not isinstance(chave, str):
            raise ValueError("assinatura (chave) inválida")
        if not isinstance(valor, dict):
            raise ValueError("valor deve ser um dict")

        # Permitir apenas esses campos serem alterados via patch
        allowed = {"conta_despesa", "fornecedor_norm", "tokens", "origem"}
        set_doc = {k: v for k, v in valor.items() if k in allowed}

        # Normalização opcional dos tokens
        if "tokens" in set_doc and set_doc["tokens"] is not None:
            if not isinstance(set_doc["tokens"], list):
                raise ValueError("tokens devem ser uma lista de strings")
            set_doc["tokens"] = [str(t).strip().upper()
                                 for t in set_doc["tokens"] if str(t).strip()]

        # Sempre atualiza o carimbo de atualização
        set_doc["updated_at"] = datetime.utcnow()

        if not set_doc and incrementar_aplicacoes <= 0:
            raise ValueError("nenhum campo permitido para atualizar")

        update_ops = {"$set": set_doc}
        if incrementar_aplicacoes > 0:
            update_ops["$inc"] = {
                "stats.aplicacoes": int(incrementar_aplicacoes)}

        doc = self.collection.find_one_and_update(
            {"assinatura": chave},
            update_ops,
            return_document=ReturnDocument.AFTER,
        )
        if not doc:
            raise ValueError(
                f"assinatura '{chave}' não encontrada para atualizar")

        return doc

    def definir_contas_pagas(self, chave: str, valor: dict, incrementar_aplicacoes: int = 0) -> dict:
        """
        Upsert do vínculo da assinatura:
        - Se existir: atualiza campos permitidos e carimba updated_at.
        - Se não existir: cria com created_at/updated_at e stats.aplicacoes=0
        Regras:
            * 'chave' = assinatura canônica (ex.: 'RFB|FGTS')
            * Para INSERT é obrigatório 'conta_despesa' em valor.
            * Campos permitidos no update: conta_despesa, fornecedor_norm, tokens, origem.
        Retorna o documento final (após upsert).
        """
        if not chave or not isinstance(chave, str):
            raise ValueError("assinatura (chave) inválida")
        if not isinstance(valor, dict):
            raise ValueError("valor deve ser um dict")

        allowed = {"conta_despesa", "fornecedor_norm", "tokens", "origem"}
        set_doc = {k: v for k, v in valor.items() if k in allowed}

        # tokens normalizados
        if "tokens" in set_doc and set_doc["tokens"] is not None:
            if not isinstance(set_doc["tokens"], list):
                raise ValueError("tokens deve ser uma lista de strings")
            norm_tokens = []
            for t in set_doc["tokens"]:
                s = str(t).strip().upper()
                if s:
                    norm_tokens.append(s)
            set_doc["tokens"] = list(dict.fromkeys(norm_tokens))

        # default de origem (caso não venha)
        if "origem" not in set_doc:
            set_doc["origem"] = "manual"

        # se for INSERT, conta_despesa é obrigatória
        existente = self.collection.find_one({"assinatura": chave})
        if not existente and ("conta_despesa" not in set_doc or not isinstance(set_doc["conta_despesa"], str)):
            raise ValueError("para criar, 'conta_despesa' é obrigatório e deve ser string")

        set_doc["updated_at"] = datetime.utcnow()

        set_on_insert = {
            "assinatura": chave,
            "created_at": datetime.utcnow(),
            "stats": {"aplicacoes": 0},
        }

        update_ops = {"$set": set_doc, "$setOnInsert": set_on_insert}
        if incrementar_aplicacoes > 0:
            update_ops["$inc"] = {"stats.aplicacoes": int(incrementar_aplicacoes)}

        doc = self.collection.find_one_and_update(
            {"assinatura": chave},
            update_ops,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc

    def deletar_contas_pagas(self, chave: str) -> dict:
        """
        Remove definitivamente o vínculo da assinatura.
         - chave: assinatura canônica (ex.: 'RFB|FGTS')
         Retorna o documento deletado.
         Lança ValueError se não encontrar.        
        """
        if not chave or not isinstance(chave, str):
            raise ValueError("assinatura (chave) inválida")

        doc = self.collection.find_one_and_delete({"assinatura": chave})
        if not doc:
            raise ValueError(
                f"assinatura '{chave}' não encontrada para deletar")

        return doc

    def listar_contas_pagas(
            self,
            termo: str | None = None,
            fornecedor: str | None = None,
            tokens: list[str] | None = None,
            conta: str | None = None,
            limit: int = 100,
            skip: int = 0,
            ordenar_por: str = 'assinatura',
            descendente: bool = False,
            campos: list[str] | None = None,
            retornar_total: bool = False,
    ):
        """
        LIsta vínculos da coleção "contas_pagas" com filtro opcionais.

        Parâmetros
        ----------
        termo: str | None
            Procura (regex, case-insensitive) em 'assinatura' OU 'fornecedor_norm'.
        fornecedor : str | None
            Filtro exato por fornecedor normalizado (UPPER, sem acento).
        tokens : list[str] | None
            Exige que TODOS os tokens (UPPER) estejam presentes (match $all).
        conta : str | None
            Filtro por 'conta_despesa'.
        limit : int
            Limite de documentos retornados (pagina).
        skip : int
            Deslocamento (offset) para paginação.
        ordenar_por : str
            Campo para ordenação (padrão: 'assinatura').
        descendente : bool
            True para ordem decrescente.
        campos : list[str] | None
            Projeção: lista de campos a retornar (ex.: ['assinatura','conta_despesa']).
        retornar_total : bool
            Se True, retorna {'total': X, 'items': [...]} para paginação; caso contrário, retorna apenas a lista.

        Retorna
        -------
        list[dict] | dict   
            Lista de documentos ou dict com total/items.
        """
        query = {}

        if termo:
            # Busca em assinatura OU fornecedor_norm
            rx = re.compile(
                re.escape(str(termo).strip().upper()), re.IGNORECASE)
            query["$or"] = [{"assinatura": rx}, {"fornecedor_norm": rx}]

        if fornecedor:
            query["fornecedor_norm"] = str(fornecedor).strip().upper()

        if conta:
            query["conta_despesa"] = str(conta).strip()

        if tokens:
            norm_tokens = [str(t).strip().upper()
                           for t in tokens if str(t).strip()]
            if norm_tokens:
                query["tokens"] = {"$all": norm_tokens}

        projection = None
        if campos:
            projection = {c: 1 for c in campos}
            # Para ocultar o _id, descomente:
            # projection["_id"] = 0

        sort_dir = -1 if descendente else 1

        cursor = (
            self.collection.find(query, projection)
            .sort(ordenar_por, sort_dir)
            .skip(int(skip))
            .limit(int(limit))
        )
        items = list(cursor)

        if retornar_total:
            total = self.collection.count_documents(query)
            return {"total": total, "items": items}

        return items
