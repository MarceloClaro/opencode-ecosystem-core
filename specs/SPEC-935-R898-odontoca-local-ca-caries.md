# SPEC-935-R898 — OdontoCA Local: Autômatos Celulares + ML para Predição de Cárie

- **Status:** draft → active (após aprovação do orquestrador)
- **Data:** 2026-10-15
- **Orquestrador:** marceloclaro
- **Modo:** TDD estrito (RED → GREEN → REFACTOR)

## 1. Contexto

O site `rx.engenhariaorofacial.com.br` foi auditado com REA (v6.4.0): trata-se de
visualizador de radiografias panorâmicas ("Panoramica AI"), sem backend de treino —
não é o OdontoCA. O projeto OdontoCA vive em `odonto/` (notebook Colab v1.4.0) e
roda apenas em execução notebook com downloads remotos. O usuário pediu:

1. Fazer o OdontoCA rodar **localmente**;
2. **Treinar em datasets do Kaggle** (ou outro repositório de qualidade);
3. Usar **autômatos celulares** + incrementos técnicos minerados em artigos
   científicos para melhorar acurácia/predição.

## 2. Fontes de dados (comprovadas nesta sessão)

| Fonte | Papel | Evidência |
|---|---|---|
| `odonto/manuscript_assets/robust_audit/Table_S1.xlsx` | **Primária** (coorte do manuscrito, granularidade criança×dente×tempo) | SHA-256 `b7819fee…9184fa` **confere** com o valor fixado no notebook (fail-closed) |
| Kaggle `cdc/national-health-and-nutrition-examination-survey` | **Externa** (NHANES; variáveis OHX01–OHX32 por dente) | baixado em `odonto/local/datasets/nhanes/` |
| Kaggle `svyatoslavbelkovsky/periodontal-disease-and-smoking` | apoio | baixado |
| Kaggle `adhamkhaled10/finalccc`, `utkarshx27/…NOHSS` | agregados — apenas utilitário/demo | baixados |
| Kaggle `prajwalbastewad/dental-caries-dataset` e demais de imagens | **fora de escopo** (sem torch/tensorflow no ambiente) | inventariados; extensão futura |
| Zenodo 14827784 (imagens intraorais, 1,5 GB×2) | inventário somente (auditoria, não download) | API consultada |

Ambiente: Python com sklearn 1.9.0, pandas 3.0.3, numpy 2.5.1; **sem**
xgboost/lightgbm/shap → implementação usa apenas scikit-learn com upgrades
opcionais degradação-graceful se instalados. Kaggle CLI 2.2.4 + `~/.kaggle/kaggle.json` OK.

## 3. Escopo funcional (módulo em `odonto/local/`)

Pacote Python `odontoca` com CLI `python3 -m odontoca.cli <comando>`:

- `download` — baixa/valida datasets (Kaggle CLI com consentimento explícito do
  operador por `--i-know-kaggle`; valida SHA-256 da Table_S1);
- `train` — treina modelos com CV agrupada por criança, emite relatório JSON+MD;
- `predict` — inferência com modelo salvo (joblib) e calibração;
- `report` — regera relatório a partir de predições OOF salvas;
- `ca-sim` — simulação de progressão H→C pelo autômato celular calibrado
  (apenas cenário descritivo, **nunca** alegação causal).

### 3.1 Autômato celular (núcleo do incremento)

Estado por dente: `H` (saudável), `C` (cárie), `F` (restaurado), `M` (ausente) —
codificação do `Status_Tooth`/`Future_Status_Tooth` da Table_S1.

- **Topologia:** mapa FDI (decíduos 51–85, permanentes 11–48) + posição espacial
  `X,Y,Z` da Table_S1; **vizinhos por arco** (mesmo quadrante, adjacentes) e por
  **proximidade Euclidiana** (raio configurável) — replicando a hipótese de
  "transmissão" de cárie entre dentes vizinhos (beta-binomial espacial,
  PMC2948643; MRF espacial, PMC5087817).
- **Regra de transição:** `P(C_{t+1} | estado do dente em t, nº vizinhos com C,
  dmfs do host, nicho, posição)` estimada por regressão logística/boosting
  **nos dados** (regra aprendida, não imposta) — análogo a regra de autômato
  celular calibrada; verificação de que a regra aprendida reproduz as taxas
  observadas H→C por subgrupo (auditoria de calibração por nicho/molar).
- **Features CA:** `neighbor_caries_count` (arco prev/next, como o pipeline
  original), `neighbor_caries_spatial` (raio), `is_molar`, `niche`, coord
  espacial, dmfs host, tempo desde última visita.

### 3.2 Incrementos minerados em artigos (com DOI verificado ou fonte citada)

| # | Incremento | Fonte (auditada nesta sessão) | Uso |
|---|---|---|---|
| 1 | Ensemble de probabilidades (+2,6–5,1 p.p. AUROC) | Kang et al., PLOS ONE 19(9):e0310004, **DOI 10.1371/journal.pone.0310004** ✅ Crossref | média de probs de modelos diversos |
| 2 | Gradient boosting como melhor tabular | Väyrynen et al., Community Dental Health 41(S1), **DOI 10.1177/0265539X2024041004012** ✅ Crossref | `HistGradientBoostingClassifier` |
| 3 | Seleção por importância (RFE/RF) | BMC Oral Health 2025, 10.1186/s12903-025-05419-2 | RFE opcional |
| 4 | Interpretabilidade por importância de permutação | revisão Priyanka 2025 (10.1007/s44163-025-00391-w); SHAP se instalado | relatório |
| 5 | Calibração de probabilidade (Brier) | TRIPOD+AI; padrão OdontoCA | Platt/Isotônica |
| 6 | Dependência espacial entre dentes vizinhos | PMC2948643 (beta-binomial espacial); PMC5087817 (MRF/Potts) | features CA |
| 7 | Transições Markov multi-estado H→C | OdontoCA v1.4.0 (multi-state); diss. Iowa | alvo |
| 8 | Ensemble + calibração sem vazamento | meta-análise Luke & Rezallah 2025 (PMC11969992) | CV agrupada |
| 9 | Progressão como difusão anisotrópica (homogeneização) | Fabregas & Rubinstein 2014, *Math. Med. Biol.* 31(4):319–337, **DOI 10.1093/imammb/dqt008** ✅ Crossref | fundamenta a regra espacial |
| 10 | Autômato celular de biofilme / disbiose por açúcar | Head et al. 2017, *Sci. Rep.* 7, **DOI 10.1038/s41598-017-17660-z** ✅ Crossref | precedente de CA em cárie |
| 11 | Limiar de decisão por Youden (alvos desbalanceados) | TRIPOD+AI; prática de calibração | `best_threshold()` |

**Resultado empírico registrado (2026-10-15, revisado):** Table_S1 `onset` na
**coorte travada** (gate fail-closed `996/83/81`, replicando `build_transitions`
da cell 15 + verificação da cell 58) → ensemble AUROC **0.805** (IC95%
0.767–0.837), AUPRC 0.225, Brier 0.073; nesta coorte o ensemble **não** supera
todos os base (RF 0.819, logística 0.814, gradient boosting 0.788). Kaggle
imagens (`walidphd/dental-caries-classificationv3`, 957 imagens) → ensemble
AUROC **0.896** (0.868–0.922), AUPRC 0.972; aqui o ensemble **supera** todos os
base. Conclusão: o ganho de ensemble é **específico do dataset**.
Nenhuma alegação de superioridade sobre o estado da arte.

**Correção registrada (R898b):** a primeira derivação de `onset` (ordenação por
mês, sem exigir `Timepoint` consecutivo) produziu 1.175/120/88 — **divergente**
da coorte travada; foi substituída pela derivação fiel (996/83/81) e o AUROC
corrigido é 0.805 (o 0.827 anterior era sobre coorte divergente e foi retirado).

Fora de escopo justificado: CNN/YOLO/imagens (sem torch/TF), alegação de
"melhor acurácia que o estado da arte" (comparação empírica apenas, revisão
humana obrigatória).

## 4. Critérios de aceitação (FR) — mapeados a testes

| FR | Critério | Teste |
|---|---|---|
| FR-001 | `load_table_s1` rejeita arquivo cujo SHA-256 ≠ `b7819fee…9184fa` (fail-closed, exceção) e aceita o correto | `test_data.py::test_source_hash_fail_closed` |
| FR-002 | Topologia FDI: 20 decíduos (51–55, 61–65, 71–75, 81–85) + 32 permanentes (11–18, 21–28, 31–38, 41–48) = 52; adjacentes de arco corretos (54↔55 e 55↔56 inexistente em decíduo — decíduos terminam em 5; quadrante por dezena) | `test_topology.py` |
| FR-003 | `add_ca_features` produz `neighbor_caries_count ∈ {0,1,2}` e `neighbor_caries_spatial ≥ 0` | `test_ca.py::test_neighbor_count_bounds` |
| FR-004 | Extração de transições fiel a `build_transitions` (cell 15): transição de **um passo** = `Timepoint` consecutivo (`delta_timepoints == 1`) **e** `delta_months > 0`; coorte em risco = `Status_Tooth(t) == H`; evento = `Status_Tooth(t+1) == C`. **Não** usar `Future_Status_Tooth` (não é transição temporal); excluir posição composta `T5161` | `test_train.py::test_onset_requires_consecutive_timepoint`, `::test_onset_requires_positive_month_interval`, `::test_onset_excludes_composite_position` |
| FR-005 | Ensemble retorna `p ∈ [0,1]` e AUROC ≥ min(modelos base) − 0,02 (não degrada) em dataset sintético com sinal | `test_train.py::test_ensemble_not_worse` |
| FR-006 | CV agrupada: nenhum `HostID` aparece em treino e teste do mesmo fold (sem vazamento) | `test_train.py::test_grouped_no_leak` |
| FR-007 | Métricas incluem AUROC, AUPRC, Brier, sensibilidade no limiar e IC bootstrap 95% | `test_train.py::test_metrics_complete` |
| FR-008 | CLI `train` roda de ponta a ponta em CSV sintético e emite `report.json` + `report.md` válidos | `test_end2end.py` |
| FR-009 | `predict` carrega joblib salvo e devolve probabilidade em [0,1] com modelo congelado | `test_end2end.py::test_predict_roundtrip` |
| FR-010 | Auditoria abaixo-do-aqui: baseline 50% (ou prevalência) reportado ao lado do modelo; se modelo < baseline → flag `BELOW_BASELINE` | `test_train.py::test_below_chance_flag` |
| FR-011 | `ca-sim` descreve cenário com taxa H→C reproduzida por calibração, rotulado `descritivo, não causal` no relatório | `test_ca.py::test_sim_label` |
| FR-012 | Kaggle download só com `--i-know-kaggle` (consentimento explícito) e registra proveniência (ref, sha256 do zip) | `test_data.py::test_kaggle_consent` |
| FR-013 | Gate fail-closed de coorte (`--verify-locked`): a coorte derivada de `Table_S1` deve ser exatamente **996 linhas / 83 eventos / 81 crianças** (replica a cell 58); divergência levanta `CohortMismatchError` e aborta (saída 3) | `test_train.py::test_locked_cohort_reproduced`, `::test_verify_locked_cohort_raises_on_mismatch` |

## 5. Fora de escopo

- Treino de modelos de imagem (CNN/YOLO/SAM) — requer torch/ultralytics;
  inventário somente.
- Alegações causais de progressão; substituição do notebook Colab;
  qualquer alegação de Qualis/aceitação/nota.

## 6. Riscos e mitigações

- **Overclaim:** relatório traz baseline e CI; linguagem "comparação empírica".
- **Leakage temporal:** split por `HostID` + opcionalmente por `Timepoint`.
- **Dataset NHANES variável:** mapeamento OHX→alvo é opcional (`--target`);
  schema detectado automaticamente com override manual.
- **Ambiente sem xgboost:** `HistGradientBoostingClassifier` (sklearn ≥1.0);
  XGBoost/LightGBM entram só se detectados (`importlib.find_spec`).

## 7. Definição de pronto

`cd odonto/local && python3 -m pytest tests/ -q` → todos verdes (GREEN),
relatório de treino gerado na Table_S1 verificada **e** em dataset Kaggle
(NHANES), reflexão registrada no MetaBus e ciclo no EvolutionRegistry.
