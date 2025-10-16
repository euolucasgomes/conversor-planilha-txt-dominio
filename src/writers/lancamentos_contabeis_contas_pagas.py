# src/writers/lancamentos_contabeis_contas_pagas.py
from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any, Dict, Iterable


class LancamentosContabeisContasPagas:
    """
    Writer de lançamentos de Contas a Pagar no formato TXT do Domínio (TOTVS).

    Espera cada item de `lancamentos` com as chaves:
      - data: str "dd/mm/aaaa" ou datetime/date
      - debito: str (conta de despesa)
      - credito: str (conta contábil do banco)
      - valor: str "1.234,56" ou float/Decimal
      - historico: str (será truncado se necessário pelo Processador)
    """

    def __init__(self, encoding: str = "cp1252"):
        self.encoding = encoding
        self.sep = ";"

    # ---------- helpers de formatação ----------

    def _formatar_data(self, data: Any) -> str:
        if isinstance(data, (datetime, date)):
            return data.strftime("%d/%m/%Y")
        # já vem como "dd/mm/aaaa"
        return str(data).strip()

    def _formatar_valor(self, valor: Any) -> str:
        """
        Retorna sempre com vírgula decimal: "1234,56".
        Aceita float/int/Decimal ou str já formatada.
        """
        if isinstance(valor, (int, float)):
            return f"{float(valor):.2f}".replace(".", ",")
        s = str(valor).strip()
        # Se já parecer formato brasileiro, mantém:
        if "," in s:
            return s
        # Caso venha "1234.56" ou "1.234.56" → normaliza
        try:
            num = float(s.replace(".", "").replace(",", "."))
            return f"{num:.2f}".replace(".", ",")
        except Exception:
            # fallback: retorna cru
            return s

    def formatar_linha(self, lancamento: Dict[str, Any]) -> str:
        data = self._formatar_data(lancamento["data"])
        valor = self._formatar_valor(lancamento["valor"])

        conta_debito = str(lancamento["debito"]).strip()
        conta_credito = str(lancamento["credito"]).strip()

        historico = str(lancamento.get("historico", "")).strip().upper()

        # Padrão Domínio: DATA;DEBITO;CREDITO;VALOR;;HISTORICO;;;;
        campos = [
            data,
            conta_debito,
            conta_credito,
            valor,
            "",            # campo vazio conforme layout
            historico,
            "", "", "", "" # campos finais vazios
        ]
        return self.sep.join(campos)

    # ---------- persistência ----------

    def salvar_txt(self, lancamentos: Iterable[Dict[str, Any]], caminho_arquivo: str, modo: str = "a") -> str:
        """
        Escreve/Anexa o TXT no caminho indicado.
        - modo: "a" (append) por padrão; use "w" para sobrescrever.
        Retorna o caminho do arquivo gerado.
        """
        os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        with open(caminho_arquivo, modo, encoding=self.encoding, newline="") as f:
            for lancamento in lancamentos:
                linha = self.formatar_linha(lancamento)
                f.write(linha + "\n")
        return caminho_arquivo
