from src.readers.LeitorTarifas import LeitorTarifas
from src.readers.LeitorContasPagas import LeitorContasPagas

def main():
    input_file = "data/input/MODELO DE PLANILHA.xlsx"

    leitor_tarifas = LeitorTarifas(input_file)
    tarifas_df = leitor_tarifas.ler_tarifas()

    leitor_contas = LeitorContasPagas(input_file)
    contas_df = leitor_contas.ler_contas_pagas()

    return tarifas_df, contas_df

if __name__ == "__main__":
    main()
