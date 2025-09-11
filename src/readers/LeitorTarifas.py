import pandas as pd

class LeitorTarifas:
    def __init__(self, modelo_planilha):
        self.modelo_planilha = modelo_planilha

    def ler_tarifas(self):
        self.df = pd.read_excel(self.modelo_planilha, sheet_name="Tarifas bancárias")

        print(self.df.head())