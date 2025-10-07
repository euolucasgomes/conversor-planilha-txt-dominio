import pandas as pd
from src.readers.leitor_apropriacoes import LeitorApropriacoes
from src.db.repositorio_parametros import RepositorioParametros

class ProcessadorApropriacoes:

    def __init__(self, file_path):
        self.leitor = LeitorApropriacoes(file_path)
        self.repo_parametros = RepositorioParametros()

    def processar_apropriacoes(self):

        df_apropriacoes = self.leitor.ler_apropriacoes()

        resultado = []

        for _, linha in df_apropriacoes.iterrows():
            
            data = linha['DATA']
            conta_debito = linha['DEBITO']
            conta_credito = linha['CREDITO']
            valor = linha['VALOR']
            cd_historico = linha['CD HIST']
            historico = linha['HIST']

            resultado.append({
                "data": data,
                "debito": conta_debito,
                "credito": conta_credito,
                "valor": valor,
                "cd_historico": cd_historico,
                "historico": historico,
            })

        return resultado