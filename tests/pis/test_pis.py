from decimal import Decimal

from tributus_engine.models import Pis01_02, Pis03


def test_pis01_02():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_pis = Decimal('0.65')

    pis01_02 = Pis01_02(
        valor_produto=valor_produto,
        valor_frete=valor_frete,
        valor_seguro=valor_seguro,
        despesas_acessorias=despesas_acessorias,
        valor_desconto=valor_desconto,
        aliquota_pis=aliquota_pis,
    )

    assert pis01_02.base_pis == Decimal('177.03')
    assert pis01_02.valor_pis == Decimal('1.15')


def test_pis03():
    base_calculo = Decimal('15.00')
    aliquota_por_unidade = Decimal('0.764')

    pis03 = Pis03(
        base_calculo=base_calculo,
        aliquota_por_unidade=aliquota_por_unidade,
    )

    assert pis03.valor_pis == Decimal('11.46')