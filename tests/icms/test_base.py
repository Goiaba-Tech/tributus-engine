from decimal import Decimal
from tributus_engine.implementations.icms.base import (
    BaseIcmsProprio,
    BaseIcmsST,
    BaseReduzidaIcmsProprio,
    BaseReduzidaIcmsST,
)

def test_base_icms_proprio():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('15.00')

    base_icms_proprio = BaseIcmsProprio(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto, valor_ipi
    )

    v_bc = base_icms_proprio.calcular_base_icms_proprio()
    assert v_bc == Decimal('148.50')

def test_base_icms_st():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('0')
    mva = Decimal('40.65')

    base_icms_proprio = BaseIcmsProprio(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto
    )

    v_bc = base_icms_proprio.calcular_base_icms_proprio()

    base_icms_st = BaseIcmsST(v_bc, mva, valor_ipi)

    v_bc_st = base_icms_st.calcular_base_icms_st()

    assert v_bc == Decimal('133.50')
    assert v_bc_st == Decimal('187.77')

def test_base_reduzida_icms_proprio():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('0')
    percentual_reducao = Decimal('10.00')

    base_reduzida_icms_proprio = BaseReduzidaIcmsProprio(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto, percentual_reducao, valor_ipi
    )

    v_bc = base_reduzida_icms_proprio.calcular_base_reduzida_icms_proprio()
    assert v_bc == Decimal('120.15')

def test_base_reduzida_icms_st():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('0.75')
    despesas_acessorias = Decimal('2.25')
    valor_desconto = Decimal('15.00')
    valor_ipi = Decimal('0')
    mva = Decimal('40.65')
    percentual_reducao_st = Decimal('10.00')

    base_icms_proprio = BaseIcmsProprio(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto
    )

    v_bc = base_icms_proprio.calcular_base_icms_proprio()

    base_icms_st = BaseReduzidaIcmsST(v_bc, mva, percentual_reducao_st, valor_ipi)

    v_bc_st = base_icms_st.calcular_base_reduzida_icms_st()

    assert v_bc == Decimal('130.50')
    assert v_bc_st == Decimal('165.19')
