from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DetalheCalculo:
    descricao: str
    valor: float


class Imovel(ABC):
    """Classe base para imóveis da R.M Imóveis."""

    TAXA_GARAGEM_PADRAO = 300.00

    def __init__(self, aluguel_base: float, possui_garagem: bool = False) -> None:
        if aluguel_base <= 0:
            raise ValueError("O aluguel-base deve ser maior que zero.")
        self.aluguel_base = float(aluguel_base)
        self.possui_garagem = possui_garagem

    @property
    @abstractmethod
    def categoria(self) -> str:
        """Nome legível da categoria do imóvel."""

    @abstractmethod
    def detalhar_composicao(self) -> list[DetalheCalculo]:
        """Retorna os itens que compõem o cálculo do aluguel mensal."""

    def calcular_aluguel_mensal(self) -> float:
        total = sum(item.valor for item in self.detalhar_composicao())
        return round(total, 2)


class Apartamento(Imovel):
    """Regra de locação para apartamentos (1 ou 2 quartos, garagem e desconto sem crianças)."""

    ALUGUEL_BASE = 700.00
    ADICIONAL_DOIS_QUARTOS = 200.00
    DESCONTO_SEM_CRIANCAS = 0.05

    def __init__(
        self,
        quartos: int,
        possui_garagem: bool = False,
        possui_criancas: bool = True,
    ) -> None:
        if quartos not in (1, 2):
            raise ValueError("Apartamento aceita apenas 1 ou 2 quartos.")
        super().__init__(aluguel_base=self.ALUGUEL_BASE, possui_garagem=possui_garagem)
        self.quartos = quartos
        self.possui_criancas = possui_criancas

    @property
    def categoria(self) -> str:
        return f"Apartamento ({self.quartos} quarto{'s' if self.quartos > 1 else ''})"

    def detalhar_composicao(self) -> list[DetalheCalculo]:
        itens = [DetalheCalculo("Aluguel-base (Apartamento 1 quarto)", self.aluguel_base)]

        if self.quartos == 2:
            itens.append(
                DetalheCalculo("Adicional 2 quartos (Apartamento)", self.ADICIONAL_DOIS_QUARTOS)
            )

        if self.possui_garagem:
            itens.append(DetalheCalculo("Vaga de garagem", self.TAXA_GARAGEM_PADRAO))

        subtotal_com_adicionais = sum(item.valor for item in itens)

        # Desconto de 5% aplicado após os adicionais quando não há crianças
        if not self.possui_criancas:
            desconto = -round(subtotal_com_adicionais * self.DESCONTO_SEM_CRIANCAS, 2)
            itens.append(DetalheCalculo("Desconto sem crianças (5%)", desconto))

        return itens


class Casa(Imovel):
    """Regra de locação para casas (1 ou 2 quartos e garagem)."""

    ALUGUEL_BASE = 900.00
    ADICIONAL_DOIS_QUARTOS = 250.00

    def __init__(self, quartos: int, possui_garagem: bool = False) -> None:
        if quartos not in (1, 2):
            raise ValueError("Casa aceita apenas 1 ou 2 quartos.")
        super().__init__(aluguel_base=self.ALUGUEL_BASE, possui_garagem=possui_garagem)
        self.quartos = quartos

    @property
    def categoria(self) -> str:
        return f"Casa ({self.quartos} quarto{'s' if self.quartos > 1 else ''})"

    def detalhar_composicao(self) -> list[DetalheCalculo]:
        itens = [DetalheCalculo("Aluguel-base (Casa 1 quarto)", self.aluguel_base)]

        if self.quartos == 2:
            itens.append(
                DetalheCalculo("Adicional 2 quartos (Casa)", self.ADICIONAL_DOIS_QUARTOS)
            )

        if self.possui_garagem:
            itens.append(DetalheCalculo("Vaga de garagem", self.TAXA_GARAGEM_PADRAO))

        return itens


class Estudio(Imovel):
    """Regra de locação para estúdios (pacote inicial de 2 vagas + vagas adicionais)."""

    ALUGUEL_BASE = 1200.00
    VALOR_PACOTE_DUAS_VAGAS = 250.00
    VALOR_VAGA_ADICIONAL = 60.00

    def __init__(
        self,
        utiliza_estacionamento: bool = False,
        vagas_adicionais: int = 0,
    ) -> None:
        if vagas_adicionais < 0:
            raise ValueError("Quantidade de vagas adicionais não pode ser negativa.")
        if vagas_adicionais > 0 and not utiliza_estacionamento:
            raise ValueError(
                "Não é possível adicionar vagas extras sem contratar o pacote inicial de estacionamento."
            )
        super().__init__(aluguel_base=self.ALUGUEL_BASE, possui_garagem=utiliza_estacionamento)
        self.utiliza_estacionamento = utiliza_estacionamento
        self.vagas_adicionais = vagas_adicionais

    @property
    def categoria(self) -> str:
        total_vagas = (2 + self.vagas_adicionais) if self.utiliza_estacionamento else 0
        return f"Estúdio ({total_vagas} vaga{'s' if total_vagas != 1 else ''})"

    def detalhar_composicao(self) -> list[DetalheCalculo]:
        itens = [DetalheCalculo("Aluguel-base (Estúdio)", self.aluguel_base)]

        if self.utiliza_estacionamento:
            itens.append(
                DetalheCalculo(
                    "Pacote inicial de estacionamento (até 2 vagas)",
                    self.VALOR_PACOTE_DUAS_VAGAS,
                )
            )
            if self.vagas_adicionais > 0:
                total_extras = round(self.vagas_adicionais * self.VALOR_VAGA_ADICIONAL, 2)
                itens.append(
                    DetalheCalculo(
                        f"Vagas adicionais ({self.vagas_adicionais} x R$ 60,00)",
                        total_extras,
                    )
                )

        return itens


class TaxaContratual:
    """Representa a taxa contratual fixa e seu parcelamento em até 5 vezes."""

    VALOR_TOTAL = 2000.00
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int = 1) -> None:
        if not isinstance(parcelas, int) or not (1 <= parcelas <= self.MAX_PARCELAS):
            raise ValueError("A taxa contratual deve ser parcelada entre 1 e 5 vezes.")
        self.parcelas = parcelas

    @property
    def valor_total(self) -> float:
        return self.VALOR_TOTAL

    @property
    def valor_parcela(self) -> float:
        return round(self.VALOR_TOTAL / self.parcelas, 2)

    def parcela_no_mes(self, mes: int) -> float:
        """Retorna o valor da parcela da taxa contratual referente ao mês (1 a 12)."""
        if mes < 1 or mes > 12:
            raise ValueError("O mês deve estar entre 1 e 12.")
        return self.valor_parcela if mes <= self.parcelas else 0.00