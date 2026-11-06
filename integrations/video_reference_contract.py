"""R1059: checks estruturais de receitas e intercâmbio; não certifica estética."""
from __future__ import annotations

import math
from pathlib import PurePosixPath


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: número finito obrigatório")
    return value


def _indexed(items, label):
    if not isinstance(items, list):
        raise ValueError(f"{label}: lista obrigatória")
    result = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise ValueError(f"{label}: ID obrigatório")
        if item["id"] in result:
            raise ValueError(f"{label}: ID duplicado")
        result[item["id"]] = item
    return result


def _interval(item, duration, allow_point=False):
    start = _number(item.get("start_s"), "start_s")
    end = _number(item.get("end_s"), "end_s")
    if start < 0 or end < start or (not allow_point and start == end):
        raise ValueError("Intervalo inválido")
    if duration is not None and end > duration + 1e-6:
        raise ValueError("Intervalo excede duração observada")
    return start, end


def validate_recipe(data):
    """Valida limites, IDs e cobertura; não substitui o contrato completo da skill."""
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise ValueError("Versão de receita não suportada")
    reference = data.get("reference", {})
    duration = reference.get("duration_s")
    if duration is not None and _number(duration, "duration_s") <= 0:
        raise ValueError("Duração deve ser positiva ou desconhecida")
    coverage = data.get("coverage", {})
    for modality in ("visual", "audio", "transcription"):
        item = coverage.get(modality, {})
        status = item.get("status")
        if status not in {"completa", "parcial", "indisponivel", "nao_aplicavel"}:
            raise ValueError("Status de cobertura inválido")
        if status != "completa" and not item.get("limitations"):
            raise ValueError("Cobertura incompleta exige limitações")
        intervals = item.get("intervals", [])
        if not isinstance(intervals, list):
            raise ValueError("Intervalos devem ser lista")
        parsed = sorted(_interval(v, duration) for v in intervals)
        if status == "completa":
            if duration is None or not parsed or item.get("gaps"):
                raise ValueError("Cobertura integral não sustentada")
            if any(v.get("method") in {"frame_pontual", "contact_sheet", "metadata", None} for v in intervals):
                raise ValueError("Método não demonstra cobertura temporal integral")
            cursor = 0.0
            for start, end in parsed:
                if abs(start - cursor) > 1e-6:
                    raise ValueError("Cobertura contém lacuna ou sobreposição")
                cursor = end
            if abs(cursor - duration) > 1e-6:
                raise ValueError("Cobertura não alcança duração total")
    evidence = _indexed(data.get("evidence"), "evidence")
    for item in evidence.values():
        if item.get("start_s") is None and item.get("end_s") is None:
            continue
        _interval(item, duration, allow_point=True)
    findings = _indexed(data.get("findings"), "findings")
    for item in findings.values():
        status, ids = item.get("status"), item.get("evidence_ids", [])
        if status not in {"observado", "inferido", "nao_verificavel"}:
            raise ValueError("Status de achado inválido")
        if status != "nao_verificavel" and not ids:
            raise ValueError("Achado sem evidência")
        if not isinstance(ids, list) or any(eid not in evidence for eid in ids):
            raise ValueError("Evidência citada não existe")
        if status == "nao_verificavel" and not item.get("limitations"):
            raise ValueError("Limitação deve ser declarada")
    rules = _indexed(data.get("reusable_rules"), "reusable_rules")
    for item in rules.values():
        ids = item.get("finding_ids", [])
        if not ids or any(fid not in findings for fid in ids):
            raise ValueError("Regra sem achado rastreável")
        if item.get("scope") not in {"pontual", "recorrente", "proposta_condicional"}:
            raise ValueError("Escopo de regra inválido")
    return {"status": "valid", "scope": "structural_only", "external_validation": False}


def validate_frame_manifest(data, *, count, fps, width, height):
    """Exige sequência relativa e contínua; integridade física é etapa separada."""
    for key, expected in (("fps", fps), ("width", width), ("height", height)):
        if _number(data.get(key), key) != expected:
            raise ValueError(f"{key} diverge do contrato")
    frames = data.get("frames", [])
    if not isinstance(frames, list) or len(frames) != count:
        raise ValueError("Contagem de frames divergente")
    names = set()
    for index, frame in enumerate(frames):
        if type(frame.get("index")) is not int or frame["index"] != index:
            raise ValueError("Sequência não contínua")
        name = frame.get("file")
        if not isinstance(name, str) or not name or "\\" in name or ":" in name:
            raise ValueError("Caminho de frame inválido")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or path.suffix != ".png" or name in names:
            raise ValueError("Caminho não confinado ou duplicado")
        names.add(name)
    return {"status": "valid", "frames": count, "physical_integrity_checked": False}


def project_equirectangular(lon, lat, bbox, width, height):
    """WGS84 graus → pixels sem recorte implícito; bbox west,south,east,north."""
    lon, lat = _number(lon, "longitude"), _number(lat, "latitude")
    if not -180 <= lon <= 180 or not -90 <= lat <= 90:
        raise ValueError("Coordenadas fora de WGS84")
    if len(bbox) != 4:
        raise ValueError("bbox deve ter quatro valores")
    west, south, east, north = [_number(x, "bbox") for x in bbox]
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("bbox inválida ou cruza antimeridiano")
    if not west <= lon <= east or not south <= lat <= north:
        raise ValueError("Ponto fora da extensão do mapa")
    if _number(width, "width") <= 0 or _number(height, "height") <= 0:
        raise ValueError("Dimensões devem ser positivas")
    return ((lon - west) * width / (east - west), (north - lat) * height / (north - south))
