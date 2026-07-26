# -*- coding: utf-8 -*-
"""Testes R145/R212 — estabilidade e watchdog do TouchTerrain.

Os testes unitários formalizam, em RED, os contratos da SPEC-935-R212 v1.2
(CA29/CA30): liveness local em ``/healthz``, três falhas consecutivas,
cooldown, lock interprocesso, restart sem ``sudo`` e estado injetável. Rede,
subprocessos e esperas reais são proibidos nesses testes.

As verificações da instalação em ``/etc``, da aplicação em ``/opt`` e das
portas locais continuam explicitamente externas e opt-in.
"""

from __future__ import annotations

import fcntl
import http.client
import importlib.util
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest import mock
from urllib.parse import urlsplit

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WATCHDOG_SCRIPT = ROOT / "scripts" / "touchterrain_watchdog.py"
TOUCHTERRAIN_APP = Path(
    "/opt/geomaker/touchterrain/touchterrain/server/TouchTerrain_app.py"
)
TIMER_UNIT = Path("/etc/systemd/system/geomaker-touchterrain-watchdog.timer")
SERVICE_UNIT = Path("/etc/systemd/system/geomaker-touchterrain-watchdog.service")
RUN_EXTERNAL_TESTS = os.getenv("OPENCODE_RUN_EXTERNAL_TESTS") == "1"
EXTERNAL_SKIP_REASON = (
    "teste externo desabilitado; defina OPENCODE_RUN_EXTERNAL_TESTS=1"
)

LOCAL_HEALTH_URL = "http://127.0.0.1:8081/healthz"
FAKE_SERVICE = "touchterrain-fake.service"


def _load_watchdog_module() -> ModuleType:
    """Carrega o script-alvo sem executar sua CLI."""

    if not WATCHDOG_SCRIPT.exists():
        pytest.fail(f"watchdog script não encontrado: {WATCHDOG_SCRIPT}")
    spec = importlib.util.spec_from_file_location(
        "touchterrain_watchdog_test_target", WATCHDOG_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _block_real_external_io(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Impede I/O externo nos testes herméticos; libera somente ``external``."""

    if request.node.get_closest_marker("external") is not None:
        return

    def blocked(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AssertionError(
            "teste hermético do watchdog tentou rede, subprocesso ou espera real"
        )

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(http.client.HTTPConnection, "connect", blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", blocked)
    monkeypatch.setattr(urllib.request, "urlopen", blocked)
    monkeypatch.setattr(subprocess, "Popen", blocked)
    monkeypatch.setattr(subprocess, "run", blocked)
    monkeypatch.setattr(subprocess, "call", blocked)
    monkeypatch.setattr(subprocess, "check_call", blocked)
    monkeypatch.setattr(subprocess, "check_output", blocked)
    monkeypatch.setattr(os, "system", blocked)
    monkeypatch.setattr(time, "sleep", blocked)


@dataclass
class FakeClock:
    """Relógio controlado, sem dependência do tempo de parede."""

    value: float = 10_000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        assert seconds >= 0
        self.value += seconds


@dataclass
class WatchdogHarness:
    """Dependências observáveis de um ciclo hermético do watchdog."""

    module: ModuleType
    state_path: Path
    lock_path: Path
    clock: FakeClock
    health_probe: mock.Mock
    restart: mock.Mock

    def run(
        self,
        *,
        state_path: Path | None = None,
        lock_path: Path | None = None,
    ) -> Any:
        """Executa um ciclo usando somente caminhos e doubles do teste."""

        with (
            mock.patch.object(self.module.time, "time", self.clock),
            mock.patch.object(self.module.time, "monotonic", self.clock),
        ):
            return self.module.run_once(
                url=LOCAL_HEALTH_URL,
                service=FAKE_SERVICE,
                timeout=0.25,
                state_path=state_path if state_path is not None else self.state_path,
                lock_path=lock_path if lock_path is not None else self.lock_path,
            )


@pytest.fixture
def watchdog_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> WatchdogHarness:
    """Monta watchdog sem rede, systemd, relógio ou estado globais."""

    module = _load_watchdog_module()
    clock = FakeClock()
    health_probe = mock.Mock(return_value=False)
    restart = mock.Mock(return_value=True)
    monkeypatch.setattr(module, "check_health", health_probe)
    monkeypatch.setattr(module, "restart_service", restart)
    monkeypatch.setattr(module, "log", mock.Mock())
    return WatchdogHarness(
        module=module,
        state_path=tmp_path / "watchdog-state.json",
        lock_path=tmp_path / "watchdog.lock",
        clock=clock,
        health_probe=health_probe,
        restart=restart,
    )


# ── R145 CA-1: check_health() distingue falha e sucesso ───────────────────────


def test_ca1_check_health_detecta_conexao_recusada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA-1 negativo: conexão recusada local resulta em serviço não saudável."""

    # Arrange
    watchdog = _load_watchdog_module()
    calls: list[tuple[str, float]] = []

    def fake_urlopen(url: str, timeout: float) -> Any:
        calls.append((url, timeout))
        raise urllib.error.URLError("conexão recusada simulada")

    monkeypatch.setattr(watchdog.urllib.request, "urlopen", fake_urlopen)

    # Act
    healthy = watchdog.check_health(LOCAL_HEALTH_URL, timeout=1.0)

    # Assert
    assert healthy is False
    assert calls == [(LOCAL_HEALTH_URL, 1.0)]


def test_ca1_check_health_detecta_resposta_valida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA-1 positivo: HTTP 200 local resulta em serviço saudável."""

    # Arrange
    watchdog = _load_watchdog_module()
    calls: list[tuple[str, float]] = []

    class FakeResponse:
        status = 200

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *exc_info: object) -> bool:
            del exc_info
            return False

    def fake_urlopen(url: str, timeout: float) -> FakeResponse:
        calls.append((url, timeout))
        return FakeResponse()

    monkeypatch.setattr(watchdog.urllib.request, "urlopen", fake_urlopen)

    # Act
    healthy = watchdog.check_health(LOCAL_HEALTH_URL, timeout=5.0)

    # Assert
    assert healthy is True
    assert calls == [(LOCAL_HEALTH_URL, 5.0)]


# ── R145 CA-2 / R212 CA29: restart sem elevação de privilégio ─────────────────


def test_ca29_restart_service_usa_systemctl_restart_sem_sudo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA29 positivo: systemd já fornece privilégio; ``sudo`` é proibido."""

    # Arrange
    watchdog = _load_watchdog_module()
    fake_run = mock.Mock(return_value=SimpleNamespace(returncode=0))
    monkeypatch.setattr(watchdog.subprocess, "run", fake_run)

    # Act
    restarted = watchdog.restart_service(FAKE_SERVICE)

    # Assert
    assert restarted is True
    fake_run.assert_called_once()
    positional, keyword = fake_run.call_args
    command = list(positional[0])
    assert command == ["systemctl", "restart", FAKE_SERVICE]
    assert "sudo" not in command
    assert keyword.get("shell", False) is False


def test_ca29_restart_service_retorna_false_quando_systemctl_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA29 negativo: código não zero é propagado como falha booleana."""

    # Arrange
    watchdog = _load_watchdog_module()
    fake_run = mock.Mock(return_value=SimpleNamespace(returncode=1))
    monkeypatch.setattr(watchdog.subprocess, "run", fake_run)

    # Act
    restarted = watchdog.restart_service(FAKE_SERVICE)

    # Assert
    assert restarted is False
    command = list(fake_run.call_args.args[0])
    assert command == ["systemctl", "restart", FAKE_SERVICE]
    assert "sudo" not in command


# ── R212 CA29: URL local, falhas consecutivas, cooldown, lock e estado ─────────


def test_ca29_default_url_termina_em_healthz_e_eh_puramente_local() -> None:
    """CA29: o padrão usa liveness local e nunca a readiness pesada ``/main``."""

    # Arrange
    watchdog = _load_watchdog_module()

    # Act
    default_url = watchdog.DEFAULT_URL
    parsed = urlsplit(default_url)

    # Assert
    assert default_url.endswith("/healthz")
    assert parsed.path == "/healthz"
    assert parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    assert parsed.query == ""
    assert parsed.fragment == ""
    assert not default_url.endswith("/main")


def test_ca29_uma_falha_isolada_persiste_estado_sem_reiniciar(
    watchdog_harness: WatchdogHarness, tmp_path: Path
) -> None:
    """CA29 negativo: uma amostra ruim isolada não causa restart prematuro."""

    # Arrange
    harness = watchdog_harness
    harness.health_probe.return_value = False

    # Act
    harness.run()

    # Assert
    harness.health_probe.assert_called_once_with(LOCAL_HEALTH_URL, timeout=0.25)
    harness.restart.assert_not_called()
    assert harness.state_path.exists()
    assert harness.state_path.parent == tmp_path


def test_ca29_tres_falhas_consecutivas_disparam_um_restart(
    watchdog_harness: WatchdogHarness,
) -> None:
    """CA29 positivo/negativo: somente a terceira falha cruza o limiar."""

    # Arrange
    harness = watchdog_harness
    harness.health_probe.return_value = False

    # Act
    restart_counts: list[int] = []
    for _ in range(3):
        harness.run()
        restart_counts.append(harness.restart.call_count)

    # Assert
    assert restart_counts == [0, 0, 1]
    harness.restart.assert_called_once_with(FAKE_SERVICE)


def test_ca29_sucesso_intermediario_zera_sequencia_de_falhas(
    watchdog_harness: WatchdogHarness,
) -> None:
    """CA29: falhas separadas por sucesso não são tratadas como consecutivas."""

    # Arrange
    harness = watchdog_harness
    harness.health_probe.side_effect = [False, False, True, False, False, False]

    # Act
    restart_counts: list[int] = []
    for _ in range(6):
        harness.run()
        restart_counts.append(harness.restart.call_count)

    # Assert
    assert restart_counts == [0, 0, 0, 0, 0, 1]
    harness.restart.assert_called_once_with(FAKE_SERVICE)


def test_ca29_cooldown_impede_novo_restart_mesmo_com_nova_rajada(
    watchdog_harness: WatchdogHarness,
) -> None:
    """CA29: duas rajadas no mesmo instante geram no máximo um restart."""

    # Arrange
    harness = watchdog_harness
    harness.health_probe.return_value = False

    # Act
    restart_counts: list[int] = []
    for _ in range(6):
        harness.run()
        restart_counts.append(harness.restart.call_count)

    # Assert
    assert restart_counts[:3] == [0, 0, 1]
    assert restart_counts[3:] == [1, 1, 1]
    harness.restart.assert_called_once_with(FAKE_SERVICE)


def test_ca29_lock_ocupado_impede_ciclo_concorrente_e_liberado_permite_ciclo(
    watchdog_harness: WatchdogHarness,
) -> None:
    """CA29 negativo/positivo: lock ocupado falha fechado sem bloquear o timer."""

    # Arrange
    harness = watchdog_harness
    harness.lock_path.touch()

    # Act
    with harness.lock_path.open("a+", encoding="utf-8") as lock_owner:
        fcntl.flock(lock_owner.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            harness.run()
        finally:
            fcntl.flock(lock_owner.fileno(), fcntl.LOCK_UN)
    harness.run()

    # Assert
    harness.health_probe.assert_called_once_with(LOCAL_HEALTH_URL, timeout=0.25)
    harness.restart.assert_not_called()
    assert harness.state_path.exists()


def test_ca29_state_path_injetado_isola_contadores_em_tmp_path(
    watchdog_harness: WatchdogHarness, tmp_path: Path
) -> None:
    """CA29: estados distintos não compartilham a sequência de falhas."""

    # Arrange
    harness = watchdog_harness
    state_a = tmp_path / "instance-a" / "state.json"
    lock_a = tmp_path / "instance-a" / "watchdog.lock"
    state_b = tmp_path / "instance-b" / "state.json"
    lock_b = tmp_path / "instance-b" / "watchdog.lock"
    harness.health_probe.return_value = False

    # Act
    restart_counts: list[int] = []
    for state_path, lock_path in (
        (state_a, lock_a),
        (state_a, lock_a),
        (state_b, lock_b),
        (state_a, lock_a),
    ):
        harness.run(state_path=state_path, lock_path=lock_path)
        restart_counts.append(harness.restart.call_count)

    # Assert
    assert restart_counts == [0, 0, 0, 1]
    assert state_a.exists()
    assert state_b.exists()
    assert state_a.is_relative_to(tmp_path)
    assert state_b.is_relative_to(tmp_path)


# ── R145 CA-4 / R212 CA30: instalação real, sempre external opt-in ────────────


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca4_timer_unit_existe() -> None:
    """CA-4 externo: a instalação real contém a unit timer."""

    # Arrange
    timer_unit = TIMER_UNIT

    # Act
    exists = timer_unit.exists()

    # Assert
    assert exists, f"unit não encontrada: {timer_unit}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca4_service_unit_existe() -> None:
    """CA-4 externo: a instalação real contém a unit de serviço."""

    # Arrange
    service_unit = SERVICE_UNIT

    # Act
    exists = service_unit.exists()

    # Assert
    assert exists, f"unit não encontrada: {service_unit}"


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca30_service_unit_usa_healthz_sem_main_ou_sudo() -> None:
    """CA30 externo: a unit usa liveness local e não eleva privilégio."""

    # Arrange
    assert SERVICE_UNIT.exists(), f"unit não encontrada: {SERVICE_UNIT}"
    content = SERVICE_UNIT.read_text("utf-8")

    # Act
    exec_start_lines = [
        line.strip() for line in content.splitlines() if line.strip().startswith("ExecStart=")
    ]
    exec_start = " ".join(exec_start_lines)

    # Assert
    assert "touchterrain_watchdog.py" in exec_start
    assert "/healthz" in exec_start
    assert "/main" not in exec_start
    assert "sudo" not in exec_start.split()
    assert "Type=oneshot" in content


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca4_timer_habilitado_e_ativo() -> None:
    """CA-4 externo: o timer real está habilitado e ativo."""

    # Arrange
    timer_name = "geomaker-touchterrain-watchdog.timer"

    # Act
    enabled = subprocess.run(
        ["systemctl", "is-enabled", timer_name],
        capture_output=True,
        text=True,
    )
    active = subprocess.run(
        ["systemctl", "is-active", timer_name],
        capture_output=True,
        text=True,
    )

    # Assert
    assert enabled.stdout.strip() == "enabled", (
        f"timer não habilitado: {enabled.stdout!r} {enabled.stderr!r}"
    )
    assert active.stdout.strip() == "active", (
        f"timer não ativo: {active.stdout!r} {active.stderr!r}"
    )


# ── R145 CA-5 / R212 CA30: aplicação real, sempre external opt-in ─────────────


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca5_basethick_regressao_acesso_seguro() -> None:
    """CA-5 externo: a correção R143 permanece na aplicação implantada."""

    # Arrange
    assert TOUCHTERRAIN_APP.exists(), f"aplicação não encontrada: {TOUCHTERRAIN_APP}"

    # Act
    content = TOUCHTERRAIN_APP.read_text("utf-8")

    # Assert
    assert "args[k] = float(args.get(k" in content or "args.get(k, 0)" in content, (
        "Regressão detectada: acesso a 'basethick' voltou a ser direto."
    )
    assert "args[k] = float(args[k])" not in content


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca30_app_real_expoe_healthz_e_preserva_main() -> None:
    """CA30 externo: a aplicação implantada separa liveness e readiness."""

    # Arrange
    assert TOUCHTERRAIN_APP.exists(), f"aplicação não encontrada: {TOUCHTERRAIN_APP}"
    content = TOUCHTERRAIN_APP.read_text("utf-8")

    # Act
    routes = set(
        re.findall(
            r"@\w+\.(?:route|get)\(\s*['\"]([^'\"]+)['\"]",
            content,
        )
    )

    # Assert
    assert "/healthz" in routes, "aplicação real não expõe a rota local /healthz"
    assert "/main" in routes, "readiness funcional /main foi removida"


# ── R145 CA-6 / R212 CA30: endpoints reais, sempre external opt-in ────────────


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca30_healthz_real_responde_sem_redirecionamento() -> None:
    """CA30 externo: o endpoint leve real responde HTTP 200."""

    # Arrange
    url = "http://127.0.0.1:8081/healthz"

    # Act
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.status
    except urllib.error.URLError as error:
        pytest.fail(f"/healthz real inacessível: {error}")

    # Assert
    assert status == 200


@pytest.mark.external
@pytest.mark.skipif(not RUN_EXTERNAL_TESTS, reason=EXTERNAL_SKIP_REASON)
def test_ca6_main_endpoint_responde_apos_remediacao() -> None:
    """CA-6 externo: ``/main`` permanece como readiness funcional."""

    # Arrange
    url = "http://127.0.0.1:8081/main"

    # Act
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            status = response.status
    except urllib.error.URLError as error:
        pytest.fail(f"/main ainda inacessível/travado após remediação: {error}")

    # Assert
    assert status in (200, 302, 303)


# ── R145 CA-7: watchdog permanece stdlib ──────────────────────────────────────


def test_ca7_watchdog_usa_apenas_stdlib() -> None:
    """CA-7: o watchdog não introduz clientes HTTP ou locks externos."""

    # Arrange
    forbidden_imports = ("requests", "httpx", "aiohttp", "filelock")

    # Act
    content = WATCHDOG_SCRIPT.read_text("utf-8")

    # Assert
    for package in forbidden_imports:
        assert f"import {package}" not in content
        assert f"from {package}" not in content
