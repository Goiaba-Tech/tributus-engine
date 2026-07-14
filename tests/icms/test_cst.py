from decimal import Decimal
from tributus_engine.implementations.icms.cst import (
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
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('15.00')
    aliquota_icms_proprio = Decimal('18.00')

    icms00 = Icms00(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio
    )

    v_bc = icms00.base_icms_proprio()
    v_icms = icms00.valor_icms_proprio()

    assert v_bc == Decimal('148.50')
    assert v_icms == Decimal('26.73')

def test_icms10():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('4.74')
    valor_seguro = Decimal('1.89')
    despesas_acessorias = Decimal('0.95')
    valor_desconto = Decimal('2.370')
    valor_ipi = Decimal('15.00')
    aliquota_icms_proprio = Decimal('12.00')
    aliquota_icms_st = Decimal('18.00')
    mva = Decimal('40.65')
    percentual_reducao_st = Decimal('10')

    icms10 = Icms10(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio, aliquota_icms_st,
        mva, percentual_reducao_st
    )

    v_bc = icms10.base_icms_proprio()
    v_icms = icms10.valor_icms_proprio()
    v_bc_st = icms10.base_icms_st()
    v_icms_st = icms10.valor_icms_st()
    # v_icms_st_deson = icms10.valor_icms_st_desonerado() # Not tested in C# test provided, but method exists

    assert v_bc == Decimal('140.21')
    assert v_icms == Decimal('16.83')
    assert v_bc_st == Decimal('192.48')
    assert v_icms_st == Decimal('17.82')

def test_icms20():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('0')
    aliquota_icms_proprio = Decimal('18.00')
    percentual_reducao = Decimal('10.00')

    icms20 = Icms20(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio, percentual_reducao
    )

    v_bc = icms20.base_reduzida_icms_proprio()
    v_icms = icms20.valor_icms_proprio()
    v_icms_deson = icms20.valor_icms_desonerado()

    assert v_bc == Decimal('120.15')
    assert v_icms == Decimal('21.63')
    assert v_icms_deson == Decimal('2.40')

def test_icms30():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('15.00')
    aliquota_icms_proprio = Decimal('12.00')
    aliquota_icms_st = Decimal('18.00')
    mva = Decimal('40.65')
    percentual_reducao_st = Decimal('10')

    icms30 = Icms30(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio, aliquota_icms_st,
        mva, percentual_reducao_st
    )

    v_bc_st = icms30.base_icms_st()
    v_icms_st = icms30.valor_icms_st()
    v_icms_deson = icms30.valor_icms_desonerado()

    assert v_bc_st == Decimal('183.99')
    assert v_icms_st == Decimal('17.10')
    assert v_icms_deson == Decimal('16.02')

def test_icms51():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('3.00')
    despesas_acessorias = Decimal('1.50')
    valor_desconto = Decimal('13.50')
    valor_ipi = Decimal('15')
    aliquota_icms_proprio = Decimal('18.00')
    percentual_reducao = Decimal('10.00')
    percentual_diferimento = Decimal('10.00')

    icms51 = Icms51(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio, percentual_reducao,
        percentual_diferimento
    )

    v_bc = icms51.base_icms_proprio()
    v_icms_op = icms51.valor_icms_operacao()
    v_icms_dif = icms51.valor_icms_diferido()
    v_icms = icms51.valor_icms_proprio()

    assert v_bc == Decimal('135.15')
    assert v_icms_op == Decimal('24.33')
    assert v_icms_dif == Decimal('2.43')
    assert v_icms == Decimal('21.90')

def test_icms70():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('0.75')
    despesas_acessorias = Decimal('2.25')
    valor_desconto = Decimal('15.00')
    valor_ipi = Decimal('15.00')
    aliquota_icms_proprio = Decimal('12.00')
    aliquota_icms_st = Decimal('18.00')
    mva = Decimal('40.65')
    percentual_reducao = Decimal('10.00')
    percentual_reducao_st = Decimal('10.00')

    icms70 = Icms70(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_ipi, valor_desconto, aliquota_icms_proprio, aliquota_icms_st,
        mva, percentual_reducao, percentual_reducao_st
    )

    v_bc = icms70.base_icms_proprio()
    v_icms = icms70.valor_icms_proprio()
    v_icms_deson = icms70.valor_icms_proprio_desonerado()
    v_bc_st = icms70.base_icms_st()
    v_icms_st = icms70.valor_icms_st()
    v_icms_st_deson = icms70.valor_icms_st_desonerado()

    assert v_bc == Decimal('117.45')
    assert v_icms == Decimal('14.09')
    assert v_icms_deson == Decimal('1.57')
    assert v_bc_st == Decimal('163.67')
    assert v_icms_st == Decimal('15.37')
    assert v_icms_st_deson == Decimal('5.81')

def test_icms101():
    valor_produto = Decimal('135.00')
    valor_frete = Decimal('7.50')
    valor_seguro = Decimal('0.75')
    despesas_acessorias = Decimal('2.25')
    valor_desconto = Decimal('15.00')
    percentual_credito_sn = Decimal('1.25')

    icms101 = Icms101(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_desconto, percentual_credito_sn
    )

    v_bc = icms101.calcular_base_icms_proprio()
    v_cred_sn = icms101.valor_credito_sn()

    assert v_bc == Decimal('130.50')
    assert v_cred_sn == Decimal('1.63')

def test_icms201():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_icms_proprio = Decimal('18.00')
    aliquota_icms_st = Decimal('18.00')
    mva = Decimal('38.00')
    percentual_credito_sn = Decimal('1.25')
    percentual_reducao = Decimal('0')
    percentual_reducao_st = Decimal('0')

    icms201 = Icms201(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_desconto, aliquota_icms_proprio, aliquota_icms_st, mva,
        percentual_credito_sn, percentual_reducao, percentual_reducao_st
    )

    v_bc = icms201.calcular_base_icms_proprio()
    v_icms = icms201.valor_icms_proprio()
    v_cred_sn = icms201.valor_credito_sn()
    v_bc_st = icms201.base_icms_st()
    v_icms_st = icms201.valor_icms_st()

    assert v_bc == Decimal('177.03')
    assert v_icms == Decimal('31.87')
    assert v_cred_sn == Decimal('2.21')
    assert v_bc_st == Decimal('244.30')
    assert v_icms_st == Decimal('12.10')

def test_icms202_203():
    valor_produto = Decimal('180.00')
    valor_frete = Decimal('4.96')
    valor_seguro = Decimal('0.50')
    despesas_acessorias = Decimal('1.49')
    valor_desconto = Decimal('9.92')
    aliquota_icms_proprio = Decimal('18.00')
    aliquota_icms_st = Decimal('18.00')
    mva = Decimal('38.00')
    percentual_reducao = Decimal('0')
    percentual_reducao_st = Decimal('0')

    icms202_203 = Icms202_203(
        valor_produto, valor_frete, valor_seguro, despesas_acessorias,
        valor_desconto, aliquota_icms_proprio, aliquota_icms_st, mva,
        percentual_reducao, percentual_reducao_st
    )

    v_bc = icms202_203.calcular_base_icms_proprio()
    v_icms = icms202_203.valor_icms_proprio()
    v_bc_st = icms202_203.base_icms_st()
    v_icms_st = icms202_203.valor_icms_st()

    assert v_bc == Decimal('177.03')
    assert v_icms == Decimal('31.87')
    assert v_bc_st == Decimal('244.30')
    assert v_icms_st == Decimal('12.10')
