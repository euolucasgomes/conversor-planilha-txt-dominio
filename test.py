from db.repositorio_parametros import RepositorioParametros

if __name__ == "__main__":

    repo = RepositorioParametros()

    conta_tarifa = repo.obter_parametro("conta_tarifa_bancaria")
    
    if not conta_tarifa:
        conta_tarifa = input("Informe a conta contábil de tarifa bancária: ")
        repo.definir_parametro("conta_tarifa_bancaria", conta_tarifa)

print("Conta tarifa bancária:", conta_tarifa)
