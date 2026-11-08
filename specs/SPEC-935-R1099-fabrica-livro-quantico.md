# SPEC-935-R1099 — Fábrica do livro quântico: agentes, skills, hooks, harness e MCP

**Status:** implemented
**Data:** 2026-11-08
**Origem:** produção do livro *Do Bit ao Todo — 3000 Laudas de Física Quântica*.

## 1. Objetivo

Transformar a experiência de produção do livro em infraestrutura reutilizável:
agentes especializados, skills operacionais, hooks de segurança/proveniência,
harness de execução, handoff e um servidor MCP local somente leitura.

## 2. Artefatos

| Tipo | Artefato | Função |
|---|---|---|
| Agente | `livro-quantico-orchestrator` | orquestra spec, build, testes, auditoria e publicação |
| Agente | `quantum-experiment-auditor` | audita counts, task IDs, incerteza e limites |
| Agente | `quantum-lean-verifier` | verifica Lean 4 e classifica claims |
| Agente | `quantum-tools-coach` | instala e opera Qiskit, PennyLane, Cirq, GJQ e Lean |
| Agente | `repetition-editor` | audita e reduz repetição sem perder objetivos |
| Agente | `gjq-experiment-runner` | executa E01–E18 no GJQ com simulação prévia e auditoria |
| Agente | `david-bohm-wholeness` | lente de totalidade, diálogo e suposições (persona) |
| Agente | `richard-feynman-explainer` | lente de clareza, estimativa e contraexemplo (persona) |
| Skill | `producao-livro-quantico` | pipeline completo |
| Skill | `auditoria-experimentos-quanticos` | validação de E01–E18 |
| Skill | `verificacao-lean-quantum` | prova formal |
| Skill | `trilhas-ferramentas-quanticas` | instalação e uso |
| Skill | `edicao-antirrepeticao` | corte de repetição |
| Skill | `pacote-publicacao-cientifica` | eficácia, peer review, licença e metadados |
| Skill | `gjq-experimentos-quanticos` | execução GJQ, JSON, task ID e auditoria |
| Hook | `.opencode/hooks/quantum_secret_guard.sh` | bloqueia chave GJQ literal |
| Hook | `hooks/quantum_guards.py` | hardware sem simulação e claim Lean sem prova |
| Harness | `harnesses/livro-quantico/HARNESS.md` | etapas e gates |
| Handoff | `handoffs/livro-quantico/HANDOFF.md` | passagem de estado |
| MCP | `integrations/livro_quantico_mcp.py` | estado, experimentos, counts, Lean, repetição, checklist, Bohm/Feynman e painel de 13 |
| MCP | `integrations/gjq_experiments_mcp.py` | executa E01–E18 no GJQ com gates e auditoria |
| Scanner | `scanners/bohm_scanner.py` | triagem lexical de totalidade, diálogo, fragmentação e limites |
| Painel | `academic/bohm_feynman_panel.py` | 20 revisores, incluindo personas Bohm e Feynman |

## 3. Critérios de aceitação

- [ ] Agentes validam pelo contrato `managed-v1`.
- [ ] Skills têm `SKILL.md` com descrição e limites.
- [ ] Hook de segredo retorna GRANTED em fontes sem chave.
- [ ] `audit_counts` rejeita soma diferente de shots.
- [ ] Harness e handoff existem e citam os artefatos.
- [ ] MCP é registrado em `opencode.json` como local, read-only.
- [ ] Testes `tests/test_r1099_livro_quantico_package.py` passam.
- [ ] PDF do livro continua com 3550 páginas e links resolvidos.
- [ ] Grupo MiroFish `revisores_20` tem 20 membros, incluindo A35/A36; `revisores_13` permanece como compatibilidade.
- [ ] MCP `gjq-experiments` exige `confirm=True` e simulação prévia.
- [ ] Nenhum agente persona afirma ser a pessoa histórica ou endossa o texto.

## 4. Não objetivos

- Não declara eficácia pedagógica.
- Não substitui peer review.
- Não cria conta de plataforma.
- Não executa backend no MCP.
- Não promove confiança por presença de artefato.

## 5. Verificação

```bash
python3 -m pytest tests/test_r1099_livro_quantico_package.py -q
.venv/bin/python -m integrations.livro_quantico_mcp
.opencode/hooks/quantum_secret_guard.sh educacao_quantica_bohm/livro_pixel
```
