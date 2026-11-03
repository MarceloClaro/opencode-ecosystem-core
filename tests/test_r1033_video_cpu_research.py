"""Aceites documentais R1033: não validam qualidade de vídeo/voz."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports/r1033-video-cpu"


def dossier():
    return json.loads((BASE / "evidence.json").read_text())


def test_sources_have_saved_receipts_and_hashes():
    data = dossier()
    assert len(data["sources"]) >= 10
    for src in data["sources"]:
        assert src["url"].startswith("https://")
        assert src["retrieved_at"]
        file = (BASE / src["file"]).resolve()
        assert file.is_relative_to(BASE.resolve())
        assert hashlib.sha256(file.read_bytes()).hexdigest() == src["sha256"]


def test_candidate_limits_and_separate_licenses():
    candidates = dossier()["candidates"]
    assert len(candidates) >= 8
    for item in candidates:
        assert item["source_ids"]
        assert item["cpu_status"]
        assert item["code_license"]
        assert item["model_license"]
        assert item["benchmark_executed_this_round"] is False


def test_scope_and_playlist_uncertainties():
    data = dossier()
    for flag in ("installed", "downloaded_playlist_media", "cloned_new_voices", "rendered", "published"):
        assert data["actions"][flag] is False
    assert data["playlist"]["id"] == "PL2dcm-6042EC788TGxgH3qWF7MjpoJIv9"
    assert data["playlist"]["speaker_consent"] == "not_provided_for_playlist"
    assert data["local_inventory"]
    assert data["failures"]


def test_strategy_addresses_required_pipeline_and_human_gate():
    text = (BASE / "README.md").read_text().lower()
    for term in ("diarização", "sobrepostas", "pt-br", "srt", "vtt", "ass", "consentimento", "cpu", "música", "piloto", "revisão humana", "licença", "não executado"):
        assert term in text, term


def test_candidate_sources_exist_and_local_files_unchanged():
    data = dossier()
    ids = {s["id"] for s in data["sources"]}
    assert len(ids) == len(data["sources"])
    for item in data["candidates"]:
        assert set(item["source_ids"]) <= ids
    for item in data["local_inventory"]:
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]


def test_review_findings_are_reconciled_without_runtime_claims():
    data = dossier()
    assert data["review"]["independent_status"] == "textual_readonly_completed"
    assert data["review"]["quality_certified"] is False
    assert data["review"]["task_id"] == "task-1ed85850"
    assert "Argos Translate" in {item["name"] for item in data["candidates"]}
    text = (BASE / "README.md").read_text()
    assert "t3_pt_br.safetensors" in text
    assert "jonatasgrosman/wav2vec2-large-xlsr-53-portuguese" in text
    assert "compatibilidade ainda não demonstrada" in text
