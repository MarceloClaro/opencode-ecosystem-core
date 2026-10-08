"""Prepare a portable clinical-validation addendum for the OdontoCA notebook."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "manuscript_assets"
ORIGINAL = ROOT / "OdontoCA_v1_3_2_FULL_RESEARCH_COM_IMAGEM_FLUXOGRAMA_EXECUTED (3).ipynb"
SCRIPT = ASSETS / "real_clinical_prediction.py"
ADDENDUM = ASSETS / "colab_clinical_addendum.py"
NOTEBOOK = ROOT / "OdontoCA_v1_3_3_CLINICAL_INTERNAL_VALIDATION.ipynb"


def code() -> str:
    source = SCRIPT.read_text(encoding="utf-8")
    source = source.replace('from tempfile import gettempdir\n', 'from io import BytesIO\nimport sys\nimport requests\n')
    source = source.replace('matplotlib.use("Agg")\n', '')
    source = source.replace('from reproduce_evidence import NOTEBOOK, SOURCE_COMMIT, SOURCE_SHA256, fit_calibration\n', '''from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit

SOURCE_COMMIT = "e5868fe5664460c7aac1c5b6d7980776ad26b29c"
SOURCE_URL = (
    "https://raw.githubusercontent.com/HuangShiLab/Single-tooth-ECC/"
    + SOURCE_COMMIT + "/Figures_and_Tables_in_Manuscript/Table_S1.xlsx"
)
SOURCE_SHA256 = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"


def fit_calibration(y, p):
    score = logit(np.clip(p, 1e-6, 1 - 1e-6))
    offset = minimize_scalar(
        lambda intercept: log_loss(y, expit(intercept + score), normalize=False),
        method="bounded", bounds=(-12, 12),
    )
    line = minimize(
        lambda coef: log_loss(y, expit(coef[0] + coef[1] * score), normalize=False),
        x0=np.array([0.0, 1.0]), method="BFGS",
    )
    if not np.isfinite(line.x).all():
        raise AssertionError("Nonfinite calibration coefficients")
    return {
        "mean_predicted": float(p.mean()),
        "observed_fraction": float(y.mean()),
        "calibration_in_the_large": float(offset.x),
        "calibration_slope": float(line.x[1]),
        "calibration_model_intercept": float(line.x[0]),
    }
''')
    source = source.replace('OUT = Path(__file__).resolve().parent\nRAW = Path(gettempdir()) / "OdontoCA_Table_S1_source.xlsx"\n', '''OUT = Path(
    "/content/OdontoCA_v1_3/09_clinical_addendum"
    if "google.colab" in sys.modules else "/tmp/odonto_colab_addendum"
)
OUT.mkdir(parents=True, exist_ok=True)
''')
    begin = source.index('def source_frame()')
    finish = source.index('\n\ndef build_pipeline', begin)
    source = source[:begin] + '''def source_frame() -> tuple[pd.DataFrame, dict]:
    if not all(name in globals() for name in ("clean_single_tooth", "build_transitions")):
        raise RuntimeError("Execute as células anteriores de reconstrução longitudinal primeiro")
    response = requests.get(SOURCE_URL, timeout=90)
    response.raise_for_status()
    content = response.content
    digest = hashlib.sha256(content).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError("O hash SHA-256 do suplemento clínico é diferente do auditado")
    meta = pd.read_excel(BytesIO(content), sheet_name="all_metadata")
    meta.columns = [str(col).strip() for col in meta.columns]
    _, _, clean = clean_single_tooth(meta)
    _, _, onset = build_transitions(clean)
    onset = onset.copy()
    onset["neighbor_caries_count"] = (
        onset["neighbor_prev_state_t"].eq("C").astype(int)
        + onset["neighbor_next_state_t"].eq("C").astype(int)
    )
    if len(onset) != 997 or int(onset["progression_event"].sum()) != 84:
        raise AssertionError("As contagens da coorte de origem não foram reproduzidas")
    zero_interval = onset.loc[onset["delta_months"].le(0)]
    frame = onset.loc[onset["delta_months"].gt(0)].reset_index(drop=True)
    if len(frame) != 996 or int(frame["progression_event"].sum()) != 83:
        raise AssertionError("A coorte analítica com seguimento positivo mudou")
    return frame, {
        "source_sha256": digest,
        "reproduced_eligible": 997,
        "reproduced_events": 84,
        "excluded_nonpositive_followup_interval": len(zero_interval),
        "excluded_events": int(zero_interval["progression_event"].sum()),
    }
''' + source[finish:]
    source = source.replace('"analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),\n', '')
    return source


def main() -> None:
    addendum_code = code()
    compile(addendum_code, str(ADDENDUM), "exec")
    ADDENDUM.write_text(addendum_code, encoding="utf-8")
    notebook = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    while notebook["cells"] and notebook["cells"][-1]["cell_type"] == "code" and not "".join(notebook["cells"][-1]["source"]).strip():
        notebook["cells"].pop()
    markdown = '''# 28. Adendo clínico v1.3.3 — validação interna exploratória

**Estado executado separadamente:** a análise abaixo foi executada sobre o suplemento clínico público Table S1, fixado no commit `e5868fe5` e verificado por SHA-256. Os resultados anteriores do perfil `CI_SMOKE` são sintéticos e não representam desempenho clínico.

**Coorte e alvo:** 997 transições H→H/H→C foram reconstruídas (84 eventos). Uma transição com intervalo de seguimento zero foi excluída: **996 transições, 83 eventos, 81 crianças**; seguimento de 2–5 meses. O alvo é incidência de cárie em um dente inicialmente hígido.

**Método:** dois modelos de regressão logística penalizada, mínimo clínico e clínico-espacial; cinco folds externos e três internos estratificados e agrupados por criança; seleção de regularização dentro do treino; 1.000 reamostragens bootstrap por criança das predições fora da amostra. A classe positiva é localizada explicitamente. Variáveis futuras, o desfecho e o intervalo de seguimento não entram como preditores.

| Modelo | AP | ROC-AUC | Brier | Inclinação de calibração |
|---|---:|---:|---:|---:|
| Clínico mínimo | 0,166 | 0,686 | 0,0806 | 0,516 |
| Clínico-espacial | 0,178 | 0,737 | 0,0754 | 0,605 |

A diferença de AP foi 0,012, com intervalo bootstrap de 95% de −0,046 a 0,058. Portanto, a vantagem do modelo espacial **não está estabelecida**. A calibração ainda precisa melhorar. Não houve validação externa, microbioma real pareado nem imagem clínica pareada. Nenhum resultado autoriza uso assistencial.

**Fluxo atualizado:** Table S1 pública → verificação de versão/hash → reconstrução dente-visita → exclusão de intervalo não positivo → atributos disponíveis em t → CV aninhada agrupada por criança → predições fora da amostra → discriminação, calibração e bootstrap → validação externa prospectiva antes de qualquer avaliação de uso clínico.

A célula seguinte reproduz a análise depois de executar as células anteriores de reconstrução longitudinal. Salva somente estatísticas agregadas e figuras em `/content/OdontoCA_v1_3/09_clinical_addendum`; não exporta registros individuais.
'''
    (ASSETS / "colab_clinical_addendum.md").write_text(markdown, encoding="utf-8")
    (ASSETS / "colab_transfer.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"></head><body><pre id="markdown">'
        + escape(markdown)
        + '</pre><pre id="code">'
        + escape(addendum_code)
        + '</pre></body></html>',
        encoding="utf-8",
    )
    notebook["cells"].append({"cell_type": "markdown", "id": "clinical-v133-method", "metadata": {}, "source": markdown.splitlines(keepends=True)})
    notebook["cells"].append({"cell_type": "code", "id": "clinical-v133-code", "execution_count": None, "metadata": {}, "outputs": [], "source": addendum_code.splitlines(keepends=True)})
    NOTEBOOK.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {ADDENDUM} and {NOTEBOOK} ({len(notebook['cells'])} cells)")


if __name__ == "__main__":
    main()
