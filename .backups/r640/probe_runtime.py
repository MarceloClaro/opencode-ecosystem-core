"""Verificação real explícita e limitada; não é teste unitário."""
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from integrations.harness_runtime import HarnessRuntime

runtime = HarnessRuntime()
prompt = "Responda somente REDE_R640_EXECUCAO_REAL. Não use ferramentas nem leia ou altere arquivos."

def probe(ecosystem):
    result = runtime.execute(ecosystem, prompt, timeout=45)
    return {"executor": ecosystem, **result}

with ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(probe, ("claude", "antigravity", "codex")))
report = {"kind": "real_cli_probe", "results": results}
print(json.dumps(report, ensure_ascii=False, indent=2))
with open(".backups/r640/runtime-probe.json", "w", encoding="utf-8") as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
