from src.services.processador_tarifas import ProcessadorTarifas
from src.services.processador_receitas import ProcessadorReceitas
from src.services.processador_apropriacoes import ProcessadorApropriacoes
from src.writers.lancamentos_contabeis_tarifas import LancamentosContabeisTarifas
from src.writers.lancamentos_contabeis_receitas import LancamentosContabeisReceitas
from src.writers.lancamentos_contabeis_apropriacoes import LancamentosContabeisApropriacoes
from src.menus.menu_contas_bancarias import MenuContasBancarias
from src.services.processador_contas_pagas import ProcessadorContasPagas
from src.writers.lancamentos_contabeis_contas_pagas import LancamentosContabeisContasPagas



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

# === APROPRIAÇÕES ===
def importar_apropriacoes():
    print("\n=== Importação de Apropriações ===")

    processador = ProcessadorApropriacoes("data/input/MODELO DE PLANILHA.xlsx")
    apropriacoes_processadas = processador.processar_apropriacoes()

    print("\n=== Resultado do processamento ===")
    for apropriacao in apropriacoes_processadas:
        print(apropriacao)

    print("\n=== Gerando arquivo de lançamentos contábeis ===")

    escritor = LancamentosContabeisApropriacoes()
    escritor.salvar_txt(
        apropriacoes_processadas,
        "data/output/lancamentos_contabeis_apropriacoes.txt"
    )

    print("\nArquivo 'lancamentos_contabeis_apropriacoes.txt' gerado com sucesso.")

# === CONTAS A PAGAR ===
def importar_contas_pagas():
    print("\n=== Importação de Contas a Pagar ===")

    processador = ProcessadorContasPagas("data/input/MODELO DE PLANILHA.xlsx")
    lancamentos, resumo = processador.processar_contas_pagas()

    print("\n=== Resumo do processamento ===")
    print(f"Auto (memória): {resumo.get('auto_memoria', 0)}")
    print(f"Sugestão/Manual: {resumo.get('via_sugestao_ou_manual', 0)}")
    print(f"Erros: {resumo.get('erros', 0)}")

    print("\n=== Amostra de lançamentos (máx. 5) ===")
    for l in lancamentos[:5]:
        print(l)

    print("\n=== Gerando arquivo de lançamentos contábeis ===")
    escritor = LancamentosContabeisContasPagas()
    escritor.salvar_txt(
        lancamentos,
        "data/output/lancamentos_contabeis_contas_pagas.txt",  # nome do arquivo para Contas a Pagar
        modo="w"  # use "a" se quiser appendar
    )
    print("\nArquivo 'lancamentos_contabeis_contas_pagas.txt' gerado com sucesso.")

# === MENU PRINCIPAL ===
def main():
    while True:
        print("\n=== SISTEMA DE CONVERSÃO CONTÁBIL ===")
        print("1. Importar Tarifas Bancárias")
        print("2. Importar Receitas")
        print("3. Importar Apropriações")
        print("4. Importar Contas a Pagar")         # <— NOVO
        print("5. Gerenciar Contas Bancárias")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            importar_tarifas()
        elif opcao == '2':
            importar_receitas()
        elif opcao == '3':
            importar_apropriacoes()
        elif opcao == '4':
            importar_contas_pagas()                 # <— NOVO
        elif opcao == '5':
            menu = MenuContasBancarias()
            menu.exibir_menu()
        elif opcao == '6':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")



if __name__ == "__main__":
    main()