import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations import chatgpt_tunnel_full_mcp as mod  # noqa: E402


SPEC = ROOT / "specs/SPEC-935-R1218-tunnel-mcp-completo.md"


def test_spec_r1218_existe():
    assert SPEC.is_file()
    text = SPEC.read_text(encoding="utf-8")
    assert "SPEC-935-R1218" in text
    assert "integrations.ecosystem_mcp" in text
    assert "não alterar" in text or "Não alterar" in text


def test_constantes_sao_fechadas():
    assert mod.TUNNEL_ID == "tunnel_6af9e26d203c8191ab67eb7e9aa3d805"
    assert mod.MCP_MODULE == "integrations.ecosystem_mcp_tunnel"
    assert mod.BUNDLE_SHA256 == "fa53182b766aeaceb652d86aee291c48daf7b90b5d73586dba370f4c1801325e"
    assert mod.STATE_DIR.name == "opencode-core-tunnel-full"
    assert mod.KEY_FILE.name == "runtime.key"


def test_comando_mcp_aponta_modulo_completo():
    argv = mod.build_mcp_command(ROOT)
    assert str(ROOT / ".venv/bin/python") in argv
    assert "-B" in argv
    assert "-m" in argv
    assert mod.MCP_MODULE in argv
    assert "chatgpt_status_mcp" not in " ".join(argv)


def test_argv_tunel_usa_referencia_de_chave_e_sem_log_bruto(tmp_path):
    binary = tmp_path / "tunnel-client-runtime"
    key = tmp_path / "runtime.key"
    argv = mod.build_tunnel_argv(
        binary=binary,
        state_dir=tmp_path,
        key_file=key,
        mcp_command=mod.build_mcp_command(ROOT),
    )
    joined = " ".join(argv)
    assert f"--control-plane.tunnel-id={mod.TUNNEL_ID}" in joined
    assert f"--control-plane.api-key=file:{key}" in joined
    assert "--control-plane.base-url=https://api.openai.com" in joined
    assert "--mcp.oauth-discovery=disabled" in joined
    assert "--log.http-raw-unsafe=false" in joined
    assert "--tracing.enabled=false" in joined
    assert "--health.listen-addr=127.0.0.1:0" in joined
    assert "integrations.ecosystem_mcp" in joined
    assert "chatgpt_status_mcp" not in joined


def test_validate_private_file_rejeita_modo_permissivo(tmp_path):
    key = tmp_path / "runtime.key"
    key.write_text("x", encoding="utf-8")
    key.chmod(0o644)
    with pytest.raises(mod.UserError):
        mod.validate_private_file(key)


def test_validate_private_file_aceita_modo_600(tmp_path):
    key = tmp_path / "runtime.key"
    key.write_text("x", encoding="utf-8")
    key.chmod(0o600)
    assert mod.validate_private_file(key) == key


def test_extract_runtime_rejeita_hash_divergente(tmp_path):
    bundle = tmp_path / "bundle.zip"
    payload = b"fake-runtime"
    with ZipFile(bundle, "w") as zf:
        zf.writestr("tunnel-client-runtime", payload)
    with pytest.raises(mod.UserError):
        mod.extract_runtime(bundle, tmp_path / "state", "0" * 64)


def test_extract_runtime_valida_hash_e_modo(tmp_path):
    bundle = tmp_path / "bundle.zip"
    payload = b"fake-runtime"
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest() if bundle.exists() else None
    with ZipFile(bundle, "w") as zf:
        zf.writestr("tunnel-client-runtime", payload)
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    state = tmp_path / "state"
    binary = mod.extract_runtime(bundle, state, digest)
    assert binary.is_file()
    assert binary.read_bytes() == payload
    assert os.stat(binary).st_mode & 0o777 == 0o700
    assert os.stat(state).st_mode & 0o777 == 0o700


def test_status_sem_pid_retorna_parado(tmp_path):
    result = mod.status(tmp_path)
    assert result["tunel"] == "parado"
    assert result["mcp"] == "integrations.ecosystem_mcp_tunnel"


def test_status_aceita_observed_at_do_v0_0_21(tmp_path, monkeypatch):
    (tmp_path / "tunnel.pid").write_text(f"{os.getpid()}\n", encoding="ascii")
    (tmp_path / "health-url").write_text("http://127.0.0.1:36135", encoding="ascii")
    observed = datetime.now(timezone.utc).isoformat()
    monkeypatch.setattr(mod, "_alive", lambda _pid: True)

    def fake_fetch(_base, path, *, json_body=False, require_success=False):
        if path == "/readyz":
            return 200
        return {"details": {"observed_at": observed, "consecutive_failures": 0}}

    monkeypatch.setattr(mod, "_fetch", fake_fetch)
    result = mod.status(tmp_path)
    assert result["tunel"] == "polling_confirmado"
    assert result["ultimo_poll_utc"] == observed


def test_stop_recusa_pid_desconhecido(tmp_path, monkeypatch):
    pid_file = tmp_path / "tunnel.pid"
    pid_file.write_text("999999\n", encoding="ascii")
    proc = tmp_path / "999999"
    proc.mkdir()
    monkeypatch.setattr(mod, "_proc_cmdline", lambda _pid: [b"/bin/sleep", b"999"])
    with pytest.raises(mod.UserError):
        mod.stop(tmp_path)


def test_start_sem_confirm_falha_fechado(tmp_path, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("start sem confirm não deve iniciar processo")

    monkeypatch.setattr(mod.subprocess, "Popen", explode)
    code = mod.main(["start", "--state-dir", str(tmp_path)])
    assert code == 2


def test_plan_nao_inicia_processo(tmp_path, monkeypatch, capsys):
    def explode(*_args, **_kwargs):
        raise AssertionError("plan não deve iniciar processo")

    monkeypatch.setattr(mod.subprocess, "Popen", explode)
    code = mod.main([
        "plan",
        "--state-dir", str(tmp_path),
        "--core-dir", str(ROOT),
        "--key-file", str(tmp_path / "runtime.key"),
    ])
    out = capsys.readouterr().out
    assert code == 0
    assert "integrations.ecosystem_mcp" in out
    assert "chatgpt_status_mcp" not in out
