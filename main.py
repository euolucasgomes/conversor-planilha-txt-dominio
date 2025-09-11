from src.readers.LeitorTarifas import LeitorTarifas

def main():
    input_file = "data/input/MODELO DE PLANILHA.xlsx"
    leitor = LeitorTarifas(input_file)
    leitor.ler_tarifas()


if __name__ == "__main__":
    main()