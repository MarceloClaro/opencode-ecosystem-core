"""R828: declarações do chamador nunca constituem evidência de execução."""
import importlib

import pytest


def test_motor_canonico_nao_expoe_aprovacao_por_flag_ou_texto_arbitrario():
    spec_engine = importlib.import_module("sdd.spec_engine")
    runner = importlib.import_module("sdd.tdd_runner")
    assert not hasattr(spec_engine, "verify_delivery")
    assert not hasattr(runner, "require_red_first")
    assert not hasattr(runner.TDDRunner, "require_red_first")
    assert callable(spec_engine.SpecVerifier.verify)
    assert callable(runner.TDDRunner.run_spec_test)


@pytest.mark.parametrize("module,args", [
    ("protocolos.sdd_spec_first", ("SPEC-935-R999999",)),
    ("protocolos.sdd_gate", ("SPEC-935-R999999", True)),
    ("protocolos.tdd_red_green_refactor", ("texto-sem-execucao", True)),
])
def test_contrato_de_entrada_aprovado_nao_e_gate_runtime(module, args):
    result = importlib.import_module(module).check(*args)
    assert result["approved"] is True  # Apenas forma dos argumentos, não entrega.
    assert result["input_valid"] is True
    assert result["runtime_gate"] is False
    assert result["execution_verified"] is False
    assert result["verification"] == "input_contract_only"
    assert "approved_str" not in result
    assert "RED" not in result and "GREEN" not in result


@pytest.mark.parametrize("module,args", [
    ("protocolos.sdd_spec_first", (None,)),
    ("protocolos.sdd_gate", ("SPEC-935-R832", False)),
    ("protocolos.sdd_gate", ("SPEC-935-R832", 1)),
    ("protocolos.tdd_red_green_refactor", ("", True)),
    ("protocolos.tdd_red_green_refactor", ("texto-sem-execucao", 1)),
])
def test_contrato_invalido_permanece_fechado_e_sem_alegacao_runtime(module, args):
    result = importlib.import_module(module).check(*args)
    assert result["approved"] is False
    assert result["input_valid"] is False
    assert result["runtime_gate"] is False
    assert result["execution_verified"] is False
    assert result["verification"] == "input_contract_only"


def test_flags_tdd_sao_declarações_nao_fases_executadas():
    from protocolos.tdd_red_green_refactor import check
    result = check("qualquer-texto", True)
    assert result["declared_red_hash"] == "qualquer-texto"
    assert result["declared_green"] is True
    assert result["execution_verified"] is False

