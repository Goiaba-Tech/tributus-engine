from decimal import Decimal
from tributus_engine.models import (
    Icms00,
    Icms10,
    Icms20,
    Icms30,
    Icms51,
    Icms70,
    Icms101,
    Icms201,
    Icms202_203,
)


def test_icms00():
    icms00 = Icms00(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('15.00'),
        aliquota_icms_proprio=Decimal('18.00'),
    )

    assert icms00.base_icms_proprio == Decimal('148.50')
    assert icms00.valor_icms_proprio == Decimal('26.73')


def test_icms10():
    icms10 = Icms10(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('4.74'),
        valor_seguro=Decimal('1.89'),
        despesas_acessorias=Decimal('0.95'),
        valor_desconto=Decimal('2.370'),
        valor_ipi=Decimal('15.00'),
        aliquota_icms_proprio=Decimal('12.00'),
        aliquota_icms_st=Decimal('18.00'),
        mva=Decimal('40.65'),
        percentual_reducao_st=Decimal('10'),
    )

    assert icms10.base_icms_proprio == Decimal('140.21')
    assert icms10.valor_icms_proprio == Decimal('16.83')
    assert icms10.base_icms_st == Decimal('192.48')
    assert icms10.valor_icms_st == Decimal('17.82')


def test_icms20():
    icms20 = Icms20(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('0'),
        aliquota_icms_proprio=Decimal('18.00'),
        percentual_reducao=Decimal('10.00'),
    )

    assert icms20.base_reduzida_icms_proprio == Decimal('120.15')
    assert icms20.valor_icms_proprio == Decimal('21.63')
    assert icms20.valor_icms_desonerado == Decimal('2.40')


def test_icms30():
    icms30 = Icms30(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('15.00'),
        aliq_icms_proprio=Decimal('12.00'),
        aliq_icms_st=Decimal('18.00'),
        mva=Decimal('40.65'),
        percentual_reducao_st=Decimal('10'),
    )

    assert icms30.base_icms_st == Decimal('183.99')
    assert icms30.valor_icms_st == Decimal('17.10')
    assert icms30.valor_icms_desonerado == Decimal('16.02')


def test_icms51():
    icms51 = Icms51(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('3.00'),
        despesas_acessorias=Decimal('1.50'),
        valor_desconto=Decimal('13.50'),
        valor_ipi=Decimal('15'),
        aliq_icms_proprio=Decimal('18.00'),
        percentual_reducao=Decimal('10.00'),
        percentual_diferimento=Decimal('10.00'),
    )

    assert icms51.base_icms_proprio == Decimal('135.15')
    assert icms51.valor_icms_operacao == Decimal('24.33')
    assert icms51.valor_icms_diferido == Decimal('2.43')
    assert icms51.valor_icms_proprio == Decimal('21.90')


def test_icms70():
    icms70 = Icms70(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('0.75'),
        despesas_acessorias=Decimal('2.25'),
        valor_desconto=Decimal('15.00'),
        valor_ipi=Decimal('15.00'),
        aliquota_icms_proprio=Decimal('12.00'),
        aliquota_icms_st=Decimal('18.00'),
        mva=Decimal('40.65'),
        percentual_reducao=Decimal('10.00'),
        percentual_reducao_st=Decimal('10.00'),
    )

    assert icms70.base_icms_proprio == Decimal('117.45')
    assert icms70.valor_icms_proprio == Decimal('14.09')
    assert icms70.valor_icms_proprio_desonerado == Decimal('1.57')
    assert icms70.base_icms_st == Decimal('163.67')
    assert icms70.valor_icms_st == Decimal('15.37')
    assert icms70.valor_icms_st_desonerado == Decimal('5.81')


def test_icms101():
    icms101 = Icms101(
        valor_produto=Decimal('135.00'),
        valor_frete=Decimal('7.50'),
        valor_seguro=Decimal('0.75'),
        despesas_acessorias=Decimal('2.25'),
        valor_desconto=Decimal('15.00'),
        percentual_credito_sn=Decimal('1.25'),
    )

    assert icms101.base_icms_proprio == Decimal('130.50')
    assert icms101.valor_credito_sn == Decimal('1.63')


def test_icms201():
    icms201 = Icms201(
        valor_produto=Decimal('180.00'),
        valor_frete=Decimal('4.96'),
        valor_seguro=Decimal('0.50'),
        despesas_acessorias=Decimal('1.49'),
        valor_desconto=Decimal('9.92'),
        aliquota_icms_proprio=Decimal('18.00'),
        aliquota_icms_st=Decimal('18.00'),
        mva=Decimal('38.00'),
        percentual_credito_sn=Decimal('1.25'),
        percentual_reducao=Decimal('0'),
        percentual_reducao_st=Decimal('0'),
    )

    assert icms201.base_icms_proprio == Decimal('177.03')
    assert icms201.valor_icms_proprio == Decimal('31.87')
    assert icms201.valor_credito_sn == Decimal('2.21')
    assert icms201.base_icms_st == Decimal('244.30')
    assert icms201.valor_icms_st == Decimal('12.10')


def test_icms202_203():
    icms202_203 = Icms202_203(
        valor_produto=Decimal('180.00'),
        valor_frete=Decimal('4.96'),
        valor_seguro=Decimal('0.50'),
        despesas_acessorias=Decimal('1.49'),
        valor_desconto=Decimal('9.92'),
        aliquota_icms_proprio=Decimal('18.00'),
        aliquota_icms_st=Decimal('18.00'),
        mva=Decimal('38.00'),
        percentual_reducao=Decimal('0'),
        percentual_reducao_st=Decimal('0'),
    )

    assert icms202_203.base_icms_proprio == Decimal('177.03')
    assert icms202_203.valor_icms_proprio == Decimal('31.87')
    assert icms202_203.base_icms_st == Decimal('244.30')
    assert icms202_203.valor_icms_st == Decimal('12.10')