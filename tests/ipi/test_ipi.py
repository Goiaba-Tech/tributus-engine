from decimal import Decimal

from tributus_engine.models import IpiAdValorem, IpiEspecifico


def test_ipi_ad_valorem():
    valor_produto = Decimal('1080.00')
    valor_frete = Decimal('0.00')
    valor_seguro = Decimal('0.00')
    despesas_acessorias = Decimal('0.00')
    aliquota_ipi = Decimal('10.00')

    ipi = IpiAdValorem(
        valor_produto=valor_produto,
        valor_frete=valor_frete,
        valor_seguro=valor_seguro,
        despesas_acessorias=despesas_acessorias,
        aliquota_ipi=aliquota_ipi,
    )

    assert ipi.base_ipi == Decimal('1080.00')
    assert ipi.valor_ipi == Decimal('108.00')


def test_ipi_especifico():
    base_calculo = Decimal('15.00')
    aliquota_por_unidade = Decimal('0.764')

    ipi = IpiEspecifico(
        base_calculo=base_calculo,
        aliquota_por_unidade=aliquota_por_unidade,
    )

    assert ipi.valor_ipi == Decimal('11.46')