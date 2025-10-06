import pandas as pd
from src.readers.leitor_receitas import LeitorReceitas
from src.db.repositorio_parametros import RepositorioParametros
from src.db.repositorio_contas_bancarias import RepositorioContasBancarias

class ProcessadorReceitas:

    def __init__(self, file_path):
        self.leitor = LeitorReceitas(file_path)
        self.repo_parametros = RepositorioParametros()
        self.repo_contas_bancarias = RepositorioContasBancarias()

    def processar_receitas(self):

        df_receitas = self.leitor.ler_receitas()

        conta_transitoria_recebimento = self.repo_parametros.obter_parametro("conta_transitoria_recebimento")
        
        if conta_transitoria_recebimento is None:
            conta_transitoria_recebimento = input("Informe a conta contábil para conta transitória de recebimento: ")
            self.repo_parametros.criar_parametro("conta_transitoria_recebimento", conta_transitoria_recebimento)

        resultado = []

        for _, linha in df_receitas.iterrows():
            
            numero_conta = linha['C/C']

            conta_contabil_banco = self.repo_contas_bancarias.obter_contas_bancarias(numero_conta)

            nf = str(linha['NF']).split('.')[0] if not pd.isna(linha['NF']) else ""
            cliente = str(linha['CLIENTE']).strip() if not pd.isna(linha['CLIENTE']) else ""
            
            if conta_contabil_banco is None:
                conta_contabil_banco = input(f"Informe a conta contábil para o banco {numero_conta}: ")
                self.repo_contas_bancarias.criar_contas_bancarias(numero_conta, conta_contabil_banco)

            resultado.append({
                "data": linha['DATA PAGAMENTO'],
                "valor": linha['VALOR PAGO'],
                "numero_conta": numero_conta,
                "conta_contabil_banco": conta_contabil_banco,
                "conta_transitoria_recebimento": conta_transitoria_recebimento,
                "nf": nf,
                "cliente": cliente
            })

        return resultado