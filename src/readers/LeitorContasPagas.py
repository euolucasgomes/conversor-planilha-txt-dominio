from src.readers.BaseLeitor import BaseLeitor


class LeitorContasPagas(BaseLeitor):

    def ler_contas_pagas(self):
        self.df = self.ler("Contas pagas")

        print(self.df.head())

        return self.df
