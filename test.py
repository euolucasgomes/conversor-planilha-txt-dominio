from src.db.RepositorioParametros import RepositorioParametros

if __name__ == "__main__":
    repo = RepositorioParametros()
    repo.definir_parametro("conta_tarifa_bancaria", "40094")
    print(repo.obter_parametro("conta_tarifa_bancaria"))
