"""R839: pytest real e histórico local autenticado; sem oráculo simulado."""

import importlib
import json
from pathlib import Path

import pytest

from sdd.spec_engine import Specification


class _Project:
    """Carrega a API na chamada do teste, distinguindo ausência de coleta inválida."""

    def __init__(self, root, state, spec, implementation, test):
        self.root, self.state, self.spec = root, state, spec
        self.implementation, self.test, self.history = implementation, test, None

    def __iter__(self):
        if self.history is None:
            try:
                module = importlib.import_module("sdd.tdd_history")
            except ModuleNotFoundError as exc:
                assert exc.name != "sdd.tdd_history", (
                    "API de histórico executado ainda não existe"
                )
                raise
            self.history = module.TDDHistory(root=self.root, state_dir=self.state)
        return iter((self.history, self.spec, self.implementation, self.test))


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "tests").mkdir()
    implementation = root / "implementation.py"
    implementation.write_text("def result():\n    return 1\n", encoding="utf-8")
    test = root / "tests" / "test_contract.py"
    test.write_text(
        "from implementation import result\ndef test_result():\n    assert result() == 2\n",
        encoding="utf-8",
    )
    spec = Specification(
        "SPEC-TEST-R839",
        "Contrato estável",
        "resultado igual a dois",
        component="implementation",
        test_file="tests/test_contract.py",
    )
    spec.add_criterion("O resultado é dois")
    return _Project(root, tmp_path / "private-history", spec, implementation, test)


def pair(project):
    history, spec, implementation, _ = project
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is True, red.to_dict()
    implementation.write_text("def result():\n    return 2\n", encoding="utf-8")
    green = history.run(spec, phase="green", timeout_seconds=20)
    return red, green


def test_ciclo_real_preserva_teste_e_ignora_status_mutavel(project):
    history, spec, _, test = project
    test_before = test.read_bytes()
    red, green = pair(project)
    assert green.accepted is True, green.to_dict()
    spec.status = "verified"
    spec.declared_status = "green"
    validated = history.validate_pair(spec, green)
    assert validated["verified"] is True
    assert validated["red_receipt_id"] == red.receipt_id
    assert validated["green_receipt_id"] == green.receipt_id
    assert history.validate_pair(spec, green.receipt_id)["verified"] is True
    assert test.read_bytes() == test_before
    assert Path(green.receipt_path).is_file()
    assert history.preflight(spec)["verified"] is True


def test_green_sem_red_nao_e_entrega_aceita(project):
    history, spec, implementation, _ = project
    implementation.write_text("def result():\n    return 2\n", encoding="utf-8")
    assert history.preflight(spec)["verified"] is False
    green = history.run(spec, phase="green", timeout_seconds=20)
    assert green.accepted is False
    assert history.validate_pair(spec, green)["verified"] is False
    assert (
        history.validate_pair(spec, {"red_hash": "qualquer", "tests_green": True})[
            "verified"
        ]
        is False
    )


@pytest.mark.parametrize(
    "body",
    [
        "import modulo_inexistente_r839\n",
        "def test_broken(:\n    pass\n",
        "# nenhum teste coletável\n",
        "import pytest\n@pytest.mark.skip(reason='não executado')\ndef test_result():\n    assert False\n",
        "import pytest\n@pytest.mark.xfail(reason='hipótese')\ndef test_result():\n    assert False\n",
        "def test_result():\n    raise ValueError('sem asserção')\n",
    ],
)
def test_falha_sem_assercao_executada_nao_e_red(project, body):
    history, spec, _, test = project
    test.write_text(body, encoding="utf-8")
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is False
    assert red.status == "rejected"
    assert history.preflight(spec)["verified"] is False


def test_timeout_nao_e_red(project):
    history, spec, _, test = project
    test.write_text(
        "import time\ndef test_result():\n    time.sleep(5)\n    assert False\n",
        encoding="utf-8",
    )
    red = history.run(spec, phase="red", timeout_seconds=0.15)
    assert red.accepted is False
    assert red.status == "rejected"


def test_mudar_teste_ou_spec_nao_reutiliza_par(project):
    history, spec, _, test = project
    _, green = pair(project)
    original = test.read_text(encoding="utf-8")
    test.write_text(original + "\n# contrato alterado\n", encoding="utf-8")
    assert history.validate_pair(spec, green)["verified"] is False
    assert history.preflight(spec)["verified"] is False
    test.write_text(original, encoding="utf-8")
    spec.objective = "outro contrato"
    assert history.validate_pair(spec, green)["verified"] is False


def test_par_nao_cruza_identificador_de_spec(project):
    history, spec, _, _ = project
    _, green = pair(project)
    spec.spec_id = "SPEC-TEST-OUTRA"
    assert history.validate_pair(spec, green)["verified"] is False


def test_adulteracao_de_payload_e_junit_e_detectada(project):
    history, spec, _, _ = project
    _, green = pair(project)
    path = Path(green.receipt_path)
    original = path.read_bytes()
    envelope = json.loads(original)
    envelope["payload"]["phase"] = "red"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    assert history.validate_pair(spec, green)["verified"] is False
    path.write_bytes(original)
    junit = path.parent / "junit.xml"
    junit.write_text("<testsuites/>", encoding="utf-8")
    assert history.validate_pair(spec, green)["verified"] is False


def test_adulteracao_da_cadeia_ou_traversal_e_detectada(project):
    history, spec, _, _ = project
    _, green = pair(project)
    ledger = history.state_dir / "ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    ledger.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
    assert history.validate_pair(spec, green)["verified"] is False
    assert history.validate_pair(spec, "../../receipt.json")["verified"] is False


def test_red_aposteriori_nao_autentica_green_anterior(project):
    history, spec, implementation, _ = project
    implementation.write_text("def result():\n    return 2\n", encoding="utf-8")
    green = history.run(spec, phase="green", timeout_seconds=20)
    implementation.write_text("def result():\n    return 1\n", encoding="utf-8")
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is True
    assert history.validate_pair(spec, green)["verified"] is False


def test_alteracao_de_fonte_durante_pytest_nao_e_red(project):
    history, spec, _, test = project
    test.write_text(
        "from pathlib import Path\ndef test_result():\n    Path('implementation.py').write_text('changed = True\\n')\n    assert False\n",
        encoding="utf-8",
    )
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is False


def test_chave_privada_fora_de_outputs_e_sem_leitura_publica(project):
    history, _, _, _ = project
    secret = history.state_dir / "hmac.key"
    assert secret.is_file()
    assert secret.stat().st_mode & 0o077 == 0
    history_class = type(history)
    with pytest.raises(ValueError):
        history_class(root=history.root, state_dir=history.root / "outputs" / "history")


def test_processos_filhos_da_fase_sao_encerrados_apos_saida_do_pytest(project):
    import os
    import time

    if os.name != "posix":
        pytest.skip("Sondagem de grupo POSIX; Windows exige prova própria.")
    history, spec, _, test = project
    test.write_text(
        "import subprocess,sys\nfrom pathlib import Path\ndef test_child():\n    child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\n    Path('owned-child.pid').write_text(str(child.pid))\n    assert False\n"
    )
    history.run(spec, phase="red", timeout_seconds=20)
    pid = int((history.root / "owned-child.pid").read_text())

    def live():
        path = Path(f"/proc/{pid}/stat")
        return path.exists() and path.read_text().split(") ", 1)[1].split()[0] != "Z"

    deadline = time.monotonic() + 2
    while live() and time.monotonic() < deadline:
        time.sleep(0.02)
    try:
        assert not live()
    finally:
        if live():
            os.kill(pid, 9)  # Apenas o filho desta sondagem, PID registrado pelo teste.


def test_mudar_fixture_do_oraculo_nao_converte_red_em_green(project):
    history, spec, _, test = project
    fixture = history.root / "tests/fixtures/expected.json"
    fixture.parent.mkdir()
    fixture.write_text('{"value":2}')
    test.write_text(
        "import json\nfrom pathlib import Path\nfrom implementation import result\ndef test_result():\n    assert result() == json.loads(Path('tests/fixtures/expected.json').read_text())['value']\n"
    )
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is True
    fixture.write_text('{"value":1}')
    assert history.preflight(spec)["verified"] is False
    green = history.run(spec, phase="green", timeout_seconds=20)
    assert green.accepted is False


def test_green_nao_autentica_codigo_typescript_posteriormente_alterado(project):
    history, spec, _, _ = project
    source = history.root / "adapter.ts"
    source.write_text("export const value=1;")
    _, green = pair(project)
    source.write_text("export const value=2;")
    assert history.validate_pair(spec, green)["verified"] is False


@pytest.mark.parametrize(
    "relative",
    [
        "tests/conftest.py",
        "tests/oracle_helper.py",
        "pytest.ini",
        "pyproject.toml",
        "conftest.py",
        ".pytest.ini",
        "tox.ini",
        "pytest.toml",
        ".pytest.toml",
    ],
)
def test_mudar_suporte_ou_configuracao_do_oraculo_invalida_red(project, relative):
    history, spec, _, _ = project
    path = history.root / relative
    content = "[pytest]\n" if relative == "pytest.ini" else "# suporte original\n"
    path.write_text(content)
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is True
    path.write_text(content + "# alteração entre as fases\n")
    assert history.preflight(spec)["verified"] is False


def test_addopts_nao_desvia_execucao_do_alvo_da_spec(project):
    history, spec, _, _ = project
    other = history.root / "tests/test_other.py"
    other.write_text("def test_other():\n    assert False\n")
    (history.root / "pytest.ini").write_text(
        "[pytest]\naddopts = --deselect=tests/test_contract.py::test_result tests/test_other.py\n"
    )
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is True
    collected = json.loads(
        (Path(red.receipt_path).parent / "collected.json").read_text()
    )["nodeids"]
    assert collected == ["tests/test_contract.py::test_result"]


def test_escopo_fora_da_arvore_tests_e_recusado(project):
    history, spec, _, _ = project
    custom = history.root / "custom_tests"
    custom.mkdir()
    (custom / "test_other.py").write_text("def test_other():\n    assert False\n")
    spec.test_file = "custom_tests/test_other.py"
    red = history.run(spec, phase="red", timeout_seconds=20)
    assert red.accepted is False and "core_test_scope_must_be_tests" in red.reason_codes
