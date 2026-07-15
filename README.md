# Tributus Engine (Pacote Python)

Pacote Python da biblioteca **Tributus Engine** para cálculo tributário brasileiro.

**Versão:** 0.5.1  
**Requer:** Python ≥ 3.10, Pydantic ≥ 2.13.4  
**Licença:** AGPL v3

---

## Instalação

```bash
pip install tributus-engine
```

## O que a biblioteca cobre

- **ICMS** — CSTs: 00, 10, 20, 30, 51, 70, 90, 101, 201, 202/203, 900
- **FCP** — Fundo de Combate à Pobreza (próprio, ST e diferido)
- **IPI** — Ad valorem e específico (por unidade)
- **PIS** — Ad valorem (CST 01/02) e específico (CST 03)
- **COFINS** — Ad valorem (CST 01/02) e específico (CST 03)
- **IBS** — Imposto sobre Bens e Serviços (Reforma Tributária)
- **CBS** — Contribuição sobre Bens e Serviços (Reforma Tributária)
- Biblioteca de cálculo tributário com método centralizado via payload JSON
- Validação de entrada via schemas **Pydantic**
- Modo de cálculo **ad valorem** (percentual) e **específico** (por unidade)
- **Catálogo fiscal por NCM/CEST e UF** *(planejado)*

## Casos de uso

- Cálculo fiscal em ERP
- API REST de tributação
- Simulação de impacto tributário por produto
- Cenários com alíquota manual para homologação e testes

## Uso Rápido

### 1) Engine simplificada com payload dict

```python
from tributus_engine import TaxEngine

engine = TaxEngine()

payload = {
    "values": {
        "quantity": 5,
        "unit_price": 200.00,
        "gross_value": 1000.00,
        "discount_value": 100.00,
        "freight_value": 50.00,
        "insurance_value": 10.00,
        "other_expenses": 20.00
    },
    "taxes": {
        "icms": {
            "cst": "00",
            "aliquota_icms_proprio": 17.00
        },
        "ipi": {
            "aliquota_ipi": 10.00
        },
        "pis": {
            "aliquota_pis": 1.20
        },
        "cofins": {
            "aliquota_cofins": 5.40
        },
        "ipi": {
            "aliquota_ipi": 10
        }
    }
}

result = engine.calculate_from_dict(payload)

# Retorno simplificado (detailed=False)
print(result.to_dict())
# {'amounts': {'ipi': '108.00', 'icms': '184.96', 'pis': '9.54', 'cofins': '42.93'},
#  'messages': [],
#  'total': '345.43'}

# Retorno completo (detailed=True)
print(result.to_dict(detailed=True))
```

### 2) Estrutura de `taxes` suportada

Cada imposto é ativado simplesmente declarando seu bloco dentro de `taxes`.

Campos aceitos por imposto:

- **`ipi`**: `aliquota_ipi` (porcentagem, modo *ad valorem*) ou `mode: "specific"` + `aliquota_por_unidade` + `base_calculo` (modo *específico*).
- **`icms`**: `cst`, `aliquota_icms_proprio`, `aliquota_icms_st`, `mva`, `percentual_reducao`, `percentual_reducao_st`, `percentual_diferimento`, `percentual_credito_sn`, `include_ipi_in_base` (bool, padrão `True`).
- **`fcp`**: `aliquota_fcp`, `aliquota_fcp_st`, `aliquota_diferimento_fcp`, `use_st_base` (bool).
- **`fcp_st`**: `aliquota_fcp_st`.
- **`pis`**: `aliquota_pis` (porcentagem) ou `mode: "specific"` + `aliquota_por_unidade` + `base_calculo`.
- **`cofins`**: `aliquota_cofins` (porcentagem) ou `mode: "specific"` + `aliquota_por_unidade` + `base_calculo`.
- **`ibs`**: `aliquota_efetiva_percentual`, `percentual_diferimento`.
- **`cbs`**: `aliquota_efetiva_percentual`, `percentual_diferimento`.

**Regras:**
- Se o bloco do imposto existe em `taxes`, ele é considerado **ativo** e será calculado.
- Se a alíquota não estiver configurada dentro do bloco, o cálculo é ignorado e uma mensagem é adicionada em `result.messages`.
- Se o bloco não existir, o imposto é simplesmente ignorado.
- O campo `enabled` (lista de strings) pode ser usado para habilitar tributos explicitamente, inclusive nomes como `"icms_st"`, `"fcp_st"`, `"fcp_diferido"`, `"icms_credito_sn"`.

### 3) Retorno completo (`detailed=True`)

```json
{
  "taxes": {
    "ipi": {"base": "1080.00", "rate": "10.00", "amount": "108.00", "metadata": {"mode": "ad_valorem"}},
    "icms": {"base": "1088.00", "rate": "17.00", "amount": "184.96", "metadata": {"type": "Icms00"}},
    "pis": {"base": "795.04", "rate": "1.20", "amount": "9.54", "metadata": {"mode": "ad_valorem"}},
    "cofins": {"base": "795.04", "rate": "5.40", "amount": "42.93", "metadata": {"mode": "ad_valorem"}}
  },
  "calculation_order": ["ipi", "icms", "pis", "cofins"],
  "messages": [],
  "total": "345.43"
}
```

### 4) Validação direta com schemas Pydantic

Os schemas de payload podem ser usados diretamente para validar dados:

```python
from tributus_engine import PayloadSchema

payload_validado = PayloadSchema.model_validate(payload)
# Se inválido, levanta ValidationError com mensagens descritivas
```

### 5) Uso avançado: ICMS com CST 10 (com ST) + FCP

```python
payload = {
    "values": {
        "gross_value": "1500.00",
        "discount_value": "0.00",
        "freight_value": "50.00",
        "insurance_value": "10.00",
        "other_expenses": "20.00"
    },
    "taxes": {
        "icms": {
            "cst": "10",
            "aliquota_icms_proprio": "12.00",
            "aliquota_icms_st": "18.00",
            "mva": "40.00"
        },
        "fcp": {
            "aliquota_fcp": "2.00",
            "aliquota_fcp_st": "2.00"
        }
    }
}

result = engine.calculate_from_dict(payload, detailed=True)
# Inclui icms, icms_st, fcp e fcp_st
```

## Ordem de cálculo

A engine resolve automaticamente a ordem de dependência entre os tributos:

1. **IPI** (calculado primeiro, pode compor base do ICMS)
2. **ICMS** (depende do IPI; PIS/COFINS dependem do ICMS)
3. **FCP** (depende do ICMS)
4. **PIS** (depende do ICMS para dedução na base)
5. **COFINS** (depende do ICMS para dedução na base)
6. **IBS / CBS** (independentes, calculados por último)

## Tratamento de erros

Quando o payload é inválido, a engine retorna mensagens descritivas em português:

```python
payload_invalido = {"values": {}, "taxes": {}}
result = engine.calculate_from_dict(payload_invalido)
print(result.messages)
# ['chave inválida em \'values → quantity\': não é um campo reconhecido']
```

## CSTs de ICMS suportados

| CST | Descrição |
|-----|-----------|
| 00  | Tributação integral |
| 10  | Tributação + ST |
| 20  | Base reduzida |
| 30  | Isento / não tributado + ST |
| 51  | Diferimento |
| 70  | Redução + ST |
| 90  | Outras (com redução, ST, etc.) |
| 101 | Simples Nacional — crédito |
| 201 | Simples Nacional — crédito + ST |
| 202/203 | Simples Nacional — ST |
| 900 | Outras (Simples Nacional) |

## Desenvolvimento

```bash
# Instalar em modo editável
python -m pip install -e .

# Instalar dependências de desenvolvimento
python -m pip install -e ".[dev]"

# Executar testes
python -m pytest tests

# Com cobertura
python -m pytest tests --cov=tributus_engine
```

## Licença

GNU Affero General Public License v3 &copy; 2026 Mackilem Van der Laan

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU Affero General Public License publicada pela Free Software Foundation, versão 3 da Licença, ou (a seu critério) qualquer versão posterior.
