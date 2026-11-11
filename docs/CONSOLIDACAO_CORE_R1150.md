# Consolidação R1150 — N-of-1 único e auditoria de catálogo

**Data:** 2026-11-10
**Depende de:** R1132, R1148, R1149
**Relatório:** `reports/r1150/catalog_audit.json` (SHA-256
`cd813ad657471f0fb6277ee4710963fc19ebbbf82274d03b930f4c0c4be1d1c6`)

## 1. N-of-1: uma fonte, dois usos

Antes havia duas camadas:

- `core_cognition.n_of_1`: validador de protocolo ABAB, ética, desfechos e
  resumo descritivo;
- `mci.n_of_1`: runner com randomização, lock, adesão, eventos adversos e
  SCED.

Agora `core_cognition.n_of_1` contém **os dois**: validador + runner. O módulo
`mci.n_of_1` é um **shim de compatibilidade** que reexporta as funções
canônicas. Teste de identidade garante que não há segunda implementação.

```python
import core_cognition.n_of_1 as canonical
import mci.n_of_1 as compatibility
assert compatibility.run_n_of_1 is canonical.run_n_of_1
```

O validador e o runner coexistem no mesmo arquivo:

```python
validated = canonical.validate_protocol(canonical.template())
lock = canonical.lock_preregistration(protocol)
report = canonical.run_n_of_1(protocol, observations, lock["hash"])
```

## 2. Auditoria de catálogo

`integrations/catalog_audit.py` compara:

- `agents/catalog/*.md` (374 arquivos);
- `opencode.json` (374 agentes, 35 MCPs);
- ids canônicos (nome do arquivo), `agent_id` declarado, nomes e descrições;
- prompts, comandos/URLs de MCP, specs/tests referenciados.

### Resultado real

| Item | Resultado |
|---|---:|
| Arquivos de catálogo | 374 |
| Agentes em `opencode.json` | 374 |
| MCPs em `opencode.json` | 35 |
| Duplicatas de id canônico | **0** |
| Duplicatas de `agent_id` declarado | **0** |
| Duplicatas de nome | **0** |
| Prompts repetidos | **0** |
| Comandos/URLs de MCP repetidos | **0** |
| Drift catálogo ↔ config | **0** |
| Specs/tests ausentes | **0** |
| `agent_id` legado divergente | **2** |
| Descrições quase idênticas | **1 par** |

### Os dois metadados legados

| Arquivo | `agent_id` declarado | Id canônico |
|---|---|---|
| `kdp-metadata-isbn-phd.md` | `kdp-metadata-and-isbn-phd` | `kdp-metadata-isbn-phd` |
| `university_synthetic.md` | `synthetic_university` | `university_synthetic` |

Eles são mantidos como legado porque o baseline de ciclo de vida
(`agents/lifecycle_baseline.json`) usa os hashes atuais. Alterar o `agent_id`
sem migração quebra `opencode_cli --check`. O auditor reporta a divergência,
mas não reescreve o baseline.

### O par quase idêntico

`gjq-backend-guoji-04` × `gjq-backend-guoji-07` têm Jaccard **0,917** nas
descrições. São backends distintos (dois hardwares de 100 qubits), com perfis
próprios; **não devem ser fundidos** só pela similaridade textual.

## 3. Comandos

```bash
# auditoria
python3 integrations/catalog_audit.py --output reports/r1150/catalog_audit.json

# testes
python3 -m pytest tests/test_r1150_n_of_1_consolidation.py \
  tests/test_r1150_catalog_audit.py -q

# consistência da configuração
python3 -m integrations.opencode_cli --check
```

## 4. Limites

- A auditoria é textual/estrutural; não prova equivalência funcional.
- `agent_id` legado não é migrado automaticamente; exige atualização de
  baseline e teste de contrato.
- O par `guoji-04`/`guoji-07` é similar por texto, não por função.
- Nenhum agente foi removido ou fundido nesta rodada.
- Nenhum hardware foi executado.

## 5. Impacto na nota

Os dois itens que impediam a nota sobem: **coesão arquitetural** (N-of-1 único)
e **operação/auditoria de catálogo** (0 duplicatas, 0 drift). A nota ainda não
chega a 10/10 por CI de workflow pendente, worktree sujo e ausência de
validação externa.
