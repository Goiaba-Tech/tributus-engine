from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Optional

from ...interfaces import (
    IIcms00, IIcms10, IIcms20, IIcms30, IIcms51, IIcms70, IIcms90,
    IIcms101, IIcms201, IIcms202_203, IIcms900
)
from .base import (
    BaseIcmsProprio, BaseIcmsST, BaseReduzidaIcmsProprio, BaseReduzidaIcmsST,
    ValorIcmsProprio, ValorIcmsST
)

@dataclass
class Icms00(IIcms00):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    
    _base_icms: BaseIcmsProprio = field(init=False)

    def __post_init__(self):
        self._base_icms = BaseIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_ipi
        )

    def base_icms_proprio(self) -> Decimal:
        return self._base_icms.calcular_base_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

@dataclass
class Icms10(IIcms10):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal = Decimal('0')

    _bc_icms_proprio: BaseIcmsProprio = field(init=False)

    def __post_init__(self):
        self._bc_icms_proprio = BaseIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto
        )

    def base_icms_proprio(self) -> Decimal:
        return self._bc_icms_proprio.calcular_base_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == 0:
            return self._base_icms_st_normal()
        else:
            bc_reduzida_icms_st = BaseReduzidaIcmsST(
                self.base_icms_proprio(), self.mva, self.percentual_reducao_st, self.valor_ipi
            )
            return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def _base_icms_st_normal(self) -> Decimal:
        bc_icms_st = BaseIcmsST(self.base_icms_proprio(), self.mva, self.valor_ipi)
        return bc_icms_st.calcular_base_icms_st()

    def _valor_icms_st_normal(self, base_icms_st: Decimal) -> Decimal:
        return ValorIcmsST(base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

    def valor_icms_st(self) -> Decimal:
        return self._valor_icms_st_normal(self.base_icms_st())

    def valor_icms_st_desonerado(self) -> Decimal:
        valor_icms_st_normal = self._valor_icms_st_normal(self._base_icms_st_normal())
        valor_icms_st_desonerado = valor_icms_st_normal - self.valor_icms_st()
        return valor_icms_st_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms20(IIcms20):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    percentual_reducao: Decimal

    _base_reduzida_icms: BaseReduzidaIcmsProprio = field(init=False)

    def __post_init__(self):
        self._base_reduzida_icms = BaseReduzidaIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.percentual_reducao, self.valor_ipi
        )

    def base_reduzida_icms_proprio(self) -> Decimal:
        return self._base_reduzida_icms.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        base_reduzida_icms = self.base_reduzida_icms_proprio()
        valor_icms = base_reduzida_icms * (self.aliquota_icms_proprio / 100)
        return valor_icms.quantize(Decimal('0.01'))

    def valor_icms_desonerado(self) -> Decimal:
        icms00 = Icms00(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_ipi, self.valor_desconto, self.aliquota_icms_proprio
        )
        valor_icms_normal = icms00.valor_icms_proprio()
        valor_icms_desonerado = valor_icms_normal - self.valor_icms_proprio()
        return valor_icms_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms30(IIcms30):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliq_icms_proprio: Decimal
    aliq_icms_st: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal = Decimal('0')

    _bc_icms_proprio: BaseIcmsProprio = field(init=False)

    def __post_init__(self):
        self._bc_icms_proprio = BaseIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto
        )

    def base_icms_proprio(self) -> Decimal:
        return self._bc_icms_proprio.calcular_base_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.base_icms_proprio(), self.aliq_icms_proprio).calcular_valor_icms_proprio()
    
    def valor_icms_desonerado(self) -> Decimal:
        return self.valor_icms_proprio()

    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == 0:
            bc_icms_st = BaseIcmsST(self.base_icms_proprio(), self.mva, self.valor_ipi)
            return bc_icms_st.calcular_base_icms_st()
        else:
            bc_reduzida_icms_st = BaseReduzidaIcmsST(
                self.base_icms_proprio(), self.mva, self.percentual_reducao_st, self.valor_ipi
            )
            return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.base_icms_st(), self.aliq_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

@dataclass
class Icms51(IIcms51):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliq_icms_proprio: Decimal
    percentual_reducao: Decimal
    percentual_diferimento: Decimal

    def base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == 0:
            bc_icms_proprio = BaseIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto, self.valor_ipi
            )
            return bc_icms_proprio.calcular_base_icms_proprio()
        else:
            bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto, self.percentual_reducao, self.valor_ipi
            )
            return bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_operacao(self) -> Decimal:
        return ValorIcmsProprio(self.base_icms_proprio(), self.aliq_icms_proprio).calcular_valor_icms_proprio()

    def valor_icms_diferido(self) -> Decimal:
        valor_icms_operacao = self.valor_icms_operacao()
        valor_icms_diferido = (valor_icms_operacao * (self.percentual_diferimento / 100))
        return valor_icms_diferido.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

    def valor_icms_proprio(self) -> Decimal:
        valor_icms_proprio = self.valor_icms_operacao() - self.valor_icms_diferido()
        return valor_icms_proprio.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms70(IIcms70):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_ipi: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao: Decimal
    percentual_reducao_st: Decimal = Decimal('0')

    _bc_reduzida_icms_proprio: BaseReduzidaIcmsProprio = field(init=False)

    def __post_init__(self):
        self._bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.percentual_reducao
        )

    def base_icms_proprio(self) -> Decimal:
        return self._bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_icms_proprio_desonerado(self) -> Decimal:
        icms00 = Icms00(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, Decimal('0'), self.valor_desconto, self.aliquota_icms_proprio
        )
        valor_icms_normal = icms00.valor_icms_proprio()
        valor_icms_desonerado = valor_icms_normal - self.valor_icms_proprio()
        return valor_icms_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == 0:
            bc_icms_st = BaseIcmsST(self.base_icms_proprio(), self.mva, self.valor_ipi)
            return bc_icms_st.calcular_base_icms_st()
        else:
            bc_reduzida_icms_st = BaseReduzidaIcmsST(
                self.base_icms_proprio(), self.mva, self.percentual_reducao_st, self.valor_ipi
            )
            return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.base_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

    def valor_icms_st_desonerado(self) -> Decimal:
        icms10 = Icms10(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_ipi, self.valor_desconto,
            self.aliquota_icms_proprio, self.aliquota_icms_st, self.mva
        )
        valor_icms_st_normal = icms10.valor_icms_st()
        valor_icms_st_desonerado = valor_icms_st_normal - self.valor_icms_st()
        return valor_icms_st_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms90(IIcms90):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    valor_ipi: Decimal = Decimal('0')
    percentual_reducao: Decimal = Decimal('0')
    percentual_reducao_st: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        base_icms_proprio = BaseIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_ipi
        )
        return base_icms_proprio.calcular_base_icms_proprio()

    def calcular_base_reduzida_icms_proprio(self) -> Decimal:
        bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.percentual_reducao, self.valor_ipi
        )
        return bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.calcular_base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_icms_proprio_base_reduzida(self) -> Decimal:
        return ValorIcmsProprio(self.calcular_base_reduzida_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_icms_proprio_desonerado(self) -> Decimal:
        icms00 = Icms00(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_ipi, self.valor_desconto, self.aliquota_icms_proprio
        )
        valor_icms_normal = icms00.valor_icms_proprio()
        valor_icms_desonerado = valor_icms_normal - self.valor_icms_proprio_base_reduzida()
        return valor_icms_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

    def calcular_base_icms_st(self) -> Decimal:
        bc_icms_st = BaseIcmsST(self.calcular_base_icms_proprio(), self.mva, self.valor_ipi)
        return bc_icms_st.calcular_base_icms_st()

    def calcular_base_reduzida_icms_st(self) -> Decimal:
        bc_reduzida_icms_st = BaseReduzidaIcmsST(
            self.calcular_base_icms_proprio(), self.mva, self.percentual_reducao_st, self.valor_ipi
        )
        return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.calcular_base_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

    def valor_icms_st_base_reduzida(self) -> Decimal:
        return ValorIcmsST(self.calcular_base_reduzida_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

    def valor_icms_st_desonerado(self) -> Decimal:
        icms10 = Icms10(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_ipi, self.valor_desconto,
            self.aliquota_icms_proprio, self.aliquota_icms_st, self.mva
        )
        valor_icms_st_normal = icms10.valor_icms_st()
        valor_icms_st_desonerado = valor_icms_st_normal - self.valor_icms_st_base_reduzida()
        return valor_icms_st_desonerado.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms101(IIcms101):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    percentual_credito_sn: Decimal
    percentual_reducao: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == 0:
            base_icms_proprio = BaseIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto
            )
            return base_icms_proprio.calcular_base_icms_proprio()
        else:
            base_reduzida = BaseReduzidaIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto, self.percentual_reducao
            )
            return base_reduzida.calcular_base_reduzida_icms_proprio()

    def valor_credito_sn(self) -> Decimal:
        valor_credito_sn = (self.calcular_base_icms_proprio() * (self.percentual_credito_sn / 100))
        return valor_credito_sn.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

@dataclass
class Icms201(IIcms201):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_credito_sn: Decimal
    percentual_reducao: Decimal = Decimal('0')
    percentual_reducao_st: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == 0:
            base_icms_proprio = BaseIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto
            )
            return base_icms_proprio.calcular_base_icms_proprio()
        else:
            bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto, self.percentual_reducao
            )
            return bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.calcular_base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_credito_sn(self) -> Decimal:
        valor_credito_sn = (self.calcular_base_icms_proprio() * (self.percentual_credito_sn / 100))
        return valor_credito_sn.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == 0:
            bc_icms_st = BaseIcmsST(self.calcular_base_icms_proprio(), self.mva)
            return bc_icms_st.calcular_base_icms_st()
        else:
            bc_reduzida_icms_st = BaseReduzidaIcmsST(
                self.calcular_base_icms_proprio(), self.mva, self.percentual_reducao_st
            )
            return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.base_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

@dataclass
class Icms202_203(IIcms202_203):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao: Decimal = Decimal('0')
    percentual_reducao_st: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == 0:
            base_icms_proprio = BaseIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto
            )
            return base_icms_proprio.calcular_base_icms_proprio()
        else:
            bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
                self.valor_produto, self.valor_frete, self.valor_seguro,
                self.despesas_acessorias, self.valor_desconto, self.percentual_reducao
            )
            return bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.calcular_base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == 0:
            bc_icms_st = BaseIcmsST(self.calcular_base_icms_proprio(), self.mva)
            return bc_icms_st.calcular_base_icms_st()
        else:
            bc_reduzida_icms_st = BaseReduzidaIcmsST(
                self.calcular_base_icms_proprio(), self.mva, self.percentual_reducao_st
            )
            return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.base_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

@dataclass
class Icms900(IIcms900):
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_credito_sn: Decimal = Decimal('0')
    valor_ipi: Decimal = Decimal('0')
    percentual_reducao: Decimal = Decimal('0')
    percentual_reducao_st: Decimal = Decimal('0')

    def calcular_base_icms_proprio(self) -> Decimal:
        base_icms_proprio = BaseIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.valor_ipi
        )
        return base_icms_proprio.calcular_base_icms_proprio()

    def calcular_base_reduzida_icms_proprio(self) -> Decimal:
        bc_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
            self.valor_produto, self.valor_frete, self.valor_seguro,
            self.despesas_acessorias, self.valor_desconto, self.percentual_reducao, self.valor_ipi
        )
        return bc_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()

    def valor_icms_proprio(self) -> Decimal:
        return ValorIcmsProprio(self.calcular_base_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_icms_proprio_base_reduzida(self) -> Decimal:
        # Note: The original C# code used Round(val, 2) here instead of Round(val, 2, MidpointRounding.ToEven) in one place, 
        # but mostly consistent. I'll stick to standard rounding for consistency unless tests fail.
        # Actually in C# Icms900.ValorIcmsProprio used Round(val, 2) (default is ToEven in C#? No, default is ToEven in Math.Round(decimal), but here it was explicit).
        # Wait, C# `decimal.Round(val, 2)` uses `MidpointRounding.ToEven` by default.
        return ValorIcmsProprio(self.calcular_base_reduzida_icms_proprio(), self.aliquota_icms_proprio).calcular_valor_icms_proprio()

    def valor_credito_sn(self) -> Decimal:
        if self.percentual_reducao == 0:
            valor_credito_sn = (self.calcular_base_icms_proprio() * (self.percentual_credito_sn / 100))
        else:
            valor_credito_sn = (self.calcular_base_reduzida_icms_proprio() * (self.percentual_credito_sn / 100))
        
        return valor_credito_sn.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

    def calcular_base_icms_st(self) -> Decimal:
        bc_icms_st = BaseIcmsST(self.calcular_base_icms_proprio(), self.mva, self.valor_ipi)
        return bc_icms_st.calcular_base_icms_st()

    def calcular_base_reduzida_icms_st(self) -> Decimal:
        bc_reduzida_icms_st = BaseReduzidaIcmsST(
            self.calcular_base_icms_proprio(), self.mva, self.percentual_reducao_st, self.valor_ipi
        )
        return bc_reduzida_icms_st.calcular_base_reduzida_icms_st()

    def valor_icms_st(self) -> Decimal:
        return ValorIcmsST(self.calcular_base_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()

    def valor_icms_st_base_reduzida(self) -> Decimal:
        return ValorIcmsST(self.calcular_base_reduzida_icms_st(), self.aliquota_icms_st, self.valor_icms_proprio()).calcular_valor_icms_st()
