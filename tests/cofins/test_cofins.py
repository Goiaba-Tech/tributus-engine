from decimal import Decimal
from tributus_engine.models import Cofins01_02, Cofins03


def test_cofins01_02():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_cofins = Decimal('3.00')

    cofins01_02 = Cofins01_02(
        valor_produto=valor_produto,
        valor_frete=valor_frete,
        valor_seguro=valor_seguro,
        despesas_acessorias=despesas_acessorias,
        valor_desconto=valor_desconto,
        aliquota_cofins=aliquota_cofins,
    )

    assert cofins01_02.base_cofins == Decimal('177.03')
    assert cofins01_02.valor_cofins == Decimal('5.31')


def test_cofins01_02_com_icms():
    """Testa COFINS com exclusão do ICMS da base."""
    cofins = Cofins01_02(
        valor_produto=Decimal('180.00'),
        valor_frete=Decimal('4.96'),
        valor_seguro=Decimal('0.50'),
        despesas_acessorias=Decimal('1.49'),
        valor_desconto=Decimal('9.92'),
        aliquota_cofins=Decimal('3.00'),
        valor_icms=Decimal('20.00'),
    )
    assert cofins.base_cofins == Decimal('157.03')
    assert cofins.valor_cofins == Decimal('4.71')


def test_cofins03():
    quantidade_tributada = Decimal('15.00')
    aliquota_unidade = Decimal('0.764')

    cofins03 = Cofins03(
        base_calculo=quantidade_tributada,
        aliquota_por_unidade=aliquota_unidade,
    )

    assert cofins03.valor_cofins == Decimal('11.46')