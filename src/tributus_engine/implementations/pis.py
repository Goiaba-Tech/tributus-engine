from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from ..interfaces import IPis01_02, IPis03

@dataclass
class BasePIS:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_icms: Decimal = Decimal('0')

    def calcular_base_pis(self) -> Decimal:
        base_pis = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias -
            self.valor_desconto
        )
        base_pis = base_pis - self.valor_icms
        return base_pis.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Pis01_02(IPis01_02):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_pis: Decimal
    valor_icms: Decimal = Decimal('0')

    _base_pis: BasePIS = field(init=False)

    def __post_init__(self):
        self._base_pis = BasePIS(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_icms
        )

    def base_pis(self) -> Decimal:
        return self._base_pis.calcular_base_pis()

    def valor_pis(self) -> Decimal:
        return (self.base_pis() * (self.aliquota_pis / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Pis03(IPis03):
    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    def valor_pis(self) -> Decimal:
        return (self.aliquota_por_unidade * self.base_calculo).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
