from decimal import Decimal

from tributus_engine.implementations.ibs_cbs import BaseIbsCbs, Cbs, IbsUf


def test_base_ibs_cbs():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')

    base_ibs_cbs = BaseIbsCbs(
        valor_produto,
        valor_frete,
        valor_seguro,
        despesas_acessorias,
    )

    v_bc = base_ibs_cbs.calcular_base_ibs_cbs()

    assert v_bc == Decimal('186.95')


def test_cbs():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    aliquota_efetiva = Decimal('8.80')
    percentual_diferimento = Decimal('12.00')

    cbs = Cbs(
        valor_produto,
        valor_frete,
        valor_seguro,
        despesas_acessorias,
        aliquota_efetiva,
        percentual_diferimento,
    )

    v_bc = cbs.valor_base_ibs_cbs()
    v_diferimento = cbs.diferimento()
    v_cbs = cbs.valor_cbs()

    assert v_bc == Decimal('186.95')
    assert v_diferimento == Decimal('1.97')
    assert v_cbs == Decimal('14.48')


def test_ibs_uf():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    aliquota_efetiva = Decimal('17.50')
    percentual_diferimento = Decimal('20.00')

    ibs_uf = IbsUf(
        valor_produto,
        valor_frete,
        valor_seguro,
        despesas_acessorias,
        aliquota_efetiva,
        percentual_diferimento,
    )

    v_bc = ibs_uf.valor_base_ibs_cbs()
    v_diferimento = ibs_uf.diferimento()
    v_ibs_uf = ibs_uf.valor_ibs_uf()

    assert v_bc == Decimal('186.95')
    assert v_diferimento == Decimal('6.54')
    assert v_ibs_uf == Decimal('26.18')
