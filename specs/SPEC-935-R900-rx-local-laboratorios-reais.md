# SPEC-935-R900 — RX local: laboratórios reais (dataset, treinamento, autômatos celulares, validação)

- **Status:** active
- **Data:** 2026-10-15
- **Orquestrador:** marceloclaro
- **Modo:** TDD estrito (RED → GREEN → REFACTOR)
- **Depende de:** SPEC-935-R899 (backend mock da cópia local), SPEC-935-R898 (OdontoCA local: CA + ML)

## 1. Contexto e problema

A cópia local em `odonto/rx-site-local/` está funcional como **interface**, mas
todos os dados são mock: `/training-progress` é `0/300` fixo, `/review`,
`/validacao`, `/cadastro` e `/docs` são páginas explicativas, e nenhuma rota
expõe o trabalho real já existente no repositório:

- dataset clínico travado `manuscript_assets/robust_audit/Table_S1.xlsx`
  (SHA-256 `b7819fee…84fa`, coorte 996/83/81);
- datasets de imagem em `odonto/local/datasets/` (~91 MB);
- dois laboratórios de treino reais em `odonto/local/outputs/`
  (`table_s1_onset`, `kaggle_caries_img`) com `report.json`, `model.joblib`,
  `oof_predictions.csv`;
- o motor de **autômatos celulares** `odontoca/ca.py`
  (`add_ca_features`, `CARule`, `simulate_evolution`, `claim_level = descritivo_nao_causal`).

O usuário pediu: *"prossiga para validar framework já ative
Análise/Revisão/Validação/Cadastro/API-JSON e implemente o dataset, treinamento,
autômatos celulares e os laboratórios para a validação funcional melhorada rx"*.

## 2. Objetivo

Transformar a cópia local de **mock puro** em **híbrido honesto**: expor os
laboratórios **reais** locais (dataset, treinamento, CA, validação) por API-JSON
e páginas funcionais, mantendo rótulo explícito de `real` vs `mock`, e **sem
jamais** elevar o nível de alegação (`descritivo_nao_causal` /
`comparacao_empirica`) nem sugerir inferência de IA hospedada.

## 3. Requisitos funcionais

| ID | Requisito | Critério de aceitação |
|---|---|---|
| FR-001 | Pacote `backend/` | `odonto/rx-site-local/backend/` importável (`paths`, `datasets`, `labs`, `ca_lab`, `jobs`, `api`) sem dependência de rede; `odontoca` resolvido via `sys.path` para `odonto/local` |
| FR-002 | Probe de capacidade | `GET /api/health` → `{real:true, odontoca:bool, sklearn:bool, pandas:bool, datasets:int, models:int, ca:bool, claim_level}`; degrada (sem exceção) se `odontoca`/`sklearn` ausentes |
| FR-003 | Inventário de datasets | `GET /api/datasets` → lista real de `odonto/local/datasets/*` + `Table_S1.xlsx` com `name, path, kind, bytes, sha256, rows?, columns?, source?`; `sha256` do Table_S1 **deve** ser igual a `b7819fee…84fa` |
| FR-004 | Amostra real | `GET /api/datasets/sample?name=&n=&sheet=` → `columns` + até `n` linhas reais; `name` inválido/traversal → `404/400 JSON` (fail-closed) |
| FR-005 | Laboratórios de treino | `GET /api/models` → lê `outputs/*/report.json` reais com `auroc, auprc, brier, ci95, n, events, threshold, threshold_opt, claim_level, flag`; expõe `mock:false, real:true` |
| FR-006 | Treinamento real | `POST /api/train` inicia job em thread (`dataset`, `task`, `folds`, `seed`); `GET /api/train/status?id=` → `state, progress{completed,total,percentage}, report?`; `GET /api/train/jobs` lista jobs |
| FR-007 | Progresso real no front | `GET /training-progress` mantém shape `{completed,target,remaining,percentage}` e passa a reportar o job real quando houver; senão reporta o marco persistido (`basis:"artifact-count"`, `source`) — nunca inventa |
| FR-008 | Autômatos celulares reais | `POST /api/ca/simulate` (`steps, seed, n_teeth, rule`) usa `odontoca.ca` real → `{claim_level:"descritivo_nao_causal", steps, history[len==steps], final[n_teeth], rule:"prior"|"fitted", disclaimer}` |
| FR-009 | CA demo determinístico | `GET /api/ca/demo` → cenário reprodutível (seed fixo) para render inicial |
| FR-010 | Validação consolidada | `GET /api/validation` → `cohort_gate` (996/83/81 + sha256 + `locked_ok`), métricas dos dois laboratórios, `external_validation{status:"bloqueado", reason}`, `honest_tier` |
| FR-011 | Páginas funcionais | `/review`, `/validacao`, `/cadastro`, `/docs` servem dashboards reais (HTML+JS inline, sem CDN) que consomem as APIs acima, com selo `REAL`/`MOCK` por painel e banner MOCK preservado |
| FR-012 | Config de rede | `POST /api/train` aceita apenas datasets da allowlist (nomes do inventário); recusa caminho arbitrário |
| FR-013 | Testes | `python3 -m pytest odonto/rx-site-local/tests/ -q` → todos verdes, incluindo `test_real_api.py` (novos) |
| FR-014 | Anti-overclaim | Toda resposta real traz `real:true`; CA traz `claim_level=descritivo_nao_causal`; validação traz `comparacao_empirica`; nenhum texto "verificado/Qualis/cura/prova" |
| FR-015 | Regressão | `tests/test_serve.py` (10) e suite Odonto (**42**) permanecem verdes; `doctor` 22/22 |

## 4. Não escopo

- Nenhuma chamada de rede, nenhum download novo de dataset (Kaggle só com consentimento — SPEC-935-R898).
- Nenhuma inferência de modelo de produção; treino local só com `scikit-learn` (sem torch/tensorflow).
- Nenhuma alegação causal/qualidade; CA é **descritivo**, ML é **comparação empírica**.
- Não alterar `index.html`/`editor.js` capturados (somente injetar banner/servir).
- Não substituir a página original `/`; apenas enriquecer as 5 rotas pendentes.

## 5. Evidências planejadas

| Etapa | Evidência |
|---|---|
| RED | `tests/test_real_api.py` falha antes da implementação |
| GREEN | `pytest odonto/rx-site-local/tests/ -q` → verdes |
| HTTP real | `curl`/probe de cada endpoint; SHA-256 do Table_S1 conferido |
| Navegador | `ecosystem_browser` em `/cadastro`, `/review`, `/validacao`, `/docs`: sem erro de console, dados reais visíveis |
| Registro | `EvolutionRegistry` ciclo `SPEC-935-R900`; observação no MetaBus |

## 6. Riscos e limites

- Relógio de treino real pode exceder o timeout de uma requisição → job assíncrono com *polling* (FR-006).
- `sklearn` ausente no ambiente de destino → FR-002 degrada e o painel mostra aviso, não erro.
- O marco `n/300` do front é de interface; usar dados reais com rótulo `source` evita overclaim.
- `editor.js` já é truncado na cópia; edição no navegador não é exercitada aqui.
