# -*- coding: utf-8 -*-
"""Testes RED da CA9 da SPEC-935-R212 para o doctor do LiteRT-LM.

O supervisor é sempre substituído por um mock. Assim, estes testes não abrem
rede, não consultam readiness real e não criam processos locais.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


_OTHER_DOCTOR_CHECKS = (
    ("_check_formal_specs", "specs_formais"),
    ("_check_evolution_registry", "evolution_registry"),
    ("_check_loop_specs", "loop_specs"),
    ("_check_metacognitive_memory", "memoria_metacognitiva"),
    ("_check_opencode_config", "opencode_config"),
    ("_check_corrigendum", "corrigendum"),
    ("_check_external_clis", "external_clis"),
    ("_check_llm_providers", "llm_providers"),
    # Checks adicionados a run_doctor() em ciclos posteriores ao R212
    # (Colibri/OLMoE, LLM Reduction Layer, cobertura de episteme do R368) —
    # sem isolá-los aqui, rodam de verdade e podem chamar time.time(),
    # estourando o relógio falso de 2 valores usado por este teste.
    ("_check_colibri", "colibri"),
    ("_check_llm_reduction_metrics", "llm_reduction_metrics"),
    ("_check_episteme_coverage", "episteme_coverage"),
)

_AFFIRMATIVE_INFERENCE_CLAIMS = (
    "inferência real confirmada",
    "inferência real comprovada",
    "inferência real validada",
    "inferência real executada",
    "inferência real realizada",
    "inferência real bem-sucedida",
    "inferência real disponível",
    "inferência real operacional",
    "inferência concluída com sucesso",
    "modelo respondeu com sucesso",
    "resposta real gerada",
)


def _required_litert_check(doctor_module: ModuleType) -> Callable[[], Any]:
    """Expõe ausência do contrato como RED explícito, em vez de ``skip``."""

    check = getattr(doctor_module, "_check_litert_lm", None)
    assert callable(check), (
        "CA9 requer marceloclaro.doctor._check_litert_lm; "
        "implemente-o somente na fase GREEN"
    )
    return check


def _mock_litert_supervisor(
    monkeypatch: pytest.MonkeyPatch,
    *,
    status_result: object | None = None,
    status_error: BaseException | None = None,
) -> tuple[ModuleType, mock.Mock, mock.Mock]:
    """Substitui tanto a definição canônica quanto eventual alias no doctor."""

    from integrations import litert_lm_supervisor as supervisor_module
    from marceloclaro import doctor as doctor_module

    supervisor = mock.create_autospec(
        supervisor_module.LiteRTSupervisor,
        instance=True,
    )
    if status_error is None:
        supervisor.status.return_value = status_result
    else:
        supervisor.status.side_effect = status_error

    supervisor_factory = mock.create_autospec(
        supervisor_module.LiteRTSupervisor,
        return_value=supervisor,
    )
    monkeypatch.setattr(
        supervisor_module,
        "LiteRTSupervisor",
        supervisor_factory,
    )
    # Aceita tanto import no escopo do módulo quanto import local na função.
    monkeypatch.setattr(
        doctor_module,
        "LiteRTSupervisor",
        supervisor_factory,
        raising=False,
    )
    return doctor_module, supervisor_factory, supervisor


def _status_for(state: str) -> object:
    """Cria o envelope público real sem executar o supervisor."""

    from integrations.litert_lm_supervisor import SupervisorState, SupervisorStatus

    return SupervisorStatus(
        state=SupervisorState(state),
        ready=state == "ready",
        pid=212 if state in {"starting", "ready"} else None,
        host="127.0.0.1",
        port=9379,
        failure_count=3 if state == "circuit_open" else 0,
        circuit_open_until=900.0 if state == "circuit_open" else None,
    )


def _assert_no_real_inference_claim(detail: str) -> None:
    normalized = detail.casefold()
    for claim in _AFFIRMATIVE_INFERENCE_CLAIMS:
        assert claim not in normalized, (
            "Readiness do supervisor não constitui evidência de inferência real: "
            f"alegação indevida encontrada em {detail!r}"
        )


@pytest.mark.parametrize(
    ("supervisor_state", "expected_doctor_status"),
    [
        pytest.param("ready", "pass", id="ready-resulta-em-pass"),
        pytest.param("starting", "warn", id="starting-resulta-em-warn"),
        pytest.param("offline", "warn", id="offline-resulta-em-warn"),
        pytest.param("circuit_open", "warn", id="circuit-open-resulta-em-warn"),
        pytest.param("unavailable", "warn", id="unavailable-resulta-em-warn"),
    ],
)
def test_check_litert_lm_mapeia_todos_os_estados_sem_falso_fail(
    monkeypatch: pytest.MonkeyPatch,
    supervisor_state: str,
    expected_doctor_status: str,
):
    """CA9: distingue os cinco estados; indisponibilidade degrada, não falha."""

    # Arrange: prepara um status estruturado e um supervisor inteiramente mockado.
    status = _status_for(supervisor_state)
    doctor_module, supervisor_factory, supervisor = _mock_litert_supervisor(
        monkeypatch,
        status_result=status,
    )

    # Act: executa somente o check individual, sem qualquer I/O externo.
    result = _required_litert_check(doctor_module)()

    # Assert: conserva o estado no detalhe e aplica a severidade definida pela CA9.
    assert result.name == "litert_lm"
    assert result.status == expected_doctor_status
    assert supervisor_state in result.detail.casefold()
    supervisor_factory.assert_called_once()
    supervisor.status.assert_called_once_with()


def test_check_litert_lm_ready_nao_declara_inferencia_real(
    monkeypatch: pytest.MonkeyPatch,
):
    """CA9 positivo/segurança: ``ready`` prova readiness, não uma geração real."""

    # Arrange: o único fato fornecido pelo mock é que o daemon está ready.
    doctor_module, _factory, _supervisor = _mock_litert_supervisor(
        monkeypatch,
        status_result=_status_for("ready"),
    )

    # Act: converte o status do supervisor em DoctorCheck.
    result = _required_litert_check(doctor_module)()

    # Assert: o detalhe pode reportar ready, mas não fabricar evidência de inferência.
    assert result.status == "pass"
    assert isinstance(result.detail, str) and result.detail.strip()
    _assert_no_real_inference_claim(result.detail)


def test_check_litert_lm_indisponivel_redige_segredos_do_erro_do_supervisor(
    monkeypatch: pytest.MonkeyPatch,
):
    """CA9 negativo/segurança: erro vira warn sanitizado, sem ecoar credenciais."""

    # Arrange: injeta canários somente na exceção do supervisor mockado.
    secret_values = (
        "sk-ca9-nao-expor-7f4c91",
        "ghp_CA9NaoExporToken8821",
        "senha-ca9-nao-expor-4402",
    )
    unsafe_error = RuntimeError(
        "supervisor indisponível; "
        f"OPENAI_API_KEY={secret_values[0]}; "
        f"Authorization=Bearer {secret_values[1]}; "
        f"password={secret_values[2]}; inferência real confirmada"
    )
    doctor_module, supervisor_factory, supervisor = _mock_litert_supervisor(
        monkeypatch,
        status_error=unsafe_error,
    )

    # Act: consulta o check sem permitir fallback para rede ou processo real.
    result = _required_litert_check(doctor_module)()

    # Assert: falha de diagnóstico é unavailable/warn e seu detalhe é seguro.
    assert result.name == "litert_lm"
    assert result.status == "warn"
    assert "unavailable" in result.detail.casefold()
    for secret in secret_values:
        assert secret not in result.detail
    _assert_no_real_inference_claim(result.detail)
    supervisor_factory.assert_called_once()
    supervisor.status.assert_called_once_with()


def test_run_doctor_inclui_exatamente_um_check_litert_lm(
    monkeypatch: pytest.MonkeyPatch,
):
    """CA9: a agregação registra o check LiteRT uma única vez."""

    from marceloclaro import doctor as doctor_module

    # Arrange: isola todos os checks para impedir filesystem, rede ou processos.
    for function_name, check_name in _OTHER_DOCTOR_CHECKS:
        isolated_check = mock.Mock(
            name=function_name,
            return_value=doctor_module.DoctorCheck(
                check_name,
                "pass",
                "check isolado pelo teste R212",
            ),
        )
        monkeypatch.setattr(doctor_module, function_name, isolated_check)

    litert_check = mock.Mock(
        name="_check_litert_lm",
        return_value=doctor_module.DoctorCheck(
            "litert_lm",
            "warn",
            "offline; readiness não comprova inferência real",
        ),
    )
    monkeypatch.setattr(
        doctor_module,
        "_check_litert_lm",
        litert_check,
        raising=False,
    )
    fake_clock = mock.Mock(side_effect=(100.0, 100.0))
    monkeypatch.setattr(doctor_module.time, "time", fake_clock)

    # Act: agrega somente os doubles determinísticos.
    report = doctor_module.run_doctor()

    # Assert: não há omissão nem duplicação do nome canônico do check.
    check_names = [check["name"] for check in report["checks"]]
    assert check_names.count("litert_lm") == 1
    litert_check.assert_called_once_with()
    assert report["checks_total"] == len(report["checks"])
