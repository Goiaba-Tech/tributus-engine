from decimal import Decimal
from tributus_engine.models import Fcp, FcpDiferido, FcpEfetivo, FcpST


def test_fcp():
    base_fcp = Decimal('135.00')
    aliquota_fcp = Decimal('2.00')

    fcp = Fcp(base_calculo=base_fcp, aliquota_fcp=aliquota_fcp)

    assert fcp.valor_fcp == Decimal('2.70')


def test_fcp_diferido():
    valor_fcp = Decimal('5.00')
    aliquota_diferimento_fcp = Decimal('10.00')

    fcp_dif = FcpDiferido(valor_fcp=valor_fcp, aliquota_diferimento_fcp=aliquota_diferimento_fcp)

    assert fcp_dif.valor_fcp_diferido == Decimal('0.50')


def test_fcp_efetivo():
    valor_fcp = Decimal('5.00')
    valor_fcp_diferido = Decimal('0.50')

    fcp_efet = FcpEfetivo(valor_fcp=valor_fcp, valor_fcp_diferido=valor_fcp_diferido)

    assert fcp_efet.valor_fcp_efetivo == Decimal('4.50')


def test_fcp_st():
    base_fcp_st = Decimal('135.00')
    aliquota_fcp_st = Decimal('2.00')

    fcp_st = FcpST(base_calculo_st=base_fcp_st, aliquota_fcp_st=aliquota_fcp_st)

    assert fcp_st.valor_fcp_st == Decimal('2.70')