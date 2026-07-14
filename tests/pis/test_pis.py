from decimal import Decimal
from tributus_engine.implementations.pis import (
    BasePIS,
    Pis01_02,
    Pis03,
)

def test_base_pis():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')

    base_pis = BasePIS(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto
    )

    v_bc = base_pis.calcular_base_pis()
    assert v_bc == Decimal('177.03')

def test_pis01_02():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_pis = Decimal('0.65')

    pis01_02 = Pis01_02(
        valor_produto, valor_frete, valor_seguro,
        despesas_acessorias, valor_desconto, aliquota_pis
    )

    v_bc = pis01_02.base_pis()
    v_pis = pis01_02.valor_pis()

    assert v_bc == Decimal('177.03')
    assert v_pis == Decimal('1.15')

def test_pis03():
    quantidade_tributada = Decimal('15.00')
    aliquota_unidade = Decimal('0.764')

    pis03 = Pis03(quantidade_tributada, aliquota_unidade)

    v_pis = pis03.valor_pis()

    assert v_pis == Decimal('11.46')
