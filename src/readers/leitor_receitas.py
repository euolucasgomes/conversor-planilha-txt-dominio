from src.readers.base_leitor import BaseLeitor


class LeitorReceitas(BaseLeitor):

    def ler_receitas(self):
        self.df = self.ler("Receitas")
        self.df = self.df.dropna(subset=["DATA PAGAMENTO", "VALOR PAGO"])

        print(self.df.head())

        return self.df
