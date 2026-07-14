from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

from ...interfaces import IFcp, IFcpDif, IFcpEfet, IFcpST

@dataclass
class Fcp(IFcp):
    base_calculo: Decimal
    aliquota_fcp: Decimal

    def valor_fcp(self) -> Decimal:
        return (self.aliquota_fcp / 100 * self.base_calculo).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class FcpDiferido(IFcpDif):
    valor_fcp: Decimal
    aliquota_diferimento_fcp: Decimal

    def valor_fcp_diferido(self) -> Decimal:
        return (self.valor_fcp * self.aliquota_diferimento_fcp / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class FcpEfetivo(IFcpEfet):
    valor_fcp: Decimal
    valor_fcp_diferido: Decimal

    def valor_fcp_efetivo(self) -> Decimal:
        return (self.valor_fcp - self.valor_fcp_diferido).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class FcpST(IFcpST):
    base_calculo_st: Decimal
    aliquota_fcp_st: Decimal

    def valor_fcp_st(self) -> Decimal:
        return (self.aliquota_fcp_st / 100 * self.base_calculo_st).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
