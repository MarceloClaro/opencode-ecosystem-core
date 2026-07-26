# -*- coding: utf-8 -*-
"""Testes RED da SPEC-935-R212 para o supervisor LiteRT-LM.

Este arquivo define o contrato público esperado de
``integrations.litert_lm_supervisor`` antes da implementação. Todos os pontos
externos são doubles locais: não há socket, daemon, ``systemctl`` nem processo
real. Os testes de artefatos leem somente arquivos versionados do workspace.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_NAME = "integrations.litert_lm_supervisor"
PLUGIN_PATH = PROJECT_ROOT / ".opencode" / "plugins" / "litert-lm-provider.ts"
SYSTEMD_UNIT_PATH = PROJECT_ROOT / "deploy" / "systemd" / "litert-lm.service"
START_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "litert-lm-start.sh"
LOOPBACK_HOST = "127.0.0.1"
LITERT_PORT = 9379
CIRCUIT_OPEN_SECONDS = 15 * 60


class FakeClock:
    """Relógio monotônico controlado, sem espera de tempo real."""

    def __init__(self, initial: float = 0.0) -> None:
        self._value = initial
        self._lock = threading.Lock()

    def __call__(self) -> float:
        with self._lock:
            return self._value

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        assert seconds >= 0
        with self._lock:
            self._value += seconds


class SequenceProbe:
    """Readiness fake que conserva o último valor após consumir a sequência."""

    def __init__(self, values: Sequence[bool]) -> None:
        assert values
        self._values = deque(values)
        self._last = values[-1]
        self.calls = 0

    def __call__(self, *args: object, **kwargs: object) -> bool:
        del args, kwargs
        self.calls += 1
        if self._values:
            self._last = self._values.popleft()
        return self._last


class FakeProcess:
    """Subprocesso mínimo e observável usado por todos os testes de lifecycle."""

    def __init__(self, pid: int, *, hangs_after_terminate: bool = False) -> None:
        self.pid = pid
        self.returncode: int | None = None
        self.hangs_after_terminate = hangs_after_terminate
        self.terminate_calls = 0
        self.kill_calls = 0
        self.wait_calls: list[float | None] = []

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminate_calls += 1

    def kill(self) -> None:
        self.kill_calls += 1

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls.append(timeout)
        if self.hangs_after_terminate and self.terminate_calls and not self.kill_calls:
            raise subprocess.TimeoutExpired(cmd="fake-litert", timeout=timeout)
        self.returncode = -9 if self.kill_calls else -15
        return self.returncode


def _load_supervisor_api() -> ModuleType:
    """Carrega a API RED sem transformar módulo ausente em skip de teste."""

    module_spec = importlib.util.find_spec(MODULE_NAME)
    assert module_spec is not None, (
        "Módulo de produção ausente: crie integrations/litert_lm_supervisor.py "
        "somente na fase GREEN"
    )
    module = importlib.import_module(MODULE_NAME)
    required = {
        "LiteRTSupervisor",
        "SupervisorConfig",
        "SupervisorState",
        "main",
    }
    missing = sorted(name for name in required if not hasattr(module, name))
    assert not missing, f"API pública R212 incompleta; símbolos ausentes: {missing}"
    return module


def _supervisor_config(api: ModuleType, runtime_dir: Path):
    """Cria configuração curta, persistida apenas em ``tmp_path``."""

    return api.SupervisorConfig(
        runtime_dir=runtime_dir,
        startup_timeout_seconds=3.0,
        poll_interval_seconds=1.0,
        failure_threshold=3,
        circuit_open_seconds=float(CIRCUIT_OPEN_SECONDS),
    )


def _new_supervisor(
    api: ModuleType,
    runtime_dir: Path,
    *,
    process_factory: Callable[..., FakeProcess],
    readiness_probe: Callable[..., bool],
    clock: FakeClock | None = None,
    pid_is_alive: Callable[[int], bool] | None = None,
    config: object | None = None,
):
    """Instancia o supervisor exclusivamente com dependências determinísticas."""

    fake_clock = clock or FakeClock()
    return api.LiteRTSupervisor(
        config or _supervisor_config(api, runtime_dir),
        process_factory=process_factory,
        readiness_probe=readiness_probe,
        pid_is_alive=pid_is_alive or (lambda _pid: False),
        clock=fake_clock,
        sleeper=fake_clock.sleep,
    )


def _status_mapping(status: object) -> dict[str, Any]:
    """Normaliza somente formatos estruturados; texto ou bool falham fechado."""

    if isinstance(status, Mapping):
        return dict(status)
    if is_dataclass(status) and not isinstance(status, type):
        return asdict(status)
    if hasattr(status, "_asdict"):
        return dict(status._asdict())
    pytest.fail(f"Status deve ser estruturado, não {type(status).__name__}")


def _state_text(value: object) -> str:
    raw = value.value if isinstance(value, Enum) else value
    return str(raw).strip().lower()


def _assert_state(payload: Mapping[str, Any], expected: object) -> None:
    assert "state" in payload
    assert _state_text(payload["state"]) == _state_text(expected)


def _spawn_call(factory: mock.Mock) -> tuple[list[str], dict[str, Any]]:
    """Extrai argv/kwargs sem impor chamada posicional ao process factory."""

    factory.assert_called()
    call = factory.call_args
    if call.args:
        raw_argv = call.args[0]
    else:
        raw_argv = next(
            call.kwargs[key]
            for key in ("args", "argv", "command")
            if key in call.kwargs
        )
    assert isinstance(raw_argv, (list, tuple)), "Spawn deve usar argv, não shell"
    return [str(item) for item in raw_argv], dict(call.kwargs)


def _assert_option(argv: Sequence[str], option: str, expected: str) -> None:
    joined = " ".join(argv)
    pattern = rf"(?:^|\s){re.escape(option)}(?:=|\s+){re.escape(expected)}(?:\s|$)"
    assert re.search(pattern, joined), f"Esperado {option}={expected!r} em {argv!r}"


def _invoke_main(main: Callable[[Sequence[str]], object], argv: Sequence[str]) -> int:
    """Aceita CLI que retorna código ou usa ``SystemExit`` do argparse."""

    try:
        result = main(argv)
    except SystemExit as exc:
        result = exc.code
    return 0 if result is None else int(result)


def _typescript_without_comment_lines(source: str) -> str:
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"(?m)^\s*//.*$", "", without_blocks)


def _read_required_unit() -> str:
    assert SYSTEMD_UNIT_PATH.is_file(), (
        "Artefato R212 ausente: deploy/systemd/litert-lm.service"
    )
    return SYSTEMD_UNIT_PATH.read_text(encoding="utf-8")


def _unit_directives(source: str) -> dict[tuple[str, str], list[str]]:
    section = ""
    directives: dict[tuple[str, str], list[str]] = {}
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        key, separator, value = line.partition("=")
        if separator:
            directives.setdefault((section, key.strip()), []).append(value.strip())
    return directives


def _systemd_seconds(value: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(ms|s|min|m|h)?", value.strip())
    assert match, f"Duração systemd não reconhecida no teste: {value!r}"
    factors = {None: 1.0, "ms": 0.001, "s": 1.0, "min": 60.0, "m": 60.0, "h": 3600.0}
    return float(match.group(1)) * factors[match.group(2)]


# ── CA1/CA9: API e estado estruturado ─────────────────────────────────────────


def test_api_publica_expoe_lifecycle_e_estados_fechados():
    """CA1/CA9: a API canônica possui lifecycle e estados não ambíguos."""

    # Arrange: carrega exclusivamente o módulo de produção esperado pela SPEC.
    api = _load_supervisor_api()
    expected_states = {"offline", "starting", "ready", "circuit_open", "unavailable"}

    # Act: projeta métodos e valores públicos sem iniciar qualquer serviço.
    methods = {name for name in ("status", "ensure", "wait", "stop") if callable(getattr(api.LiteRTSupervisor, name, None))}
    states = {_state_text(member) for member in api.SupervisorState}

    # Assert: nenhum comando ou estado obrigatório pode ficar implícito.
    assert methods == {"status", "ensure", "wait", "stop"}
    assert states == expected_states
    assert callable(api.main)


def test_status_offline_e_estruturado_sem_spawn_ou_segredos(tmp_path: Path):
    """CA1/CA3: status offline é serializável, útil e livre de credenciais."""

    # Arrange: readiness e processo são doubles; o ambiente contém um canário.
    api = _load_supervisor_api()
    process_factory = mock.Mock(name="process_factory")
    supervisor = _new_supervisor(
        api,
        tmp_path,
        process_factory=process_factory,
        readiness_probe=mock.Mock(return_value=False),
    )
    with mock.patch.dict(os.environ, {"STATUS_API_TOKEN": "status-canary"}, clear=False):
        # Act: consulta estado sem solicitar ensure.
        payload = _status_mapping(supervisor.status())

    # Assert: o contrato é estruturado e health check nunca implica spawn.
    required = {"state", "ready", "pid", "host", "port", "failure_count", "circuit_open_until"}
    assert required <= set(payload)
    _assert_state(payload, api.SupervisorState.OFFLINE)
    assert payload["ready"] is False
    assert payload["pid"] is None
    assert payload["host"] == LOOPBACK_HOST
    assert payload["port"] == LITERT_PORT
    assert "status-canary" not in json.dumps(payload, default=str)
    process_factory.assert_not_called()


def test_status_ready_preserva_campos_operacionais_sem_criar_processo(tmp_path: Path):
    """CA1/CA9 positivo: daemon já ready é reconhecido sem segundo spawn."""

    # Arrange: a sonda local informa readiness e Popen permanece sentinela.
    api = _load_supervisor_api()
    process_factory = mock.Mock(name="process_factory")
    supervisor = _new_supervisor(
        api,
        tmp_path,
        process_factory=process_factory,
        readiness_probe=mock.Mock(return_value=True),
    )

    # Act: ensure reconcilia o daemon já disponível e status materializa o estado.
    supervisor.ensure(non_blocking=True)
    payload = _status_mapping(supervisor.status())

    # Assert: ready é positivo, local e não cria um processo redundante.
    _assert_state(payload, api.SupervisorState.READY)
    assert payload["ready"] is True
    assert payload["host"] == LOOPBACK_HOST
    assert payload["port"] == LITERT_PORT
    process_factory.assert_not_called()


# ── CA2: lock interprocesso e PID validado ─────────────────────────────────────


def test_cinquenta_ensure_concorrentes_compartilham_lock_e_fazem_um_spawn(tmp_path: Path):
    """CA2 negativo: cinquenta solicitantes não podem criar daemon duplicado."""

    # Arrange: instâncias distintas compartilham runtime_dir, PID vivo e barreira.
    api = _load_supervisor_api()
    config = _supervisor_config(api, tmp_path)
    process = FakeProcess(pid=42_424)
    process_factory = mock.Mock(return_value=process)
    readiness = mock.Mock(return_value=False)
    pid_is_alive = lambda pid: pid == process.pid and process.poll() is None
    supervisors = [
        _new_supervisor(
            api,
            tmp_path,
            config=config,
            process_factory=process_factory,
            readiness_probe=readiness,
            pid_is_alive=pid_is_alive,
        )
        for _ in range(50)
    ]
    barrier = threading.Barrier(len(supervisors))

    def request_ensure(supervisor: object) -> object:
        barrier.wait()
        return supervisor.ensure(non_blocking=True)

    # Act: dispara as cinquenta chamadas simultaneamente, todas sem espera real.
    with ThreadPoolExecutor(max_workers=len(supervisors)) as executor:
        futures = [executor.submit(request_ensure, supervisor) for supervisor in supervisors]
        for future in futures:
            future.result(timeout=10)

    # Assert: o lock compartilhado deixa exatamente um processo vivo conhecido.
    assert process_factory.call_count == 1
    assert process.poll() is None


def test_pid_morto_nao_bloqueia_um_unico_spawn_de_reposicao(tmp_path: Path):
    """CA2 positivo/edge: PID stale é rejeitado e permite reposição controlada."""

    # Arrange: duas instâncias compartilham estado e dois processos fake sucessivos.
    api = _load_supervisor_api()
    config = _supervisor_config(api, tmp_path)
    first = FakeProcess(pid=101)
    replacement = FakeProcess(pid=202)
    known_processes = {first.pid: first, replacement.pid: replacement}
    process_factory = mock.Mock(side_effect=[first, replacement])

    def pid_is_alive(pid: int) -> bool:
        process = known_processes.get(pid)
        return process is not None and process.poll() is None

    supervisors = [
        _new_supervisor(
            api,
            tmp_path,
            config=config,
            process_factory=process_factory,
            readiness_probe=mock.Mock(return_value=False),
            pid_is_alive=pid_is_alive,
        )
        for _ in range(2)
    ]
    supervisors[0].ensure(non_blocking=True)
    first.returncode = 17

    # Act: a segunda instância reconcilia o PID encerrado.
    supervisors[1].ensure(non_blocking=True)

    # Assert: há uma única reposição, e o novo processo permanece vivo.
    assert process_factory.call_count == 2
    assert replacement.poll() is None


# ── CA3/CA1: ambiente mínimo e comando fixo ────────────────────────────────────


def test_spawn_usa_ambiente_minimo_e_remove_canarios_de_segredo(tmp_path: Path):
    """CA3: somente contexto operacional permitido chega ao processo filho."""

    # Arrange: o pai contém variáveis úteis, lixo e três classes de segredo.
    api = _load_supervisor_api()
    parent_environment = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(tmp_path / "home"),
        "LANG": "pt_BR.UTF-8",
        "LITERT_LM_MODELS_DIR": str(tmp_path / "models"),
        "OPENAI_API_KEY": "key-canary-r212",
        "HF_TOKEN": "token-canary-r212",
        "DATABASE_SECRET": "secret-canary-r212",
        "UNRELATED_PARENT_SETTING": "must-not-be-inherited",
    }
    process_factory = mock.Mock(return_value=FakeProcess(pid=303))
    with mock.patch.dict(os.environ, parent_environment, clear=True):
        supervisor = _new_supervisor(
            api,
            tmp_path,
            process_factory=process_factory,
            readiness_probe=mock.Mock(return_value=False),
        )

        # Act: solicita somente o spawn não bloqueante do fake.
        supervisor.ensure(non_blocking=True)

    # Assert: preserva mínimos úteis e remove nomes/valores sensíveis e lixo.
    _argv, kwargs = _spawn_call(process_factory)
    child_environment = kwargs["env"]
    assert child_environment["PATH"] == parent_environment["PATH"]
    assert child_environment["HOME"] == parent_environment["HOME"]
    assert child_environment["LITERT_LM_MODELS_DIR"] == parent_environment["LITERT_LM_MODELS_DIR"]
    assert "UNRELATED_PARENT_SETTING" not in child_environment
    secret_name = re.compile(r"(?:^|_)(?:KEY|TOKEN|SECRET)(?:_|$)", re.IGNORECASE)
    assert not [name for name in child_environment if secret_name.search(name)]
    serialized_environment = json.dumps(child_environment, sort_keys=True)
    for canary in ("key-canary-r212", "token-canary-r212", "secret-canary-r212"):
        assert canary not in serialized_environment


def test_spawn_ignora_overrides_e_mantem_argv_fixo_em_loopback(tmp_path: Path):
    """CA1 negativo: ambiente hostil não altera comando, bind, porta ou shell."""

    # Arrange: prepara duas combinações distintas de overrides não confiáveis.
    api = _load_supervisor_api()

    def capture_spawn(runtime_dir: Path, host: str, port: str, command: str):
        factory = mock.Mock(return_value=FakeProcess(pid=404))
        environment = {
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path / "home"),
            "LITERT_LM_HOST": host,
            "LITERT_LM_PORT": port,
            "LITERT_LM_COMMAND": command,
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            supervisor = _new_supervisor(
                api,
                runtime_dir,
                process_factory=factory,
                readiness_probe=mock.Mock(return_value=False),
            )
            supervisor.ensure(non_blocking=True)
        return _spawn_call(factory)

    # Act: captura o argv sob dois ataques de configuração diferentes.
    first_argv, first_kwargs = capture_spawn(
        tmp_path / "first", "0.0.0.0", "9999", "/tmp/evil-one"
    )
    second_argv, second_kwargs = capture_spawn(
        tmp_path / "second", "::", "1234", "/tmp/evil-two"
    )

    # Assert: comando é invariável, sem shell e explicitamente preso ao loopback.
    assert first_argv == second_argv
    _assert_option(first_argv, "--host", LOOPBACK_HOST)
    _assert_option(first_argv, "--port", str(LITERT_PORT))
    joined = " ".join(first_argv)
    assert all(value not in joined for value in ("0.0.0.0", "9999", "::", "/tmp/evil"))
    assert first_kwargs.get("shell", False) is False
    assert second_kwargs.get("shell", False) is False
    assert Path(first_kwargs["cwd"]).resolve() == PROJECT_ROOT
    assert Path(second_kwargs["cwd"]).resolve() == PROJECT_ROOT


# ── CA4: circuit breaker ───────────────────────────────────────────────────────


def test_tres_falhas_abrem_circuito_e_half_open_respeita_relogio_fake(tmp_path: Path):
    """CA4: limiar três bloqueia novos spawns até completar quinze minutos."""

    # Arrange: todo spawn falha de forma local e o relógio inicia em instante fixo.
    api = _load_supervisor_api()
    clock = FakeClock(initial=100.0)
    process_factory = mock.Mock(side_effect=OSError("spawn deliberadamente falhou"))
    supervisor = _new_supervisor(
        api,
        tmp_path,
        process_factory=process_factory,
        readiness_probe=mock.Mock(return_value=False),
        clock=clock,
    )

    # Act: falha duas vezes, cruza o limiar na terceira e tenta durante cooldown.
    supervisor.ensure(non_blocking=True)
    supervisor.ensure(non_blocking=True)
    before_threshold = _status_mapping(supervisor.status())
    supervisor.ensure(non_blocking=True)
    opened = _status_mapping(supervisor.status())
    supervisor.ensure(non_blocking=True)
    clock.advance(CIRCUIT_OPEN_SECONDS - 1)
    supervisor.ensure(non_blocking=True)

    # Assert: duas falhas não abrem; três abrem; chamadas precoces não fazem spawn.
    assert before_threshold["failure_count"] == 2
    assert _state_text(before_threshold["state"]) != _state_text(api.SupervisorState.CIRCUIT_OPEN)
    assert opened["failure_count"] == 3
    _assert_state(opened, api.SupervisorState.CIRCUIT_OPEN)
    assert process_factory.call_count == 3

    # Arrange/Act do half-open: ultrapassa o instante permitido sem tempo real.
    clock.advance(1.1)
    supervisor.ensure(non_blocking=True)

    # Assert: exatamente uma nova tentativa é admitida após o cooldown.
    assert process_factory.call_count == 4


# ── CA5: readiness, término e reap ─────────────────────────────────────────────


def test_processo_que_fica_ready_nao_e_terminado(tmp_path: Path):
    """CA5 positivo: readiness dentro do orçamento preserva o filho saudável."""

    # Arrange: a sonda fica offline antes do spawn e ready durante o wait fake.
    api = _load_supervisor_api()
    process = FakeProcess(pid=505)
    probe = SequenceProbe([False, False, True])
    supervisor = _new_supervisor(
        api,
        tmp_path,
        process_factory=mock.Mock(return_value=process),
        readiness_probe=probe,
        clock=FakeClock(),
        pid_is_alive=lambda pid: pid == process.pid and process.poll() is None,
    )

    # Act: ensure bloqueante aguarda apenas o relógio controlado.
    result = _status_mapping(supervisor.ensure(non_blocking=False))

    # Assert: o estado é ready e nenhum sinal/reap prematuro ocorreu.
    _assert_state(result, api.SupervisorState.READY)
    assert process.terminate_calls == 0
    assert process.kill_calls == 0
    assert process.wait_calls == []
    assert process.poll() is None


def test_processo_nao_ready_e_terminado_reaped_e_removido_do_status(tmp_path: Path):
    """CA5 negativo: timeout não deixa processo ou PID órfão conhecido."""

    # Arrange: readiness nunca chega e o fake exige kill após terminate.
    api = _load_supervisor_api()
    process = FakeProcess(pid=606, hangs_after_terminate=True)
    supervisor = _new_supervisor(
        api,
        tmp_path,
        process_factory=mock.Mock(return_value=process),
        readiness_probe=mock.Mock(return_value=False),
        clock=FakeClock(),
        pid_is_alive=lambda pid: pid == process.pid and process.poll() is None,
    )

    # Act: esgota o startup timeout usando somente avanços do relógio fake.
    result = _status_mapping(supervisor.ensure(non_blocking=False))

    # Assert: terminate, fallback kill e wait final ocorreram; estado registra falha.
    assert process.terminate_calls == 1
    assert process.kill_calls == 1
    assert len(process.wait_calls) >= 2
    assert process.poll() is not None
    assert result["pid"] is None
    assert result["ready"] is False
    assert result["failure_count"] == 1
    assert _state_text(result["state"]) in {
        _state_text(api.SupervisorState.OFFLINE),
        _state_text(api.SupervisorState.UNAVAILABLE),
    }


# ── CLI pública ────────────────────────────────────────────────────────────────


def test_cli_status_json_emite_envelope_estruturado(capsys: pytest.CaptureFixture[str]):
    """CA1/CA9: ``main status --json`` não reduz estado a texto informal."""

    # Arrange: substitui o supervisor usado pela CLI por fachada sem I/O.
    api = _load_supervisor_api()
    expected = {
        "state": "offline",
        "ready": False,
        "pid": None,
        "host": LOOPBACK_HOST,
        "port": LITERT_PORT,
        "failure_count": 0,
        "circuit_open_until": None,
    }
    fake_supervisor = mock.Mock()
    fake_supervisor.status.return_value = expected

    with mock.patch.object(api, "LiteRTSupervisor", return_value=fake_supervisor):
        # Act: executa a função main diretamente, sem subprocesso de CLI.
        exit_code = _invoke_main(api.main, ["status", "--json"])

    # Assert: saída é JSON válido e conserva tipos/campos operacionais.
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == expected
    fake_supervisor.status.assert_called_once_with()


def test_cli_ensure_non_blocking_nao_chama_wait(capsys: pytest.CaptureFixture[str]):
    """CA1/CA6 negativo: flag não bloqueante jamais entra no caminho ``wait``."""

    # Arrange: wait falharia imediatamente se a CLI tentasse bloquear o bootstrap.
    api = _load_supervisor_api()
    result = {
        "state": "starting",
        "ready": False,
        "pid": 707,
        "host": LOOPBACK_HOST,
        "port": LITERT_PORT,
        "failure_count": 0,
        "circuit_open_until": None,
    }
    fake_supervisor = mock.Mock()
    fake_supervisor.ensure.return_value = result
    fake_supervisor.wait.side_effect = AssertionError("CLI não bloqueante chamou wait")

    with mock.patch.object(api, "LiteRTSupervisor", return_value=fake_supervisor):
        # Act: solicita bootstrap pelo mesmo contrato usado pelo plugin.
        exit_code = _invoke_main(api.main, ["ensure", "--non-blocking"])

    # Assert: ensure recebe a intenção explícita e retorna imediatamente.
    assert exit_code == 0
    fake_supervisor.ensure.assert_called_once_with(non_blocking=True)
    fake_supervisor.wait.assert_not_called()
    assert "starting" in capsys.readouterr().out


# ── CA6: bootstrap do plugin ───────────────────────────────────────────────────


def test_plugin_preserva_provider_hook_e_solicita_bootstrap_nao_bloqueante():
    """CA6: carregamento mantém ProviderHook e dispara ensure sem espera síncrona."""

    # Arrange: lê TypeScript como artefato estático e remove linhas de comentário.
    assert PLUGIN_PATH.is_file(), f"Plugin LiteRT ausente: {PLUGIN_PATH}"
    source = PLUGIN_PATH.read_text(encoding="utf-8")
    code = _typescript_without_comment_lines(source)

    # Act: identifica contrato existente e marcadores executáveis do bootstrap.
    has_plugin_contract = bool(
        re.search(r'import\s+type\s*\{[^}]*\bPlugin\b[^}]*\}\s+from\s+["\']@opencode-ai/plugin["\']', code)
        and re.search(r"export\s+const\s+LiteRTProvider\s*:\s*Plugin", code)
        and re.search(r"\bprovider\s*:", code)
    )
    supervisor_reference = (
        "integrations.litert_lm_supervisor" in code
        or "integrations/litert_lm_supervisor.py" in code
    )
    has_async_spawn = any(
        marker in code for marker in ("Bun.spawn(", "Deno.Command(", "spawn(", "$`")
    )

    # Assert: ProviderHook sobrevive e bootstrap usa caminho/flag fixos, sem sync.
    assert has_plugin_contract, "Bootstrap não pode remover o contrato Plugin/provider"
    assert supervisor_reference, "Plugin deve chamar o supervisor canônico do workspace"
    assert re.search(r'["\']ensure["\']', code)
    assert re.search(r'["\']--non-blocking["\']', code)
    assert has_async_spawn, "Bootstrap deve iniciar processo de modo assíncrono"
    assert not any(marker in code for marker in ("spawnSync(", "execSync(", "systemSync("))
    assert str(PROJECT_ROOT) not in code, "Plugin não pode gravar path específico da máquina"
    assert any(marker in code for marker in ("cwd:", "directory", "worktree")), (
        "Bootstrap deve ancorar o comando no workspace recebido pelo plugin"
    )


# ── CA8: unit systemd --user versionada ────────────────────────────────────────


def test_unit_systemd_litert_lm_existe_no_caminho_versionado():
    """CA8 positivo: a unit opcional integra o repositório em caminho estável."""

    # Arrange: define o único caminho canônico auditável pela distribuição.
    expected_path = PROJECT_ROOT / "deploy" / "systemd" / "litert-lm.service"

    # Act: consulta apenas metadados locais do artefato, sem chamar systemctl.
    exists = expected_path.is_file()

    # Assert: ausência é RED explícito, nunca skip condicionado ao host.
    assert exists, f"Unit systemd R212 ausente: {expected_path}"


def test_unit_systemd_executa_foreground_loopback_com_restart_e_quotas_limitados():
    """CA8 negativo/positivo: unit é local, foreground e limitada por recursos."""

    # Arrange: carrega e interpreta somente diretivas do arquivo versionado.
    source = _read_required_unit()
    directives = _unit_directives(source)

    def one(section: str, key: str) -> str:
        values = directives.get((section, key), [])
        assert len(values) == 1, f"Esperada uma diretiva [{section}] {key}; obtido {values}"
        return values[0]

    # Act: projeta lifecycle, comando e limites relevantes à SPEC.
    exec_start = one("Service", "ExecStart")
    restart = one("Service", "Restart")
    restart_seconds = _systemd_seconds(one("Service", "RestartSec"))
    burst = int(one("Unit", "StartLimitBurst"))
    interval_seconds = _systemd_seconds(one("Unit", "StartLimitIntervalSec"))
    tasks_max = one("Service", "TasksMax")
    memory_max = one("Service", "MemoryMax")
    wanted_by = one("Install", "WantedBy")

    # Assert: caminho feliz é foreground/loopback e falhas não geram restart livre.
    assert one("Service", "Type") == "simple"
    assert LOOPBACK_HOST in exec_start and str(LITERT_PORT) in exec_start
    assert "0.0.0.0" not in exec_start and "::" not in exec_start
    assert "--daemon" not in exec_start and not exec_start.rstrip().endswith("&")
    assert "--foreground" in exec_start or re.search(r"(?:^|\s)serve(?:\s|$)", exec_start)
    assert restart == "on-failure"
    assert restart_seconds >= 1
    assert burst == 3
    assert interval_seconds >= CIRCUIT_OPEN_SECONDS
    assert tasks_max.lower() not in {"", "infinity"}
    assert memory_max.lower() not in {"", "infinity"}
    assert wanted_by == "default.target"
    assert "User=root" not in source
    assert not re.search(r"(?i)(?:api[_-]?key|token|secret)\s*=", source)


def test_unit_systemd_nao_depende_de_path_interativo_para_localizar_litert():
    """CA8: systemd deve resolver o executável sem o PATH do shell interativo."""

    source = _read_required_unit()
    directives = _unit_directives(source)
    exec_values = directives.get(("Service", "ExecStart"), [])

    assert len(exec_values) == 1
    executable = exec_values[0].split(maxsplit=1)[0]
    assert executable.startswith(("/", "%h/")), (
        "ExecStart deve usar caminho absoluto ou specifier %h; "
        f"recebido {executable!r}"
    )


def test_script_start_legado_delega_ao_supervisor_sem_nohup_ou_pgrep():
    """Lifecycle shell não pode manter um quarto mecanismo concorrente."""

    source = START_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "integrations.litert_lm_supervisor" in source
    assert "nohup litert-lm serve" not in source
    assert "pgrep -f" not in source


def test_provider_python_importa_supervisor_canonico():
    """Provider legado deve compartilhar lock/circuit breaker do supervisor."""

    provider_path = PROJECT_ROOT / "integrations" / "litert_lm_provider.py"
    source = provider_path.read_text(encoding="utf-8")

    assert "litert_lm_supervisor" in source
    assert "LiteRTSupervisor" in source
