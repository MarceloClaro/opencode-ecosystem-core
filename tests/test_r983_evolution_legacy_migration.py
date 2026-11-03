"""SPEC-983: migração explícita com proveniência integral e backup byte-a-byte."""
from __future__ import annotations

import hashlib
import json

import pytest

from evolution.cycles import EvolutionRegistry


def _write(path, cycles, **extensions):
    document = {"schema_extension": {"owner": "operator", "version": 9},
                **extensions, "cycles": cycles}
    raw = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def test_preview_is_read_only_and_reports_migration_reasons(tmp_path):
    path = tmp_path / "cycles.json"
    raw = _write(path, [
        {"round_id": "R7", "objective": "good", "changes": ["kept"]},
        {"round_id": "R8", "objective": "legacy nested", "changes": {
            "id": "old-8", "score": 8.5, "timestamp": "2026-10-20T10:00:00+00:00",
            "changes": ["one", "two"]}},
        {"id": "R9", "titulo": "formato antigo", "spec": "SPEC-old"},
        "not-a-cycle-object",
    ])
    registry = EvolutionRegistry(path)

    preview = registry.preview_legacy_migration()

    assert path.read_bytes() == raw
    assert preview["modelled_count"] == 1
    assert preview["unmodelled_count"] == 3
    assert preview["migratable_count"] == 2
    assert preview["unmigratable_count"] == 1
    assert preview["entries"][0]["source_index"] == 1
    assert "changes_not_list" in preview["entries"][0]["reason_codes"]
    assert preview["entries"][1]["source_index"] == 2
    assert "legacy_identity_mapped" in preview["entries"][1]["reason_codes"]
    assert preview["entries"][2]["reason_codes"] == ["entry_not_object"]


def test_migration_preserves_original_payload_backup_order_and_extensions(tmp_path):
    path = tmp_path / "cycles.json"
    good = {"round_id": "R1", "objective": "valid", "changes": ["keep"],
            "extension": {"opaque": [1, 2]}}
    legacy_nested = {"round_id": "R2", "objective": "nested wrapper", "changes": {
        "id": "evo-old", "spec": "SPEC-old", "title": "title retained",
        "score": 8.5, "timestamp": "2026-10-20T10:00:00+00:00",
        "changes": ["first", {"detail": "second"}]}}
    legacy_old = {"id": "R3", "titulo": "Registro antigo", "spec": "SPEC-legacy"}
    before = _write(path, [good, legacy_nested, legacy_old])
    backup = tmp_path / "cycles.json.before-r983"
    registry = EvolutionRegistry(path)

    receipt = registry.migrate_legacy_entries(backup_path=backup)

    assert receipt["status"] == "migrated"
    assert receipt["migrated_count"] == 2
    assert receipt["remaining_unmodelled_count"] == 0
    assert backup.read_bytes() == before
    assert receipt["backup_sha256"] == hashlib.sha256(before).hexdigest()
    migrated_document = json.loads(path.read_text(encoding="utf-8"))
    assert migrated_document["schema_extension"] == {"owner": "operator", "version": 9}
    rows = migrated_document["cycles"]
    assert len(rows) == 3
    assert rows[0] == good
    migrations = {item["source_index"]: item for item in migrated_document["legacy_migrations"]}
    assert migrations[1]["migration_id"] == "R983-v1"
    assert migrations[1]["source_sha256"]
    backup_doc = json.loads(backup.read_text(encoding="utf-8"))
    assert backup_doc["cycles"][1] == legacy_nested
    assert migrations[1]["backup_sha256"] == receipt["backup_sha256"]
    assert (path.parent / migrations[1]["backup_path"]).read_bytes() == before
    assert rows[1]["changes"] == ["first", '{"detail":"second"}']
    assert rows[1]["score"] == 8.5
    assert rows[1]["timestamp"] == pytest.approx(1792490400.0)
    assert not ({"legacy_original", "legacy_migration"} & set(rows[1]))
    assert rows[2]["round_id"] == "R3"
    assert rows[2]["objective"] == "Registro antigo"
    assert backup_doc["cycles"][2] == legacy_old

    reloaded = EvolutionRegistry(path)
    assert len(reloaded.cycles) == 3
    assert reloaded.preview_legacy_migration()["migratable_count"] == 0
    assert reloaded.migrate_legacy_entries(backup_path=backup)["status"] == "already_migrated"
    after_second_call = json.loads(path.read_text(encoding="utf-8"))
    assert after_second_call == migrated_document
    reloaded.record("new cycle after migration", ["later"], round_id="R4")
    after_new_cycle = json.loads(path.read_text(encoding="utf-8"))
    assert after_new_cycle["legacy_migrations"] == migrated_document["legacy_migrations"]
    assert after_new_cycle["cycles"][-1]["round_id"] == "R4"


def test_synthetic_identity_is_deterministic_and_does_not_collide(tmp_path):
    path = tmp_path / "cycles.json"
    good = {"round_id": "R5", "objective": "existing", "changes": []}
    malformed = {"round_id": "R5", "objective": "legacy duplicate", "changes": {"changes": ["x"]}}
    _write(path, [good, malformed])
    registry = EvolutionRegistry(path)

    receipt = registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")
    rows = json.loads(path.read_text())["cycles"]
    migrations = json.loads(path.read_text())["legacy_migrations"]

    assert receipt["migrated_count"] == 1
    assert rows[1]["round_id"].startswith("legacy-entry-1-")
    assert "synthetic_identity" in migrations[0]["reason_codes"]
    assert json.loads((tmp_path / migrations[0]["backup_path"]).read_text())["cycles"][1] == malformed


def test_invalid_score_is_not_guessed_and_original_is_retained(tmp_path):
    path = tmp_path / "cycles.json"
    malformed = {"round_id": "R20", "objective": "old format", "changes": {"changes": ["x"]},
                 "score": "9.5", "timestamp": "not-a-date"}
    _write(path, [malformed])
    registry = EvolutionRegistry(path)

    registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")

    result = json.loads(path.read_text())
    row = result["cycles"][0]
    assert row["score"] is None
    assert row["timestamp"] == 0.0
    original = json.loads((tmp_path / result["legacy_migrations"][0]["backup_path"]).read_text())["cycles"][0]
    assert original == malformed
    assert "score_invalid" in result["legacy_migrations"][0]["reason_codes"]
    assert "timestamp_invalid" in result["legacy_migrations"][0]["reason_codes"]


def test_non_object_entries_remain_intact_and_keep_doctor_warning(tmp_path, monkeypatch):
    path = tmp_path / "cycles.json"
    legacy = {"round_id": "R2", "objective": "legacy", "changes": {"changes": ["migrated"]}}
    source = _write(path, ["opaque", legacy])
    registry = EvolutionRegistry(path)

    receipt = registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")

    rows = json.loads(path.read_text())["cycles"]
    assert rows[0] == "opaque"
    migrated = json.loads(path.read_text())["legacy_migrations"]
    assert json.loads((tmp_path / migrated[0]["backup_path"]).read_text())["cycles"][1] == legacy
    assert receipt["remaining_unmodelled_count"] == 1
    assert path.exists()
    assert registry._raw_document["cycles"][0] == "opaque"

    from marceloclaro import doctor as doctor_module
    monkeypatch.setattr(doctor_module, "REPO_ROOT", str(tmp_path))
    (tmp_path / "evolution").mkdir(exist_ok=True)
    (tmp_path / "evolution" / "cycles.json").write_bytes(path.read_bytes())
    check = doctor_module._check_evolution_registry()
    assert check.status == "warn"
    assert "não modelada" in check.detail
    assert source != path.read_bytes()  # the dictionary entry migrated, opaque row did not


def test_conflicting_backup_refuses_before_changing_source_or_memory(tmp_path):
    path = tmp_path / "cycles.json"
    before = _write(path, [{"round_id": "R30", "objective": "legacy", "changes": {"changes": ["x"]}}])
    registry = EvolutionRegistry(path)
    backup = tmp_path / "before.json"
    backup.write_bytes(b"different backup")

    with pytest.raises(FileExistsError):
        registry.migrate_legacy_entries(backup_path=backup)

    assert path.read_bytes() == before
    assert len(registry.cycles) == 0


def test_migrated_registry_is_fully_modelled_by_doctor(tmp_path, monkeypatch):
    path = tmp_path / "cycles.json"
    _write(path, [
        {"round_id": "R60", "objective": "valid", "changes": []},
        {"round_id": "R61", "objective": "legacy", "changes": {"changes": ["old"]}},
    ])
    registry = EvolutionRegistry(path)
    result = registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")
    assert result["remaining_unmodelled_count"] == 0

    evolution_dir = tmp_path / "evolution"
    evolution_dir.mkdir()
    isolated_state = evolution_dir / "cycles.json"
    isolated_state.write_bytes(path.read_bytes())
    from marceloclaro import doctor as doctor_module
    monkeypatch.setattr(doctor_module, "REPO_ROOT", str(tmp_path))

    check = doctor_module._check_evolution_registry()

    assert check.status == "pass"
    assert "2/2 ciclos carregados" in check.detail


def test_migration_preserves_declared_audit_chain_links(tmp_path):
    path = tmp_path / "cycles.json"
    first = {"round_id": "R70", "objective": "anchor one", "changes": [],
             "state_merkle_root": "a" * 64, "prev_state_merkle_root": ""}
    second = {"round_id": "R71", "objective": "anchor two", "changes": [],
              "state_merkle_root": "b" * 64, "prev_state_merkle_root": "a" * 64}
    legacy = {"round_id": "R72", "objective": "old", "changes": {"changes": ["x"]}}
    _write(path, [first, second, legacy])
    registry = EvolutionRegistry(path)
    assert registry.verify_state_chain()["ok"] is True

    registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")

    reloaded = EvolutionRegistry(path)
    chain = reloaded.verify_state_chain()
    assert chain["ok"] is True
    assert chain["anchored"] == 2


def test_concurrent_change_blocks_migration_and_preserves_current_bytes(tmp_path):
    path = tmp_path / "cycles.json"
    before = _write(path, [{"round_id": "R40", "objective": "legacy", "changes": {"changes": ["x"]}}])
    registry = EvolutionRegistry(path)
    path.write_bytes(before + b" ")
    current = path.read_bytes()

    with pytest.raises(RuntimeError, match="mudou concorrentemente"):
        registry.migrate_legacy_entries(backup_path=tmp_path / "before.json")

    assert path.read_bytes() == current
    assert registry.cycles == []


def test_cli_defaults_to_read_only_preview(tmp_path, monkeypatch, capsys):
    from scripts import migrate_evolution_legacy as command

    path = tmp_path / "cycles.json"
    raw = _write(path, [{"round_id": "R50", "objective": "legacy", "changes": {"changes": ["x"]}}])
    backup = tmp_path / "before.json"
    monkeypatch.setattr(command, "DEFAULT_STATE", path)
    monkeypatch.setattr(command, "DEFAULT_BACKUP", backup)

    assert command.main([]) == 0

    report = json.loads(capsys.readouterr().out)
    assert report["writes_performed"] is False
    assert report["migratable_count"] == 1
    assert path.read_bytes() == raw
    assert not backup.exists()
