"""Registro de motores de inferência da reprodução (SPEC-935-R853).

Expõe as três opções que o operador pode escolher, com detecção HONESTA de
disponibilidade (fail-closed): nenhum motor indisponível finge produzir
resultado. Capabilities declaradas por motor:

  stub        — determinístico/sintético (sempre disponível; demo do contrato)
  weights     — pesos reais do operador (.pt) via Ultralytics       [Opção 1]
  open_base   — modelos abertos base (MedSAM) para /segment/sam      [Opção 3]

A Opção 2 (treinar pesos próprios) não é motor de inferência: é o pipeline em
`repro/training/`, descrito aqui apenas como metadado para o seletor.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

ENGINE_IDS = ("stub", "weights", "open_base")


@dataclass
class EngineInfo:
    id: str
    option: int
    title: str
    kind: str  # "inference" | "training"
    capabilities: list[str]
    available: bool
    requires: list[str]
    env_vars: dict[str, str] = field(default_factory=dict)
    detail: str = ""
    how_to_enable: str = ""


def _has(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def environment() -> dict[str, bool]:
    return {m: _has(m) for m in ("torch", "ultralytics", "segment_anything", "cv2", "onnxruntime")}


def _default_weights_dir() -> str:
    return os.environ.get("RX_WEIGHTS_DIR", "")


def _default_medsam_ckpt() -> str:
    return os.environ.get("RX_MEDSAM_CKPT", "")


def find_weights(weights_dir: str) -> list[str]:
    """Procura arquivos .pt sob `weights_dir` (best.pt etc.). Não baixa nada."""
    if not weights_dir:
        return []
    root = Path(weights_dir).expanduser()
    if not root.exists():
        return []
    return sorted(str(p) for p in root.rglob("*.pt"))


def engine_statuses() -> list[EngineInfo]:
    env = environment()
    wdir = _default_weights_dir()
    ckpt = _default_medsam_ckpt()
    weights = find_weights(wdir)

    stub = EngineInfo(
        id="stub", option=0, title="Demonstração (stub determinístico)", kind="inference",
        capabilities=["detection", "sam", "bundle"], available=True, requires=[],
        detail="Motor sintético; caixas derivadas do tamanho da imagem. NÃO é clínico.",
        how_to_enable="Nada a fazer — é o padrão.",
    )

    weights_ok = bool(env["ultralytics"]) and bool(weights)
    if not env["ultralytics"]:
        w_detail = "falta o pacote 'ultralytics' (pip install ultralytics)"
    elif not wdir:
        w_detail = "defina RX_WEIGHTS_DIR apontando para os .pt do operador"
    elif not weights:
        w_detail = f"nenhum .pt encontrado em {wdir}"
    else:
        w_detail = f"{len(weights)} peso(s) encontrado(s): {Path(weights[0]).name}…"
    weights_eng = EngineInfo(
        id="weights", option=1, title="Pesos reais do operador (.pt)", kind="inference",
        capabilities=["detection", "bundle"], available=weights_ok,
        requires=["ultralytics", "RX_WEIGHTS_DIR"], env_vars={"RX_WEIGHTS_DIR": wdir or "<caminho dos .pt>"},
        detail=w_detail,
        how_to_enable="pip install ultralytics && export RX_WEIGHTS_DIR=/caminho/artifacts/training/.../weights",
    )

    sam_ok = bool(env["torch"]) and bool(env["segment_anything"]) and bool(ckpt) and Path(ckpt).expanduser().exists()
    if not env["torch"]:
        o_detail = "falta 'torch' (pip install torch)"
    elif not env["segment_anything"]:
        o_detail = "falta 'segment_anything' (pip install git+https://github.com/facebookresearch/segment-anything)"
    elif not ckpt:
        o_detail = "defina RX_MEDSAM_CKPT com o checkpoint medsam_vit_b"
    else:
        o_detail = "MedSAM pronto para /segment/sam"
    open_base = EngineInfo(
        id="open_base", option=3, title="Modelos abertos base (MedSAM)", kind="inference",
        capabilities=["sam"], available=sam_ok,
        requires=["torch", "segment_anything", "RX_MEDSAM_CKPT"],
        env_vars={"RX_MEDSAM_CKPT": ckpt or "<medsam_vit_b.pth>"},
        detail=o_detail,
        how_to_enable="pip install torch segment_anything && export RX_MEDSAM_CKPT=/caminho/medsam_vit_b.pth",
    )

    training = EngineInfo(
        id="training", option=2, title="Treinar pesos próprios (pipeline)", kind="training",
        capabilities=["train"], available=False, requires=["GPU", "datasets OdontoAI/DENTEX/Kaggle"],
        detail="Não é motor de inferência; ver repro/training/ (receita publicada + download).",
        how_to_enable="Ver outputs/core-r853-rx/repro/training/README.md (treinar em host com GPU).",
    )
    return [stub, weights_eng, training, open_base]


def as_dicts() -> list[dict]:
    return [asdict(e) for e in engine_statuses()]


def by_id(engine_id: str) -> EngineInfo | None:
    for e in engine_statuses():
        if e.id == engine_id:
            return e
    return None


def resolve(engine_id: str | None) -> str:
    """Motor efetivo: explícito > RX_ENGINE > 'stub'."""
    return engine_id or os.environ.get("RX_ENGINE", "stub")


# Ordem de preferência ao servir uma capacidade que o motor ativo NÃO cobre:
# motores REAIS primeiro, o stub sintético por último (SPEC-935-R876).
_PREFERENCE = ("weights", "open_base", "stub")


def providers_for(capability: str) -> list[str]:
    """Ids de motores de INFERÊNCIA que declaram `capability`, em ordem de preferência."""
    infos = {e.id: e for e in engine_statuses()}
    ordered = [eid for eid in _PREFERENCE if eid in infos and capability in infos[eid].capabilities]
    for eid, e in infos.items():  # inclui motores futuros, de forma determinística
        if e.kind == "inference" and capability in e.capabilities and eid not in ordered:
            ordered.append(eid)
    return ordered


def resolve_capability(capability: str, preferred: str | None = None) -> str | None:
    """Motor que DEVE servir `capability` (composição por capacidade).

    Regra: usa o motor preferido (ativo) se ele cobrir a capacidade e estiver
    DISPONÍVEL; caso contrário, o primeiro provedor disponível na ordem de
    preferência. Devolve `None` quando NENHUM motor disponível cobre a
    capacidade — quem chama deve converter isso em fail-closed (409).
    """
    infos = {e.id: e for e in engine_statuses()}
    pref = infos.get(preferred or "")
    if pref is not None and pref.kind == "inference" and capability in pref.capabilities and pref.available:
        return pref.id
    for eid in providers_for(capability):
        if infos[eid].available:
            return eid
    return None


CAPABILITIES = ("detection", "sam", "bundle")


def serving_map(preferred: str | None = None) -> dict[str, str | None]:
    """Mapa `capability -> motor efetivo` (transparência em /health e /opcoes)."""
    return {c: resolve_capability(c, preferred) for c in CAPABILITIES}



def require_available(engine_id: str, capability: str) -> EngineInfo:
    """Fail-closed: levanta se o motor não existe, não cobre a capability ou está indisponível.

    Retorna EngineInfo quando pode ser usado.
    """
    info = by_id(engine_id)
    if info is None:
        raise ValueError(f"motor desconhecido: {engine_id}")
    if info.kind != "inference":
        raise ValueError(f"motor '{engine_id}' não é de inferência (é '{info.kind}')")
    if capability not in info.capabilities:
        raise ValueError(f"motor '{engine_id}' não cobre '{capability}' (tem {info.capabilities})")
    if not info.available:
        raise ValueError(f"motor '{engine_id}' indisponível: {info.detail}")
    return info
