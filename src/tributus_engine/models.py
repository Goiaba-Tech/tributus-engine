from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field, computed_field

ZERO = Decimal("0.00")


def _round2(value: Decimal) -> Decimal:
    """Arredonda para 2 casas decimais com banker's rounding (half-even)."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def _pct(percentual: Decimal) -> Decimal:
    """Converte percentual para fator de multiplicação. Ex: 18 → 0.18."""
    return percentual / Decimal("100")


def _to_decimal(v: Any) -> Decimal:
    """Aceita str, float ou Decimal e retorna Decimal formatado."""
    if v is None or v == "":
        return ZERO
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


# Tipo que aceita str | float | Decimal e converte para Decimal automaticamente
Decimalable = Annotated[
    Decimal,
    BeforeValidator(_to_decimal),
]


# =============================================================================
# COFINS
# =============================================================================


class Cofins01_02(BaseModel):
    model_config = {"extra": "forbid"}

    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_cofins: Decimal
    valor_icms: Decimal = ZERO

    @computed_field
    @property
    def base_cofins(self) -> Decimal:
        base = (
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
            - self.valor_desconto
            - self.valor_icms
        )
        return _round2(base)

    @computed_field
    @property
    def valor_cofins(self) -> Decimal:
        return _round2(self.base_cofins * _pct(self.aliquota_cofins))


class Cofins03(BaseModel):
    model_config = {"extra": "forbid"}

    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    @computed_field
    @property
    def valor_cofins(self) -> Decimal:
        return _round2(self.aliquota_por_unidade * self.base_calculo)


# =============================================================================
# PIS
# =============================================================================


class Pis01_02(BaseModel):
    model_config = {"extra": "forbid"}

    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_pis: Decimal
    valor_icms: Decimal = ZERO

    @computed_field
    @property
    def base_pis(self) -> Decimal:
        base = (
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
            - self.valor_desconto
            - self.valor_icms
        )
        return _round2(base)

    @computed_field
    @property
    def valor_pis(self) -> Decimal:
        return _round2(self.base_pis * _pct(self.aliquota_pis))


class Pis03(BaseModel):
    model_config = {"extra": "forbid"}

    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    @computed_field
    @property
    def valor_pis(self) -> Decimal:
        return _round2(self.aliquota_por_unidade * self.base_calculo)


# =============================================================================
# IPI
# =============================================================================


class IpiAdValorem(BaseModel):
    model_config = {"extra": "forbid"}

    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_ipi: Decimal

    @computed_field
    @property
    def base_ipi(self) -> Decimal:
        return _round2(
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
        )

    @computed_field
    @property
    def valor_ipi(self) -> Decimal:
        return _round2(self.base_ipi * _pct(self.aliquota_ipi))


class IpiEspecifico(BaseModel):
    model_config = {"extra": "forbid"}

    base_calculo: Decimal
    aliquota_por_unidade: Decimal

    @computed_field
    @property
    def valor_ipi(self) -> Decimal:
        return _round2(self.aliquota_por_unidade * self.base_calculo)


# =============================================================================
# IBS / CBS
# =============================================================================


class Ibs(BaseModel):
    model_config = {"extra": "forbid"}

    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_efetiva_percentual: Decimal
    percentual_diferimento: Decimal = ZERO

    @computed_field
    @property
    def base_ibs_cbs(self) -> Decimal:
        return _round2(
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
        )

    @computed_field
    @property
    def _valor_bruto(self) -> Decimal:
        return _round2(self.base_ibs_cbs * _pct(self.aliquota_efetiva_percentual))

    @computed_field
    @property
    def diferimento(self) -> Decimal:
        return _round2(self._valor_bruto * _pct(self.percentual_diferimento))

    @computed_field
    @property
    def valor_ibs(self) -> Decimal:
        return _round2(self._valor_bruto - self.diferimento)


class Cbs(BaseModel):
    model_config = {"extra": "forbid"}

    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    aliquota_efetiva_percentual: Decimal
    percentual_diferimento: Decimal = ZERO

    @computed_field
    @property
    def base_ibs_cbs(self) -> Decimal:
        return _round2(
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
        )

    @computed_field
    @property
    def _valor_bruto(self) -> Decimal:
        return _round2(self.base_ibs_cbs * _pct(self.aliquota_efetiva_percentual))

    @computed_field
    @property
    def diferimento(self) -> Decimal:
        return _round2(self._valor_bruto * _pct(self.percentual_diferimento))

    @computed_field
    @property
    def valor_cbs(self) -> Decimal:
        return _round2(self._valor_bruto - self.diferimento)


# =============================================================================
# FCP (Fundo de Combate à Pobreza)
# =============================================================================


class Fcp(BaseModel):
    model_config = {"extra": "forbid"}

    base_calculo: Decimal
    aliquota_fcp: Decimal

    @computed_field
    @property
    def valor_fcp(self) -> Decimal:
        return _round2(_pct(self.aliquota_fcp) * self.base_calculo)


class FcpST(BaseModel):
    model_config = {"extra": "forbid"}

    base_calculo_st: Decimal
    aliquota_fcp_st: Decimal

    @computed_field
    @property
    def valor_fcp_st(self) -> Decimal:
        return _round2(_pct(self.aliquota_fcp_st) * self.base_calculo_st)


class FcpDiferido(BaseModel):
    model_config = {"extra": "forbid"}

    valor_fcp: Decimal
    aliquota_diferimento_fcp: Decimal

    @computed_field
    @property
    def valor_fcp_diferido(self) -> Decimal:
        return _round2(self.valor_fcp * _pct(self.aliquota_diferimento_fcp))


class FcpEfetivo(BaseModel):
    model_config = {"extra": "forbid"}

    valor_fcp: Decimal
    valor_fcp_diferido: Decimal

    @computed_field
    @property
    def valor_fcp_efetivo(self) -> Decimal:
        return _round2(self.valor_fcp - self.valor_fcp_diferido)


# =============================================================================
# ICMS — Métricas de base e valor compartilhadas entre CSTs (privadas)
# =============================================================================


class _BaseIcmsProprio(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _round2(
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
            + self.valor_ipi
            - self.valor_desconto
        )


class _BaseReduzidaIcmsProprio(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    percentual_reducao: Decimal
    valor_ipi: Decimal = ZERO

    @computed_field
    @property
    def base_reduzida_icms_proprio(self) -> Decimal:
        base = (
            self.valor_produto
            + self.valor_frete
            + self.valor_seguro
            + self.despesas_acessorias
            - self.valor_desconto
        )
        result = (base - (base * _pct(self.percentual_reducao))) + self.valor_ipi
        return _round2(result)


class _BaseIcmsST(BaseModel):
    model_config = {"extra": "forbid"}
    base_icms_proprio: Decimal
    mva: Decimal
    valor_ipi: Decimal = ZERO

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        result = (self.base_icms_proprio + self.valor_ipi) * (1 + _pct(self.mva))
        return _round2(result)


class _BaseReduzidaIcmsST(BaseModel):
    model_config = {"extra": "forbid"}
    base_icms_proprio: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal
    valor_ipi: Decimal = ZERO

    @computed_field
    @property
    def base_reduzida_icms_st(self) -> Decimal:
        base_st = self.base_icms_proprio * (1 + _pct(self.mva))
        base_st = base_st - (base_st * _pct(self.percentual_reducao_st))
        return _round2(base_st + self.valor_ipi)


def _valor_icms_proprio(base: Decimal, aliquota: Decimal) -> Decimal:
    return _round2(_pct(aliquota) * base)


def _valor_icms_st(base_st: Decimal, aliquota_st: Decimal, valor_icms_proprio: Decimal) -> Decimal:
    return _round2((base_st * _pct(aliquota_st)) - valor_icms_proprio)


# =============================================================================
# ICMS — CSTs
# =============================================================================


class Icms00(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliquota_icms_proprio: Decimal

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=self.valor_ipi,
        ).base_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)


class Icms10(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=ZERO,
        ).base_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == ZERO:
            return _BaseIcmsST(
                base_icms_proprio=self.base_icms_proprio,
                mva=self.mva,
                valor_ipi=self.valor_ipi,
            ).base_icms_st
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)

    @computed_field
    @property
    def valor_icms_st_desonerado(self) -> Decimal:
        base_st_normal = _BaseIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            valor_ipi=self.valor_ipi,
        ).base_icms_st
        valor_normal = _valor_icms_st(base_st_normal, self.aliquota_icms_st, self.valor_icms_proprio)
        return _round2(valor_normal - self.valor_icms_st)


class Icms20(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliquota_icms_proprio: Decimal
    percentual_reducao: Decimal

    @computed_field
    @property
    def base_reduzida_icms_proprio(self) -> Decimal:
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _round2(self.base_reduzida_icms_proprio * _pct(self.aliquota_icms_proprio))

    @computed_field
    @property
    def valor_icms_desonerado(self) -> Decimal:
        base_normal = _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=self.valor_ipi,
        ).base_icms_proprio
        valor_normal = _valor_icms_proprio(base_normal, self.aliquota_icms_proprio)
        return _round2(valor_normal - self.valor_icms_proprio)


class Icms30(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliq_icms_proprio: Decimal
    aliq_icms_st: Decimal
    mva: Decimal
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
        ).base_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliq_icms_proprio)

    @computed_field
    @property
    def valor_icms_desonerado(self) -> Decimal:
        return self.valor_icms_proprio

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == ZERO:
            return _BaseIcmsST(
                base_icms_proprio=self.base_icms_proprio,
                mva=self.mva,
                valor_ipi=self.valor_ipi,
            ).base_icms_st
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliq_icms_st, self.valor_icms_proprio)


class Icms51(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliq_icms_proprio: Decimal
    percentual_reducao: Decimal
    percentual_diferimento: Decimal

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == ZERO:
            return _BaseIcmsProprio(
                valor_produto=self.valor_produto,
                valor_frete=self.valor_frete,
                valor_seguro=self.valor_seguro,
                despesas_acessorias=self.despesas_acessorias,
                valor_desconto=self.valor_desconto,
                valor_ipi=self.valor_ipi,
            ).base_icms_proprio
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_operacao(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliq_icms_proprio)

    @computed_field
    @property
    def valor_icms_diferido(self) -> Decimal:
        return _round2(self.valor_icms_operacao * _pct(self.percentual_diferimento))

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _round2(self.valor_icms_operacao - self.valor_icms_diferido)


class Icms70(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    valor_ipi: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao: Decimal
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
            valor_ipi=ZERO,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_icms_proprio_desonerado(self) -> Decimal:
        base_normal = _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=ZERO,
        ).base_icms_proprio
        valor_normal = _valor_icms_proprio(base_normal, self.aliquota_icms_proprio)
        return _round2(valor_normal - self.valor_icms_proprio)

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == ZERO:
            return _BaseIcmsST(
                base_icms_proprio=self.base_icms_proprio,
                mva=self.mva,
                valor_ipi=self.valor_ipi,
            ).base_icms_st
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)

    @computed_field
    @property
    def valor_icms_st_desonerado(self) -> Decimal:
        bc_st_normal = _BaseIcmsST(
            base_icms_proprio=_BaseIcmsProprio(
                valor_produto=self.valor_produto,
                valor_frete=self.valor_frete,
                valor_seguro=self.valor_seguro,
                despesas_acessorias=self.despesas_acessorias,
                valor_desconto=self.valor_desconto,
            ).base_icms_proprio,
            mva=self.mva,
            valor_ipi=self.valor_ipi,
        ).base_icms_st
        bc_proprio_normal = _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
        ).base_icms_proprio
        valor_normal = _valor_icms_st(
            bc_st_normal, self.aliquota_icms_st,
            _valor_icms_proprio(bc_proprio_normal, self.aliquota_icms_proprio),
        )
        return _round2(valor_normal - self.valor_icms_st)


class Icms90(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    valor_ipi: Decimal = ZERO
    percentual_reducao: Decimal = ZERO
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=self.valor_ipi,
        ).base_icms_proprio

    @computed_field
    @property
    def base_reduzida_icms_proprio(self) -> Decimal:
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_icms_proprio_base_reduzida(self) -> Decimal:
        return _valor_icms_proprio(self.base_reduzida_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_icms_proprio_desonerado(self) -> Decimal:
        base_normal = _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=self.valor_ipi,
        ).base_icms_proprio
        valor_normal = _valor_icms_proprio(base_normal, self.aliquota_icms_proprio)
        return _round2(valor_normal - self.valor_icms_proprio_base_reduzida)

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        return _BaseIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            valor_ipi=self.valor_ipi,
        ).base_icms_st

    @computed_field
    @property
    def base_reduzida_icms_st(self) -> Decimal:
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)

    @computed_field
    @property
    def valor_icms_st_base_reduzida(self) -> Decimal:
        return _valor_icms_st(self.base_reduzida_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)


class Icms101(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    percentual_credito_sn: Decimal
    percentual_reducao: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == ZERO:
            return _BaseIcmsProprio(
                valor_produto=self.valor_produto,
                valor_frete=self.valor_frete,
                valor_seguro=self.valor_seguro,
                despesas_acessorias=self.despesas_acessorias,
                valor_desconto=self.valor_desconto,
            ).base_icms_proprio
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_credito_sn(self) -> Decimal:
        return _round2(self.base_icms_proprio * _pct(self.percentual_credito_sn))


class Icms201(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_credito_sn: Decimal
    percentual_reducao: Decimal = ZERO
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == ZERO:
            return _BaseIcmsProprio(
                valor_produto=self.valor_produto,
                valor_frete=self.valor_frete,
                valor_seguro=self.valor_seguro,
                despesas_acessorias=self.despesas_acessorias,
                valor_desconto=self.valor_desconto,
            ).base_icms_proprio
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_credito_sn(self) -> Decimal:
        return _round2(self.base_icms_proprio * _pct(self.percentual_credito_sn))

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == ZERO:
            return _BaseIcmsST(
                base_icms_proprio=self.base_icms_proprio,
                mva=self.mva,
            ).base_icms_st
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)


class Icms202_203(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_reducao: Decimal = ZERO
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        if self.percentual_reducao == ZERO:
            return _BaseIcmsProprio(
                valor_produto=self.valor_produto,
                valor_frete=self.valor_frete,
                valor_seguro=self.valor_seguro,
                despesas_acessorias=self.despesas_acessorias,
                valor_desconto=self.valor_desconto,
            ).base_icms_proprio
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        if self.percentual_reducao_st == ZERO:
            return _BaseIcmsST(
                base_icms_proprio=self.base_icms_proprio,
                mva=self.mva,
            ).base_icms_st
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)


class Icms900(BaseModel):
    model_config = {"extra": "forbid"}
    valor_produto: Decimal
    valor_frete: Decimal
    valor_seguro: Decimal
    despesas_acessorias: Decimal
    valor_desconto: Decimal
    aliquota_icms_proprio: Decimal
    aliquota_icms_st: Decimal
    mva: Decimal
    percentual_credito_sn: Decimal = ZERO
    valor_ipi: Decimal = ZERO
    percentual_reducao: Decimal = ZERO
    percentual_reducao_st: Decimal = ZERO

    @computed_field
    @property
    def base_icms_proprio(self) -> Decimal:
        return _BaseIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            valor_ipi=self.valor_ipi,
        ).base_icms_proprio

    @computed_field
    @property
    def base_reduzida_icms_proprio(self) -> Decimal:
        return _BaseReduzidaIcmsProprio(
            valor_produto=self.valor_produto,
            valor_frete=self.valor_frete,
            valor_seguro=self.valor_seguro,
            despesas_acessorias=self.despesas_acessorias,
            valor_desconto=self.valor_desconto,
            percentual_reducao=self.percentual_reducao,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_proprio

    @computed_field
    @property
    def valor_icms_proprio(self) -> Decimal:
        return _valor_icms_proprio(self.base_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_icms_proprio_base_reduzida(self) -> Decimal:
        return _valor_icms_proprio(self.base_reduzida_icms_proprio, self.aliquota_icms_proprio)

    @computed_field
    @property
    def valor_credito_sn(self) -> Decimal:
        if self.percentual_reducao == ZERO:
            return _round2(self.base_icms_proprio * _pct(self.percentual_credito_sn))
        return _round2(self.base_reduzida_icms_proprio * _pct(self.percentual_credito_sn))

    @computed_field
    @property
    def base_icms_st(self) -> Decimal:
        return _BaseIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            valor_ipi=self.valor_ipi,
        ).base_icms_st

    @computed_field
    @property
    def base_reduzida_icms_st(self) -> Decimal:
        return _BaseReduzidaIcmsST(
            base_icms_proprio=self.base_icms_proprio,
            mva=self.mva,
            percentual_reducao_st=self.percentual_reducao_st,
            valor_ipi=self.valor_ipi,
        ).base_reduzida_icms_st

    @computed_field
    @property
    def valor_icms_st(self) -> Decimal:
        return _valor_icms_st(self.base_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)

    @computed_field
    @property
    def valor_icms_st_base_reduzida(self) -> Decimal:
        return _valor_icms_st(self.base_reduzida_icms_st, self.aliquota_icms_st, self.valor_icms_proprio)


# =============================================================================
# Schemas de entrada (payload) — com Decimalable para aceitar str | float | Decimal
# =============================================================================


class ValuesSchema(BaseModel):
    model_config = {"extra": "forbid"}
    quantity: Decimalable = ZERO
    unit_price: Decimalable = ZERO
    gross_value: Decimalable | None = None
    discount_value: Decimalable = ZERO
    freight_value: Decimalable = ZERO
    insurance_value: Decimalable = ZERO
    other_expenses: Decimalable = ZERO


class IcmsSchema(BaseModel):
    model_config = {"extra": "forbid"}
    cst: str = "00"
    aliquota_icms_proprio: Decimalable = ZERO
    aliquota_icms_st: Decimalable = ZERO
    mva: Decimalable = ZERO
    percentual_reducao: Decimalable = ZERO
    percentual_reducao_st: Decimalable = ZERO
    percentual_credito_sn: Decimalable = ZERO
    percentual_diferimento: Decimalable = ZERO
    include_ipi_in_base: bool = True


class FcpSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_fcp: Decimalable = ZERO
    aliquota_fcp_st: Decimalable = ZERO
    aliquota_diferimento_fcp: Decimalable = ZERO
    use_st_base: bool = False


class FcpStSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_fcp_st: Decimalable = ZERO


class IpiSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_ipi: Decimalable = ZERO
    aliquota_por_unidade: Decimalable = ZERO
    mode: str = ""
    base_calculo: Decimalable = ZERO


class PisSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_pis: Decimalable = ZERO
    aliquota_por_unidade: Decimalable = ZERO
    mode: str = ""
    base_calculo: Decimalable = ZERO


class CofinsSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_cofins: Decimalable = ZERO
    aliquota_por_unidade: Decimalable = ZERO
    mode: str = ""
    base_calculo: Decimalable = ZERO


class IbsSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_efetiva_percentual: Decimalable = ZERO
    percentual_diferimento: Decimalable = ZERO


class CbsSchema(BaseModel):
    model_config = {"extra": "forbid"}
    aliquota_efetiva_percentual: Decimalable = ZERO
    percentual_diferimento: Decimalable = ZERO


class TaxesSchema(BaseModel):
    model_config = {"extra": "forbid"}
    icms: IcmsSchema | None = None
    ipi: IpiSchema | None = None
    pis: PisSchema | None = None
    cofins: CofinsSchema | None = None
    fcp: FcpSchema | None = None
    fcp_st: FcpStSchema | None = None
    ibs: IbsSchema | None = None
    cbs: CbsSchema | None = None
    enabled: list[str] | None = None


class PayloadSchema(BaseModel):
    model_config = {"extra": "forbid"}
    values: ValuesSchema = Field(default_factory=ValuesSchema)
    taxes: TaxesSchema = Field(default_factory=TaxesSchema)