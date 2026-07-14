from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from ..interfaces import ICofins01_02, ICofins03

@dataclass
class BaseCofins:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_icms: Decimal = Decimal('0')

    def calcular_base_cofins(self) -> Decimal:
        base_cofins = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias -
            self.valor_desconto
        )
        base_cofins = base_cofins - self.valor_icms
        return base_cofins.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Cofins01_02(ICofins01_02):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_cofins: Decimal
    valor_icms: Decimal = Decimal('0')

    _base_cofins: BaseCofins = field(init=False)

    def __post_init__(self):
        self._base_cofins = BaseCofins(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_icms
        )

    def base_cofins(self) -> Decimal:
        return self._base_cofins.calcular_base_cofins()

    def valor_cofins(self) -> Decimal:
        return (self.base_cofins() * (self.aliquota_cofins / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Cofins03(ICofins03):
    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    def valor_cofins(self) -> Decimal:
        return (self.aliquota_por_unidade * self.base_calculo).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
