# OdontoCA Local — Autômatos Celulares + ML para Predição de Cárie

> **SPEC-935-R898** · comparação empírica sob revisão humana.
> **Não** garantimos acurácia superior, aceitação editorial ou uso clínico.

Módulo Python local que roda **sem Colab e sem downloads remotos**, treina em
dataset Kaggle e na fonte primária verificada do manuscrito, e usa um **autômato
celular** (topologia dentária + regra de transição aprendida) como núcleo de features.

## Instalação / requisitos

Ambiente de reprodução observado: Python 3.14.4. Para criar um ambiente local
com versões explícitas (incluindo `openpyxl`, backend necessário para ler a
fonte primária XLSX):

```bash
# runtime reproduzível
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# dependências de teste, separadas do runtime
python -m pip install -r requirements-dev.txt

# verificação local das dependências obrigatórias
python -c "import sklearn, pandas, numpy, cv2, joblib, openpyxl"
# opcionais (melhoram, mas não são exigidos): xgboost, lightgbm, shap
```

A instalação de dependências não baixa datasets. A fonte clínica continua
protegida pelo gate SHA-256 e downloads Kaggle exigem `--i-know-kaggle`.

## Uso

```bash
cd odonto/local

# 0) testes (TDD)
python3 -m pytest tests/ -q              # 26 testes

# 1) fonte primária do manuscrito (SHA-256 verificado, fail-closed)
python3 -m odontoca.cli train \
  --xlsx ../manuscript_assets/robust_audit/Table_S1.xlsx \
  --task onset --group HostID --out outputs/table_s1_onset --folds 5

# 2) dataset Kaggle rotulado (features clássicas de imagem)
kaggle datasets download -d walidphd/dental-caries-classificationv3 --unzip -p datasets/caries-cls
python3 -c "from odontoca import imagefeatures as f; f.build_image_dataset('datasets/caries-cls').to_csv('datasets/caries_features.csv', index=False)"
python3 -m odontoca.cli train --csv datasets/caries_features.csv --target label --out outputs/kaggle_caries_img

# 3) inferência com modelo salvo
python3 -m odontoca.cli predict --model outputs/kaggle_caries_img/model.joblib \
  --csv datasets/caries_features.csv --out outputs/pred.csv

# 4) download Kaggle com consentimento explícito
python3 -m odontoca.cli download --ref owner/slug --dest datasets/x --i-know-kaggle
```

## Resultados (validação interna, CV)

| Dataset | Fonte | N | AUROC (IC95%) | AUPRC | Brier | Sens/Espec (limiar ótimo) |
|---|---|---|---|---|---|---|
| Table_S1 `onset` H→C | fonte primária **SHA-256 verificado**, coorte travada | 996 (83 eventos) | **0.805** (0.767–0.837) | 0.225 | 0.073 | 0.940 / 0.608 |
| Kaggle cárie (imagens) | `walidphd/dental-caries-classificationv3` | 957 (783/174) | **0.896** (0.868–0.922) | 0.972 | 0.093 | 0.822 / 0.868 |

**Gate fail-closed de coorte (FR-012):** `--verify-locked` exige exatamente
**996 linhas / 83 eventos / 81 crianças** — a coorte travada do manuscrito
(cell 58). A derivação reproduz `build_transitions` do notebook: transições de
**um passo** (`Timepoint` consecutivo) com `delta_months > 0`, restritas a
posições primárias de 2 dígitos (exclui o composto `T5161`).

**Sobre o ensemble (correção honesta):** na coorte Table_S1 corrigida, o ensemble
(AUROC 0.805) **não** supera todos os base — RF 0.819 e logística 0.814 ficam
acima; ele supera apenas o gradient boosting (0.788). No dataset de **imagens**
do Kaggle, o ensemble (0.896) supera todos os base (logística 0.840,
gradient boosting 0.888, RF 0.886). Portanto o ganho de ensemble é
**específico do dataset**, não uma regra geral.

## Autômato celular (§3.1 da spec)

- **Topologia FDI:** 20 decíduos + 32 permanentes; vizinhança de arco e por
  proximidade Euclidiana (X/Y/Z da Table_S1).
- **Regra aprendida:** `P(H→C)` estimada dos dados por features de vizinhança
  (`neighbor_caries_count`, `neighbor_caries_spatial`), molaridade, dmfs e tempo.
- **Reprodução do achado do manuscrito:** os eventos H→C ocorrem
  **exclusivamente em molares decíduos** (T54/T55/T64/T65/T74/T75/T84/T85).
- **Simulação** (`ca-sim`) é **descritiva, não causal**.

## Incrementos minerados (DOIS verificados no Crossref)

1. Ensemble de probabilidades — Kang et al., *PLOS ONE* 19(9):e0310004, 2024 — `10.1371/journal.pone.0310004` ✅
2. Gradient boosting tabular — Väyrynen et al., *Community Dental Health* 41(S1), 2024 — `10.1177/0265539X2024041004012` ✅
3. Modelo matemático de progressão (homogeneização, difusão anisotrópica) — Fabregas & Rubinstein, *Math. Med. Biol.* 31(4):319–337, 2014 — `10.1093/imammb/dqt008` ✅
4. Autômato celular de biofilme / disbiose — Head et al., *Scientific Reports* 7, 2017 — `10.1038/s41598-017-17660-z` ✅
5. Dependência espacial entre dentes vizinhos — MRF espacial (PMC5087817) e beta-binomial espacial (PMC2948643)
6. Limiar de decisão por Youden para alvos desbalanceados — implementado
7. Calibração de probabilidade (Platt) — implementado

## Limitações (explícitas)

- **Sem xgboost/lightgbm/shap** no ambiente: o pipeline usa scikit-learn
  (`HistGradientBoostingClassifier`, RF, logística) com fallback documentado.
- **Sem deep learning**: imagens usam features clássicas (OpenCV), não CNN —
  extensão para torch/ultralytics é futura e fora do escopo.
- Validação **interna**; não substitui validação externa (TRIPOD+AI).
- Alvos desbalanceados: o limiar 0,5 não é adequado; use o limiar ótimo **apenas**
  com revisão clínica humana.
- Kaggle só faz download com consentimento explícito (`--i-know-kaggle`).

## Layout

```
odonto/local/
├── odontoca/          data.py topology.py ca.py models.py train.py predict.py cli.py imagefeatures.py
├── tests/             test_data topology ca train images end2end (26 testes)
├── datasets/          cachês locais (não versionados em peso)
└── outputs/           model.joblib, report.json, report.md, oof_predictions.csv
```
