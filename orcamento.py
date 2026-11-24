from __future__ import annotations

import csv
from pathlib import Path

from models import Imovel, TaxaContratual


class OrcamentoLocacao:
    """Consolida o orçamento mensal, a taxa contratual e exporta a projeção de 12 meses."""

    def __init__(self, imovel: Imovel, taxa_contratual: TaxaContratual) -> None:
        self.imovel = imovel
        self.taxa_contratual = taxa_contratual

    @property
    def valor_aluguel_mensal(self) -> float:
        return self.imovel.calcular_aluguel_mensal()

    def gerar_projecao_12_meses(self) -> list[dict[str, float | int | str]]:
        aluguel = self.valor_aluguel_mensal
        projecao: list[dict[str, float | int | str]] = []

        for mes in range(1, 13):
            parcela_taxa = self.taxa_contratual.parcela_no_mes(mes)
            total_mes = round(aluguel + parcela_taxa, 2)
            status_taxa = (
                f"Parcela {mes}/{self.taxa_contratual.parcelas}"
                if mes <= self.taxa_contratual.parcelas
                else "Taxa quitada"
            )
            projecao.append(
                {
                    "mes": mes,
                    "aluguel_mensal": f"{aluguel:.2f}",
                    "parcela_taxa_contratual": f"{parcela_taxa:.2f}",
                    "total_previsto_mes": f"{total_mes:.2f}",
                    "status_taxa": status_taxa,
                }
            )

        return projecao

    def exportar_csv(self, caminho_arquivo: str | Path = "projecao_12_meses.csv") -> Path:
        destino = Path(caminho_arquivo)
        dados = self.gerar_projecao_12_meses()

        with destino.open(mode="w", newline="", encoding="utf-8") as arquivo_csv:
            campos = [
                "mes",
                "aluguel_mensal",
                "parcela_taxa_contratual",
                "total_previsto_mes",
                "status_taxa",
            ]
            escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(dados)

        return destino.resolve()

    def formatar_resumo(self) -> str:
        linhas = [
            "=" * 56,
            "RENTSMART — R.M IMÓVEIS | RESUMO DO ORÇAMENTO DE LOCAÇÃO",
            "=" * 56,
            f"Imóvel selecionado: {self.imovel.categoria}",
            "-" * 56,
            "COMPOSIÇÃO DO ALUGUEL MENSAL:",
        ]

        for item in self.imovel.detalhar_composicao():
            linhas.append(f"  - {item.descricao}: R$ {item.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        aluguel_fmt = f"R$ {self.valor_aluguel_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        linhas.extend(
            [
                "-" * 56,
                f"ALUGUEL MENSAL FINAL: {aluguel_fmt}",
                "=" * 56,
                "TAXA CONTRATUAL (ITEM SEPARADO DO ALUGUEL MENSAL):",
                f"  - Valor total da taxa contratual: R$ {self.taxa_contratual.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"  - Condição de parcelamento: {self.taxa_contratual.parcelas}x de R$ {self.taxa_contratual.valor_parcela:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "=" * 56,
            ]
        )
        return "\n".join(linhas)