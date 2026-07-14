from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from ..interfaces import IIpi50AdValorem, IIpiEspecifico

@dataclass
class BaseIPI:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal

    def calcular_base_ipi(self) -> Decimal:
        base_ipi = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias
        )
        return base_ipi.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Ipi50AdValorem(IIpi50AdValorem):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_ipi: Decimal

    _base_calculo: BaseIPI = field(init=False)

    def __post_init__(self):
        self._base_calculo = BaseIPI(
            self.valor_produto, self.valor_frete, self.valor_seguro, self.despesas_acessorias
        )

    def calcular_base_ipi(self) -> Decimal:
        return self._base_calculo.calcular_base_ipi()

    def valor_ipi(self) -> Decimal:
        return (self.calcular_base_ipi() * (self.aliquota_ipi / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Ipi50Especifico(IIpiEspecifico):
    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    def valor_ipi(self) -> Decimal:
        return (self.aliquota_por_unidade * self.base_calculo).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
