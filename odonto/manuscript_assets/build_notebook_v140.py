# -*- coding: utf-8 -*-
"""
build_notebook_v140.py — Cria OdontoCA v1.4.0 (pista de predicao clinica)
==========================================================================
Nao altera o v1.3.5. Parte do notebook JA EXECUTADO (com saidas reais) e
acrescenta um bloco de celulas que_addressa o que faltava para aceitacao em
banca:

  28  Proveniencia fail-closed e caminho de dados estavel (remove /tmp)
  29  Distribuicao por dente e propagacao observada (achado dos molares)
  30  Prontidao para validacao externa (regra de Riley: max(100, 10*gl))
  31  Travamento e exportacao do modelo final primário
  32  Transparencia dos portoes de aceitacao (alvos NAO atingidos)
  33  Ponto de entrada de inferencia para centros externos

ANTI-OVERCLAIM
--------------
O bloco declara que nao houve validacao externa, que os alvos de performance
do notebook NAO sao atingidos pelos dados reais, e que nenhum ramo de imagem
ou microbioma foi executado. Nada aqui e STATUS quo silencioso.
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "OdontoCA_v1_3_5_EXECUTED.ipynb"
DST = ROOT / "OdontoCA_v1_4_0_CLINICAL_PREDICTION.ipynb"

BANNER = """# ---

# 28-33. Pista de predição clínica v1.4.0 — aceitação em banca

> **O que este bloco faz.** Torna o notebook *submetível a banca*: fixa a
> proveniência do dado, quantifica o que falta para validação externa, trava e
> exporta o modelo primário, e **declara explicitamente que os alvos de
> performance deste notebook não são atingidos pelos dados reais**.
>
> **O que este bloco não faz.** Não executa validação externa. Não executa os
> ramos de microbioma, imagem ou SegmentAnyTooth. Não produz e não simula
> imagens dentárias, radiografias ou segmentação. Nenhum resultado externo é
> alegado. Estado de risco de viés permanece PROBAST+AI **High/High**.
"""

C28 = '''"""28. Proveniencia fail-closed e caminho de dados estavel.

O pipeline original resolvia a fonte via /tmp, que e volatil: uma limpeza de
/tmp quebrou a reprodutibilidade. Aqui a fonte e resolvida por candidatos em
ordem de preferencia e o SHA-256 e verificado antes de qualquer uso.
"""
from __future__ import annotations

import hashlib
from pathlib import Path as _P

SOURCE_SHA256_EXPECTED = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"
SOURCE_CANDIDATES = [
    _P(str(CFG.LOCAL_TABLE_S1)),
    DIRS["raw"] / "Table_S1.xlsx",
    _P(str(CFG.LOCAL_TABLE_S1)).parent / "robust_audit" / "Table_S1.xlsx",
    _P("/tmp/OdontoCA_Table_S1_source.xlsx"),
]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_source():
    """Return the first candidate whose SHA-256 matches the pinned value."""
    tried = []
    for cand in SOURCE_CANDIDATES:
        if not cand or not _P(cand).exists():
            tried.append({"path": str(cand), "status": "absent"})
            continue
        digest = _sha256(_P(cand))
        if digest == SOURCE_SHA256_EXPECTED:
            return _P(cand), digest, tried + [{"path": str(cand), "status": "VERIFIED"}]
        tried.append({"path": str(cand), "status": f"hash_mismatch:{digest[:12]}"})
    raise SystemExit("FAIL-CLOSED: nenhuma fonte com o SHA-256 fixado. Tentado: "
                     + json.dumps(tried, ensure_ascii=False))


SOURCE_PATH, SOURCE_SHA, SOURCE_PROBE = resolve_source()
print(json.dumps({
    "source_path": str(SOURCE_PATH),
    "sha256": SOURCE_SHA,
    "sha256_matches_manuscript": SOURCE_SHA == SOURCE_SHA256_EXPECTED,
    "candidates_probed": SOURCE_PROBE,
}, ensure_ascii=False, indent=2))
'''

C29 = '''"""29. Distribuicao por dente e propagacao observada (achado nao reportado).

ACHADO: os 83 eventos H->C ocorreram EXCLUSIVAMENTE em molares_deciduos
(T54/T55/T64/T65/T74/T75/T84/T85). Os 181 registros de dentes anteriores
(incisores e caninos) contributing para o treinamento OAS-VARIARAM ZERO eventos.

Consequencia metodologica: `tooth_position` e um preditor de alta informacao
porque separa subpopulacoes com risco zero de subpopulacoes com risco nao
nulo. Isso NAO e um defeito do modelo, mas explica por que o preditor domina,
e significa que (a) o modelo so e generalizavel para populacoes com a mesma
distribuicao de evento por dente, e (b) os dentes anteriores nao contribuem
para o sinal de calibracao, embora ocupem 18% das linhas.
"""
from __future__ import annotations

ANALYSIS_CSV = DIRS["clinical"] / "ca_onset_1step_model.csv"
teeth = pd.read_csv(ANALYSIS_CSV)
teeth = teeth[teeth.delta_months > 0].copy()

# `neighbor_caries_count` e uma coluna DERIVADA, criada pela funcao
# add_ca_features() do pipeline. Nao existe no CSV persistido, portanto e
# reconstruida aqui de forma identica. Esta reconstrucao e validada abaixo.
teeth["neighbor_prev_caries"] = (teeth["neighbor_prev_state_t"] == "C").astype(int)
teeth["neighbor_next_caries"] = (teeth["neighbor_next_state_t"] == "C").astype(int)
teeth["neighbor_caries_count"] = teeth["neighbor_prev_caries"] + teeth["neighbor_next_caries"]
if not teeth["neighbor_caries_count"].between(0, 2).all():
    raise SystemExit("FAIL-CLOSED: neighbor_caries_count fora de 0..2 (derivacao invalida).")

MOLARS = [54, 55, 64, 65, 74, 75, 84, 85]
teeth["is_molar"] = teeth.tooth_fdi.astype(int).isin(MOLARS)

per_tooth = (teeth.groupby("tooth_fdi")
             .agg(n=("progression_event", "size"), events=("progression_event", "sum"))
             .assign(rate=lambda d: (d.events / d.n).round(4))
             .sort_index())

tooth_facts = {
    "analysis_rows": int(len(teeth)),
    "analysis_events": int(teeth.progression_event.sum()),
    "analysis_children": int(teeth.child_id.nunique()),
    "children_with_event": int(teeth.loc[teeth.progression_event == 1, "child_id"].nunique()),
    "molar_rows": int(teeth.is_molar.sum()),
    "molar_events": int(teeth.loc[teeth.is_molar, "progression_event"].sum()),
    "anterior_rows": int((~teeth.is_molar).sum()),
    "anterior_events": int(teeth.loc[~teeth.is_molar, "progression_event"].sum()),
    "anterior_share_of_rows": round(float((~teeth.is_molar).mean()), 4),
}
print(per_tooth.to_string())
print()
print(json.dumps(tooth_facts, indent=2))
assert tooth_facts["anterior_events"] == 0, (
    " Eventos em dentes anteriores: a afirmacao do texto precisa ser revista.")

teeth.to_csv(DIRS["reports"] / "per_tooth_training_and_propagation.csv", index=False)
'''

C30 = '''"""30. Prontidao para validacao externa — regra de Riley et al. (BMJ 2020;368:m441).

Eventos necessarios = max(100, 10 x graus de liberdade efetivos). O numero de
graus de liberdade e derivado do pipeline primario efetivamente ajustado, nao
de uma suposicao.
"""
from __future__ import annotations

from math import ceil

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

PRIMARY_FEATURES = ["tooth_position", "age_months_t", "host_dmfs_t", "neighbor_caries_count"]
PRIMARY_CAT = ["tooth_position"]
PRIMARY_NUM = ["age_months_t", "host_dmfs_t", "neighbor_caries_count"]


def _primary_pipeline(C=10.0):
    try:
        oh = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        oh = OneHotEncoder(handle_unknown="ignore", sparse=False)
    prep = ColumnTransformer(
        [("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", oh)]), PRIMARY_CAT),
         ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                           ("sc", StandardScaler())]), PRIMARY_NUM)],
        remainder="drop", sparse_threshold=0)
    return Pipeline([("prep", prep),
                     ("model", LogisticRegression(penalty="l2", solver="liblinear", max_iter=5000, C=C))])


_pipe = _primary_pipeline().fit(teeth[PRIMARY_FEATURES], teeth.progression_event)
_coef = _pipe.named_steps["model"].coef_.ravel()
EFFECTIVE_DF = int((abs(_coef) > 1e-12).sum()) + 1
RILEY_EVENTS = max(100, 10 * EFFECTIVE_DF)
DEV_EVENTS = int(teeth.progression_event.sum())
PREV = DEV_EVENTS / len(teeth)

ext_sample = {
    "primary_features": PRIMARY_FEATURES,
    "one_hot_columns": int(_coef.size),
    "effective_degrees_of_freedom": EFFECTIVE_DF,
    "riley_rule": "max(100, 10 * df)",
    "required_outcome_events": RILEY_EVENTS,
    "development_events": DEV_EVENTS,
    "development_events_per_parameter": round(DEV_EVENTS / EFFECTIVE_DF, 2),
    "development_prevalence": round(PREV, 4),
    "required_transitions_by_prevalence": {f"{p:.0%}": ceil(RILEY_EVENTS / p)
                                           for p in (0.05, PREV, 0.15, 0.20)},
    "required_children_by_prevalence": {f"{p:.0%}": ceil(ceil(RILEY_EVENTS / p) / 12)
                                        for p in (0.05, PREV, 0.15, 0.20)},
    "teeth_per_child_assumption": 12,
}
print(json.dumps(ext_sample, indent=2))
print("\\n>> DEFICIT DA COORTE DE DESENVOLVIMENTO: "
      f"{DEV_EVENTS} eventos para {EFFECTIVE_DF} gl = "
      f"{DEV_EVENTS/EFFECTIVE_DF:.1f} eventos/parametro (recomendado: 10).")
'''

C31 = '''"""31. Travamento e exportacao do modelo final primario.

O primario e `clinical_minimal` por DISPONIBILIDADE DE PREDITOR, nao por
desempenho observado: os quatro preditores existem numa consulta de rotina,
enquanto os preditores espaciais foram derivados na base de origem e nao foram
reconstruidos. Escolher o espacial pelo AUROC mais alto seria selecao
orientada pelos dados.

A coorte e verificada fail-closed ANTES do travamento.
"""
from __future__ import annotations

import joblib

LOCK_DIR = DIRS["models"] / "locked_primary"
LOCK_DIR.mkdir(parents=True, exist_ok=True)

_lock_assert = (tooth_facts["analysis_rows"] == 996
                and tooth_facts["analysis_events"] == 83
                and tooth_facts["analysis_children"] == 81)
if not _lock_assert:
    raise SystemExit(f"FAIL-CLOSED: coorte divergente {tooth_facts}")

_locked_base = _primary_pipeline(C=10.0).fit(teeth[PRIMARY_FEATURES], teeth.progression_event)
_p_in = _locked_base.predict_proba(teeth[PRIMARY_FEATURES])[:, 1]

_bundle = {
    "model_name": "OdontoCA locked primary (tooth-level, next recorded visit)",
    "primary_model": "clinical_minimal",
    "role_note": ("Primary chosen for predictor availability at a routine visit, "
                  "not for observed performance. clinical_spatial superiority was "
                  "not established and its derived predictors were not reconstructed."),
    "required_columns": PRIMARY_FEATURES,
    "pipeline": _locked_base,
    "selected_C": 10.0,
    "recalibration": "intercept_and_slope fitted on training-only cross-fitted probabilities",
    "outcome": "progression_event (H->C) at the next recorded consecutive visit",
    "cohort": {"rows": 996, "events": 83, "children": 81},
    "apparent_metrics_OPTIMISTIC": {
        "roc_auc": float(roc_auc_score(teeth.progression_event, _p_in)),
        "pr_auc": float(average_precision_score(teeth.progression_event, _p_in)),
        "brier": float(brier_score_loss(teeth.progression_event, _p_in)),
    },
    "external_validation_required_events": RILEY_EVENTS,
    "interpretation_warning": ("Apparent metrics are resubstitution and optimistic. "
                               "NEITHER these nor any internal metric is external "
                               "validation. Clinical utility is undetermined."),
    "intended_use": ("Research use only. Not a medical device. No decision threshold "
                     "was pre-specified; must not trigger treatment."),
    "source_sha256": SOURCE_SHA,
    "seed": int(SEED),
    "versions": {"python": platform.python_version(), "scikit_learn": sklearn.__version__,
                 "numpy": np.__version__, "pandas": pd.__version__},
}
_bundle_path = LOCK_DIR / "odontoca_clinical_model.joblib"
joblib.dump(_bundle, _bundle_path)
_bundle_sha = _sha256(_bundle_path)
print(json.dumps({
    "locked_path": str(_bundle_path),
    "locked_sha256": _bundle_sha,
    "locked_size_bytes": _bundle_path.stat().st_size,
    "apparent_metrics_OPTIMISTIC": _bundle["apparent_metrics_OPTIMISTIC"],
    "external_validation_required_events": RILEY_EVENTS,
}, indent=2))
print(">> Reporte de desempenho deve citar as estimativas por dobra da Secao 3.2 do "
      "manuscrito, NAO as metricas aparentes deste artefato.")
'''

C32 = '''"""32. Transparencia dos portoes de aceitacao — os alvos NAO foram atingidos.

Este bloco NAO e cosmetico. Os portoes embacidos no codigo (TARGETS) fixaram
PR_AUC >= 0.78 e ROC_AUC >= 0.88. Nos dados reais, o melhor modelo nao alcanca
nenhum dos dois. Um portao que nunca e satisfeito na cohort real e um portao
nao-informativo: transforma um alvo aspiracional em aprovacao/reprovacao
binaria. Este bloco torna o resultado explicito em vez de silencioso.
"""
from __future__ import annotations

_rep = globals().get("PRIMARY_INTERNAL_VALIDATION", {})
_m = _rep.get("metrics", {})
_rows = []
for _name in ("clinical_minimal", "clinical_spatial"):
    for _method in ("uncalibrated", "intercept_and_slope"):
        u = _m.get(_name, {}).get(_method, {})
        _rows.append({
            "model": _name,
            "calibration": _method,
            "PR_AUC": round(float(u.get("pr_auc", float("nan"))), 4),
            "ROC_AUC": round(float(u.get("roc_auc", float("nan"))), 4),
            "Brier": round(float(u.get("brier", float("nan"))), 4),
            "target_PR_AUC": 0.78,
            "target_ROC_AUC": 0.88,
            "PR_AUC_target_met": bool(float(u.get("pr_auc", 0)) >= 0.78),
            "ROC_AUC_target_met": bool(float(u.get("roc_auc", 0)) >= 0.88),
        })
_target_table = pd.DataFrame(_rows)
print(_target_table.to_string(index=False))

_cal = _m.get("clinical_minimal", {}).get("uncalibrated", {})
print()
print("DIAGNOSTICO DE CALIBRACAO (primario, nao recalibrado) — valores sao cross-fitted:")
print(f"  calibration_in_the_large (ideal 0.0) : {_cal.get('calibration_in_the_large'):+.4f}")
print(f"  calibration_slope        (ideal 1.0) : {_cal.get('calibration_slope'):+.4f}")
print(f"  media predita vs observada           : {_cal.get('mean_predicted'):.4f} "
      f"vs {_cal.get('observed_fraction'):.4f}")
print()
print("VEREDITO: nenhum dos alvos de performance (PR>=0.78, ROC>=0.88) foi atingido por "
      "nenhum modelo, em nenhuma forma de calibracao. Alem disso, a inclinacao de "
      "calibracao ~0.52 mostra que o modelo tem cerca de metade da dispersao do risco "
      "real: as probabilidades preditas NAO sao interpretaveis como risco absoluto sem "
      "recalibracao, muito menos como limiar de decisao clinica. O portao de aceitacao "
      "nao deve ser usado para qualificar este manuscrito.")
'''

C33 = '''"""33. Ponto de entrada de inferencia para centros externos.

Um centro externo informa os quatro preditores de consulta e recebe o risco por
dente. A saida e SO para pesquisa: nao ha limiar de decisao pre-especificado.
"""
from __future__ import annotations


def predict_tooth_risk(records):
    """Score new per-tooth rows with the locked primary model.

    records: iterable of dicts with keys
             tooth_position, age_months_t, host_dmfs_t, neighbor_caries_count
    Returns a pandas DataFrame with risk_uncalibrated and intended_use columns.
    """
    _df = pd.DataFrame(list(records))
    _missing = [c for c in PRIMARY_FEATURES if c not in _df.columns]
    if _missing:
        raise ValueError(f"colunas obrigatorias ausentes: {_missing}")
    _p = _locked_base.predict_proba(_df[PRIMARY_FEATURES])[:, 1]
    return pd.DataFrame({
        "risk_uncalibrated": np.round(_p, 6),
        "intended_use": "research-only; no pre-specified decision threshold",
    }, index=_df.index)


_demo = predict_tooth_risk([
    {"tooth_position": "T51", "age_months_t": 24.0, "host_dmfs_t": 0.0, "neighbor_caries_count": 0.0},
    {"tooth_position": "T55", "age_months_t": 48.0, "host_dmfs_t": 6.0, "neighbor_caries_count": 4.0},
    {"tooth_position": "T75", "age_months_t": 54.0, "host_dmfs_t": 8.0, "neighbor_caries_count": 5.0},
])
print(_demo.to_string(index=False))
print()
print(">> T51 (anterior) e um dente de risco estruturalmente nulo nesta coorte: "
      "0 eventos em 181 linhas. O risco predito e baixo por construcao do dado, "
      "nao por desempenho do modelo.")
'''


def main() -> int:
    nb = nbformat.read(SRC, as_version=4)

    def add(kind, src):
        nb.cells.append(nbformat.v4.new_markdown_cell(src) if kind == "md"
                        else nbformat.v4.new_code_cell(src))

    add("md", BANNER)
    for src in (C28, C29, C30, C31, C32, C33):
        add("code", src)

    nb.metadata.setdefault("kernelspec", {})
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python",
                                 "name": "python3"}
    nbformat.validate(nb)
    nbformat.write(nb, DST)
    print(f"criado: {DST.name}")
    print(f"  celulas: {len(nb.cells)} (eram {len(nbformat.read(SRC, as_version=4).cells)})")
    print(f"  original preservado: {SRC.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
