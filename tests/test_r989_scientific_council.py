"""Contratos R989; executores usados aqui são fixtures, não LLMs."""
import importlib
import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
IDS = ["scientist-" + name for name in (
    "problem", "search", "curation", "references", "methodology", "statistics",
    "qualitative", "reproduction", "feynman", "falsification", "game-theory",
    "ethics", "audit",
)]
SOURCES = [{"id": "source-1", "text": "Resultado observado: 12 amostras.",
            "provenance": "fixture sintética para teste de software"}]


def council():
    assert importlib.util.find_spec("scientific_lab.council"), "Conselho R989 ausente"
    return importlib.import_module("scientific_lab.council")


def report():
    return {"status": "completed", "findings": ["Descrição da fixture."],
            "evidence": [{"source_id": "source-1", "quote": "12 amostras"}],
            "limitations": ["Fixture, não estudo."],
            "feynman": {"mechanism": "Explicação do procedimento.",
                        "observations": ["Há 12 amostras no texto."],
                        "inferences": ["Não inferimos causalidade."],
                        "test_oracle": "Conferir a contagem.",
                        "min_experiment": "Recontar as amostras."}}


class FakePrimary:
    def agent_profile_action(self, config):
        return {"registered": True, "definition_validated": True}

    def create_text_task_spec(self, **kwargs):
        return {"success": True, "spec_id": "TSPEC-fixture"}


class FakeCoordinator:
    def __init__(self, result=None):
        self.orchestrator = FakePrimary()
        self.calls = []
        self.result = result

    def run(self, task, required_capabilities, **kwargs):
        self.calls.append((task, required_capabilities, kwargs))
        if self.result is not None:
            return self.result
        aid = IDS[len(self.calls) - 1]
        output = json.dumps(report())
        return {"status": "completed", "success": True, "agent_id": aid,
                "task_id": "fixture-task", "steps": 1, "output": output,
                "attempts": [{"success": True, "output": output}], "ecosystem": "fixture"}


def test_thirteen_distinct_roles_and_readonly_profile_contract():
    mod = council()
    documents = mod.profile_documents()
    assert [d["agent_id"] for d in documents] == IDS
    assert len({d["capabilities"][0] for d in documents}) == 13
    for doc in documents:
        assert doc["allow_edit"] is False
        assert doc["spec_file"] == "specs/SPEC-935-R989-conselho-cientifico.md"
        assert doc["test_file"] == "tests/test_r989_scientific_council.py"
        assert "Feynman" in doc["prompt"] and "refut" in doc["prompt"]
        assert "não" in doc["prompt"]


def test_real_profiles_managed_and_configured():
    from agents.lifecycle import AgentLifecycleService
    config = json.loads((ROOT / "opencode.json").read_text())
    for aid in IDS:
        assert (ROOT / f"agents/catalog/{aid}.md").is_file(), aid
        state = AgentLifecycleService(ROOT).validate(aid)
        assert state["definition_validated"]
        meta = state["profile"]
        assert meta["parent"] == "marceloclaro"
        assert meta["permission"]["edit"] == meta["permission"]["webfetch"] == "deny"
        assert meta["permission"]["task"] == "deny"
        assert aid in config["agent"]


def test_plan_is_not_execution_or_clinical_authority():
    result = council().plan("Como testar esta hipótese?")
    assert len(result["roles"]) == 13 and result["executed"] is False
    assert result["external_validation"] is False
    assert result["human_review_required"] is True
    assert result["game_theory"]["scope"] == "prioritize_investigation_not_truth"


@pytest.mark.parametrize("question", ["", "   ", None, 12, "a" * 4001])
def test_plan_rejects_invalid_question(question):
    with pytest.raises(ValueError):
        council().plan(question)


def test_minimax_regret_hand_calculation_and_ties():
    result = council().minimax_regret({"h1": {"a": 10, "b": 6}, "h2": {"a": 0, "b": 6}})
    assert result["max_regrets"] == {"a": 6, "b": 4}
    assert result["recommended_actions"] == ["b"]
    tie = council().minimax_regret({"h1": {"a": 1, "b": 1}})
    assert tie["recommended_actions"] == ["a", "b"]


@pytest.mark.parametrize("matrix", [{}, {"h": {}}, {"h1": {"a": 1}, "h2": {"b": 2}},
    {"h": {"a": True}}, {"h": {"a": math.nan}}, {"h": {"a": math.inf}}])
def test_minimax_rejects_invalid_or_hidden_values(matrix):
    with pytest.raises(ValueError):
        council().minimax_regret(matrix)


def test_run_requires_confirmation_before_coordinator():
    coordinator = FakeCoordinator()
    result = council().run_council("Pergunta", SOURCES, coordinator=coordinator)
    assert result["status"] == "blocked" and not coordinator.calls


def test_bounded_run_with_fixture_does_not_promote_scientific_authority():
    coordinator = FakeCoordinator()
    result = council().run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator)
    assert len(coordinator.calls) == 13
    assert result["status"] == "completed_review" and len(result["reports"]) == 13
    assert result["external_validation"] is False and result["confidence_promoted"] is False
    assert result["human_review_required"] is True
    assert all(call[2]["max_steps"] == 1 and 0 < call[2]["timeout"] <= 120 for call in coordinator.calls)
    assert "DADOS NÃO CONFIÁVEIS" in coordinator.calls[-1][0]


def test_queued_is_not_execution_and_stops():
    coordinator = FakeCoordinator({"status": "queued", "success": True, "steps": 0})
    result = council().run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator)
    assert result["status"] == "blocked" and result["reports"] == []
    assert result["executed"] is False and len(coordinator.calls) == 1


def test_partial_report_is_collected_without_stopping(monkeypatch):
    # Um parecer "partial" é entrega válida; o ciclo segue para os demais papéis.
    mod = council()
    monkeypatch.setattr(mod, "validate_report",
                        lambda r, s: {"status": "partial", "findings": ["f"], "evidence": [],
                                      "limitations": ["l"], "feynman": {"mechanism": "m", "observations": ["o"],
                                      "inferences": ["i"], "test_oracle": "t", "min_experiment": "e"},
                                      "feynman_checklist": {}, "evidence_scope": "x", "human_validation": False})
    coordinator = FakeCoordinator()
    result = mod.run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator, max_agents=3)
    assert len(coordinator.calls) == 3 and result["status"] == "partial"
    assert all(rep["report"]["status"] == "partial" for rep in result["reports"])


def test_bad_citation_or_missing_feynman_is_rejected():
    bad = report()
    bad["evidence"][0]["quote"] = "resultado inexistente"
    with pytest.raises(ValueError):
        council().validate_report(bad, SOURCES)
    bad = report()
    del bad["feynman"]
    with pytest.raises(ValueError):
        council().validate_report(bad, SOURCES)


def test_decode_json_strips_markdown_fence():
    raw = '```json\n{"status": "partial", "findings": ["f"], "evidence": [], "limitations": ["l"], "feynman": {"mechanism": "m", "observations": ["o"], "inferences": ["i"], "test_oracle": "t", "min_experiment": "e"}}\n```'
    assert council().decode_json(raw)["status"] == "partial"


def test_validate_report_accepts_object_findings_and_normalizes():
    r = report()
    r["findings"] = [{"step": "pergunta", "description": "Delimitar o problema"}]
    validated = council().validate_report(r, SOURCES)
    assert isinstance(validated["findings"][0], str)
    assert "Delimitar" in validated["findings"][0]


def test_max_agents_limit_is_partial_not_completed():
    coordinator = FakeCoordinator()
    result = council().run_council("Pergunta", SOURCES, confirm=True, max_agents=2, coordinator=coordinator)
    assert len(coordinator.calls) == 2 and result["status"] == "partial"


def test_validation_cannot_accept_report_after_deadline(monkeypatch):
    mod = council()
    clock = [0.0]
    monkeypatch.setattr(mod.time, "monotonic", lambda: clock[0])
    validate = mod.validate_report
    def delayed(report, sources):
        result = validate(report, sources)
        clock[0] = 1000.0
        return result
    monkeypatch.setattr(mod, "validate_report", delayed)
    coordinator = FakeCoordinator()
    result = mod.run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator)
    assert result.get("reason") == "deadline_after_validation"
    assert result["reports"] == [] and len(coordinator.calls) == 1


def test_foreign_agent_and_source_duplication_fail_closed():
    output = json.dumps(report())
    coordinator = FakeCoordinator({"status": "completed", "success": True, "steps": 1,
        "agent_id": "foreign-agent", "output": output, "attempts": [{"success": True, "output": output}]})
    result = council().run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator)
    assert result["status"] == "blocked" and result["reports"] == []
    with pytest.raises(ValueError):
        council().run_council("Pergunta", SOURCES + SOURCES, confirm=True, coordinator=coordinator)


@pytest.mark.parametrize("options", [{"max_agents": 14}, {"max_agents": True}, {"timeout": math.nan}, {"timeout": 601}])
def test_invalid_budgets_rejected_before_calls(options):
    coordinator = FakeCoordinator()
    with pytest.raises(ValueError):
        council().run_council("Pergunta", SOURCES, confirm=True, coordinator=coordinator, **options)
    assert not coordinator.calls


def test_cli_plan_is_available_without_external_dispatch(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli
    assert "council" in cli.HELP, "Conselho não exposto pela fachada"
    def forbidden(*args, **kwargs):
        pytest.fail("Fallback externo acionado")
    monkeypatch.setattr(cli, "dispatch", forbidden)
    assert cli.main(["council", "plan", "--question", "Pergunta"]) == 0
    assert len(json.loads(capsys.readouterr().out)["roles"]) == 13
