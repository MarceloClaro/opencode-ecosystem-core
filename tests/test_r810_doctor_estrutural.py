"""R810: doctor estrutural não executa sondagens operacionais implícitas."""

from types import SimpleNamespace
import json
import subprocess
import urllib.request

import pytest


def test_default_doctor_does_not_execute_network_processes_or_examples(monkeypatch):
    from marceloclaro import doctor
    from integrations.deepmind import (
        AutoFormalizerEngine, EqualitySaturationEngine, Lean4ProofVerifier,
        OpenCodeAlphaGeometry, OpenCodeAlphaProof,
    )
    from integrations.medical import ClinicalInvestigationPipeline

    effects = []

    def forbidden(kind):
        def block(*args, **kwargs):
            effects.append(kind)
            raise RuntimeError("sondagem operacional bloqueada pelo teste")
        return block

    monkeypatch.setattr(subprocess, "run", forbidden("subprocess"))
    monkeypatch.setattr(urllib.request, "urlopen", forbidden("http"))
    for owner, method in ((Lean4ProofVerifier, "verify_lean_code"),
                          (EqualitySaturationEngine, "saturate"),
                          (OpenCodeAlphaProof, "search_proof"),
                          (OpenCodeAlphaGeometry, "solve"),
                          (AutoFormalizerEngine, "informal_to_lean4"),
                          (ClinicalInvestigationPipeline, "investigate")):
        monkeypatch.setattr(owner, method, forbidden(method))

    report = doctor.run_doctor()

    assert effects == []
    assert report["diagnostic_mode"] == "structural"
    assert report["verification"] == "installation_only"
    assert "rea" in {check["name"] for check in report["checks"]}


def test_live_lean_check_executes_an_explicit_probe(monkeypatch):
    from marceloclaro import doctor
    from integrations.deepmind import Lean4ProofVerifier

    probes = []

    def verify(self, code):
        probes.append(code)
        return SimpleNamespace(status="controlled_probe")

    monkeypatch.setattr(Lean4ProofVerifier, "verify_lean_code", verify)

    result = doctor._check_lean4_egraph_engine(live=True)

    assert len(probes) == 1
    assert "theorem sample_th" in probes[0]
    assert result.status == "pass"
    assert "controlled_probe" in result.detail


@pytest.mark.parametrize("include_commit", [False, True])
def test_rea_git_commit_collection_is_explicit(tmp_path, monkeypatch, include_commit):
    from integrations.rea_bridge import ReaBridge

    (tmp_path / ".git").mkdir()
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "rea-agents", "version": "6.4.0"}), encoding="utf-8")
    monkeypatch.setattr(ReaBridge, "_source_dir", staticmethod(lambda: tmp_path))
    monkeypatch.setattr(ReaBridge, "_resolve_node", staticmethod(lambda: None))
    monkeypatch.setattr("integrations.rea_bridge.shutil.which", lambda name: "/tools/git")
    git_calls = []

    def git_run(*args, **kwargs):
        git_calls.append(True)
        return SimpleNamespace(returncode=0, stdout="a" * 40)

    monkeypatch.setattr(subprocess, "run", git_run)
    bridge = ReaBridge()

    report = bridge.status() if include_commit else bridge.status(include_commit=False)

    assert len(git_calls) == int(include_commit)
    assert report["provenance"]["commit"] == ("a" * 40 if include_commit else None)


@pytest.mark.parametrize("arguments,live", [([], False), (["--live"], True)])
def test_cli_doctor_selects_structural_or_explicit_live_mode(monkeypatch, capsys,
                                                          arguments, live):
    from marceloclaro import cli, doctor

    modes = []

    def run_doctor(*, live=False):
        modes.append(live)
        return {"overall": "degraded", "diagnostic_mode": "live" if live else "structural"}

    monkeypatch.setattr(doctor, "run_doctor", run_doctor)
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "doctor", *arguments])

    assert cli.main() == 0
    assert modes == [live]


def test_cli_doctor_rejects_unknown_options_before_checks(monkeypatch):
    from marceloclaro import cli, doctor

    monkeypatch.setattr(doctor, "run_doctor", lambda **kwargs: pytest.fail("checks não autorizados"))
    monkeypatch.setattr(cli.sys, "argv", ["marceloclaro", "doctor", "--unknown"])

    with pytest.raises(SystemExit):
        cli.main()
