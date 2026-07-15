from decimal import Decimal

from tributus_engine.models import Icms00, Icms10, Icms20


def test_base_icms_proprio():
    """Testa base de ICMS próprio via Icms00."""
    icms00 = Icms00(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('15.00'),
        aliquota_icms_proprio=Decimal('0'),  # zero para isolar o teste de base
    )

    assert icms00.base_icms_proprio == Decimal('148.50')


def test_base_icms_st():
    """Testa base de ICMS ST via Icms10."""
    icms10 = Icms10(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('0'),
        aliquota_icms_proprio=Decimal('0'),
        aliquota_icms_st=Decimal('0'),
        mva=Decimal('40.65'),
    )

    assert icms10.base_icms_proprio == Decimal('133.50')
    assert icms10.base_icms_st == Decimal('187.77')


def test_base_reduzida_icms_proprio():
    """Testa base reduzida de ICMS próprio via Icms20."""
    icms20 = Icms20(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('0'),
        aliquota_icms_proprio=Decimal('0'),
        percentual_reducao=Decimal('10.00'),
    )

    assert icms20.base_reduzida_icms_proprio == Decimal('120.15')


def test_base_reduzida_icms_st():
    """Testa base reduzida de ICMS ST via Icms10 com redução ST."""
    icms10 = Icms10(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('0.75'),
        despesas_acessorias=Decimal('2.25'),
        valor_desconto=Decimal('15.00'),
        valor_ipi=Decimal('0'),
        aliquota_icms_proprio=Decimal('0'),
        aliquota_icms_st=Decimal('0'),
        mva=Decimal('40.65'),
        percentual_reducao_st=Decimal('10.00'),
    )

    assert icms10.base_icms_proprio == Decimal('130.50')
    assert icms10.base_icms_st == Decimal('165.19')