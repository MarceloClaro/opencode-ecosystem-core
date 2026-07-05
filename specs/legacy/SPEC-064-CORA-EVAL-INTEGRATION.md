# SPEC-064: CORA-Eval Integration Layer — Skills, Agentes, MCPs & Hooks

## Metadados
- **ID**: SPEC-064
- **Status**: ✅ Implementado — v1.0.0
- **Autoria**: OpenCode Ecosystem v7.0 / R28
- **Data**: 2026-07-02
- **Relacionado**: SPEC-046, SPEC-047, SPEC-059, SPEC-062, SPEC-028–031

---

## 1. Objetivo

Estabelecer a camada de integração formal entre as **26 suítes TDD CORA-Eval** (D1–D26, 261 CTs) e os demais componentes do OpenCode Ecosystem:

| Camada | Componentes |
|--------|-------------|
| **Skills** | 227 skills em 13 categorias |
| **Agentes** | 128 agentes especializados |
| **MCPs** | 46 servidores MCP (pubmed, openalex, ncbi...) |
| **Hooks** | Pre-commit, CI/CD GitHub Actions |
| **SPECs** | 63+ SPECs referenciadas por domínio |

---

## 2. Arquitetura de Integração

```
Query/Tarefa do Usuário
        │
        ▼
classify_query_domain(query)   ← cora_eval_integration.py
        │
        ├── Domínio D1–D26 identificado
        │
        ▼
route_to_skills(domain)   ──► Skills OpenCode ativadas
route_to_mcps(domain)     ──► MCPs consultados
route_to_agents(domain)   ──► Agentes delegados
        │
        ▼
run_domain_suite(domain)  ──► pytest test_d*.py
        │
        ▼
DomainResult              ──► generate_cora_eval_report()
```

---

## 3. Mapa Domínio ↔ Skill ↔ MCP ↔ Agente

### Ciências Fundamentais (D1–D12)

| Domínio | Skills Primárias | MCPs | Agentes |
|---------|-----------------|------|---------|
| D1 Matemática | aletheia-math-research, symbolic-math, reasoning-orchestrator-v12 | — | phd-auditor |
| D2 Física | aletheia-math-research, symbolic-math | — | phd-auditor |
| D3 Estatística | academic-ml-pipeline, reasoning-orchestrator-v12 | — | phd-auditor |
| D4 Química | chembl-database, pubchem_database | chembl, pubchem | — |
| D5 Biologia Molecular | ncbi-sequence-fetch, uniprot-database | ncbi, uniprot | — |
| D6 Geociências | geographer | — | geographer |
| D7 Verificação de Código | code-review, formal-verification, swarm-review | — | codereviewer, securityaudit |
| D8 Literatura | literature-search-openalex, pubmed-database | openalex, pubmed | phd-auditor |
| D9 Metodologia | academic-ml-pipeline, reasoning-orchestrator-v12 | — | phd-auditor |
| D10 Interdisciplinar | cora-debate, reasoning-orchestrator-v12 | — | phd-auditor, marceloclaro |
| D11 Longo Horizonte | agent-node-pipeline, reasoning-orchestrator-v12 | — | marceloclaro |
| D12 Mecatrônica | symbolic-math, logic-programming | — | — |

### Ciências Aplicadas (D13–D20)

| Domínio | Skills Primárias | MCPs | Agentes | SPEC |
|---------|-----------------|------|---------|------|
| D13 Pedagogia | reasoning-orchestrator-v12, cora-debate | pubmed, openalex | marceloclaro | — |
| D14 Data Science | academic-ml-pipeline | — | phd-auditor | — |
| D15 Economia Tokens | cora-debate, nexus-strategy | — | marceloclaro | SPEC-022, SPEC-023 |
| D16 Bioinformática | ncbi-sequence-fetch, ensembl_database | ncbi, ensembl, uniprot | — | — |
| D17 IA Constitucional | cora-debate, formal-verification, automation_governance | — | marceloclaro | SPEC-046 |
| D18 Direito Computacional | triagem-juridica, gerador-contratos, pesquisa-jurisprudencia | — | marceloclaro | SPEC_JUR_* |
| D19 Worldbuilding | geographer, anthropologist, historian | — | geographer, anthropologist | SPEC_AGE_* |
| D20 Neurociência | aletheia-math-research, academic-ml-pipeline | pubmed | phd-auditor | — |

### Domínios Avançados (D21–D26)

| Domínio | Skills Primárias | MCPs | Agentes | SPEC |
|---------|-----------------|------|---------|------|
| D21 Medicina Digital | pubmed-database, alphafold, clinical-case-study | pubmed, openfda | phd-auditor | — |
| D22 Causalidade/RUMI | cora-debate, aletheia-math-research | — | marceloclaro | SPEC-057-ARCHE-RLT |
| D23 Inferência Ativa | aletheia-opencode-native, reasoning-orchestrator-v12 | — | marceloclaro | SPEC-059 |
| D24 Engenharia Reversa | code-review, swarm-review, securityaudit, code-graphrag | — | codereviewer | — |
| D25 Metacognição/ToT | cora-debate, reasoning-orchestrator-v12 | — | marceloclaro | SPEC-062 |
| D26 Computação Quântica | aletheia-math-research, formal-verification | — | phd-auditor | — |

---

## 4. Integration Hub — `hooks/cora_eval_integration.py`

### Funções Principais

```python
# Classificar query em domínios CORA-Eval
domains = classify_query_domain("Como aplicar SM-2 a flashcards educacionais?")
# → ["D13", "D25"]

# Obter skills para um domínio
skills = route_to_skills("D22")
# → ["cora-debate", "aletheia-math-research", "reasoning-orchestrator-v12"]

# Executar validação de um domínio
result = run_domain_suite("D22")
# → DomainResult(domain_id="D22", passed=8, failed=0)

# Relatório completo
results = run_all_domains()
report = generate_cora_eval_report(results)
```

### CLI

```bash
# Relatório de todos os domínios
python hooks/cora_eval_integration.py report

# Gerar hook de pré-commit
python hooks/cora_eval_integration.py hook

# Gerar CI/CD YAML
python hooks/cora_eval_integration.py ci > .github/workflows/cora-eval.yml

# Roteamento de query para domínios
python hooks/cora_eval_integration.py route "causalidade e machine learning"

# Validar domínio específico
python hooks/cora_eval_integration.py validate D22
```

---

## 5. Hooks de CI/CD

### Pre-Commit
```bash
# Ativar: cp hooks/pre-commit-cora-eval.sh .git/hooks/pre-commit
hooks/pre-commit-cora-eval.sh     ← valida todos D1–D26
```

### GitHub Actions
```yaml
# .github/workflows/cora-eval.yml
# Ativa em: push/PR com alterações em tests/test_d*.py
# Batches: D1–D12, D13–D20, D21–D26
# Artefato: cora_eval_report.md
```

---

## 6. Flows de Integração por Caso de Uso

### Caso A: Pesquisa Acadêmica
```
marceloclaro → classify_query_domain("DNA sequencing") → D5, D16
     → route_to_mcps(D16) → ncbi, ensembl, uniprot
     → route_to_skills(D16) → ncbi-sequence-fetch
     → run_domain_suite(D16) → DomainResult(passed=8)
     → SEEKER pipeline → phd-auditor → LaTeX/PDF
```

### Caso B: Análise de Código Crítico
```
marceloclaro → classify_query_domain("segurança código Python") → D7, D24
     → route_to_skills(D24) → code-review, swarm-review, securityaudit
     → run_domain_suite(D24) → DomainResult(passed=8)
     → swarm-review (3 agentes) → relatório consolidado
```

### Caso C: Dossiê Jurídico LGPD
```
marceloclaro → classify_query_domain("contrato LGPD dados pessoais") → D18
     → route_to_skills(D18) → triagem-juridica, gerador-contratos
     → run_domain_suite(D18) → DomainResult(passed=8)
     → triagem-juridica → classify_lgpd_basis() → gerador-contratos
```

### Caso D: Raciocínio de Longo Horizonte
```
marceloclaro → classify_query_domain("planejamento causal multinível") → D11, D22, D25
     → cora-debate (7 verificadores V1-V7)
     → reasoning-orchestrator-v12 (212+ tipos de raciocínio)
     → run_domain_suite([D11, D22, D25])
     → synthesis-agent → relatório final
```

---

## 7. Critérios de Aceitação

- [x] `hooks/cora_eval_integration.py` criado com DOMAIN_REGISTRY completo (D1–D26)
- [x] `hooks/pre-commit-cora-eval.sh` executável e funcional
- [x] `.github/workflows/cora-eval.yml` com 3 batches CI
- [x] `classify_query_domain()` mapeia queries → domínios por keywords
- [x] `route_to_skills/mcps/agents()` retorna recursos do ecossistema
- [x] 261 CTs passando em `pytest tests/test_d*.py`
- [x] SPECs D13–D26 criadas em `specs/SPEC_COR_d*.md`
- [ ] `menu.py` atualizado com submenu `CORA-Eval` (pendente)
- [ ] Hook instalado em `.git/hooks/pre-commit` (requer confirmação do usuário)

---

## 8. Referências Cruzadas

| SPEC | Domínios CORA-Eval Relacionados |
|------|---------------------------------|
| SPEC-022 Token Economy Core | D15 |
| SPEC-023 Agent Economics | D15 |
| SPEC-028 Noological Scanner | D10, D11 |
| SPEC-046 Antigravity CLI Integration | D17 |
| SPEC-051 Autonomia Metacognition | D23, D25 |
| SPEC-057 ARCHE-RLT | D22 |
| SPEC-059 Active Inference Self-Evolution | D23 |
| SPEC-060 Game Theory Strategic Reasoning | D15 |
| SPEC-062 Metacognitive Search Engine | D25 |
| SPEC_JUR_* (6 specs) | D18 |
| SPEC_AGE_* (académico) | D19 |
| SPEC_COR_d1-d12 (12 specs) | D1–D12 |
| SPEC_COR_d13-d26 (14 specs) | D13–D26 ← este ciclo |
