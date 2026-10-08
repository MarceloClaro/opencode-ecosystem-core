"""Gate direcionado a contratos alterados e regressões relevantes."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
prefixes = ("test_r640_", "test_r644_", "test_r233_", "test_r116_", "test_r547_",
            "test_r548_", "test_r473_", "test_r110_", "test_r621_", "test_r618_",
            "test_r622_", "test_r608_", "test_r212_")
extra = {"test_ecosystem.py", "test_catalog_loader.py", "test_opencode_cli.py", "test_runai.py"}
files = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "tests").glob("test_*.py")
               if path.name.startswith(prefixes) or path.name in extra)
log_path = ROOT / ".backups/r644/release-gate.log"
with log_path.open("w", encoding="utf-8") as log:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", *files],
                            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
text = log_path.read_text(encoding="utf-8")
summary = {"returncode": result.returncode, "test_files": files, "summary": text[-7000:]}
(ROOT / ".backups/r644/release-gate.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
raise SystemExit(result.returncode)
