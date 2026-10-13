"""R839: contratos negativos de entrega; dublê GREEN nunca cria RED histórico."""

import pytest

from sdd.spec_engine import (
    Specification,
    SpecRegistry,
    SpecVerifier,
    _issue_trusted_test_evidence,
)


def isolated_verifier(spec):
    # Sem registro global ou carregamento de specs: apenas o contrato da unidade.
    registry = object.__new__(SpecRegistry)
    registry.specs = {spec.spec_id: spec}
    return SpecVerifier(registry)


def test_spec_r839_possui_contrato_executavel_valido():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R839")
    assert spec.evidence_contract_valid is True, spec.evidence_contract_error
    assert set(spec.criterion_test_targets) == {"historico", "entrega", "verificador"}


@pytest.mark.parametrize(
    "test_file",
    [
        "tests/test_r839_verifier_delivery.py",
        "tests/r839-no-such-test.py",
    ],
)
def test_programmatic_software_spec_is_not_delivery_without_red_or_green(test_file):
    spec = Specification(
        "SPEC-TEST-R839-PROGRAMMATIC",
        "Software",
        "Entrega registrada",
        test_file=test_file,
    )
    spec.add_criterion(
        "A entrega declara resultado", lambda output: output == {"done": True}
    )
    outcome = isolated_verifier(spec).verify(spec.spec_id, {"done": True})
    assert outcome["verified"] is False
    assert outcome["red_history_required"] is True
    assert outcome["verification_scope"] == "software_delivery_gate"
    assert spec.status == "red"


@pytest.mark.parametrize("receipt_id", [None, "0" * 64])
def test_runtime_green_object_cannot_replace_executed_red(receipt_id):
    spec = Specification(
        "SPEC-TEST-R839-NO-RED",
        "Software",
        "Entrega registrada",
        test_file="tests/test_r839_verifier_delivery.py",
    )
    spec.add_criterion(
        "A entrega declara resultado", lambda output: output == {"done": True}
    )
    # Objeto emitido pelo runtime em uma unidade controlada: nenhum pytest foi
    # executado nesta fixture. O contrato deve rejeitá-lo por ausência de RED.
    green = _issue_trusted_test_evidence(
        spec.spec_id,
        spec.test_file,
        executed=True,
        passed=True,
        returncode=0,
        summary="controlled GREEN claim",
        tdd_history_receipt_id=receipt_id,
    )
    outcome = isolated_verifier(spec).verify(
        spec.spec_id, {"done": True}, trusted_test_evidence=green
    )
    assert outcome["verified"] is False
    assert outcome["red_history_required"] is True
    assert outcome["red_history_valid"] is False
    assert spec.status == "red"


def test_criteria_inspection_is_explicit_and_does_not_promote_confidence(monkeypatch):
    import sdd.spec_engine as module

    spec = Specification(
        "SPEC-TEST-R839-INSPECTION",
        "Inspeção",
        "Critério satisfeito",
        test_file="tests/test_r839_verifier_delivery.py",
    )
    spec.add_criterion(
        "A entrega declara resultado", lambda output: output == {"done": True}
    )
    promoted = []
    monkeypatch.setattr(
        module.metabus.memory,
        "update_topic_confidence",
        lambda *args, **kwargs: promoted.append((args, kwargs)),
    )
    outcome = isolated_verifier(spec).verify(
        spec.spec_id, {"done": True}, require_red_history=False
    )
    assert outcome["verified"] is True
    assert outcome["verification_scope"] == "criteria_only"
    assert promoted == []


def test_inspecao_de_software_nao_promove_estado_nem_evento(monkeypatch):
    from sdd import spec_engine as module

    spec = module.Specification(
        "SPEC-TEST-INSPECT", "Inspeção", "Critérios", test_file="tests/test_feature.py"
    )
    spec.add_criterion("Saída verdadeira", lambda out: out is True)
    spec.status = "red"
    registry = object.__new__(module.SpecRegistry)
    registry.specs = {spec.spec_id: spec}
    events = []
    monkeypatch.setattr(
        module.metabus,
        "publish_subsystem_event",
        lambda *args, **kwargs: events.append(args),
    )
    result = module.SpecVerifier(registry).verify(
        spec.spec_id, True, require_red_history=False
    )
    assert (
        result["verified"] is True and result["verification_scope"] == "criteria_only"
    )
    assert spec.status == "red"
    assert events[-1][2]["verification_scope"] == "criteria_only"
    assert events[-1][2]["red_history_valid"] is False
