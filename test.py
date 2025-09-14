from src.services.processador_tarifas import ProcessadorTarifas

def main():
    print("=== Importação de Tarifas Bancárias ===")

    # Passa o caminho da planilha no construtor
    processador = ProcessadorTarifas("data/input/MODELO DE PLANILHA.xlsx")

    # Processa as tarifas (agora sem precisar passar o path de novo)
    tarifas_processadas = processador.processar_tarifas()

    print("\n=== Resultado do processamento ===")
    for tarifa in tarifas_processadas:
        print(tarifa)


if __name__ == "__main__":
    main()
