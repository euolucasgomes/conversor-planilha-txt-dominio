class BaseLeitor:
    def __init__(self, file_path):
        self.file_path = file_path

    def ler(self, sheet_name: str):
        import pandas as pd
        return pd.read_excel(self.file_path, sheet_name=sheet_name)