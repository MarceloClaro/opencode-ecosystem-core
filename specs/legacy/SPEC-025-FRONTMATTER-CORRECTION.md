# SPEC-025: Frontmatter Correction Campaign — Skills Registry YAML Sanitization

**Status**: Draft
**Versão**: 1.0
**Data**: 2026-06-08
**Autor**: AutoEvolve / OpenCode Ecosystem v5.1.0
**Ciclo**: Round 17 — SDD→TDD→FIX→VERIFY→LEARN

---

## 1. SDD — Design Orientado a Especificação

### 1.1 Problema

O `self-healer` do ecossistema OpenCode reporta **67 problemas de frontmatter**
no skills registry. A inspeção direta revelou que 22 desses são **falsos positivos**
(skills science têm frontmatter YAML válido, mas o scanner os classifica como
`has_frontmatter: false` devido a chaves duplicadas ou bug no parser).

Os problemas **genuínos** são:

| Tipo | Quantidade | Skills |
|------|-----------|--------|
| Sem `---` delimiters + sem `name:` | 2 | `behavioral-nudge`, `agent-activation` |
| Tem `---` mas sem `name:` + sem `description:` | 1 | `codereviewer` |
| Tem `---` mas sem `description:` | 14 | 5 reasoning, 1 agency, ~8 science |
| Chaves YAML duplicadas | 2 | `uv`, `science_skills_common` |

**Total real**: ≈19 intervenções necessárias (vs. 67 reportados).

### 1.2 Arquitetura da Correção

```
Cada SKILL.md deve seguir este contrato YAML mínimo:

---
name: <kebab-case-identifier>
category: <category>
version: "1.0.0"
kind: <python|javascript|markdown>
description: >-
  Frase em PT-BR descrevendo propósito e gatilho de uso.
  Máximo 200 caracteres, sem duplicatas.
---
```

### 1.3 Escopo

#### Incluído:
- [x] Adicionar `---` + `name:` + `description:` em behavioral-nudge e agent-activation
- [x] Adicionar `name:` + `description:` em codereviewer
- [x] Adicionar `description:` em automation-governance
- [x] Adicionar `description:` em 5 skills reasoning (critical-reasoning, formal-verification, logic-programming, symbolic-math, test-generation)
- [x] Adicionar `description:` em ~8 skills science que têm frontmatter sem descrição
- [x] Remover chaves YAML duplicadas em uv e science_skills_common
- [x] Escrever `test_frontmatter_validator.py` para verificação automatizada
- [x] Atualizar `skills_registry.json` após correções
- [x] Registrar métricas no `memory.json` (Round 17)

#### Excluído (escopo futuro):
- Oversize remediation (23 skills >2.5KB)
- 99 skills não registradas (em `.claude/skills/`)
- Bug no `bash` tool (crash `Object.keys(state.correctionPatterns)`)
- Bug no `self-healer_health_fix` (`ServiceNotFoundError: state_manager`)
- CJK leak detection (já está em 0 — corretor pt-br funcional)

### 1.4 Critérios de Validação

1. **Frontmatter Obrigatório**: toda SKILL.md deve começar com `---`, conter
   `name:`, `category:`, `version:`, `kind:`, `description:`, e fechar com `---`
2. **Sem Chaves Duplicadas**: nenhuma chave YAML pode aparecer mais de uma vez
   no mesmo frontmatter
3. **name em kebab-case**: identificador no formato `meu-identificador`
4. **description em PT-BR**: descrição em português brasileiro formal
5. **Sem CJK**: zero caracteres CJK em qualquer SKILL.md
6. **YAML Parsable**: o frontmatter deve ser parseável por `yaml.safe_load()`
7. **Registro Consistente**: `skills_registry.json` deve refletir o estado real
   após correções (has_frontmatter=true, has_name=true, has_description=true)

---

## 2. TDD — Test-Driven Development

### 2.1 Plano de Testes

O script `test_frontmatter_validator.py` deve verificar:

| # | Caso de Teste | Entrada | Saída Esperada |
|---|--------------|---------|---------------|
| 1 | SKILL.md bem-formada | `---\nname: foo\ncategory: science\nversion: "1.0.0"\nkind: python\ndescription: >-\n  Foo.\n---\n# Foo\nBody` | ✅ PASS |
| 2 | SKILL.md sem frontmatter | `# Foo\nBody` | ❌ FAIL — missing_frontmatter |
| 3 | SKILL.md sem `---` abertura | `name: foo\ncategory: science\n---\n# Foo` | ❌ FAIL — missing_delimiter |
| 4 | SKILL.md sem `name:` | `---\ncategory: science\n---` | ❌ FAIL — missing_name |
| 5 | SKILL.md sem `description:` | `---\nname: foo\ncategory: science\n---` | ❌ FAIL — missing_description |
| 6 | SKILL.md com chaves duplicadas | `---\nname: foo\ncategory: science\ncategory: science\n---` | ❌ FAIL — duplicate_keys |
| 7 | SKILL.md com CJK | `---\nname: foo\ndescription: Teste 中文\n---` | ❌ FAIL — cjk_detected |
| 8 | SKILL.md oversize | SKILL.md com >2500 bytes | ⚠️ WARN — oversize |
| 9 | Nenhuma skill com falha no registro | `skills_registry.json` todo escaneado | ✅ Todas PASS |

### 2.2 Comandos de Verificação

```bash
# Pós-correção (quando bash for restaurado):
python scripts/test_frontmatter_validator.py --dir skills/
python scripts/test_frontmatter_validator.py --dir skills/ --registry nexus/skills_registry.json

# Via code-runner alternativo (enquanto bash estiver quebrado):
# O script será executado via node-sandbox ou code-runner MCP
```

---

## 3. IMPLEMENT — Plano de Execução

### Fase 1: Teste (SDD→TDD completo)

```
1. Criar test_frontmatter_validator.py        ← TDD: teste falha primeiro
2. Executar teste contra skills atuais         ← confirma que ~19 skills falham
3. Confirmar baseline                          ← registrar estado atual
```

### Fase 2: Correções (ordem de impacto)

```
4. behavior-nudge:   adicionar --- + name + description
5. agent-activation: adicionar --- + name + description
6. codereviewer:     adicionar name + description no frontmatter existente
7. automation-governance: adicionar description no frontmatter existente
8. reasoning (5):    adicionar description em c/reasoning, f/verification, l/programming, s/math, t/generation
9. science (~8):     adicionar description em ensembl, gnomad, gtex, interpro, arxiv, biorxiv, europepmc, openfda, opentargets, pdb, pubchem, reactome, string
10. uv:               remover duplicatas de category e version
11. science_skills_common: remover duplicatas de category, version, kind
```

### Fase 3: Verificação

```
12. Re-executar test_frontmatter_validator.py   ← 0 falhas
13. Atualizar skills_registry.json               ← re-scan com dados corretos
```

### Fase 4: Aprendizado

```
14. Escrever LEARN em memory.json               ← Round 17 completo
15. Atualizar SPEC_COVERAGE.md                   ← SPEC-025 registrada
```

---

## 4. CQs — Critical Questions

| # | Pergunta | Resposta |
|---|---------|----------|
| CQ1 | O scanner `has_frontmatter` está correto para os 22 science skills? | **Não** — inspeção visual de 4 deles (pymol, pubmed, alphafold, chembl) confirma frontmatter válido. O scanner provavelmente falha devido a chaves duplicadas ou sensibilidade a encoding. |
| CQ2 | As skills behavioral-nudge e agent-activation têm 5 linhas cada — estão truncadas? | **Sim** — cada uma tem exatamente 5 linhas, sugerindo que o conteúdo foi cortado ou nunca foi completo. A correção deve preservar o conteúdo existente e adicionar apenas o frontmatter. |
| CQ3 | Por que a description de automation-governance está vazia se o conteúdo tem descrição em markdown? | O frontmatter tem `---` delimiters e `name:`, `category:`, etc., mas **não tem o campo `description:`**. O texto descritivo está no body (`# Automation Governance Architect\n\nAgente especializado...`) mas não no YAML. |
| CQ4 | O `test_frontmatter_validator.py` precisa ser executável enquanto `bash` está quebrado? | **Sim** — será executado via `code-runner` (Python MCP) ou `node-sandbox` (JS alternativo). |
| CQ5 | As descrições para skills reasoning devem ser em português? | **Sim** — todo o ecossistema OpenCode segue o padrão pt-BR. As skills reasoning atualmente têm conteúdo em português. |

---

## 5. Edge Cases

| # | Caso | Tratamento |
|---|------|-----------|
| EC1 | SKILL.md começa com `# Title` mas não tem `---` | Adicionar `---` antes da primeira linha + frontmatter + `---` após |
| EC2 | Frontmatter tem `name:` mas o valor é vazio (`name:`) | Considerar como `has_name: false` — preencher com kebab-case do diretório |
| EC3 | `description:` usa `|` (literal block) vs `>` (folded block) | Ambos são válidos em YAML. Preferir `> -` para compatibilidade com parser Python |
| EC4 | Arquivo termina sem newline no final | Adicionar `\n` no final (POSIX compliance) |
| EC5 | Chave duplicada com valores diferentes (ex.: `category: science` e `category: agency`) | Remover a linha duplicada. A primeira ocorrência prevalece. |
| EC6 | Skill tem BOM (Byte Order Mark) no início | Remover BOM antes do parsing e antes de escrever |

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| `write` tool corromper encoding UTF-8 | Baixa | Alto | Verificar com `Read` pós-escrita |
| Editar SKILL.md e remover conteúdo acidentalmente | Média | Alto | Ler arquivo completo antes de editar; usar `diff` entre old/new |
| `code-runner` Python não suportar `yaml` module | Média | Médio | Usar `pyyaml` via pip ou fallback com `node-sandbox` JS |
| skills_registry.json ser sobrescrito por scan automático | Baixa | Médio | Fazer backup do registry antes de modificar |
| Esquecer de registrar SPEC-025 no SPEC_COVERAGE.md | Baixa | Baixo | Checklist na Fase 4 |

---

## 7. Acceptance Tests

1. ✅ `behavioral-nudge/SKILL.md`: começa com `---` + tem `name:` + `description:`
2. ✅ `agent-activation/SKILL.md`: começa com `---` + tem `name:` + `description:`
3. ✅ `codereviewer/SKILL.md`: frontmatter tem `name:` + `description:`
4. ✅ `automation-governance/SKILL.md`: frontmatter tem `description:`
5. ✅ 5 skills reasoning: cada uma tem `description:` no frontmatter
6. ✅ ~8 skills science: cada uma tem `description:` no frontmatter
7. ✅ `uv/SKILL.md`: sem chaves YAML duplicadas
8. ✅ `science_skills_common/SKILL.md`: sem chaves YAML duplicadas
9. ✅ `test_frontmatter_validator.py --dir skills/ --registry nexus/skills_registry.json`: 0 FAIL
10. ✅ `memory.json`: Round 17 registrado com métricas

---

## 8. Comandos de Verificação (pós-restauração do bash)

```bash
# 1. Executar teste unitário
python scripts/test_frontmatter_validator.py

# 2. Verificar skills problemáticas individualmente
python -c "
import yaml
with open('skills/agency/product/behavioral-nudge/SKILL.md') as f:
    content = f.read()
    if content.startswith('---'):
        _, fm, _ = content.split('---', 2)
        data = yaml.safe_load(fm)
        print('name:', data.get('name'))
        print('description:', data.get('description'))
    else:
        print('FAIL: no frontmatter')
"

# 3. Verificar registro
python -c "
import json
with open('nexus/skills_registry.json') as f:
    reg = json.load(f)
    broken = [s['name'] for s in reg if not s.get('has_frontmatter') or not s.get('has_name') or not s.get('has_description')]
    print(f'Broken: {len(broken)}')
    for b in broken:
        print(f'  - {b}')
"
```
