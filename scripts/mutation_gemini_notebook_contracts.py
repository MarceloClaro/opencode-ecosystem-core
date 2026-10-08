"""Mutantes direcionados R674 em memória; não altera fontes do workspace."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    source_path = ROOT / "integrations/gemini_notebook.py"
    source = source_path.read_text(encoding="utf-8")
    mutants = [
        ("confirmation_removed", 'if effect != "read" and config.get("confirm") is not True:', 'if False:', "confirm"),
        ("unknown_arguments_accepted", 'schema["additionalProperties"] = False', 'schema["additionalProperties"] = True', "schema"),
        ("business_failure_promoted", 'payload.get("success") is False or payload.get("ok") is False', 'False', "business"),
    ]
    receipts = []
    with tempfile.TemporaryDirectory(prefix="notebook-mutation-") as directory:
        for name, old, new, contract in mutants:
            if source.count(old) != 1:
                raise RuntimeError("Mutação não é unívoca: " + name)
            mutated = source.replace(old, new, 1)
            scope = {"__name__": "_notebook_contract_mutant", "__file__": str(source_path)}
            exec(compile(mutated, str(source_path), "exec"), scope)
            service = scope["GeminiNotebookService"](directory, transport=object())
            killed = False
            try:
                if contract == "confirm":
                    result = service._gate("write", {})
                    assert result and result["status"] == "blocked"
                elif contract == "schema":
                    try:
                        service._validate_schema({"invented": True}, {"type": "object", "properties": {}})
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("Campo desconhecido aceito")
                else:
                    report = {"status": "completed", "transport_success": True,
                              "result": {"structuredContent": {"success": False}}}
                    assert service._normalize_result(report)["status"] == "failed"
            except AssertionError:
                killed = True
            receipts.append({"mutant": name, "killed": killed,
                             "mutant_sha256": hashlib.sha256(mutated.encode()).hexdigest()})
    result = {"scope": "three_targeted_in_memory_contract_mutants", "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "mutants": receipts, "passed": all(item["killed"] for item in receipts)}
    path = ROOT / "docs/evidence/R674_MUTATION.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
