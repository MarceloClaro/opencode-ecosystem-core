---
spec_id: SPEC-935-R747
title: Núcleo Lean — Verificação Total, Matemática Formal, Tese Auditável e Software Crítico
component: agents/catalog, .opencode/skills, integrations/lean_proof_mcp, plugins/lean-nucleo, tests/test_r747
status: proposed
round_id: R747
test_file: tests/test_r747_nucleo_lean.py
---

# SPEC-935-R747 — Núcleo Lean no Core

## 1. Contexto e Motivação

O Core já possui motores formais verificados:

- R444: `integrations/deepmind/lean4_verifier.py` + `egraph_rewriter.py` (status `syntax_verified`, `machine_checked` quando há compilador).
- R445: `integrations/deepmind/autoformalizer.py` (informal → Lean 4, Lean 4 → português, validação cruzada).
- R451/R503: sanidade formal e contraprova.

Lacuna: não há **agentes, skills, MCPs e plugins especializados** com contrato auditável para:

1. verificação total fail-closed;
2. matemática formal com Mathlib;
3. tese com provas auditáveis;
4. software crítico;
5. estudo sistemático de teoremas.

Esta SPEC define esse núcleo reutilizando os motores existentes, sem duplicá-los.

Delegação executada: `ecosystem_run task-99da2230` — Claude falhou por limite de conta, Codex entregou escopo de 15 itens (coordenador, especificador, autoformalizador, verificador, auditor; skills formalizar/auditar; MCP único; plugin único; contrato mínimo; fail-closed `sorry`/`admit`; sem compilador nunca aprovar). Workflow `workflow-4f8179412adf43648ecacb6f98f75421` bloqueou por ausência de agente interno elegível — prova da lacuna.

## 2. Requisitos e Componentes

### R747.1 — Agentes (5 arquivos em `agents/catalog/`)

1. `49_agente_lean_verificacao_total.md` — coordena o pipeline; impõe fail-closed; nunca declara prova total sem `machine_checked`.
2. `50_agente_lean_matematica_formal.md` — formaliza enunciados com Mathlib; fixa imports, versões e táticas permitidas.
3. `51_agente_lean_tese_auditavel.md` — organiza tese em capítulos com trilha: enunciado PT-BR → código `.lean` → log do verificador → reconciliação.
4. `52_agente_lean_software_critico.md` — especifica pré/pós-condições e invariantes; exige `machine_checked` para alegar correção.
5. `53_agente_lean_estudo_teoremas.md` — estuda teoremas existentes; explica tática por tática; nunca inventa lema Mathlib.

Cada agente: frontmatter YAML (`name`, `description`, `tags`, `type`), seções Missão/Entradas/Saídas/Ativação/Bloqueadores fail-closed/Handoff.

### R747.2 — Skills (2 pastas em `.opencode/skills/`)

1. `.opencode/skills/lean-verificacao-total/SKILL.md` — quando acionar, contrato mínimo (enunciado, premissas, código, versão Lean, log), tabela tática→uso, bloqueadores (`sorry`, `admit`, `axiom` sem declaração explícita).
2. `.opencode/skills/lean-tese-provas-auditaveis/SKILL.md` — estrutura de capítulo auditável, checklist de proveniência Mathlib, modelo de tabela de reconciliação.

Ambas com `disable-model-invocation: false`, comando explícito, sem execução implícita de scripts de terceiros.

### R747.3 — MCP `integrations/lean_proof_mcp.py`

Funções puras sobre os motores existentes, sem rede:

- `lean_verify(code: str) -> dict` — envolve `Lean4ProofVerifier.verify_lean_code`; `sorry`/`admit`/`axiom` → `is_valid=False`, `status=incomplete_sorry|axiom_nao_declarado`.
- `lean_export(theorem_name, statement, tactics, imports) -> dict` — envolve `format_theorem`; retorna `lean_source` + `sha256`.
- `lean_autoformalize(informal_text, domain) -> dict` — envolve `AutoFormalizerEngine.informal_to_lean4`.
- `lean_saturate(expr, rules) -> dict` — envolve `EqualitySaturationEngine` quando disponível; senão `status=indisponivel`.

Todo retorno inclui `provenance: {lean_binary, has_compiler, mathlib_version_hint, engine}` e nunca alega `machine_checked` sem compilador real.

### R747.4 — Plugin `plugins/lean-nucleo-verificacao/`

- `PLUGIN.md` (manifesto: nome, versão 0.1.0, componentes, licença, uso).
- `lean-nucleo.json` (manifesto máquina: agentes, skills, mcp, comandos).
- Reexporta sem copiar lógica dos motores.

## 3. Critérios de Aceite (SDD/TDD — `tests/test_r747_nucleo_lean.py`)

1. `test_spec_r747_registered`: SPEC-935-R747 registrada no `spec_registry`.
2. `test_agentes_lean_existem`: 5 arquivos existem com frontmatter e seção Bloqueadores/fail-closed.
3. `test_skills_lean_existem`: 2 `SKILL.md` existem com contrato mínimo e menção a `sorry`/`admit`.
4. `test_mcp_lean_verify_failclosed`: `sorry` → `is_valid=False`; código limpo com `ring` → `is_valid=True`, `status in {syntax_verified, machine_checked}`.
5. `test_mcp_lean_export_hash`: export gera `theorem <nome>` + `sha256` de 64 hex.
6. `test_mcp_lean_autoformalize`: informal → contém `theorem` e `Mathlib`.
7. `test_plugin_manifesto`: `PLUGIN.md` + `lean-nucleo.json` existem e listam os 5 agentes + 2 skills + MCP.
8. `test_sem_overclaim_sem_compilador`: sem binário Lean, nenhum caminho retorna `machine_checked` como prova total sem ressalva; `has_compiler=False` → status nunca `machine_checked` salvo execução real.

## 4. Regras Invioláveis

- `sorry`, `admit`, `axiom` não declarado → bloqueio total, sem exceção.
- Sem binário `lean`/`lake` → `syntax_verified` no máximo; declarar `não validado por compilador`.
- Não declarar Qualis, nota, aceite, superhuman ou prova total sem validação externa explícita.
- Reutilizar motores; não duplicar `lean4_verifier`, `egraph`, `autoformalizer`.
- Toda mudança relevante registra ciclo em `evolution/cycles.py` após verde.
