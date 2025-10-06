from src.services.processador_tarifas import ProcessadorTarifas
from src.writers.lancamentos_contabeis_tarifas import LancamentosContabeisTarifas


def main():
    print("=== Importação de Tarifas Bancárias ===")

    # Passa o caminho da planilha no construtor
    processador = ProcessadorTarifas("data/input/MODELO DE PLANILHA.xlsx")

    # Processa as tarifas (agora sem precisar passar o path de novo)
    tarifas_processadas = processador.processar_tarifas()

    print("\n=== Resultado do processamento ===")
    for tarifa in tarifas_processadas:
        print(tarifa)

    print("\n=== Gerando arquivo de lançamentos contábeis ===")

    escritor = LancamentosContabeisTarifas()
    escritor.salvar_txt(tarifas_processadas,
                        "data/output/lancamentos_contabeis_tarifas.txt")
    print("\nArquivo 'lancamentos_contabeis_tarifas.txt' gerado com sucesso.")


if __name__ == "__main__":
    main()
