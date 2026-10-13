"""R832/R834/R836: contratos tipados + casos negativos, separados do inventário.

Describe/plan/stages são descritivos: passar não comprova execução de agentes,
autenticação, conexão MCP ou cobertura funcional. Existência é inventário.
Cada resultado é cobrado por valor (is True/False, ==), sem agulhas em str(out).
"""
import importlib
import pathlib
import hashlib
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent


def test_agents_contratos_descritivos_e_plano():
    from agents import bernstein_orchestrator as b, antigravity_orchestrator as a
    from agents import reversa_agents as r, ws_agents as w, agent_catalog as c
    assert b.describe()["agent"] == "bernstein_orchestrator"
    assert b.delegate("")["approved"] is False
    assert b.delegate("tarefa")["approved"] is True
    assert b.delegate("revisar evidências")["task"] == "revisar evidências"
    assert a.describe()["capabilities"] == ["bridge", "delegate"]
    assert a.delegate("")["approved"] is False
    assert a.delegate("revisar evidências")["task"] == "revisar evidências"
    assert r.describe()["capabilities"] == ["scout", "analyze", "synthesize"]
    assert w.describe()["members"] == ["ws-coder", "ws-researcher", "ws-reviewer", "ws-scribe"]
    assert c.describe()["count_md"] == sum(1 for p in (REPO / "agents" / "catalog").iterdir() if p.name.endswith(".md"))


def test_mci_estritos():
    from mci import context_manager as cm, memory_updater as mu, orchestration_pipeline as op
    out = cm.budget("abc", max_chars=2)
    assert out["truncated"] is True and out["kept"] == "ab"
    assert cm.budget("ab", max_chars=5)["truncated"] is False
    m = mu.append("t", "e")
    assert m["topic"] == "t" and m["entry"] == "e"
    assert m["hash"] == hashlib.sha256(b"t:e").hexdigest()[:16]
    assert mu.append("t", "outra")["hash"] != m["hash"]
    o = op.order([{"id": "b", "deps": ["a"]}, {"id": "a", "deps": []}])
    assert o["order"] == ["a", "b"] and o["unresolved"] == []
    blocked = op.order([{"id": "b", "deps": ["a"]}, {"id": "a", "deps": ["b"]}])
    assert blocked["order"] == []
    assert blocked["unresolved"] == ["b", "a"]


def test_evolution_contratos_e_id_retido(monkeypatch):
    from evolution import cycles_manager as cm, reflection_ledger as rl
    from evolution import autoevolve_pipeline as ap, evolutionary_roadmap as er
    monkeypatch.setenv("EVOLUTION_STATE_PATH", str(REPO / "tests" / "fixtures" / "r836" / "ledger_sparse.json"))
    nxt = cm.next_id()
    assert nxt["next"] == "R42" and nxt["total"] == 5
    assert nxt["status"] == "ready"
    assert "R" not in nxt
    assert "next_id_compat" not in dir(cm) and "next_id_alias" not in dir(cm)
    before = time.time()
    reflection = rl.append("licao controlada")
    assert reflection["recorded"] is True and reflection["lesson"] == "licao controlada"
    assert before <= reflection["at"] <= time.time()
    assert ap.stages()["stages"] == ["SENSE", "DISCOVER", "INSTALL", "VERIFY", "EVOLVE", "LEARN"]
    assert er.plan()["foundations"] == ["trust", "reasoning"]
    assert er.plan()["quick_wins"] == ["docs"]


def test_protocolos_estritos():
    from protocolos import sdd_spec_first as s1, tdd_red_green_refactor as tdd
    from protocolos import a2a_blackboard as a2a, mcp_interconnect as mcp
    from protocolos import bernstein_orchestration as bo, sdd_gate as gate
    from protocolos import behavioral_gate as bg, reflexion_middleware as rm
    assert s1.check("SPEC-935-R832")["approved"] is True
    assert s1.check("")["approved"] is False
    assert s1.check(None)["approved"] is False
    assert tdd.check("abc", True)["approved"] is True
    assert tdd.check("", True)["approved"] is False
    assert tdd.check("abc", False)["approved"] is False
    assert tdd.check("abc", 1)["approved"] is False
    assert a2a.check("a", ["x"])["approved"] is True
    assert a2a.check("", [])["approved"] is False
    assert a2a.check("auditor", "review")["approved"] is False
    assert mcp.check("t", {})["approved"] is True
    assert mcp.check("", {})["approved"] is False
    assert mcp.check("status", [])["approved"] is False
    assert bo.check(["a", "b"])["order"] == ["a", "b"]
    assert gate.check("SPEC-935-R832", True)["approved"] is True
    assert gate.check("SPEC-935-R832", False)["approved"] is False
    assert gate.check("SPEC-935-R832", 1)["approved"] is False
    assert gate.check("", True)["approved"] is False
    assert bg.check("a", 0.9)["allowed"] is True
    assert bg.check("a", 0.1)["allowed"] is False
    assert rm.check("licao controlada")["recorded"] is True
    assert rm.check("licao controlada")["lesson"] == "licao controlada"


def test_integracoes_planos_descritivos():
    from integrations import antigravity_bridge as ab, cli_integrations as cli
    from integrations import pypi_searcher as pp, web_search as ws
    from integrations import mcp_servers as ms, git_manager as gm
    assert ab.plan()["bridge"] == "antigravity_bridge" and isinstance(ab.plan()["available"], bool)
    assert ab.plan("texto d'água")["argv"] == ["agy", "run", "texto d'água"]
    assert cli.plan("status")["argv"] == ["opencode", "status"]
    assert pp.plan(" pacote ")["query"] == "pacote"
    assert pp.plan(" pacote ")["argv"] == ["pip", "index", "versions", "pacote"]
    assert ws.plan("consulta sem rede")["query"] == "consulta sem rede"
    assert ms.plan("servidor-controlado")["server"] == "servidor-controlado"
    assert ms.plan()["protocol"] == "model context protocol"
    assert gm.plan("diff")["argv"] == ["git", "diff"]


@pytest.mark.parametrize("module, binary", [
    ("antigravity_bridge", "agy"),
    ("cli_integrations", "opencode"),
    ("git_manager", "git"),
])
@pytest.mark.parametrize("installed", [False, True])
def test_plano_distingue_instalacao_presente_e_ausente(module, binary, installed, monkeypatch):
    facade = importlib.import_module(f"integrations.{module}")

    def lookup(name):
        assert name == binary
        return f"/executables/{binary}" if installed else None

    monkeypatch.setattr(facade.shutil, "which", lookup)
    assert facade.plan()["available"] is installed


def test_infra_estritos():
    from infra_dados import schemas_validator as sv, data_pipeline as dp
    from infra_dados import batch_executor as be, assets_media as am, gametheory_models as gtm
    assert sv.validate({"a": 1}, ["a"])["valid"] is True
    assert sv.validate({}, ["a"])["valid"] is False
    assert sv.validate({"a": 1}, ["a", "b"])["missing"] == ["b"]
    normalized = dp.normalize([{"a": 1, "b": None}, "ignorar", {"a": 2}])
    assert normalized["count"] == 2
    assert normalized["rows"] == [{"a": 1}, {"a": 2}]
    assert dp.normalize([])["rows"] == []
    assert be.order(["b", "a"])["order"] == ["a", "b"]
    assert be.order([])["order"] == []
    manifest = am.manifest(["a.txt", "b.txt"])
    assert manifest["files"] == ["a.txt", "b.txt"]
    assert manifest["hash"] == hashlib.sha256(b"a.txt|b.txt").hexdigest()[:16]
    assert gtm.nash_2x2()["equilibria"] == [(0, 0), (1, 1)]
    assert gtm.nash_2x2([[(1, -1), (-1, 1)], [(-1, 1), (1, -1)]])["equilibria"] == []


def test_governanca_estritos():
    from governanca import cooperative_governance as cg, game_theory_analysis as gta
    from governanca import trust_scoring as ts, slashing_rules as sr, tokenomics as tk
    assert cg.quorum(7, 10)["quorum"] is True
    assert cg.quorum(3, 10)["quorum"] is False
    assert cg.quorum(6, 10)["quorum"] is True
    assert cg.quorum(5, 10)["quorum"] is False
    assert cg.quorum(0, 0)["quorum"] is False
    assert gta.nash_2x2()["equilibria"] == [(1, 1)]
    assert gta.nash_2x2([[(1, -1), (-1, 1)], [(-1, 1), (1, -1)]])["equilibria"] == []
    assert ts.score(8, 10)["score"] == 0.8
    assert ts.score(1, 10)["requires_supervision"] is True
    assert ts.score(3, 10)["requires_supervision"] is False
    assert ts.score(0, 0)["requires_supervision"] is True
    assert sr.rules()["tiers"] == {"51-100": "0%", "21-50": "5%", "1-20": "15%", "0": "30%"}
    assert tk.simulate(10, 4)["balance"] == 6.0
    assert tk.simulate(2, 4)["balance"] == -2.0
    assert tk.simulate(2, 4)["healthy"] is False


def test_z3_semantica_e_entrada_maliciosa():
    from reasoning.z3_solver import check
    assert check("x > 1", {"x": 2})["status"] == "sat"
    assert check("x > 1", {"x": 0})["status"] == "unsat"
    mal = check("__import__('os').system('x')", {})
    assert mal["status"] == "fallback" and mal["available"] is False


def test_reasoning_engines_reflete_input():
    from reasoning.reasoning_engines import route
    r1 = route("2+3")
    assert r1["engine"] == "sympy" and r1["result"] == "5"
    r2 = route("integrar sin(x)")
    assert r2["engine"] == "fallback" and r2["available"] is False
    assert r2.get("result") is None
    formal = route("integrate(sin(x), x)")
    assert formal["engine"] == "sympy" and formal["result"] == "-cos(x)"


def test_inventario_arquivos_existem_36_sem_contar_como_comportamento():
    rels = ["agents/bernstein_orchestrator.py", "agents/antigravity_orchestrator.py",
            "agents/reversa_agents.py", "agents/ws_agents.py", "agents/agent_catalog.py",
            "mci/context_manager.py", "mci/memory_updater.py", "mci/orchestration_pipeline.py",
            "evolution/cycles_manager.py", "evolution/reflection_ledger.py",
            "evolution/autoevolve_pipeline.py", "evolution/evolutionary_roadmap.py",
            "protocolos/sdd_spec_first.py", "protocolos/tdd_red_green_refactor.py",
            "protocolos/a2a_blackboard.py", "protocolos/mcp_interconnect.py",
            "protocolos/bernstein_orchestration.py", "protocolos/sdd_gate.py",
            "protocolos/behavioral_gate.py", "protocolos/reflexion_middleware.py",
            "integrations/antigravity_bridge.py", "integrations/cli_integrations.py",
            "integrations/pypi_searcher.py", "integrations/web_search.py",
            "integrations/mcp_servers.py", "integrations/git_manager.py",
            "infra_dados/schemas_validator.py", "infra_dados/data_pipeline.py",
            "infra_dados/batch_executor.py", "infra_dados/assets_media.py",
            "infra_dados/gametheory_models.py", "governanca/cooperative_governance.py",
            "governanca/game_theory_analysis.py", "governanca/trust_scoring.py",
            "governanca/slashing_rules.py", "governanca/tokenomics.py"]
    missing = [r for r in rels if not (REPO / r).is_file()]
    assert len(rels) == 36
    assert not missing, f"ausentes {missing}"


def test_r832_spec_existe():
    text = (REPO / "specs" / "SPEC-935-R832-restantes-36-realidade.md").read_text(encoding="utf-8")
    assert "SPEC-935-R832" in text
