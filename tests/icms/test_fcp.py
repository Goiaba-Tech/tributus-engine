from decimal import Decimal
from tributus_engine.implementations.icms.fcp import (
    Fcp,
    FcpDiferido,
    FcpEfetivo,
    FcpST,
)

def test_fcp():
    base_fcp = Decimal('135.00')
    aliquota_fcp = Decimal('2.00')

    fcp = Fcp(base_fcp, aliquota_fcp)

    v_fcp = fcp.valor_fcp()

    assert v_fcp == Decimal('2.70')

def test_fcp_diferido():
    valor_fcp = Decimal('5.00')
    aliquota_diferimento_fcp = Decimal('10.00')

    fcp_dif = FcpDiferido(valor_fcp, aliquota_diferimento_fcp)

    v_fcp_dif = fcp_dif.valor_fcp_diferido()

    assert v_fcp_dif == Decimal('0.50')

def test_fcp_efetivo():
    valor_fcp = Decimal('5.00')
    valor_fcp_diferido = Decimal('0.50')

    fcp_efet = FcpEfetivo(valor_fcp, valor_fcp_diferido)

    v_fcp_efet = fcp_efet.valor_fcp_efetivo()

    assert v_fcp_efet == Decimal('4.50')

def test_fcp_st():
    base_fcp_st = Decimal('135.00')
    aliquota_fcp_st = Decimal('2.00')

    fcp_st = FcpST(base_fcp_st, aliquota_fcp_st)

    v_fcp_st = fcp_st.valor_fcp_st()

    assert v_fcp_st == Decimal('2.70')
