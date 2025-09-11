from src.readers.BaseLeitor import BaseLeitor


class LeitorTarifas(BaseLeitor):

    def ler_tarifas(self):
        self.df = self.ler("Tarifas bancárias")

        print(self.df.head())

        return self.df
