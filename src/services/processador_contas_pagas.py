# src/services/processador_contas_pagas.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Callable, Dict, List, Optional, Tuple, Any

import re
import pandas as pd
from unidecode import unidecode

from src.readers.leitor_contas_pagas import LeitorContasPagas
from src.db.repositorio_parametros import RepositorioParametros
from src.db.repositorio_contas_bancarias import RepositorioContasBancarias
from src.db.repositorio_contas_pagas import RepositorioContasPagas


@dataclass
class LinhaContexto:
    fornecedor: str
    descricao: str
    documento: str
    numero_conta_banco: str
    data_movimento: str  # dd/mm/aaaa
    valor: str           # "1.234,56"


ResolverCallback = Callable[
    [str, str, List[str], List[Dict], LinhaContexto],
    str  # retorna conta_despesa escolhida
]


class ProcessadorContasPagas:
    """
    Pipeline:
      1) Lê a planilha com LeitorContasPagas
      2) Normaliza fornecedor/descrição e gera assinatura (fornecedor_norm + tokens)
      3) Resolve conta DÉBITO (despesa) pela memória → sugestão → confirmação
      4) Resolve conta CRÉDITO (banco) via contas_bancarias
      5) Monta lançamento: DATA;DEBITO;CREDITO;VALOR;;HISTORICO;;;;
    """

    _STOPWORDS_BASE = {
        "PAG", "PAGTO", "PAGAMENTO", "GUIA", "REF", "REFERENTE", "FATURA", "NF", "NFE",
        "BOLETO", "COMP", "COMPETENCIA", "MES", "MÊS", "PARC", "PARCELA", "CONF",
        "DE", "DA", "DO", "DOS", "DAS", "A", "E", "POR", "PARA"
    }
    _MESES = {"JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"}

    def __init__(self, file_path: str, resolver_callback: Optional[ResolverCallback] = None):
        self.leitor = LeitorContasPagas(file_path)
        self.repo_param = RepositorioParametros()
        self.repo_bancos = RepositorioContasBancarias()
        self.repo_memoria = RepositorioContasPagas()
        self.resolver_callback = resolver_callback

        # --- parâmetros (via obter_parametro/criar_parametro) ---
        hist = self.repo_param.obter_parametro("historico_padrao_pagamentos")
        if not hist:
            hist = "PAGTO {DOC} - {FORNECEDOR} - {DESC}"
            try:
                self.repo_param.criar_parametro("historico_padrao_pagamentos", hist)
            except Exception:
                pass
        self.hist_padrao = hist

        raw_stop = self.repo_param.obter_parametro("stopwords_descricao")
        parsed_stop = self._parse_stopwords(raw_stop)
        self.stopwords = self._STOPWORDS_BASE.union(parsed_stop).union(self._MESES)

        self.conta_despesas_fallback = self.repo_param.obter_parametro("conta_despesas_gerais")
        if not self.conta_despesas_fallback:
            conta_informada = input("Informe a conta contábil de DESPESAS GERAIS (fallback): ").strip()
            self.repo_param.criar_parametro("conta_despesas_gerais", conta_informada)
            self.conta_despesas_fallback = conta_informada

    # ---------- helpers de parâmetros ----------

    @staticmethod
    def _parse_stopwords(raw: Any) -> set:
        """Aceita None, lista/tupla/conjunto ou string (CSV/; / | / linhas)."""
        if raw is None:
            return set()
        if isinstance(raw, (list, tuple, set)):
            return {unidecode(str(x).strip().upper()) for x in raw if str(x).strip()}
        s = str(raw)
        parts = re.split(r"[,\n;|]+", s)
        return {unidecode(p.strip().upper()) for p in parts if p.strip()}

    # ---------- Normalização & assinatura ----------

    @staticmethod
    def _norm(s: str) -> str:
        return unidecode((s or "").strip().upper())

    def _limpar_ruidos(self, texto: str) -> str:
        t = self._norm(texto)
        # remove datas: dd/mm/yyyy, mm/yyyy, yyyy, dd/mm/yy
        t = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", " ", t)
        t = re.sub(r"\b\d{2}/\d{4}\b", " ", t)
        t = re.sub(r"\b20\d{2}\b", " ", t)  # remove ano 20xx
        # remove pontuação e substitui por espaço
        t = re.sub(r"[^A-Z0-9]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _extrair_tokens(self, descricao: str) -> List[str]:
        base = self._limpar_ruidos(descricao)
        if not base:
            return []
        tokens = [tok for tok in base.split(" ") if tok and tok not in self.stopwords]
        # mantém ordem mas remove duplicados
        seen = set()
        limpos = []
        for tok in tokens:
            if tok not in seen:
                seen.add(tok)
                limpos.append(tok)
        return limpos

    def _gerar_assinatura(self, fornecedor: str, descricao: str) -> Tuple[str, str, List[str]]:
        fornecedor_norm = self._norm(fornecedor)
        tokens = sorted(set(self._extrair_tokens(descricao)))  # assinatura estável
        assinatura = fornecedor_norm + "|" + "|".join(tokens) if tokens else fornecedor_norm + "|"
        return assinatura, fornecedor_norm, tokens

    # ---------- Sugestões quando memória não tem ----------

    def _sugerir_por_fornecedor_tokens(self, fornecedor_norm: str, tokens: List[str]) -> List[Dict]:
        docs = self.repo_memoria.listar_contas_pagas(
            fornecedor=fornecedor_norm,
            limit=200,
            campos=["assinatura", "conta_despesa", "tokens", "updated_at", "stats"]
        )
        if not docs:
            return []
        tokset = set(tokens)
        scored = []
        for d in docs:
            dtoks = set(d.get("tokens") or [])
            inter = len(tokset.intersection(dtoks))
            uso = (d.get("stats") or {}).get("aplicacoes", 0)
            scored.append({
                "conta_despesa": d.get("conta_despesa"),
                "assinatura": d.get("assinatura"),
                "tokens": list(d.get("tokens") or []),
                "score": inter * 10 + min(uso, 50),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        # top 3 sugestões distintas por conta
        vistos = set()
        sugestoes = []
        for s in scored:
            c = s["conta_despesa"]
            if c and c not in vistos:
                vistos.add(c)
                sugestoes.append(s)
            if len(sugestoes) >= 3:
                break
        return sugestoes

    # ---------- Resolver conta (memória → sugestão → confirmação) ----------

    def _resolver_conta_despesa(
        self,
        assinatura: str,
        fornecedor_norm: str,
        tokens: List[str],
        ctx: LinhaContexto
    ) -> Tuple[str, str]:
        """
        Retorna (conta_despesa, origem_decisao)
        origem_decisao: 'memoria' | 'sugestao' | 'manual'
        """
        # 1) memória direta
        doc = self.repo_memoria.obter_contas_pagas(assinatura)
        if doc:
            self.repo_memoria.atualizar_contas_pagas(assinatura, {}, incrementar_aplicacoes=1)
            return doc["conta_despesa"], "memoria"

        # 2) sugestões por fornecedor/tokens
        sugestoes = self._sugerir_por_fornecedor_tokens(fornecedor_norm, tokens)

        # 3) pedir confirmação (callback ou input)
        conta_escolhida = None
        if self.resolver_callback:
            conta_escolhida = self.resolver_callback(assinatura, fornecedor_norm, tokens, sugestoes, ctx)
        else:
            print("\n⚙️  Classificação necessária (conta de DÉBITO - despesa):")
            print(f"Fornecedor..: {ctx.fornecedor}")
            print(f"Descrição...: {ctx.descricao}")
            print(f"Documento...: {ctx.documento}")
            if sugestoes:
                print("Sugestões (por histórico):")
                for i, s in enumerate(sugestoes, start=1):
                    print(f"  {i}) Conta {s['conta_despesa']}  • score {s['score']}  • assinatura {s['assinatura']}")
            conta_escolhida = input("Informe a conta de despesa (ex.: 51001) ou escolha 1/2/3 das sugestões: ").strip()
            if conta_escolhida in {"1", "2", "3"}:
                idx = int(conta_escolhida) - 1
                if idx < len(sugestoes):
                    conta_escolhida = sugestoes[idx]["conta_despesa"]

        conta_escolhida = (conta_escolhida or "").strip()
        if not conta_escolhida:
            tentativa = input(f"Conta de despesa não informada. Usar fallback '{self.conta_despesas_fallback}'? (S/n): ").strip().upper()
            if tentativa in {"", "S", "SIM"}:
                conta_escolhida = self.conta_despesas_fallback
            else:
                raise ValueError("Conta de despesa não informada.")

        # grava memória para os próximos meses
        self.repo_memoria.definir_contas_pagas(
            chave=assinatura,
            valor={
                "conta_despesa": conta_escolhida,
                "fornecedor_norm": fornecedor_norm,
                "tokens": tokens,
                "origem": "manual",
            },
            incrementar_aplicacoes=1
        )
        return conta_escolhida, ("sugestao" if sugestoes else "manual")

    # ---------- Histórico / formatação ----------

    def _montar_historico(self, documento: str, fornecedor: str, descricao: str) -> str:
        h = self.hist_padrao
        h = h.replace("{DOC}", (documento or "")[:40])
        h = h.replace("{FORNECEDOR}", (fornecedor or "")[:60])
        h = h.replace("{DESC}", (descricao or "")[:80])
        return h[:240]

    # ---------- Parse robusto de data/valor ----------

    @staticmethod
    def _parse_data(raw: Any) -> Optional[datetime]:
        """Aceita Timestamp/datetime/date ou string dd/mm/aaaa | aaaa-mm-dd hh:mm:ss."""
        if isinstance(raw, (pd.Timestamp, datetime, date)):
            return pd.to_datetime(raw)
        s = str(raw).strip()
        if not s or s.upper() == "NAT":
            return None
        # tenta com pandas (aceita vários formatos)
        dt = pd.to_datetime(s, dayfirst=True, errors="coerce")
        return None if pd.isna(dt) else dt

    @staticmethod
    def _parse_valor(raw: Any) -> Optional[float]:
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return None
        if isinstance(raw, (int, float)):
            return float(raw)
        s = str(raw).strip()
        if not s:
            return None
        try:
            return float(s.replace(".", "").replace(",", "."))
        except Exception:
            return None

    # ---------- API principal ----------

    def processar_contas_pagas(self) -> Tuple[List[Dict], Dict]:
        """
        Retorna (lancamentos, resumo)
          - lancamentos: [{data, debito, credito, valor, historico, ...}]
          - resumo: contagem de auto (memória) / manual/sugestão / erros
        """
        df = self.leitor.ler_contas_pagas()

        lancamentos: List[Dict] = []
        resumo = {"auto_memoria": 0, "via_sugestao_ou_manual": 0, "erros": 0}

        for idx, row in df.iterrows():
            try:
                fornecedor = str(row.get("FORNECEDOR", "") or "")
                descricao = str(
                    row.get("DESCRIÇÃO DO SERVIÇO", "") or
                    row.get("DESCRIÇÃO DO SERVICO", "") or   # <— NOVO
                    row.get("DESCRICAO DO SERVICO", "") or
                    row.get("DESCRICAO DO SERVIÇO", "") or ""
                )
                documento = str(row.get("DOCUMENTO", "") or "")

                # pular linhas totalmente vazias
                if not fornecedor and not descricao:
                    continue

                # Data
                raw_dt = row.get("DATA MOVIMENTO", None)
                data_dt = row.get("DATA_FMT", None)
                if pd.isna(data_dt) if isinstance(data_dt, (pd.Timestamp, float)) else data_dt is None:
                    data_dt = self._parse_data(raw_dt)
                if not data_dt:
                    print(f"[AVISO] Linha {idx}: data inválida → pulando linha.")
                    resumo["erros"] += 1
                    continue
                data_str = pd.to_datetime(data_dt).strftime("%d/%m/%Y")

                # Valor
                raw_val = row.get("VALOR PAGO", None)
                valor_num = row.get("VALOR_PAGO_NUM", None)
                if valor_num is None or (isinstance(valor_num, float) and pd.isna(valor_num)):
                    valor_num = self._parse_valor(raw_val)
                if valor_num is None or valor_num <= 0:
                    print(f"[AVISO] Linha {idx}: valor inválido → pulando linha.")
                    resumo["erros"] += 1
                    continue
                valor_str = f"{float(valor_num):.2f}".replace(".", ",")

                # Banco (CRÉDITO)
                raw_banco = row.get("CONTA DE DÉBITO", "")
                numero_conta_banco = "" if raw_banco is None or str(raw_banco).strip().upper() in {"", "NAN", "NONE"} else str(raw_banco).strip()
                conta_contabil_banco = self.repo_bancos.obter_contas_bancarias(numero_conta_banco)
                if conta_contabil_banco is None:
                    conta_contabil_banco = input(f"Informe a conta contábil para o banco '{numero_conta_banco}': ").strip()
                    self.repo_bancos.criar_contas_bancarias(numero_conta_banco, conta_contabil_banco)

                # Assinatura & resolução de conta de DESPESA (DÉBITO)
                assinatura, fornecedor_norm, tokens = self._gerar_assinatura(fornecedor, descricao)
                ctx = LinhaContexto(
                    fornecedor=fornecedor,
                    descricao=descricao,
                    documento=documento,
                    numero_conta_banco=numero_conta_banco,
                    data_movimento=data_str,
                    valor=valor_str,
                )
                conta_despesa, origem = self._resolver_conta_despesa(
                    assinatura, fornecedor_norm, tokens, ctx
                )
                if origem == "memoria":
                    resumo["auto_memoria"] += 1
                else:
                    resumo["via_sugestao_ou_manual"] += 1

                historico = self._montar_historico(documento, fornecedor, descricao)

                # Estrutura pronta para o writer TXT (Domínio)
                lancamentos.append({
                    "data": data_str,
                    "debito": conta_despesa,            # DÉBITO = conta de despesa
                    "credito": conta_contabil_banco,    # CRÉDITO = conta do banco
                    "valor": valor_str,
                    "historico": historico,
                    # auxiliares
                    "fornecedor": fornecedor,
                    "descricao": descricao,
                    "documento": documento,
                    "numero_conta": numero_conta_banco,
                })

            except Exception as e:
                resumo["erros"] += 1
                print(f"[ERRO] Linha {idx} ignorada: {e}")

        return lancamentos, resumo