"""Reexecute the locked analysis, compare aggregates, and export vector plots."""
import contextlib
import io
import json
from pathlib import Path
import matplotlib.figure
import calibrated_clinical_prediction as analysis

HERE=Path(__file__).resolve().parent
OUT=HERE/'final_build'/'analysis_rerun'
OUT.mkdir(parents=True,exist_ok=True)
expected=json.loads((HERE/'calibrated_clinical_internal_validation_corrected_sklearn190.json').read_text())
save=matplotlib.figure.Figure.savefig
def save_vectors(fig, fname, *args, **kwargs):
    save(fig, fname, *args, **kwargs)
    if str(fname).endswith('.png'):
        save(fig, Path(fname).with_suffix('.pdf'), bbox_inches='tight')
        save(fig, Path(fname).with_suffix('.svg'), bbox_inches='tight')
matplotlib.figure.Figure.savefig=save_vectors
analysis.OUT=OUT
with contextlib.redirect_stdout(io.StringIO()):
    actual=analysis.run()
keys=['source','analysis_rows','analysis_events','analysis_children','event_children','event_fraction','seed','outer_folds','inner_folds','split_policy','fold_log','metrics','prevalence_reference','calibration_minus_uncalibrated','bootstrap_valid']
checks={key: actual[key]==expected[key] for key in keys}
report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'runtime':actual['runtime'], 'source_sha256':actual['source'], 'scope':'Reexecution of the same internally validated analysis; not independent clinical validation.'}
(HERE/'final_analytical_gate.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
assert all(checks.values()),checks
print('FINAL_ANALYTICAL_GATE_PASS:',len(checks),'aggregate comparisons; all results exactly reproduced')
