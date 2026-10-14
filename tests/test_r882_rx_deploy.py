"""SPEC-935-R882 — empacotamento de deploy (container) da reprodução RX.

Cobre: (a) bind configurável do `serve.py` (local dual-stack vs. nuvem com
`PORT`/`RX_HOST`); (b) contrato dos artefatos de deploy (requirements mínimos,
Dockerfile, .dockerignore, blueprint Render); (c) prova de que o engine `stub`
roda **sem** dependências pesadas — simulando o container mínimo.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

REPRO = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx" / "repro"
BACKEND = REPRO / "backend"
IMG = "/tmp/opencode/rx-test-pano.png"


def _load_serve():
    spec = importlib.util.spec_from_file_location("rx_serve_r882", REPRO / "serve.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- bind configurável
def test_bind_default_local_dualstack():
    mod = _load_serve()
    host, port = mod._resolve_bind({})
    assert host == "::", host
    assert port == 8799


def test_bind_nuvem_port_e_host():
    mod = _load_serve()
    host, port = mod._resolve_bind({"PORT": "8080", "RX_HOST": "0.0.0.0"})
    assert host == "0.0.0.0"
    assert port == 8080


def test_bind_precedencia_de_porta():
    mod = _load_serve()
    # RX_PORT vale quando não há PORT (convenção da nuvem)
    assert mod._resolve_bind({"RX_PORT": "9001"}) == ("::", 9001)
    # PORT tem precedência (convenção do provedor)
    assert mod._resolve_bind({"PORT": "7000", "RX_PORT": "9001"})[1] == 7000


# ---------------------------------------------------------------- artefatos
def test_requirements_minimos():
    raw = (BACKEND / "requirements.txt").read_text(encoding="utf-8")
    # Só as linhas de requisito valem (ignora comentários/blanks).
    lines = [ln.strip().lower() for ln in raw.splitlines()]
    reqs = [ln for ln in lines if ln and not ln.startswith("#")]
    joined = "\n".join(reqs)
    for pkg in ("fastapi", "uvicorn", "pillow", "python-multipart"):
        assert pkg in joined, f"falta {pkg} em requirements.txt"
    for heavy in ("torch", "opencv", "ultralytics", "segment"):
        assert heavy not in joined, f"{heavy} não pode estar no runtime mínimo"


def test_dockerfile_contrato():
    df = (REPRO / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:" in df
    assert "EXPOSE" in df
    assert "requirements.txt" in df
    assert "serve.py" in df


def test_dockerignore_existe():
    di = (REPRO / ".dockerignore").read_text(encoding="utf-8")
    assert "__pycache__" in di


def test_render_blueprint():
    y = (REPRO / "render.yaml").read_text(encoding="utf-8")
    assert "docker" in y.lower()
    assert "/health" in y


def test_render_blueprint_canonico_na_raiz_do_repo():
    """Regressão (SPEC-935-R885): a Render só descobre `render.yaml` na RAIZ.

    O blueprint canônico precisa ficar na raiz e apontar o contexto de build via
    `rootDir`; caso contrário "New → Blueprint" não encontra o arquivo (que, se
    estiver só em repro/, nunca é detectado).
    """
    repo = Path(__file__).resolve().parents[1]
    root_yaml = repo / "render.yaml"
    assert root_yaml.is_file(), "render.yaml canônico ausente na raiz do repositório"
    y = root_yaml.read_text(encoding="utf-8")
    assert "runtime: docker" in y
    assert "/health" in y
    assert "rootDir: outputs/core-r853-rx/repro" in y


def test_arquivos_de_deploy_nao_ignorados_pelo_git():
    """Deploy from GitHub exige que o runtime da reprodução esteja RASTREADO.

    Regressão real (R883): engines.py/store.py/serve.py e os artefatos de deploy
    estavam no .gitignore — o clone do GitHub ficaria incompleto e `app.py`
    falharia ao importar engines/store.
    """
    if shutil.which("git") is None:
        pytest.skip("git ausente")
    repo = Path(__file__).resolve().parents[1]
    obrigatorios = [
        REPRO / "serve.py",
        REPRO / "Dockerfile",
        REPRO / ".dockerignore",
        REPRO / "render.yaml",
        BACKEND / "app.py",
        BACKEND / "engines.py",
        BACKEND / "store.py",
        BACKEND / "requirements.txt",
        REPRO.parent / "DEPLOY.md",
    ]
    for f in obrigatorios:
        rel = f.relative_to(repo).as_posix()
        r = subprocess.run(["git", "-C", str(repo), "check-ignore", rel],
                           capture_output=True, text=True)
        assert r.returncode != 0, f"{rel} está IGNORADO pelo git (deploy quebraria)"


# ---------------------------------------------------------------- container mínimo
def test_stub_engine_sem_deps_pesadas():
    """O container mínimo (sem torch/cv2/numpy) serve stub + admin + predict."""
    db = Path(tempfile.mkdtemp()) / "t.db"
    code = textwrap.dedent(
        f'''
        import sys, importlib.abc, os
        BLOCK = {{"torch","cv2","numpy","segment_anything","ultralytics","onnxruntime"}}
        class Guard(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path=None, target=None):
                if name.split(".")[0] in BLOCK:
                    raise ImportError("bloqueado: " + name)
                return None
        sys.meta_path.insert(0, Guard())
        sys.path.insert(0, r"{BACKEND}")
        os.environ["RX_ADMIN_DB"] = r"{db}"
        os.environ["RX_ENGINE"] = "stub"
        import app
        from fastapi.testclient import TestClient
        c = TestClient(app.app)
        assert c.get("/health").status_code == 200
        assert c.get("/").status_code == 200
        assert c.get("/opcoes.json").status_code == 200
        assert c.post("/admin/api/login", json={{"username":"x","password":"y"}}).status_code == 200
        assert c.get("/admin/api/reviews").status_code == 200
        with open(r"{IMG}", "rb") as fh:
            assert c.post("/predict", files={{"file": ("t.png", fh, "image/png")}}).status_code == 200
        leaked = [m for m in BLOCK if m in sys.modules]
        assert not leaked, "importou pesado: %r" % leaked
        print("MINIMAL_OK")
        '''
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"stderr:\n{r.stderr[-1200:]}"
    assert "MINIMAL_OK" in r.stdout
