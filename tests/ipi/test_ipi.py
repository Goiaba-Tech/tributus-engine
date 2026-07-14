from decimal import Decimal
from tributus_engine.implementations.ipi import (
    BaseIPI,
    Ipi50AdValorem,
    Ipi50Especifico,
)

def test_base_ipi():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')

    base_ipi = BaseIPI(valor_produto, valor_frete, valor_seguro, despesas_acessorias)

    v_bc = base_ipi.calcular_base_ipi()

    assert v_bc == Decimal('186.95')

def test_ipi50_ad_valorem():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    aliquota_ipi = Decimal('10.00')

    ipi50_av = Ipi50AdValorem(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, aliquota_ipi
    )

    v_bc = ipi50_av.calcular_base_ipi()
    v_ipi = ipi50_av.valor_ipi()

    assert v_bc == Decimal('186.95')
    assert v_ipi == Decimal('18.70')

def test_ipi_especifico():
    quantidade_tributada = Decimal('15.00')
    aliquota_unidade = Decimal('0.764')

    ipi_especifico = Ipi50Especifico(quantidade_tributada, aliquota_unidade)

    v_ipi = ipi_especifico.valor_ipi()

    assert v_ipi == Decimal('11.46')
