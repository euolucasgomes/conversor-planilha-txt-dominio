from src.services.processador_tarifas import ProcessadorTarifas
from src.writers.lancamentos_contabeis_tarifas import LancamentosContabeisTarifas
from src.menus.menu_contas_bancarias import MenuContasBancarias


def importar_tarifas():
    print("\n=== Importação de Tarifas Bancárias ===")

    processador = ProcessadorTarifas("data/input/MODELO DE PLANILHA.xlsx")
    tarifas_processadas = processador.processar_tarifas()

    print("\n=== Resultado do processamento ===")
    for tarifa in tarifas_processadas:
        print(tarifa)

    print("\n=== Gerando arquivo de lançamentos contábeis ===")

    escritor = LancamentosContabeisTarifas()
    escritor.salvar_txt(
        tarifas_processadas,
        "data/output/lancamentos_contabeis_tarifas.txt"
    )

    print("\nArquivo 'lancamentos_contabeis_tarifas.txt' gerado com sucesso.")


def main():
    while True:
        print("\n=== SISTEMA DE CONVERSÃO CONTÁBIL ===")
        print("1. Importar Tarifas Bancárias")
        print("2. Gerenciar Contas Bancárias")
        print("3. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            importar_tarifas()
        elif opcao == '2':
            menu = MenuContasBancarias()
            menu.exibir_menu()
        elif opcao == '3':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()