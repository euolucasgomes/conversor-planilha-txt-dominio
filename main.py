from src.readers.LeitorTarifas import LeitorTarifas
from src.readers.LeitorContasPagas import LeitorContasPagas
from src.readers.LeitorReceitas import LeitorReceitas
from src.readers.LeitorApropriacoes import LeitorApropriacoes


def main():
    input_file = "data/input/MODELO DE PLANILHA.xlsx"

    leitor_tarifas = LeitorTarifas(input_file)
    tarifas_df = leitor_tarifas.ler_tarifas()

    leitor_contas = LeitorContasPagas(input_file)
    contas_df = leitor_contas.ler_contas_pagas()

    leitor_receitas = LeitorReceitas(input_file)
    receitas_df = leitor_receitas.ler_receitas()

    ler_apropriacoes = LeitorApropriacoes(input_file)
    apropriacoes_df = ler_apropriacoes.ler_apropriacoes()

    return tarifas_df, contas_df, receitas_df, apropriacoes_df


if __name__ == "__main__":
    main()
