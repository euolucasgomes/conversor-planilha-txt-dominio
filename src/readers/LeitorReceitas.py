from src.readers.BaseLeitor import BaseLeitor


class LeitorReceitas(BaseLeitor):

    def ler_receitas(self):
        self.df = self.ler("Receitas")

        print(self.df.head())

        return self.df
