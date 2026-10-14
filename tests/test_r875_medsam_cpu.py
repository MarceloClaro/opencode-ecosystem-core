"""SPEC-935-R875: MedSAM real (Opção 3) carregado corretamente em CPU-only.

Verifica a correção do defeito encontrado ao integrar o `medsam_vit_b.pth`
real: o checkpoint guarda storages ancoradas em CUDA e
`sam_model_registry["vit_b"](checkpoint=...)` (que usa `torch.load(f)` sem
`map_location`) falha em host CPU-only. O `_load_sam` deve mapear para CPU,
construir com `checkpoint=None` e injetar via `load_state_dict(strict=True)`,
com cache por caminho.

Estes testes são **unitários e sem GPU**: usam um `torch` falso e um registry
falso, de modo que não dependem de `torch`/`segment_anything` instalados nem do
checkpoint de 375 MB. A vertente ponta a ponta (com o MedSAM real) vive em
`test_r853_rx_repro.py::test_option3_real_sam_when_available`, que é PULADA
quando o checkpoint não existe.
"""

from __future__ import annotations

import sys
import types
from importlib import util
from pathlib import Path

import pytest

R853 = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx"


def _load_app():
    spec = util.spec_from_file_location("rx_app_r875", R853 / "repro" / "backend" / "app.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def app_mod():
    return _load_app()


def _fake_registry(built: dict):
    class _FakeSam:
        def __init__(self):
            self.loaded_with = None
            self.strict = None
            self.evaled = False

        def load_state_dict(self, sd, strict=False):  # noqa: ANN001
            self.loaded_with = sd
            self.strict = strict
            return "ok"

        def eval(self):
            self.evaled = True
            return self

    class _Registry:
        def __getitem__(self, key):
            assert key == "vit_b", f"arquitetura inesperada: {key}"

            def _build(checkpoint=None):  # noqa: ANN001
                built["checkpoint"] = checkpoint
                built["sam"] = _FakeSam()
                return built["sam"]

            return _build

    return _Registry()


def test_load_sam_maps_to_cpu_and_uses_load_state_dict(app_mod, monkeypatch):
    """Regressão do defeito CUDA: torch.load DEVE receber map_location='cpu'."""
    calls: dict = {}
    fake_torch = types.ModuleType("torch")

    def _fake_load(path, map_location=None, **kwargs):  # noqa: ANN001
        calls["path"] = path
        calls["map_location"] = map_location
        return {"image_encoder.weight": 1}

    fake_torch.load = _fake_load
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    built: dict = {}
    app_mod._SAM_CACHE.clear()
    target = "/tmp/opencode/ckpt-medsam-fake.pth"
    sam = app_mod._load_sam(target, _fake_registry(built))

    assert calls["map_location"] == "cpu", "checkpoint deve ser mapeado para CPU"
    assert calls["path"].endswith("ckpt-medsam-fake.pth")
    assert built["checkpoint"] is None, "modelo deve ser construído sem carregar arquivo"
    assert sam.loaded_with == {"image_encoder.weight": 1}
    assert sam.strict is True, "load_state_dict deve exigir correspondência exata"
    assert sam.evaled is True
    assert app_mod._SAM_CACHE, "modelo deveria ser cacheado"


def test_load_sam_caches_by_path(app_mod, monkeypatch):
    """Segunda chamada com o mesmo caminho NÃO deve reler o arquivo."""
    reads = {"n": 0}
    fake_torch = types.ModuleType("torch")

    def _fake_load(path, map_location=None, **kwargs):  # noqa: ANN001
        reads["n"] += 1
        return {"w": 1}

    fake_torch.load = _fake_load
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    built: dict = {}
    reg = _fake_registry(built)
    app_mod._SAM_CACHE.clear()
    target = "/tmp/opencode/ckpt-cache-fake.pth"
    a = app_mod._load_sam(target, reg)
    b = app_mod._load_sam(target, reg)

    assert a is b, "o mesmo objeto deve ser reutilizado (cache)"
    assert reads["n"] == 1, "o arquivo não deveria ser lido duas vezes"


def test_medsam_segment_uses_load_sam(app_mod, monkeypatch):
    """`_medsam_segment` deve delegar o carregamento a `_load_sam`."""
    import numpy as np
    from PIL import Image

    used = {"called": False}

    def _spy(ckpt, registry):  # noqa: ANN001
        used["called"] = True
        return object()

    monkeypatch.setattr(app_mod, "_load_sam", _spy)
    monkeypatch.setenv("RX_MEDSAM_CKPT", "/tmp/opencode/anything.pth")

    # SamPredictor e cv2 são reais aqui (numpy/PIL/cv2 disponíveis no .venv);
    # para o teste não depender de segment_anything nem de inferência,
    # interceptamos a classe SamPredictor via injeção de módulo falso.
    import importlib

    try:
        import segment_anything  # noqa: F401
    except Exception:  # noqa: BLE001
        pytest.skip("segment_anything ausente")

    class _FakePredictor:
        def __init__(self, sam):  # noqa: ANN001
            pass

        def set_image(self, arr):  # noqa: ANN001
            pass

        def predict(self, box=None, multimask_output=False):  # noqa: ANN001
            mask = np.zeros((64, 64), dtype=bool)
            mask[10:40, 10:40] = True
            return np.array([mask]), np.array([0.9]), None

    monkeypatch.setattr("segment_anything.SamPredictor", _FakePredictor)

    img = Image.new("RGB", (64, 64), (0, 0, 0))
    contour = app_mod._medsam_segment(img, [10.0, 10.0, 40.0, 40.0])

    assert used["called"] is True, "_load_sam deveria ser usado"
    assert len(contour) >= 3, "contorno real (fechado) esperado"
    for x, y in contour:
        assert isinstance(x, float) and isinstance(y, float)
