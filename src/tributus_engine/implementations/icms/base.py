from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

@dataclass
class BaseIcmsProprio:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        base_icms_proprio = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias +
            self.valor_ipi -
            self.valor_desconto
        )
        return base_icms_proprio.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class BaseIcmsST:
    base_icms_proprio: Decimal
    mva: Decimal
    valor_ipi: Decimal = Decimal('0')

    def calcular_base_icms_st(self) -> Decimal:
        result = (self.base_icms_proprio + self.valor_ipi) * (1 + (self.mva / 100))
        return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class BaseReduzidaIcmsProprio:
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    percentual_reducao: Decimal
    valor_ipi: Decimal = Decimal('0')

    def calcular_base_reduzida_icms_proprio(self) -> Decimal:
        base_icms = (
            self.valor_produto +
            self.valor_frete +
            self.valor_seguro +
            self.despesas_acessorias -
            self.valor_desconto
        )
        
        result = (base_icms - (base_icms * (self.percentual_reducao / 100))) + self.valor_ipi
        return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class BaseReduzidaIcmsST:
    base_icms_proprio: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal
    valor_ipi: Decimal = Decimal('0')

    def calcular_base_reduzida_icms_st(self) -> Decimal:
        base_st = self.base_icms_proprio * (1 + (self.mva / 100))
        base_st = base_st - (base_st * (self.percentual_reducao_st / 100))
        base_st_reduzida = base_st + self.valor_ipi
        return base_st_reduzida.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class ValorIcmsProprio:
    base_calculo: Decimal
    aliquota_icms_proprio: Decimal

    def calcular_valor_icms_proprio(self) -> Decimal:
        return (self.aliquota_icms_proprio / 100 * self.base_calculo).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class ValorIcmsST:
    base_calculo_st: Decimal
    aliquota_icms_st: Decimal
    valor_icms_proprio: Decimal

    def calcular_valor_icms_st(self) -> Decimal:
        return ((self.base_calculo_st * (self.aliquota_icms_st / 100)) - self.valor_icms_proprio).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
