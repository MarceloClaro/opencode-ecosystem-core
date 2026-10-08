"""Reprodução R663: executa somente métodos internos copiados com o estudo."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
configuration = json.loads((root / "configuration.json").read_text(encoding="utf-8"))
dataset = root / "dataset.csv"
digest = hashlib.sha256(dataset.read_bytes()).hexdigest()
code_digest = hashlib.sha256((root / "statistical_methods.py").read_bytes()).hexdigest()
if digest != configuration["dataset_sha256"] or code_digest != configuration["methods_sha256"]:
    print(json.dumps({"status": "blocked", "error": "dataset_hash_mismatch" if digest != configuration["dataset_sha256"] else "methods_hash_mismatch"}))
    sys.exit(2)
try:
    from statistical_methods import execute_analysis
    result = execute_analysis(dataset, configuration["method"], configuration["variables"])
    print(json.dumps({"status": "completed", "dataset_sha256": digest, "analysis": result}, sort_keys=True, allow_nan=False))
except Exception as exc:
    print(json.dumps({"status": "blocked", "error_type": type(exc).__name__}))
    sys.exit(2)
