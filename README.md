# Tributus Engine (Pacote Python)

Pacote Python da biblioteca Tributus Engine para calculo tributario brasileiro.

## Instalacao

```bash
pip install .
```

## O que a biblioteca cobre

- ICMS e CSTs principais
- FCP e DIFAL
- IPI
- PIS e COFINS
- IBS e CBS
- Biblioteca de calculo tributario com metodo centralizado via payload JSON
- Catalogo fiscal por NCM/CEST e UF

## Casos de uso

- Calculo fiscal em ERP
- API REST de tributacao
- Simulacao de impacto tributario por produto
- Cenarios com aliquota manual para homologacao e testes

## Uso Rapido

### 1) Engine simplificada com payload dict

```python
from tributus_engine import TaxEngine

engine = TaxEngine()

payload = {
    "operation": {
        "operation_type": "sale",
        "document_type": "nfe",
        "operation_date": "2026-06-02",
        "issuer_state": "SP",
        "recipient_state": "RJ",
        "issuer_country": "BR",
        "recipient_country": "BR",
        "consumer_final": True,
        "taxpayer_icms": False,
        "presence_indicator": "2"
    },
    "company": {
        "tax_regime": "lucro_presumido",
        "crt": "3",
        "has_pis_credit": False,
        "has_cofins_credit": False,
        "suframa": False,
        "taxpayer_icms": False,
        "taxpayer_ibs": False
    },
    "customer": {
        "state": "RJ",
        "taxpayer_icms": False,
        "consumer_final": True,
        "suframa": False,
        "taxpayer_ibs": False
    },
    "product": {
        "ncm": "22030000",
        "cest": "0300100",
        "origin": "0",
        "fiscal_category": "industrialized",
        "import_content": 0.0,
        "benefit_code": None,
        "is_imported": False,
        "has_st": True,
        "has_monophase": False,
        "is_fuel": False,
        "is_medicine": False
    },
    "values": {
        "quantity": "5",
        "unit_price": "200.00",
        "gross_value": "1000.00",
        "discount_value": "100.00",
        "freight_value": "50.00",
        "insurance_value": "10.00",
        "other_expenses": "20.00"
    }
}

result = engine.calculate_from_dict(payload)
print(result.to_dict())
```

### 2) Engine com taxas manuais (`taxes`)

```python
payload["taxes"] = {
    "enabled": ["ipi", "icms", "fcp", "pis", "cofins", "ibs", "cbs"],
    "rates": {
        "icms": "17.00",
        "pis": "1.20",
        "cofins": "5.40",
        "ibs": "16.00",
        "cbs": "8.50"
    },
    "icms": {
        "cst": "00",
        "aliquota_icms_proprio": "17.00"
    },
    "ipi": {
        "aliquota_ipi": "10.00"
    },
    "pis": {
        "aliquota_pis": "1.20"
    },
    "cofins": {
        "aliquota_cofins": "5.40"
    }
}

result = engine.calculate_from_dict(payload)
print(result.to_dict())
```

### 3) Estrutura de `taxes` suportada

Campos principais aceitos no payload JSON:

- `enabled`: lista dos tributos a calcular na sequencia centralizada.
- `rates`: aliquotas simples por tributo quando nao houver configuracao mais especifica.
- `ipi`: `aliquota_ipi` ou `mode: specific` + `aliquota_por_unidade`.
- `icms`: `cst`, `aliquota_icms_proprio`, `aliquota_icms_st`, `mva`, `percentual_reducao`, `percentual_reducao_st`, `percentual_diferimento`, `percentual_credito_sn`, `include_ipi_in_base`.
- `fcp`: `aliquota_fcp`, `aliquota_fcp_st`, `aliquota_diferimento_fcp`.
- `pis`: `aliquota_pis` ou `mode: specific` + `aliquota_por_unidade`.
- `cofins`: `aliquota_cofins` ou `mode: specific` + `aliquota_por_unidade`.
- `ibs`: `aliquota_efetiva_percentual`, `percentual_diferimento`.
- `cbs`: `aliquota_efetiva_percentual`, `percentual_diferimento`.

O retorno consolidado expõe `taxes.{nome}.base`, `taxes.{nome}.rate`, `taxes.{nome}.amount` e `total`.

### 4) Consulta de impostos/taxas por NCM/CEST para todas as UFs

```python
taxes_by_state = engine.list_taxes_for_sale_all_states_from_dict({
    "product": {"ncm": "22030000", "cest": "0300100"}
})

print(taxes_by_state["SP"])
print(taxes_by_state["RJ"])
```

## Modo de resolucao de taxas

Prioridade da engine:

1. `taxes` enviado no payload
2. catalogo interno por NCM/CEST/UF
3. fallback automatico do provider

Na versao atual do metodo centralizado, o fluxo principal esperado e receber as incidencias e aliquotas no proprio JSON. Catalogo/provider continuam como extensoes futuras da superficie publica.

## Desenvolvimento

```bash
python -m pip install -e .
python -m pytest tests
```
