from src.readers.leitor_tarifas import LeitorTarifas
from src.db.repositorio_parametros import RepositorioParametros
from src.db.repositorio_contas_bancarias import RepositorioContasBancarias

class ProcessadorTarifas:

    def __init__(self, file_path):
        self.leitor = LeitorTarifas(file_path)
        self.repo_parametros = RepositorioParametros()
        self.repo_contas_bancarias = RepositorioContasBancarias()

    def processar_tarifas(self):

        df_tarifas = self.leitor.ler_tarifas()

        conta_tarifas = self.repo_parametros.obter_parametro("conta_tarifas_bancarias")
        
        if conta_tarifas is None:
            conta_tarifas = input("Informe a conta contábil para tarifas bancárias: ")
            self.repo_parametros.criar_parametro("conta_tarifas_bancarias", conta_tarifas)

        resultado = []

        for _, linha in df_tarifas.iterrows():
            
            numero_conta = linha['CONTA']

            conta_contabil_banco = self.repo_contas_bancarias.obter_contas_bancarias(numero_conta)
            
            if conta_contabil_banco is None:
                conta_contabil_banco = input(f"Informe a conta contábil para o banco {numero_conta}: ")
                self.repo_contas_bancarias.criar_contas_bancarias(numero_conta, conta_contabil_banco)

            resultado.append({
                "data": linha['DATA'],
                "valor": linha['VALOR'],
                "numero_conta": numero_conta,
                "conta_contabil_banco": conta_contabil_banco,
                "conta_contabil_tarifa": conta_tarifas,
            })

        return resultado