from decimal import Decimal

from tributus_engine.models import Cbs, Ibs


def test_cbs():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    aliquota_efetiva_percentual = Decimal('8.80')
    percentual_diferimento = Decimal('12.00')

    cbs = Cbs(
        valor_produto=valor_produto,
        valor_frete=valor_frete,
        valor_seguro=valor_seguro,
        despesas_acessorias=despesas_acessorias,
        aliquota_efetiva_percentual=aliquota_efetiva_percentual,
        percentual_diferimento=percentual_diferimento,
    )

    assert cbs.base_ibs_cbs == Decimal('186.95')
    assert cbs.diferimento == Decimal('1.97')
    assert cbs.valor_cbs == Decimal('14.48')


def test_ibs():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    aliquota_efetiva_percentual = Decimal('17.50')
    percentual_diferimento = Decimal('20.00')

    ibs = Ibs(
        valor_produto=valor_produto,
        valor_frete=valor_frete,
        valor_seguro=valor_seguro,
        despesas_acessorias=despesas_acessorias,
        aliquota_efetiva_percentual=aliquota_efetiva_percentual,
        percentual_diferimento=percentual_diferimento,
    )

    assert ibs.base_ibs_cbs == Decimal('186.95')
    assert ibs.diferimento == Decimal('6.54')
    assert ibs.valor_ibs == Decimal('26.18')