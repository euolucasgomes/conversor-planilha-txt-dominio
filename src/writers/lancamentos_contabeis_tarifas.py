import datetime


class LancamentosContabeisTarifas:

    def __init__(self):
        self.encoding = 'cp1252'

    def formatar_linha(self, lancamento):

        data = lancamento['data'].strftime("%d/%m/%Y")

        valor_formatado = f"{lancamento['valor']:.2f}".replace('.', ',')

        conta_debito = lancamento['conta_contabil_tarifa']
        conta_credito = lancamento['conta_contabil_banco']

        descricao = f"Referente Tarifa bancária - Conta {lancamento['numero_conta']}".upper(
        )

        linha = f"{data};{conta_debito};{conta_credito};{valor_formatado};;{descricao};;;;"
        return linha

    def salvar_txt(self, lancamentos, caminho_arquivo):
        with open(caminho_arquivo, 'a', encoding=self.encoding) as arquivo:
            for lancamento in lancamentos:
                linha_formatada = self.formatar_linha(lancamento)
                arquivo.write(linha_formatada + "\n")
