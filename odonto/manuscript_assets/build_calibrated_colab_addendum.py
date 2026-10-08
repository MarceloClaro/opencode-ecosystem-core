"""Build the portable corrected-split and nested-calibration Colab cell."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parent
SCRIPT = ASSETS / "calibrated_clinical_prediction.py"
NOTEBOOK = ROOT / "OdontoCA_v1_3_4_CALIBRACAO_AGRUPADA.ipynb"
BASE_NOTEBOOK = ROOT / "OdontoCA_v1_3_3_CLINICAL_INTERNAL_VALIDATION.ipynb"


def portable_code() -> str:
    code = SCRIPT.read_text(encoding="utf-8")
    code = code.replace("import platform\n", "import platform\nimport sys\n")
    code = code.replace(
        "from real_clinical_prediction import (\n    BOOTSTRAPS,\n    FEATURE_SETS,\n    FORBIDDEN,\n    SEED,\n    build_pipeline,\n    interval,\n    source_frame,\n)\nfrom reproduce_evidence import fit_calibration\n",
        "# Cohort reconstruction and base-model functions are supplied by the preceding cell.\n",
    )
    code = code.replace('OUT = Path(__file__).resolve().parent\n', 'OUT = Path("/content/OdontoCA_v1_3/10_calibracao" if "google.colab" in sys.modules else "/tmp/odonto_colab_calibrated")\nOUT.mkdir(parents=True, exist_ok=True)\n')
    code = code.replace('    if sklearn.__version__ not in ("1.6.1", "1.9.0"):\n        raise RuntimeError("This version sensitivity requires scikit-learn 1.6.1 or 1.9.0")\n', '')
    code = code.replace("def run() -> dict:\n", "def run_calibrated() -> dict:\n")
    code = code.replace('if __name__ == "__main__":\n    run()\n', 'run_calibrated()\n')
    compile(code, "<OdontoCA calibration cell>", "exec")
    return code


def main() -> None:
    code = portable_code()
    markdown = '''# 29. Recalibração aninhada por criança — análise corrigida

**Correção da validação:** o resultado anterior (AP 0,2318/0,2414) é reproduzível no scikit-learn 1.6.1, porém `StratifiedGroupKFold(shuffle=True)` dessa versão pode desalinha[r] as contagens de classe e os grupos. A célula abaixo reproduz a lógica corrigida da divisão em qualquer uma das versões testadas, por permutação explícita de rótulos de grupo seguida de `shuffle=False`. Com essa divisão corrigida, os resultados-base são AP 0,1665/0,1784 e ROC-AUC 0,6865/0,7372 para os modelos mínimo/espacial. A mudança nos números decorre da divisão das crianças, sem representar piora ou melhora biológica.

**Calibração sem vazamento:** em cada uma das cinco dobras externas, o C é escolhido nas três dobras internas. As previsões cruzadas internas treinam dois mapas de risco: intercepto apenas e intercepto mais inclinação. Eles são aplicados somente ao teste externo. O ajuste do mapa não usa os rótulos das crianças do teste externo. Os intervalos das diferenças vêm de bootstrap pareado por criança das previsões externas já ajustadas.

| Modelo | Probabilidade | AP | ROC-AUC | Brier | Log-loss |
|---|---|---:|---:|---:|---:|
| Clínico mínimo | Original corrigido | 0,1665 | 0,6865 | 0,08060 | 0,28836 |
| Clínico mínimo | Intercepto + inclinação | 0,1920 | 0,7153 | 0,07451 | 0,26802 |
| Clínico espacial | Original corrigido | 0,1784 | 0,7372 | 0,07536 | 0,26899 |
| Clínico espacial | Intercepto + inclinação | Ver saída executada | Ver saída executada | Ver saída executada | Ver saída executada |

No modelo mínimo, a diferença de Brier (recalibrado − original) foi −0,00610, IC95% bootstrap por criança [−0,01173; −0,000672]. A melhora dos demais desfechos e do modelo espacial requer cautela; não há validação externa nem evidência de utilidade clínica. Esta é uma análise exploratória posterior à avaliação original. A saída contém somente métricas agregadas e figuras, em `/content/OdontoCA_v1_3/10_calibracao`.
'''
    # Avoid publishing a placeholder for the spatial result: fill from verified report.
    report = json.loads((ASSETS / "calibrated_clinical_internal_validation_corrected_sklearn190.json").read_text(encoding="utf-8"))
    spatial = report["metrics"]["clinical_spatial"]["intercept_and_slope"]
    markdown = markdown.replace("desalinha[r]", "desalinhar")
    markdown = markdown.replace(
        "| Clínico espacial | Intercepto + inclinação | Ver saída executada | Ver saída executada | Ver saída executada | Ver saída executada |",
        f"| Clínico espacial | Intercepto + inclinação | {spatial['pr_auc']:.4f} | {spatial['roc_auc']:.4f} | {spatial['brier']:.5f} | {spatial['log_loss']:.5f} |".replace(".", ","),
    )
    (ASSETS / "colab_calibrated_addendum.py").write_text(code, encoding="utf-8")
    (ASSETS / "colab_calibrated_addendum.md").write_text(markdown, encoding="utf-8")
    (ASSETS / "colab_calibrated_transfer.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"></head><body><pre id="markdown">'
        + escape(markdown) + '</pre><pre id="code">' + escape(code) + '</pre></body></html>',
        encoding="utf-8",
    )
    notebook = json.loads(BASE_NOTEBOOK.read_text(encoding="utf-8"))
    notebook["cells"].append({"cell_type": "markdown", "id": "clinical-v134-calibration-method", "metadata": {}, "source": markdown.splitlines(keepends=True)})
    notebook["cells"].append({"cell_type": "code", "id": "clinical-v134-calibration-code", "execution_count": None, "metadata": {}, "outputs": [], "source": code.splitlines(keepends=True)})
    NOTEBOOK.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {NOTEBOOK} with {len(notebook['cells'])} cells")


if __name__ == "__main__":
    main()
