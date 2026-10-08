"""R672: jobs herméticos persistem entre processos clientes separados."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import stat
import socket
import subprocess
import sys
import time

import pytest

from integrations.gemini_notebook_transport import GeminiNotebookTransport
from integrations.gemini_notebook_session import _configuration, _private_directory
from tests.test_r672_gemini_notebook_transport import SERVER


@pytest.fixture
def transport(tmp_path, monkeypatch):
    program = tmp_path/".venv/bin/notebooklm-mcp"
    program.parent.mkdir(parents=True)
    program.write_text("#!"+sys.executable+"\n"+SERVER)
    program.chmod(0o755)
    log = tmp_path/"protocol.log"
    monkeypatch.setenv("R672_PROTOCOL_LOG",str(log))
    return GeminiNotebookTransport(tmp_path),log


def test_two_transport_instances_share_server_memory(transport):
    first, log = transport
    first = GeminiNotebookTransport(first.repo_root, persistent=True)
    second = GeminiNotebookTransport(first.repo_root, persistent=True)
    try:
        started = asyncio.run(first.call_mcp("notebook_query_start", {"query":"hermetic answer"}))
        assert started["status"] == "pending"
        queried = asyncio.run(second.call_mcp("notebook_query_status", {"query_id":"job-1"}))
        assert queried["status"] == "completed"
        assert queried["result"]["structuredContent"]["answer"] == "hermetic answer"
        assert log.read_text().splitlines().count("initialize") == 1
    finally:
        asyncio.run(first.close_persistent())


def test_different_python_processes_share_server_memory(transport):
    client, log = transport
    root = Path(__file__).resolve().parents[1]
    code = "import asyncio,json,sys; from integrations.gemini_notebook_transport import GeminiNotebookTransport; t=GeminiNotebookTransport(sys.argv[1],persistent=True); r=asyncio.run(t.call_mcp(sys.argv[2],json.loads(sys.argv[3]))); print(json.dumps(r))"
    try:
        started = subprocess.run([sys.executable,"-c",code,str(client.repo_root),"notebook_query_start",json.dumps({"query":"separate clients"})],capture_output=True,text=True,cwd=root,timeout=20)
        assert started.returncode == 0
        assert json.loads(started.stdout)["status"] == "pending"
        completed = subprocess.run([sys.executable,"-c",code,str(client.repo_root),"notebook_query_status",json.dumps({"query_id":"job-1"})],capture_output=True,text=True,cwd=root,timeout=20)
        assert completed.returncode == 0
        result = json.loads(completed.stdout)
        assert result["status"] == "completed"
        assert result["result"]["structuredContent"]["answer"] == "separate clients"
        assert log.read_text().splitlines().count("initialize") == 1
    finally:
        asyncio.run(GeminiNotebookTransport(client.repo_root,persistent=True).close_persistent())


def test_broker_socket_and_metadata_are_private(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    try:
        result = asyncio.run(client.discover_mcp())
        assert result["status"] == "completed"
        base = client.repo_root / ".opencode/notebooklm/broker"
        assert stat.S_IMODE(base.stat().st_mode) == 0o700
        sockets = list(base.glob("*.sock"))
        assert len(sockets) == 1
        assert stat.S_IMODE(sockets[0].stat().st_mode) == 0o600
        for file in base.glob("*.json"):
            assert stat.S_IMODE(file.stat().st_mode) == 0o600
            assert "env_hash" not in file.read_text()
    finally:
        asyncio.run(client.close_persistent())


def test_session_directory_symlink_is_never_followed(transport, tmp_path):
    client, _ = transport
    outside = tmp_path / "external"
    outside.mkdir()
    (client.repo_root/".opencode").mkdir()
    (client.repo_root/".opencode/notebooklm").symlink_to(outside,target_is_directory=True)
    result = asyncio.run(GeminiNotebookTransport(client.repo_root,persistent=True).discover_mcp())
    assert result["status"] == "blocked"
    assert list(outside.iterdir()) == []


def test_socket_symlink_is_never_deleted_or_followed(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    config = _configuration(client)
    base = _private_directory(client.repo_root)
    target = client.repo_root/"preserved.txt"
    target.write_text("preserve")
    link = base/(config["fingerprint"][:16]+".sock")
    link.symlink_to(target)
    result = asyncio.run(client.discover_mcp())
    assert result["status"] == "blocked"
    assert link.is_symlink()
    assert target.read_text() == "preserve"


def test_broker_idle_shutdown_resets_volatile_jobs(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True,_session_idle_seconds=0.2)
    try:
        result = asyncio.run(client.call_mcp("notebook_query_start", {"query":"ephemeral"}))
        assert result["status"] == "pending"
        base = client.repo_root/".opencode/notebooklm/broker"
        deadline = time.monotonic()+3
        while list(base.glob("*.sock")) and time.monotonic()<deadline:
            time.sleep(0.03)
        assert not list(base.glob("*.sock"))
        result = asyncio.run(client.call_mcp("notebook_query_status", {"query_id":"job-1"}))
        assert result["status"] == "lost"
        assert result["volatile_jobs_lost"] is True
    finally:
        asyncio.run(client.close_persistent())


def test_broker_rejects_credential_environment_overrides(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True,env_overrides={"GOOGLE_API_KEY":"private-value"})
    result = asyncio.run(client.discover_mcp())
    assert result["status"] == "blocked"
    assert not (client.repo_root/".opencode").exists()
    assert "private-value" not in json.dumps(result)


def test_config_profile_change_updates_fingerprint_without_reading_contents(transport, monkeypatch):
    client, _ = transport
    storage = client.repo_root/"official-storage"
    storage.mkdir()
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH",str(storage))
    config = storage/"config.toml"
    config.write_text("profile='one'")
    first = _configuration(client)["fingerprint"]
    config.write_text("profile='different-two'")
    original = Path.read_text
    def no_contents(self,*args,**kwargs):
        if self == config:
            raise AssertionError("Não ler conteúdo do config para o fingerprint")
        return original(self,*args,**kwargs)
    monkeypatch.setattr(Path,"read_text",no_contents)
    second = _configuration(client)["fingerprint"]
    assert first != second


def test_broker_rejects_public_socket_permissions(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    try:
        assert asyncio.run(client.discover_mcp())["status"] == "completed"
        socket = next((client.repo_root/".opencode/notebooklm/broker").glob("*.sock"))
        socket.chmod(0o666)
        result = asyncio.run(client.discover_mcp())
        assert result["status"] == "blocked"
    finally:
        socket.chmod(0o600)
        asyncio.run(client.close_persistent())


def test_nonregular_metadata_file_is_rejected(transport):
    from integrations.gemini_notebook_session import _check_local_file
    client, _ = transport
    target = client.repo_root/"never-read-fifo"
    os.mkfifo(target,0o600)
    with pytest.raises(ValueError):
        _check_local_file(target)


def test_timeout_reports_loss_of_volatile_jobs(transport, monkeypatch):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE","sleep")
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    try:
        assert asyncio.run(client.call_mcp("notebook_query_start",{"query":"volatile"}))["status"] == "pending"
        result = asyncio.run(client.call_mcp("notebook_list",{},timeout_seconds=0.15))
        assert result["status"] == "failed"
        assert result["session_reset"] is True
        assert result["volatile_jobs_lost"] is True
        after_reset = asyncio.run(client.call_mcp("notebook_query_status",{"query_id":"job-1"}))
        assert after_reset["status"] == "lost"
        assert after_reset["volatile_jobs_lost"] is True
    finally:
        asyncio.run(client.close_persistent())


def test_close_cleans_all_workspace_sessions_and_waits_for_sockets(transport):
    client, _ = transport
    first = GeminiNotebookTransport(client.repo_root,persistent=True,env_overrides={"NOTEBOOKLM_DOWNLOAD_DIR":str(client.repo_root/"one")})
    second = GeminiNotebookTransport(client.repo_root,persistent=True,env_overrides={"NOTEBOOKLM_DOWNLOAD_DIR":str(client.repo_root/"two")})
    try:
        assert asyncio.run(first.discover_mcp())["status"] == "completed"
        assert asyncio.run(second.discover_mcp())["status"] == "completed"
        base = client.repo_root/".opencode/notebooklm/broker"
        assert len(list(base.glob("*.sock"))) == 2
        closed = asyncio.run(first.close_persistent())
        assert closed["status"] == "completed"
        assert closed["sessions_closed"] == 2
        assert not list(base.glob("*.sock"))
    finally:
        asyncio.run(first.close_persistent())
        asyncio.run(second.close_persistent())


def test_stale_owned_socket_is_replaced_without_following_paths(transport):
    client, _ = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    config = _configuration(client)
    base = _private_directory(client.repo_root)
    path = base/(config["fingerprint"][:16]+".sock")
    directory_fd = os.open(base,os.O_RDONLY|os.O_DIRECTORY)
    stale = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    try:
        stale.bind(f"/proc/self/fd/{directory_fd}/{path.name}")
        path.chmod(0o600)
    finally:
        stale.close()
        os.close(directory_fd)
    try:
        result = asyncio.run(client.discover_mcp())
        assert result["status"] == "completed"
        assert path.exists()
        assert stat.S_ISSOCK(path.stat().st_mode)
    finally:
        asyncio.run(client.close_persistent())


def test_queued_request_timeout_does_not_reset_active_job(transport, monkeypatch):
    client, _ = transport
    monkeypatch.setenv("R672_FIXTURE_MODE","sleep")
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    async def concurrent():
        assert (await client.call_mcp("notebook_query_start",{"query":"active"}))["status"] == "pending"
        active = asyncio.create_task(client.call_mcp("notebook_list",{},timeout_seconds=0.8))
        await asyncio.sleep(0.03)
        queued = await client.call_mcp("notebook_list",{},timeout_seconds=0.15)
        return await active,queued
    try:
        active,queued = asyncio.run(concurrent())
        assert queued["status"] == "blocked"
        assert queued["reason"] == "session_busy"
        assert queued["session_reset"] is False
        assert queued["volatile_jobs_lost"] is False
        assert active["session_reset"] is True
        assert active["volatile_jobs_lost"] is True
    finally:
        asyncio.run(client.close_persistent())


def test_job_status_uses_origin_session_across_different_client_environments(transport):
    client, log = transport
    root = Path(__file__).resolve().parents[1]
    code = "import asyncio,json,sys; from integrations.gemini_notebook_transport import GeminiNotebookTransport; t=GeminiNotebookTransport(sys.argv[1],persistent=True); r=asyncio.run(t.call_mcp(sys.argv[2],json.loads(sys.argv[3]))); print(json.dumps(r))"
    start_environment = {**os.environ,"PATH":"/usr/bin","NOTEBOOKLM_HL":"pt-BR"}
    status_environment = {**os.environ,"PATH":"/bin:/usr/local/bin","NOTEBOOKLM_HL":"en"}
    try:
        start = subprocess.run([sys.executable,"-c",code,str(client.repo_root),"notebook_query_start",json.dumps({"query":"not persisted question"})],capture_output=True,text=True,cwd=root,env=start_environment,timeout=20)
        started = json.loads(start.stdout)
        assert started["status"] == "pending"
        check = subprocess.run([sys.executable,"-c",code,str(client.repo_root),"notebook_query_status",json.dumps({"query_id":"job-1"})],capture_output=True,text=True,cwd=root,env=status_environment,timeout=20)
        checked = json.loads(check.stdout)
        assert checked["status"] == "completed"
        assert checked["session_id"] == started["session_id"]
        assert checked["session_fingerprint"] == started["session_fingerprint"]
        assert log.read_text().splitlines().count("initialize") == 1
        associations = list((client.repo_root/".opencode/notebooklm/broker/jobs").glob("*.json"))
        assert len(associations) == 1
        assert "not persisted question" not in associations[0].read_text()
        assert stat.S_IMODE(associations[0].stat().st_mode) == 0o600
    finally:
        asyncio.run(client.close_persistent())


def test_unknown_job_does_not_spawn_new_server(transport):
    client, log = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    result = asyncio.run(client.call_mcp("notebook_query_status",{"query_id":"unregistered-job"}))
    assert result["status"] == "lost"
    assert result["reason"] == "job_not_registered_in_core_session"
    assert result["process_executed"] is False
    assert not log.exists()


def test_closed_job_reports_loss_without_restarting_server(transport):
    client, log = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    started = asyncio.run(client.call_mcp("notebook_query_start",{"query":"volatile"}))
    assert started["status"] == "pending"
    assert asyncio.run(client.close_persistent())["status"] == "completed"
    before = log.read_text().splitlines().count("initialize")
    checked = asyncio.run(client.call_mcp("notebook_query_status",{"query_id":"job-1"}))
    assert checked["status"] == "lost"
    assert checked["volatile_jobs_lost"] is True
    assert log.read_text().splitlines().count("initialize") == before


def test_job_id_collision_never_routes_to_new_session_silently(transport):
    client, _ = transport
    first = GeminiNotebookTransport(client.repo_root,persistent=True,env_overrides={"NOTEBOOKLM_HL":"pt-BR"})
    second = GeminiNotebookTransport(client.repo_root,persistent=True,env_overrides={"NOTEBOOKLM_HL":"en"})
    try:
        started = asyncio.run(first.call_mcp("notebook_query_start",{"query":"original"}))
        assert started["status"] == "pending"
        collision = asyncio.run(second.call_mcp("notebook_query_start",{"query":"different"}))
        assert collision["status"] == "blocked"
        assert collision["untracked_job_created"] is True
        original = asyncio.run(second.call_mcp("notebook_query_status",{"query_id":"job-1"}))
        assert original["session_id"] == started["session_id"]
        assert original["result"]["structuredContent"]["answer"] == "original"
    finally:
        asyncio.run(first.close_persistent())


def test_job_registry_symlink_is_never_followed(transport):
    client, log = transport
    client = GeminiNotebookTransport(client.repo_root,persistent=True)
    base = _private_directory(client.repo_root)
    outside = client.repo_root/"outside"
    outside.mkdir()
    (base/"jobs").symlink_to(outside,target_is_directory=True)
    result = asyncio.run(client.call_mcp("notebook_query_status",{"query_id":"job-1"}))
    assert result["status"] == "blocked"
    assert (base/"jobs").is_symlink()
    assert list(outside.iterdir()) == []
    assert not log.exists()
