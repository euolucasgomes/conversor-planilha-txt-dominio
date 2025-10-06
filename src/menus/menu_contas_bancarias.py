from src.db.repositorio_contas_bancarias import RepositorioContasBancarias

class MenuContasBancarias:
    def __init__(self):
        self.repo = RepositorioContasBancarias()

    def exibir_menu(self):
        while True:
            print("\n=== MENU CONTAS BANCÁRIAS ===")
            print("1. Listar Contas Bancárias")
            print("2. Criar Conta Bancária")
            print("3. Atualizar Conta Bancária")
            print("4. Deletar Conta Bancária")
            print("5. Sair")

            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                self.listar()
            elif escolha == '2':
                self.criar()
            elif escolha == '3':
                self.atualizar()
            elif escolha == '4':
                self.deletar()
            elif escolha == '5':
                print("Saindo do menu...")
                break
            else:
                print("Opção inválida. Tente novamente.")

    def listar(self):
        contas = self.repo.listar_contas_bancarias()
        if not contas:
            print("Nenhuma conta cadastrada.")
            return
        for conta in contas:
            print(f"Conta Corrente: {conta['numero_conta']}  →  Conta Contábil: {conta['conta_contabil_banco']}")

    def criar(self):
        numero_conta = input("Número da Conta: ")
        conta_contabil_banco = input("Conta Contábil do Banco: ")
        self.repo.criar_contas_bancarias(numero_conta, conta_contabil_banco)
        print("Conta bancária criada com sucesso.")

    def atualizar(self):
        numero_conta = input("Número da Conta: ")
        conta_contabil_banco = input("Nova Conta Contábil do Banco: ")
        self.repo.atualizar_contas_bancarias(numero_conta, conta_contabil_banco)
        print("Conta bancária atualizada com sucesso.")

    def deletar(self):
        numero_conta = input("Número da Conta a ser deletada: ")
        self.repo.deletar_contas_bancarias(numero_conta)
        print("Conta bancária deletada com sucesso.")