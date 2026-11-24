from __future__ import annotations

from models import Apartamento, Casa, Estudio, Imovel, TaxaContratual
from orcamento import OrcamentoLocacao


def ler_opcao(prompt: str, opcoes_validas: tuple[str, ...]) -> str:
    opcoes_norm = tuple(op.lower() for op in opcoes_validas)
    while True:
        resposta = input(prompt).strip().lower()
        if resposta in opcoes_norm:
            return resposta
        print(f"Entrada inválida. Escolha uma das opções: {', '.join(opcoes_validas)}.")


def ler_inteiro(prompt: str, minimo: int, maximo: int) -> int:
    while True:
        bruto = input(prompt).strip()
        try:
            valor = int(bruto)
            if minimo <= valor <= maximo:
                return valor
            print(f"Digite um número inteiro entre {minimo} e {maximo}.")
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_sim_nao(prompt: str) -> bool:
    escolha = ler_opcao(f"{prompt} (s/n): ", ("s", "n"))
    return escolha == "s"


def construir_imovel() -> Imovel:
    print("\nCategorias disponíveis: [1] Apartamento | [2] Casa | [3] Estudio")
    tipo = ler_opcao("Escolha o tipo de imóvel (1/2/3): ", ("1", "2", "3"))

    if tipo == "1":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem (+ R$ 300,00/mês)?")
        criancas = ler_sim_nao("O cliente possui crianças?")
        return Apartamento(quartos=quartos, possui_garagem=garagem, possui_criancas=criancas)

    if tipo == "2":
        quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem (+ R$ 300,00/mês)?")
        return Casa(quartos=quartos, possui_garagem=garagem)

    utiliza_estacionamento = ler_sim_nao(
        "Deseja contratar o pacote inicial de estacionamento com 2 vagas (R$ 250,00)?"
    )
    vagas_extras = 0
    if utiliza_estacionamento:
        vagas_extras = ler_inteiro(
            "Quantas vagas adicionais deseja (R$ 60,00 cada, 0 para nenhuma)? ", 0, 20
        )
    return Estudio(
        utiliza_estacionamento=utiliza_estacionamento,
        vagas_adicionais=vagas_extras,
    )


def executar_sistema() -> None:
    print("Bem-vindo ao RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)")
    imovel = construir_imovel()
    parcelas = ler_inteiro(
        "Em quantas parcelas deseja pagar a taxa contratual de R$ 2.000,00 (1 a 5)? ",
        1,
        5,
    )
    taxa = TaxaContratual(parcelas=parcelas)

    orcamento = OrcamentoLocacao(imovel=imovel, taxa_contratual=taxa)
    print("\n" + orcamento.formatar_resumo())

    caminho_csv = orcamento.exportar_csv("projecao_12_meses.csv")
    print(f"\nProjeção dos 12 meses salva com sucesso em: {caminho_csv}")


if __name__ == "__main__":
    executar_sistema()