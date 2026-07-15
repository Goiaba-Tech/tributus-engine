from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from pydantic import ValidationError

from .models import (
    ZERO,
    Cofins01_02,
    Cofins03,
    Pis01_02,
    Pis03,
    IpiAdValorem,
    IpiEspecifico,
    Ibs,
    Cbs,
    Fcp,
    FcpST,
    FcpDiferido,
    FcpEfetivo,
    Icms00,
    Icms10,
    Icms20,
    Icms30,
    Icms51,
    Icms70,
    Icms90,
    Icms101,
    Icms201,
    Icms202_203,
    Icms900,
)
from .models import PayloadSchema

VALID_TAX_NAMES = {
    'icms',
    'icms_st',
    'icms_credito_sn',
    'fcp',
    'fcp_st',
    'fcp_diferido',
    'ipi',
    'pis',
    'cofins',
    'ibs',
    'cbs',
}
ORCHESTRATED_TAX_NAMES = {'ipi', 'icms', 'fcp', 'pis', 'cofins', 'ibs', 'cbs'}


def _to_decimal(value: Any, default: Decimal = ZERO) -> Decimal:
    if value is None or value == '':
        return default
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)


def _sum_amounts(values: list[Decimal]) -> Decimal:
    total = ZERO
    for value in values:
        total += value
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)


@dataclass
class ValueContext:
    quantity: Decimal = Decimal('0')
    unit_price: Decimal = ZERO
    gross_value: Decimal = ZERO
    discount_value: Decimal = ZERO
    freight_value: Decimal = ZERO
    insurance_value: Decimal = ZERO
    other_expenses: Decimal = ZERO


@dataclass
class TaxContext:
    values: ValueContext
    taxes: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        monetary_values = (
            self.values.quantity,
            self.values.unit_price,
            self.values.gross_value,
            self.values.discount_value,
            self.values.freight_value,
            self.values.insurance_value,
            self.values.other_expenses,
        )
        if any(value < ZERO for value in monetary_values):
            raise ValueError('values must be non-negative')

        if not isinstance(self.taxes, dict):
            raise ValueError('taxes must be a dict')

    def get_tax_detail(self, tax_name: str) -> dict[str, Any]:
        config = self.taxes.get(tax_name, {})
        if isinstance(config, dict):
            return config
        return {}


@dataclass
class TaxResult:
    bases: dict[str, Decimal] = field(default_factory=dict)
    rates: dict[str, Decimal] = field(default_factory=dict)
    amounts: dict[str, Decimal] = field(default_factory=dict)
    calculation_order: list[str] = field(default_factory=list)
    metadata: dict[str, dict[str, Any]] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)

    def register_tax(
        self,
        tax_name: str,
        *,
        base: Decimal,
        rate: Decimal,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.bases[tax_name] = base.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        self.rates[tax_name] = rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        self.amounts[tax_name] = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        if metadata:
            self.metadata[tax_name] = metadata

    @property
    def total(self) -> Decimal:
        return _sum_amounts(list(self.amounts.values()))

    def to_dict(self, detailed: bool = False) -> dict[str, Any]:
        if not detailed:
            return {
                'amounts': {k: v for k, v in self.amounts.items()},
                'messages': self.messages,
                'total': self.total,
            }

        taxes = {}
        for tax_name in self.amounts:
            taxes[tax_name] = {
                'base': self.bases[tax_name],
                'rate': self.rates[tax_name],
                'amount': self.amounts[tax_name],
            }
            if tax_name in self.metadata:
                taxes[tax_name]['metadata'] = self.metadata[tax_name]
        return {
            'taxes': taxes,
            'calculation_order': self.calculation_order,
            'messages': self.messages,
            'total': self.total,
        }


@dataclass
class BaseCalculator:
    gross_value: Decimal
    discount_value: Decimal
    freight_value: Decimal
    insurance_value: Decimal
    other_expenses: Decimal

    @classmethod
    def from_context(cls, context: TaxContext) -> 'BaseCalculator':
        return cls(
            gross_value=context.values.gross_value,
            discount_value=context.values.discount_value,
            freight_value=context.values.freight_value,
            insurance_value=context.values.insurance_value,
            other_expenses=context.values.other_expenses,
        )

    def base_padrao(self) -> Decimal:
        base = (
            self.gross_value
            - self.discount_value
            + self.freight_value
            + self.insurance_value
            + self.other_expenses
        )
        return base.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)


class TaxDependencyGraph:
    def __init__(self) -> None:
        self._dependencies: dict[str, set[str]] = {}

    def add_dependency(self, tax_name: str, dependency_name: str) -> None:
        self._dependencies.setdefault(tax_name, set()).add(dependency_name)
        self._dependencies.setdefault(dependency_name, set())

    def resolve_order(self, enabled_taxes: set[str], preferred_order: tuple[str, ...] | None = None) -> list[str]:
        resolved: list[str] = []
        temporary: set[str] = set()
        permanent: set[str] = set()

        def visit(tax_name: str) -> None:
            if tax_name in permanent:
                return
            if tax_name in temporary:
                raise ValueError('circular tax dependency detected')
            temporary.add(tax_name)
            dependency_names = self._ordered_tax_names(self._dependencies.get(tax_name, set()), preferred_order)
            for dependency in dependency_names:
                if dependency in enabled_taxes:
                    visit(dependency)
            temporary.remove(tax_name)
            permanent.add(tax_name)
            if tax_name in enabled_taxes:
                resolved.append(tax_name)

        for tax_name in self._ordered_tax_names(enabled_taxes, preferred_order):
            visit(tax_name)

        return resolved

    def _ordered_tax_names(self, tax_names: set[str], preferred_order: tuple[str, ...] | None) -> list[str]:
        if preferred_order is None:
            return sorted(tax_names)

        priority = {tax_name: index for index, tax_name in enumerate(preferred_order)}
        return sorted(tax_names, key=lambda tax_name: (priority.get(tax_name, len(priority)), tax_name))


class TaxEngine:
    def calculate(self, context: TaxContext, detailed: bool = False) -> TaxResult:
        """Executa o cálculo de todos os tributos habilitados para um dado contexto.

        Valida o contexto, resolve a ordem de dependência entre os tributos
        (ex: ICMS depende de IPI) e executa cada cálculo sequencialmente.

        Args:
            context: TaxContext com os valores da operação e configurações
                     dos tributos a serem calculados.

        Returns:
            TaxResult contendo as bases, alíquotas, valores calculados,
            ordem de cálculo, metadados e mensagens de erro/aviso.
        """
        context.validate()
        result = TaxResult()
        order = self._resolve_order(context)
        result.calculation_order = order

        for tax_name in order:
            self._calculate_tax(tax_name, context, result)

        return result.to_dict(detailed)

    def calculate_from_dict(self, payload: dict[str, Any], detailed: bool = False) -> TaxResult:
        """Valida e calcula tributos a partir de um payload em formato dicionário.

        O payload é validado contra o PayloadSchema (Pydantic) antes do cálculo.
        Se a validação falhar, retorna um TaxResult com as mensagens de erro
        formatadas em português.

        Args:
            payload: Dicionário no formato esperado pelo PayloadSchema,
                     contendo as chaves 'values' e 'taxes'.

        Returns:
            TaxResult com os resultados do cálculo ou mensagens de erro
            de validação.
        """
        try:
            PayloadSchema.model_validate(payload)
        except ValidationError as exc:
            result = TaxResult()
            result.messages = [
                self._format_pydantic_error(error) for error in exc.errors()
            ]
            return result
        return self.calculate(self._context_from_dict(payload), detailed)

    def _resolve_order(self, context: TaxContext) -> list[str]:
        graph = TaxDependencyGraph()
        enabled = self._enabled_taxes(context)
        preferred_order = ('ipi', 'icms', 'fcp', 'pis', 'cofins', 'ibs', 'cbs')

        if 'icms' in enabled and 'ipi' in enabled:
            graph.add_dependency('icms', 'ipi')
        if 'pis' in enabled and 'icms' in enabled:
            graph.add_dependency('pis', 'icms')
        if 'cofins' in enabled and 'icms' in enabled:
            graph.add_dependency('cofins', 'icms')
        if 'fcp' in enabled and 'icms' in enabled:
            graph.add_dependency('fcp', 'icms')

        return graph.resolve_order(enabled, preferred_order)

    def _enabled_taxes(self, context: TaxContext) -> set[str]:
        enabled = self._raw_enabled_taxes(context)
        if 'icms_st' in enabled or 'icms_credito_sn' in enabled:
            enabled.add('icms')
        if 'fcp_st' in enabled or 'fcp_diferido' in enabled:
            enabled.add('fcp')
        return {tax_name for tax_name in enabled if tax_name in ORCHESTRATED_TAX_NAMES}

    def _calculate_tax(self, tax_name: str, context: TaxContext, result: TaxResult) -> None:
        if tax_name == 'ipi':
            self._calculate_ipi(context, result)
            return
        if tax_name == 'icms':
            self._calculate_icms(context, result)
            return
        if tax_name == 'fcp':
            self._calculate_fcp(context, result)
            return
        if tax_name == 'pis':
            self._calculate_pis(context, result)
            return
        if tax_name == 'cofins':
            self._calculate_cofins(context, result)
            return
        if tax_name == 'ibs':
            self._calculate_ibs(context, result)
            return
        if tax_name == 'cbs':
            self._calculate_cbs(context, result)

    def _calculate_ipi(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'ipi')
        mode = self._mode(config, specific_key='aliquota_por_unidade')

        if mode == 'specific':
            rate = _to_decimal(config.get('aliquota_por_unidade'))
            if rate == ZERO:
                result.messages.append("IPI: 'aliquota_por_unidade' não configurada em taxes.ipi")
                return
            base = _to_decimal(config.get('base_calculo'), values.quantity)
            calculator = IpiEspecifico(base_calculo=base, aliquota_por_unidade=rate)
            amount = calculator.valor_ipi  # propriedade, não método
        else:
            rate = _to_decimal(config.get('aliquota_ipi'))
            if rate == ZERO:
                result.messages.append("IPI: 'aliquota_ipi' não configurada em taxes.ipi")
                return
            calculator = IpiAdValorem(
                valor_produto=values.gross_value,
                valor_frete=values.freight_value,
                valor_seguro=values.insurance_value,
                despesas_acessorias=values.other_expenses,
                aliquota_ipi=rate,
            )
            base = calculator.base_ipi
            amount = calculator.valor_ipi

        result.register_tax('ipi', base=base, rate=rate, amount=amount, metadata={'mode': mode})

    def _calculate_icms(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'icms')
        cst = str(config.get('cst', '00')).strip().upper().replace('-', '_')
        valor_ipi = result.amounts.get('ipi', ZERO) if config.get('include_ipi_in_base', True) else ZERO

        own_rate = _to_decimal(config.get('aliquota_icms_proprio'))
        st_rate = _to_decimal(config.get('aliquota_icms_st'))
        mva = _to_decimal(config.get('mva'))
        reducao = _to_decimal(config.get('percentual_reducao'))
        reducao_st = _to_decimal(config.get('percentual_reducao_st'))
        credito_sn = _to_decimal(config.get('percentual_credito_sn'))
        diferimento = _to_decimal(config.get('percentual_diferimento'))

        common = {
            'valor_produto': values.gross_value,
            'valor_frete': values.freight_value,
            'valor_seguro': values.insurance_value,
            'despesas_acessorias': values.other_expenses,
            'valor_desconto': values.discount_value,
        }

        if cst == '00':
            if own_rate == ZERO:
                result.messages.append("ICMS: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms00(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms00'})
            return

        if cst == '10':
            if own_rate == ZERO or st_rate == ZERO:
                result.messages.append("ICMS CST 10: 'aliquota_icms_proprio' e 'aliquota_icms_st' são obrigatórias")
                return
            calculator = Icms10(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_reducao_st=reducao_st, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms10'})
            result.register_tax('icms_st', base=calculator.base_icms_st, rate=st_rate, amount=calculator.valor_icms_st, metadata={'type': 'Icms10'})
            return

        if cst == '20':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 20: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms20(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, percentual_reducao=reducao, **common)
            result.register_tax('icms', base=calculator.base_reduzida_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms20'})
            return

        if cst == '30':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 30: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms30(valor_ipi=valor_ipi, aliq_icms_proprio=own_rate, aliq_icms_st=st_rate, mva=mva, percentual_reducao_st=reducao_st, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_desonerado, metadata={'type': 'Icms30', 'note': 'desonerado'})
            result.register_tax('icms_st', base=calculator.base_icms_st, rate=st_rate, amount=calculator.valor_icms_st, metadata={'type': 'Icms30'})
            return

        if cst == '51':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 51: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms51(valor_ipi=valor_ipi, aliq_icms_proprio=own_rate, percentual_reducao=reducao, percentual_diferimento=diferimento, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms51'})
            return

        if cst == '70':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 70: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms70(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_reducao=reducao, percentual_reducao_st=reducao_st, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms70'})
            result.register_tax('icms_st', base=calculator.base_icms_st, rate=st_rate, amount=calculator.valor_icms_st, metadata={'type': 'Icms70'})
            return

        if cst == '90':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 90: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms90(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_reducao=reducao, percentual_reducao_st=reducao_st, **common)
            base_icms = calculator.base_reduzida_icms_proprio if reducao > ZERO else calculator.base_icms_proprio
            amount_icms = calculator.valor_icms_proprio_base_reduzida if reducao > ZERO else calculator.valor_icms_proprio
            base_st = calculator.base_reduzida_icms_st if reducao_st > ZERO else calculator.base_icms_st
            amount_st = calculator.valor_icms_st_base_reduzida if reducao_st > ZERO else calculator.valor_icms_st
            result.register_tax('icms', base=base_icms, rate=own_rate, amount=amount_icms, metadata={'type': 'Icms90'})
            result.register_tax('icms_st', base=base_st, rate=st_rate, amount=amount_st, metadata={'type': 'Icms90'})
            return

        if cst == '101':
            calculator = Icms101(percentual_credito_sn=credito_sn, percentual_reducao=reducao, **common)
            result.register_tax('icms_credito_sn', base=calculator.base_icms_proprio, rate=credito_sn, amount=calculator.valor_credito_sn, metadata={'type': 'Icms101'})
            return

        if cst == '201':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 201: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms201(aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_credito_sn=credito_sn, percentual_reducao=reducao, percentual_reducao_st=reducao_st, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms201'})
            result.register_tax('icms_st', base=calculator.base_icms_st, rate=st_rate, amount=calculator.valor_icms_st, metadata={'type': 'Icms201'})
            result.register_tax('icms_credito_sn', base=calculator.base_icms_proprio, rate=credito_sn, amount=calculator.valor_credito_sn, metadata={'type': 'Icms201'})
            return

        if cst in {'202', '203', '202_203'}:
            if own_rate == ZERO:
                result.messages.append(f"ICMS CST {cst}: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms202_203(aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_reducao=reducao, percentual_reducao_st=reducao_st, **common)
            result.register_tax('icms', base=calculator.base_icms_proprio, rate=own_rate, amount=calculator.valor_icms_proprio, metadata={'type': 'Icms202_203'})
            result.register_tax('icms_st', base=calculator.base_icms_st, rate=st_rate, amount=calculator.valor_icms_st, metadata={'type': 'Icms202_203'})
            return

        if cst == '900':
            if own_rate == ZERO:
                result.messages.append("ICMS CST 900: 'aliquota_icms_proprio' não configurada em taxes.icms")
                return
            calculator = Icms900(valor_ipi=valor_ipi, aliquota_icms_proprio=own_rate, aliquota_icms_st=st_rate, mva=mva, percentual_credito_sn=credito_sn, percentual_reducao=reducao, percentual_reducao_st=reducao_st, **common)
            base_icms = calculator.base_reduzida_icms_proprio if reducao > ZERO else calculator.base_icms_proprio
            amount_icms = calculator.valor_icms_proprio_base_reduzida if reducao > ZERO else calculator.valor_icms_proprio
            base_st = calculator.base_reduzida_icms_st if reducao_st > ZERO else calculator.base_icms_st
            amount_st = calculator.valor_icms_st_base_reduzida if reducao_st > ZERO else calculator.valor_icms_st
            result.register_tax('icms', base=base_icms, rate=own_rate, amount=amount_icms, metadata={'type': 'Icms900'})
            result.register_tax('icms_st', base=base_st, rate=st_rate, amount=amount_st, metadata={'type': 'Icms900'})
            if credito_sn > ZERO:
                credit_base = base_icms
                result.register_tax('icms_credito_sn', base=credit_base, rate=credito_sn, amount=calculator.valor_credito_sn, metadata={'type': 'Icms900'})
            return

        result.messages.append(f"ICMS: CST '{cst}' não suportado")
        return

    def _calculate_fcp(self, context: TaxContext, result: TaxResult) -> None:
        config = self._tax_details(context, 'fcp')
        fcp_st_config = self._tax_details(context, 'fcp_st')
        deferment_rate = _to_decimal(config.get('aliquota_diferimento_fcp'))

        fcp_st_rate = _to_decimal(fcp_st_config.get('aliquota_fcp_st') or config.get('aliquota_fcp_st'))
        if 'icms_st' in result.bases and (
            config.get('use_st_base')
            or 'fcp_st' in self._raw_enabled_taxes(context)
            or fcp_st_rate > ZERO
        ):
            if fcp_st_rate == ZERO:
                result.messages.append("FCP ST: 'aliquota_fcp_st' não configurada em taxes.fcp ou taxes.fcp_st")
                return
            base = result.bases['icms_st']
            calculator = FcpST(base_calculo_st=base, aliquota_fcp_st=fcp_st_rate)
            amount = calculator.valor_fcp_st
            result.register_tax('fcp_st', base=base, rate=fcp_st_rate, amount=amount, metadata={'type': 'FcpST'})
            return

        base = result.bases.get('icms', BaseCalculator.from_context(context).base_padrao())
        rate = _to_decimal(config.get('aliquota_fcp'))
        if rate == ZERO:
            result.messages.append("FCP: 'aliquota_fcp' não configurada em taxes.fcp")
            return
        calculator = Fcp(base_calculo=base, aliquota_fcp=rate)
        amount = calculator.valor_fcp

        if deferment_rate > ZERO:
            deferred = FcpDiferido(valor_fcp=amount, aliquota_diferimento_fcp=deferment_rate)
            effective = FcpEfetivo(valor_fcp=amount, valor_fcp_diferido=deferred.valor_fcp_diferido)
            result.register_tax('fcp_diferido', base=base, rate=deferment_rate, amount=deferred.valor_fcp_diferido, metadata={'type': 'FcpDiferido'})
            amount = effective.valor_fcp_efetivo

        result.register_tax('fcp', base=base, rate=rate, amount=amount, metadata={'type': 'Fcp'})

    def _calculate_pis(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'pis')
        mode = self._mode(config, specific_key='aliquota_por_unidade')

        if mode == 'specific':
            rate = _to_decimal(config.get('aliquota_por_unidade'))
            if rate == ZERO:
                result.messages.append("PIS: 'aliquota_por_unidade' não configurada em taxes.pis")
                return
            base = _to_decimal(config.get('base_calculo'), values.quantity)
            calculator = Pis03(base_calculo=base, aliquota_por_unidade=rate)
            amount = calculator.valor_pis
        else:
            rate = _to_decimal(config.get('aliquota_pis'))
            if rate == ZERO:
                result.messages.append("PIS: 'aliquota_pis' não configurada em taxes.pis")
                return
            calculator = Pis01_02(
                valor_produto=values.gross_value,
                valor_frete=values.freight_value,
                valor_seguro=values.insurance_value,
                despesas_acessorias=values.other_expenses,
                valor_desconto=values.discount_value,
                aliquota_pis=rate,
                valor_icms=result.amounts.get('icms', ZERO),
            )
            base = calculator.base_pis
            amount = calculator.valor_pis

        result.register_tax('pis', base=base, rate=rate, amount=amount, metadata={'mode': mode})

    def _calculate_cofins(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'cofins')
        mode = self._mode(config, specific_key='aliquota_por_unidade')

        if mode == 'specific':
            rate = _to_decimal(config.get('aliquota_por_unidade'))
            if rate == ZERO:
                result.messages.append("COFINS: 'aliquota_por_unidade' não configurada em taxes.cofins")
                return
            base = _to_decimal(config.get('base_calculo'), values.quantity)
            calculator = Cofins03(base_calculo=base, aliquota_por_unidade=rate)
            amount = calculator.valor_cofins
        else:
            rate = _to_decimal(config.get('aliquota_cofins'))
            if rate == ZERO:
                result.messages.append("COFINS: 'aliquota_cofins' não configurada em taxes.cofins")
                return
            calculator = Cofins01_02(
                valor_produto=values.gross_value,
                valor_frete=values.freight_value,
                valor_seguro=values.insurance_value,
                despesas_acessorias=values.other_expenses,
                valor_desconto=values.discount_value,
                aliquota_cofins=rate,
                valor_icms=result.amounts.get('icms', ZERO),
            )
            base = calculator.base_cofins
            amount = calculator.valor_cofins

        result.register_tax('cofins', base=base, rate=rate, amount=amount, metadata={'mode': mode})

    def _calculate_ibs(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'ibs')
        rate = _to_decimal(config.get('aliquota_efetiva_percentual'))
        if rate == ZERO:
            result.messages.append("IBS: 'aliquota_efetiva_percentual' não configurada em taxes.ibs")
            return
        deferment = _to_decimal(config.get('percentual_diferimento'))
        calculator = Ibs(
            valor_produto=values.gross_value,
            valor_frete=values.freight_value,
            valor_seguro=values.insurance_value,
            despesas_acessorias=values.other_expenses,
            aliquota_efetiva_percentual=rate,
            percentual_diferimento=deferment,
        )
        result.register_tax('ibs', base=calculator.base_ibs_cbs, rate=rate, amount=calculator.valor_ibs, metadata={'type': 'Ibs'})

    def _calculate_cbs(self, context: TaxContext, result: TaxResult) -> None:
        values = context.values
        config = self._tax_details(context, 'cbs')
        rate = _to_decimal(config.get('aliquota_efetiva_percentual'))
        if rate == ZERO:
            result.messages.append("CBS: 'aliquota_efetiva_percentual' não configurada em taxes.cbs")
            return
        deferment = _to_decimal(config.get('percentual_diferimento'))
        calculator = Cbs(
            valor_produto=values.gross_value,
            valor_frete=values.freight_value,
            valor_seguro=values.insurance_value,
            despesas_acessorias=values.other_expenses,
            aliquota_efetiva_percentual=rate,
            percentual_diferimento=deferment,
        )
        result.register_tax('cbs', base=calculator.base_ibs_cbs, rate=rate, amount=calculator.valor_cbs, metadata={'type': 'Cbs'})

    def _format_pydantic_error(self, error: dict) -> str:
        loc = " → ".join(str(p) for p in error["loc"])
        if error["type"] == "extra_forbidden":
            return f"chave inválida em '{loc}': não é um campo reconhecido"
        if error["type"] == "missing":
            return f"campo obrigatório ausente: '{loc}'"
        if error["type"] == "literal_error":
            return f"valor inválido em '{loc}': {error['msg']}"
        return f"erro em '{loc}': {error['msg']}"

    def _context_from_dict(self, payload: dict[str, Any]) -> TaxContext:
        values_payload = payload.get('values', {})
        taxes_payload = payload.get('taxes', {})

        quantity = _to_decimal(values_payload.get('quantity'), Decimal('0'))
        unit_price = _to_decimal(values_payload.get('unit_price'))
        gross_value = values_payload.get('gross_value')
        if gross_value is None and quantity > ZERO and unit_price > ZERO:
            gross_value = (quantity * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

        values = ValueContext(
            quantity=quantity,
            unit_price=unit_price,
            gross_value=_to_decimal(gross_value),
            discount_value=_to_decimal(values_payload.get('discount_value')),
            freight_value=_to_decimal(values_payload.get('freight_value')),
            insurance_value=_to_decimal(values_payload.get('insurance_value')),
            other_expenses=_to_decimal(values_payload.get('other_expenses')),
        )

        return TaxContext(
            values=values,
            taxes=dict(taxes_payload),
        )

    def _tax_details(self, context: TaxContext, tax_name: str) -> dict[str, Any]:
        return context.get_tax_detail(tax_name)

    def _raw_enabled_taxes(self, context: TaxContext) -> set[str]:
        if not context.taxes:
            return set()

        enabled = {
            name for name, config in context.taxes.items()
            if isinstance(config, dict) and name != 'rates'
        }

        enabled_raw = context.taxes.get('enabled', [])
        if isinstance(enabled_raw, list) and enabled_raw:
            enabled.update(
                name for name in enabled_raw
                if name in VALID_TAX_NAMES
            )

        return enabled

    def _mode(self, config: dict[str, Any], *, specific_key: str) -> str:
        raw_mode = str(config.get('mode', '')).strip().lower()
        if raw_mode in {'specific', 'especifico', 'specifico'} or specific_key in config:
            return 'specific'
        return 'ad_valorem'