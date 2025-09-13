from readers.base_leitor import BaseLeitor


class LeitorApropriacoes(BaseLeitor):

    def ler_apropriacoes(self):
        self.df = self.ler("Apropriação")

        print(self.df.head())

        return self.df
