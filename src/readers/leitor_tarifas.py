from src.readers.base_leitor import BaseLeitor
import pandas as pd


class LeitorTarifas(BaseLeitor):

    def ler_tarifas(self):
        self.df = self.ler("Tarifas bancárias")

        self.df.columns = self.df.iloc[0]
        self.df = self.df.drop(0)
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.dropna(subset=["CONTA"])
        self.df["VALOR"] = pd.to_numeric(self.df["VALOR"], errors='coerce')
        self.df = self.df.dropna(subset=["VALOR"])

        print(self.df.head())

        return self.df
