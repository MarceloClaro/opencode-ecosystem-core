import asyncio
import json
from types import SimpleNamespace

import pytest

from marceloclaro.runtime_actions import validate_action
from marceloclaro.science_cli import run_science_cli


@pytest.mark.parametrize("kind,config", [
    ("runtime", {"runtime":"hermes","prompt":"p","model":"m","output_dir":"/tmp/out","env":{"API_KEY":"x"}}),
    ("dataset", {"provider":"kaggle","dataset_id":"../bad","filenames":["Iris.csv"],"output_dir":"out"}),
    ("personalizar", {"source_manifests":[],"output_dir":"out"}),
    ("plugins", {"operation":"request","plugin_id":"wolfram","action":"anything","arguments":{}}),
    ("plugins", {"operation":"local","plugin_id":"boltz-api-cli","action":"run_shell","arguments":{}}),
])
def test_invalid_configuration_rejected_before_effects(kind, config):
    with pytest.raises(ValueError):
        validate_action(kind, config)


@pytest.mark.parametrize("kind,method,config", [
    ("runtime","scientific_runtime_run",{"runtime":"hermes","prompt":"p","model":"m","output_dir":"/tmp/out"}),
    ("dataset","scientific_dataset_download",{"provider":"kaggle","dataset_id":"uciml/iris","filenames":["Iris.csv"],"output_dir":"out","revision":"1"}),
    ("personalizar","scientific_dataset_custom",{"source_manifests":["one.json"],"output_dir":"out"}),
    ("plugins","scientific_plugin_action",{"operation":"status"}),
])
def test_cli_delegates_to_same_central_method(tmp_path, capsys, kind, method, config):
    path=tmp_path/"config.json"
    path.write_text(json.dumps(config))
    calls=[]
    orchestrator=SimpleNamespace(**{method:lambda **kw: calls.append(kw) or {"status":"completed"}})
    assert run_science_cli([kind,"--config",str(path)],orchestrator=orchestrator)==0
    assert calls
    assert json.loads(capsys.readouterr().out)["status"]=="completed"


@pytest.mark.parametrize("tool",["ecosystem_scientific_runtime","ecosystem_dataset_download","ecosystem_dataset_custom","ecosystem_scientific_plugins"])
def test_new_mcp_tools_reject_invalid_input_before_orchestrator(monkeypatch,tool):
    import integrations.ecosystem_mcp as module
    monkeypatch.setattr(module,"get_library_orchestrator",lambda:pytest.fail("efeito antes da validação"))
    with pytest.raises(ValueError):
        asyncio.run(getattr(module,tool)({"unexpected":True}))


def test_central_runtime_records_observation_without_promoting_confidence(monkeypatch):
    import integrations.live_scientific_runtime as runtime
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    fake_report={"status":"completed","runtime":"hermes","external_process_executed":True,"inference_executed":True,"model_calls":1,"artifacts":{}}
    monkeypatch.setattr(runtime.LiveScientificRuntime,"run",lambda self,cfg:dict(fake_report))
    orchestrator=object.__new__(MarceloClaroOrchestrator)
    receipts=[]
    monkeypatch.setattr(orchestrator,"_record_knowledge_outcome",lambda *args:receipts.append(args) or {"persisted":True})
    report=orchestrator.scientific_runtime_run(runtime="hermes",prompt="p",model="m",output_dir="/tmp/out")
    assert report["metacognition"]["confidence_promoted"] is False
    assert receipts[0][2]["inference_executed"] is True
    assert receipts[0][2]["externally_validated"] is False
