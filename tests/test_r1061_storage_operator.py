"""R1061: storage-operator; usa arquivos temporários e rclone falso."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from integrations.storage_operator import approvals, drive, inventory, manifest, policy


def config(tmp_path: Path, root: Path | None = None) -> policy.StorageConfig:
    root = root or (tmp_path / "Downloads")
    root.mkdir(exist_ok=True)
    return policy.StorageConfig(
        allowed_roots=(str(root),),
        state_dir=str(tmp_path / "state"),
        drive_remote="gdrive",
        drive_parent="",
        max_file_bytes=10 * 1024 * 1024,
        bandwidth="8M",
        transfers=2,
        exclude_globs=(".env", "*.key", "*.pem", "id_rsa*", "*.kdbx", "*.pfx", "*.p12"),
    )


def test_root_outside_allowlist_denied(tmp_path):
    cfg = config(tmp_path)
    with pytest.raises(policy.StorageDenied):
        policy.validate_root(cfg, str(tmp_path / "outro"))


def test_traversal_and_absolute_path_denied(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    for rel in ("../fora.txt", "/etc/passwd", "a/../../fora.txt"):
        with pytest.raises(policy.StorageDenied):
            policy.validate_file(cfg, root, rel)


def test_symlink_denied(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    target = tmp_path / "fora.txt"
    target.write_text("x")
    link = root / "link.txt"
    link.symlink_to(target)
    with pytest.raises(policy.StorageDenied):
        policy.validate_file(cfg, root, "link.txt")


def test_secret_and_partial_classification(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / ".env").write_text("SECRET=1")
    (root / "doc.pdf").write_text("pdf")
    (root / "video.mp4.crdownload").write_text("partial")
    data = manifest.build_manifest(cfg, root, now=0)
    by_name = {f["relpath"]: f for f in data["files"]}
    assert by_name[".env"]["upload"] is False
    assert by_name[".env"]["reason"] == "excluded_secret"
    assert by_name["video.mp4.crdownload"]["upload"] is False
    assert by_name["video.mp4.crdownload"]["delete"] is True
    assert by_name["doc.pdf"]["upload"] is True


def test_manifest_hash_is_deterministic_and_changes(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / "a.txt").write_text("a")
    first = manifest.build_manifest(cfg, root, now=0)
    second = manifest.build_manifest(cfg, root, now=0)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    (root / "a.txt").write_text("changed")
    third = manifest.build_manifest(cfg, root, now=0)
    assert third["manifest_sha256"] != first["manifest_sha256"]


def test_manifest_write_and_load_detects_tamper(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / "a.txt").write_text("a")
    data = manifest.build_manifest(cfg, root, now=0)
    path = manifest.write_manifest(tmp_path / "m.json", data)
    loaded = manifest.load_manifest(path)
    assert loaded["manifest_sha256"] == data["manifest_sha256"]
    tampered = json.loads(path.read_text())
    tampered["files"][0]["size"] = 999
    path.write_text(json.dumps(tampered))
    with pytest.raises(manifest.ManifestError):
        manifest.load_manifest(path)


def test_remote_folder_name_has_date_time(tmp_path):
    cfg = config(tmp_path)
    folder = policy.remote_folder(Path(cfg.allowed_roots[0]), now=0)
    assert folder.startswith("Downloads_")
    assert len(folder.rsplit("_", 2)[-2:]) == 2
    assert policy.remote_path(cfg, folder) == f"gdrive:{folder}"


def test_scan_totals(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / "a.txt").write_text("12345")
    (root / "b.pdf").write_text("123")
    (root / "c.tmp").write_text("x")
    data = inventory.scan(cfg, root)
    assert data["totals"]["files"] == 3
    assert data["totals"]["bytes"] == 9
    assert data["candidates"]


def test_upload_approval_scope_and_manifest_binding(tmp_path):
    cfg = config(tmp_path)
    digest = "a" * 64
    issued = approvals.issue_approval(cfg, "upload", digest)
    payload = approvals.verify_approval(cfg, issued["token"], "upload", digest)
    assert payload["scope"] == "upload"
    with pytest.raises(approvals.ApprovalError):
        approvals.verify_approval(cfg, issued["token"], "purge", digest)


def test_approval_expiry_and_reuse(tmp_path):
    cfg = config(tmp_path)
    digest = "b" * 64
    issued = approvals.issue_approval(cfg, "upload", digest, ttl_seconds=1, now=1000)
    with pytest.raises(approvals.ApprovalError):
        approvals.verify_approval(cfg, issued["token"], "upload", digest, now=1002)
    issued2 = approvals.issue_approval(cfg, "upload", digest)
    approvals.verify_approval(cfg, issued2["token"], "upload", digest)
    with pytest.raises(approvals.ApprovalError):
        approvals.verify_approval(cfg, issued2["token"], "upload", digest)


def test_upload_requires_approval_and_uses_safe_argv(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / "a.txt").write_text("a")
    data = manifest.build_manifest(cfg, root, now=0)
    path = manifest.write_manifest(tmp_path / "m.json", data)
    calls = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return Result()

    monkeypatch.setattr(drive, "_run", fake_run)
    with pytest.raises(approvals.ApprovalError):
        drive.upload(cfg, path, "")
    issued = approvals.issue_approval(cfg, "upload", data["manifest_sha256"])
    result = drive.upload(cfg, path, issued["token"])
    assert result["ok"] is True
    argv = calls[-1][0]
    assert "--checksum" in argv
    assert "--delete" not in argv
    assert calls[-1][1].get("shell") is False


def test_purge_requires_verified_manifest_and_approval(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    victim = root / "a.txt"
    victim.write_text("a")
    keep = root / "b.txt"
    keep.write_text("b")
    data = manifest.build_manifest(cfg, root, now=0)
    data["files"] = [item for item in data["files"] if item["relpath"] == "a.txt"]
    data["totals"] = {"files": 1, "bytes": victim.stat().st_size}
    data["manifest_sha256"] = manifest.manifest_hash(data)
    path = manifest.write_manifest(tmp_path / "m.json", data)
    issued = approvals.issue_approval(cfg, "purge", data["manifest_sha256"])
    with pytest.raises(drive.PurgeError):
        drive.purge(cfg, path, issued["token"])
    data["verified"] = True
    data["verification"] = {"ok": True}
    data["manifest_sha256"] = manifest.manifest_hash(data)
    path.write_text(json.dumps(data))
    issued = approvals.issue_approval(cfg, "purge", data["manifest_sha256"])
    result = drive.purge(cfg, path, issued["token"])
    assert result["ok"] is True
    assert not victim.exists()
    assert keep.exists()


def test_purge_rejects_changed_file(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    victim = root / "a.txt"
    victim.write_text("original")
    data = manifest.build_manifest(cfg, root, now=0)
    path = manifest.write_manifest(tmp_path / "m.json", data)
    data["verified"] = True
    data["verification"] = {"ok": True}
    data["manifest_sha256"] = manifest.manifest_hash(data)
    path.write_text(json.dumps(data))
    issued = approvals.issue_approval(cfg, "purge", data["manifest_sha256"])
    victim.write_text("changed")
    with pytest.raises(drive.PurgeError):
        drive.purge(cfg, path, issued["token"])
    assert victim.exists()


def test_mcp_exposes_seven_tools_without_approval():
    from integrations.storage_operator.mcp_server import TOOL_NAMES

    assert TOOL_NAMES == {
        "storage_status", "storage_report", "storage_scan",
        "drive_plan", "drive_upload", "drive_verify", "storage_purge",
    }
    assert "approve" not in " ".join(TOOL_NAMES)


def test_manifest_skips_drive_temp_system_and_shortcuts(tmp_path):
    cfg = config(tmp_path)
    root = Path(cfg.allowed_roots[0])
    (root / ".tmp.driveupload").mkdir()
    (root / ".tmp.driveupload" / "123").write_text("temp")
    (root / "atalho.gdoc").write_text("pointer")
    (root / "desktop.ini").write_text("meta")
    (root / "real.pdf").write_text("pdf")
    data = manifest.build_manifest(cfg, root, now=0)
    by_name = {item["relpath"]: item for item in data["files"]}
    assert ".tmp.driveupload/123" not in by_name
    assert by_name["atalho.gdoc"]["upload"] is False
    assert by_name["atalho.gdoc"]["delete"] is False
    assert by_name["atalho.gdoc"]["reason"] == "drive_shortcut"
    assert by_name["desktop.ini"]["reason"] == "system_metadata"
    assert by_name["real.pdf"]["upload"] is True
