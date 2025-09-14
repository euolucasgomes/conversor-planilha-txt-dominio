from src.readers.base_leitor import BaseLeitor


class LeitorTarifas(BaseLeitor):

    def ler_tarifas(self):
        self.df = self.ler("Tarifas bancárias")

        self.df.columns = self.df.iloc[0]
        self.df = self.df.drop(0)
        self.df = self.df.reset_index(drop=True)

        print(self.df.head())

        return self.df
