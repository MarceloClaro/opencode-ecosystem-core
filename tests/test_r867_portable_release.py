"""Regressões da entrega: checkout deslocado e ausência de chave de máquina."""
import ast
import importlib.util
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("filename", ["test_r747_nucleo_lean.py", "test_r755_teorema_roteamento.py"])
def test_lean_tests_derive_root_from_their_checkout(tmp_path, filename):
    directory = tmp_path / "tests"
    directory.mkdir()
    target = directory / filename
    shutil.copyfile(ROOT / "tests" / filename, target)
    spec = importlib.util.spec_from_file_location("relocated_" + target.stem, target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert Path(module.REPO) == tmp_path


def test_machine_license_is_not_embedded_in_test_source():
    tree = ast.parse((ROOT / "tests/test_r852_jeb_provider.py").read_text())
    assert all(not isinstance(node, ast.Name) or node.id != "_OBSERVED_LICENSE_KEY"
               for node in ast.walk(tree)), "Verificar recibos não exige guardar a licença de máquina real."


def test_npm_lock_can_be_versioned():
    result = subprocess.run(["git", "check-ignore", "--no-index", ".opencode/package-lock.json"],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 1
