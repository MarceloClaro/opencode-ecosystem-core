"""Uma chamada real, metadados sanitizados e roteamento após observação."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from integrations.harness_runtime import HarnessRuntime
from marceloclaro.autonomous import AutonomousCoordinator

runtime = HarnessRuntime()
result = runtime.execute("claude", "Responda somente R644_HEALTH_OK, sem ferramentas nem alterações de arquivos.", timeout=30)
state = runtime.status()["executors"]["claude"]
route = AutonomousCoordinator(runtime=runtime).route("Revisar a integração do ecossistema")
verified = (result["success"] is False and state["available"] is True
            and state["eligible_for_auto"] is False and route["executor"] != "claude")
report = {"kind": "real_executor_health_probe", "verified_failure_cooldown_and_route": verified,
          "execution_success": result["success"], "execution_error": result.get("error"),
          "claude": state, "automatic_executor_after_observation": route.get("executor")}
(ROOT / ".backups/r644/health-probe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
