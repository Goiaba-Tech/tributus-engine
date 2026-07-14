from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from ..interfaces import ICbs, IIbsUf


@dataclass
class BaseIbsCbs:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal

    def calcular_base_ibs_cbs(self) -> Decimal:
        base_ibs_cbs = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias
        )
        return base_ibs_cbs.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)


@dataclass
class Cbs(ICbs):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_efetiva_percentual: Decimal
    percentual_diferimento: Decimal = Decimal('0')

    _base_ibs_cbs: BaseIbsCbs = field(init=False)

    def __post_init__(self):
        self._base_ibs_cbs = BaseIbsCbs(
            self.valor_produto,
            self.valor_frete,
            self.valor_seguro,
            self.despesas_acessorias,
        )

    def valor_base_ibs_cbs(self) -> Decimal:
        return self._base_ibs_cbs.calcular_base_ibs_cbs()

    def aliquota_efetiva(self) -> Decimal:
        return self.aliquota_efetiva_percentual

    def _valor_cbs_bruto(self) -> Decimal:
        return (self.valor_base_ibs_cbs() * (self.aliquota_efetiva() / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )

    def diferimento(self) -> Decimal:
        return (self._valor_cbs_bruto() * (self.percentual_diferimento / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )

    def valor_cbs(self) -> Decimal:
        return (self._valor_cbs_bruto() - self.diferimento()).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )


@dataclass
class IbsUf(IIbsUf):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_efetiva_percentual: Decimal
    percentual_diferimento: Decimal = Decimal('0')

    _base_ibs_cbs: BaseIbsCbs = field(init=False)

    def __post_init__(self):
        self._base_ibs_cbs = BaseIbsCbs(
            self.valor_produto,
            self.valor_frete,
            self.valor_seguro,
            self.despesas_acessorias,
        )

    def valor_base_ibs_cbs(self) -> Decimal:
        return self._base_ibs_cbs.calcular_base_ibs_cbs()

    def aliquota_efetiva(self) -> Decimal:
        return self.aliquota_efetiva_percentual

    def _valor_ibs_uf_bruto(self) -> Decimal:
        return (self.valor_base_ibs_cbs() * (self.aliquota_efetiva() / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )

    def diferimento(self) -> Decimal:
        return (self._valor_ibs_uf_bruto() * (self.percentual_diferimento / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )

    def valor_ibs_uf(self) -> Decimal:
        return (self._valor_ibs_uf_bruto() - self.diferimento()).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_EVEN
        )