from src.services.processador_tarifas import ProcessadorTarifas
from src.services.processador_receitas import ProcessadorReceitas
from src.writers.lancamentos_contabeis_tarifas import LancamentosContabeisTarifas
from src.writers.lancamentos_contabeis_receitas import LancamentosContabeisReceitas
from src.menus.menu_contas_bancarias import MenuContasBancarias


# === TARIFAS ===
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


# === RECEITAS ===
def importar_receitas():
    print("\n=== Importação de Receitas ===")

    processador = ProcessadorReceitas("data/input/MODELO DE PLANILHA.xlsx")
    receitas_processadas = processador.processar_receitas()

    print("\n=== Resultado do processamento ===")
    for receita in receitas_processadas:
        print(receita)

    print("\n=== Gerando arquivo de lançamentos contábeis ===")

    escritor = LancamentosContabeisReceitas()
    escritor.salvar_txt(
        receitas_processadas,
        "data/output/lancamentos_contabeis_receitas.txt"
    )

    print("\nArquivo 'lancamentos_contabeis_receitas.txt' gerado com sucesso.")


# === MENU PRINCIPAL ===
def main():
    while True:
        print("\n=== SISTEMA DE CONVERSÃO CONTÁBIL ===")
        print("1. Importar Tarifas Bancárias")
        print("2. Importar Receitas")
        print("3. Gerenciar Contas Bancárias")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            importar_tarifas()
        elif opcao == '2':
            importar_receitas()
        elif opcao == '3':
            menu = MenuContasBancarias()
            menu.exibir_menu()
        elif opcao == '4':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()