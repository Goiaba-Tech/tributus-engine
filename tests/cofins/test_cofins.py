from decimal import Decimal
from tributus_engine.implementations.cofins import (
    BaseCofins,
    Cofins01_02,
    Cofins03,
)

def test_base_cofins():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')

    base_cofins = BaseCofins(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto
    )

    v_bc = base_cofins.calcular_base_cofins()
    assert v_bc == Decimal('177.03')

def test_cofins01_02():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_cofins = Decimal('3.00')

    cofins01_02 = Cofins01_02(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto, aliquota_cofins
    )

    v_bc = cofins01_02.base_cofins()
    v_cofins = cofins01_02.valor_cofins()

    assert v_bc == Decimal('177.03')
    assert v_cofins == Decimal('5.31')

def test_cofins03():
    quantidade_tributada = Decimal('15.00')
    aliquota_unidade = Decimal('0.764')

    cofins03 = Cofins03(quantidade_tributada, aliquota_unidade)

    v_cofins = cofins03.valor_cofins()

    assert v_cofins == Decimal('11.46')
