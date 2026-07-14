from decimal import Decimal

import pytest

from tributus_engine.engine import (
    BaseCalculator,
    TaxContext,
    TaxDependencyGraph,
    TaxEngine,
    ValueContext,
)


def _context_same_state() -> TaxContext:
    return TaxContext(
        values=ValueContext(
            quantity=Decimal('10'),
            unit_price=Decimal('100.00'),
            gross_value=Decimal('1000.00'),
            discount_value=Decimal('100.00'),
            freight_value=Decimal('50.00'),
            insurance_value=Decimal('10.00'),
            other_expenses=Decimal('20.00'),
        ),
        taxes={'rates': {'icms': Decimal('18.00')}},
    )


def test_base_calculator_formula():
    context = _context_same_state()
    base_calc = BaseCalculator.from_context(context)

    assert base_calc.base_padrao() == Decimal('980.00')


def test_dependency_graph_cycle_detection():
    graph = TaxDependencyGraph()
    graph.add_dependency('a', 'b')
    graph.add_dependency('b', 'a')

    with pytest.raises(ValueError):
        graph.resolve_order({'a', 'b'})


def test_tax_engine_calculate_from_dict_payload():
    engine = TaxEngine()

    payload = {
        'operation': {
            'issuer_state': 'SP',
            'recipient_state': 'RJ',
            'operation_date': '2026-06-02',
        },
        'customer': {
            'state': 'RJ',
        },
        'values': {
            'quantity': '10',
            'unit_price': '100.00',
            'gross_value': '1000.00',
            'discount_value': '100.00',
            'freight_value': '50.00',
            'insurance_value': '10.00',
            'other_expenses': '20.00',
        },
        'taxes': {
            'enabled': ['ipi', 'icms', 'fcp', 'pis', 'cofins', 'ibs', 'cbs'],
            'rates': {
                'fcp': '2.00',
                'ibs': '16.00',
                'cbs': '8.50',
            },
            'ipi': {
                'aliquota_ipi': '10.00',
            },
            'icms': {
                'cst': '00',
                'aliquota_icms_proprio': '18.00',
            },
            'pis': {
                'aliquota_pis': '1.65',
            },
            'cofins': {
                'aliquota_cofins': '7.60',
            },
            'ibs': {
                'aliquota_efetiva_percentual': '16.00',
            },
            'cbs': {
                'aliquota_efetiva_percentual': '8.50',
            },
        },
    }

    result = engine.calculate_from_dict(payload)

    assert result.calculation_order == ['ipi', 'icms', 'fcp', 'pis', 'cofins', 'ibs', 'cbs']
    assert result.amounts['ipi'] == Decimal('108.00')
    assert result.amounts['icms'] == Decimal('195.84')
    assert result.amounts['fcp'] == Decimal('21.76')
    assert result.amounts['pis'] == Decimal('12.94')
    assert result.amounts['cofins'] == Decimal('59.60')
    assert result.amounts['ibs'] == Decimal('172.80')
    assert result.amounts['cbs'] == Decimal('91.80')
    assert result.total == Decimal('662.74')


def test_tax_engine_list_taxes_for_sale_all_states_from_dict():
    engine = TaxEngine()

    taxes_by_state = engine.list_taxes_for_sale_all_states_from_dict({
        'product': {'ncm': '22030000', 'cest': '0300100'},
        'taxes': {
            'rates': {
                'icms': '17.00',
                'pis': '1.20',
                'cofins': '5.40',
            }
        },
    })

    assert taxes_by_state['SP'] == {'icms': '17.00', 'pis': '1.20', 'cofins': '5.40'}
    assert 'RJ' in taxes_by_state


def test_tax_engine_calculate_icms_st_and_fcp_st_from_dict_payload():
    engine = TaxEngine()

    payload = {
        'operation': {
            'issuer_state': 'SP',
            'recipient_state': 'RJ',
            'operation_date': '2026-06-02',
        },
        'customer': {
            'state': 'RJ',
        },
        'values': {
            'quantity': '1',
            'unit_price': '135.00',
            'gross_value': '135.00',
            'discount_value': '2.37',
            'freight_value': '4.74',
            'insurance_value': '1.89',
            'other_expenses': '0.95',
        },
        'taxes': {
            'enabled': ['icms', 'fcp', 'fcp_st'],
            'icms': {
                'cst': '10',
                'aliquota_icms_proprio': '12.00',
                'aliquota_icms_st': '18.00',
                'mva': '40.65',
                'percentual_reducao_st': '10.00',
                'include_ipi_in_base': False,
            },
            'fcp': {
                'aliquota_fcp_st': '2.00',
            },
        },
    }

    result = engine.calculate_from_dict(payload)

    assert result.calculation_order == ['icms', 'fcp']
    assert result.amounts['icms'] == Decimal('16.83')
    assert result.amounts['icms_st'] == Decimal('15.12')
    assert result.amounts['fcp_st'] == Decimal('3.55')
