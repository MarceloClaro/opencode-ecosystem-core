# -*- coding: utf-8 -*-
"""SPEC-935-R1089-MCP — servidor MCP stdio local para HDR, RSIR e VRP.

O servidor é deliberadamente limitado: não acessa rede, não lê credenciais,
não executa shell e não abre arquivos arbitrários. Operações que dependeriam
de um backend não observado retornam ``status="unavailable"`` sem resultado
fabricado. As operações locais (validação, PNG, vetores e CVRP clássico) são
determinísticas e testáveis sem dependências externas.

Ferramentas expostas:
  - tiangong_catalog
  - hdr_handler
  - rsir_handler
  - vrp_handler
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import struct
import zlib
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

SERVER_NAME = "tiangong-hdr"

MAX_IMAGE_BYTES = 2_000_000
MAX_IMAGE_DIM = 1024
MAX_VECTOR_DIM = 4096
MAX_VRP_NODES = 200
MAX_VRP_VEHICLES = 64
FEATURE_SIDE = 28
FEATURE_DIM = FEATURE_SIDE * FEATURE_SIDE

SOURCE_HTML_SHA256 = "8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342"
SOURCE_BUNDLES = {
    "HDR": "7f6e3f71fa4fcc42cd6dafef79f881f0a32afe44db43f001eac9893e7d1f9eea",
    "RSIR": "76308919310a4b6235a21fe83a4e96d0b83949f486602ea774998a508ff8c418",
    "VRP": "38acd57efc1fd70229a9fad67bfd0a4c3d2886bc4146d562675de9383397cfe6",
}

BASE_LIMITATIONS = [
    "Análise estática REA; nenhuma execução no backend da Tiangong.",
    "Sem rede, credenciais, shell ou acesso arbitrário a arquivos.",
]

APP_LIMITATIONS = {
    "HDR": [
        "Backend QNN não observado; recognize retorna unavailable e não infere dígito.",
        "PNG suportado: 8 bits, sem entrelaçamento, tipos cinza/RGB/cinza+alfa/RGBA.",
        "Vetor de 784 valores descreve a entrada; não é saída de modelo treinado.",
    ],
    "RSIR": [
        "Modelo ViT/QViT não observado; analyze e classify retornam unavailable.",
        "features apenas valida e resume um vetor fornecido; não classifica sinal.",
        "Não há acesso a dados de sinais de rádio nem a pesos de modelo.",
    ],
    "VRP": [
        "Heurística clássica (vizinho mais próximo + 2-opt); não é QAOA nem prova de otimalidade.",
        "Capacidade é tratada como CVRP simples; janelas de tempo e frota heterogênea não são modeladas.",
        "Não há upload de dataset nem comparação com backend quântico.",
    ],
}

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class _ToolError(Exception):
    """Falha de contrato com código estável para o cliente MCP."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def sha256_hex(data: bytes) -> str:
    """SHA-256 hexadecimal, usado também pelos testes de determinismo."""
    return hashlib.sha256(data).hexdigest()


def _evidence(app: str | None) -> dict[str, Any]:
    return {
        "source_html_sha256": SOURCE_HTML_SHA256 if app else None,
        "source_bundle_sha256": SOURCE_BUNDLES.get(app) if app else None,
        "method": "static_analysis_REA",
        "provider": "REA_6.8.0_static_analysis",
    }


def _envelope(
    status: str,
    *,
    app: str | None = None,
    technique: str | None = None,
    result: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    limits = list(BASE_LIMITATIONS)
    if app:
        limits.extend(APP_LIMITATIONS.get(app, []))
    if limitations:
        limits.extend(limitations)
    return {
        "status": status,
        "app": app,
        "technique": technique,
        "result": result if result is not None else {},
        "evidence": _evidence(app),
        "limitations": limits,
    }


def _error(code: str, message: str, *, app: str | None = None,
           technique: str | None = None) -> dict[str, Any]:
    return _envelope(
        "error",
        app=app,
        technique=technique,
        result={"code": code, "message": message},
        limitations=[message],
    )


def _unavailable(code: str, message: str, *, app: str,
                 technique: str, result: dict[str, Any]) -> dict[str, Any]:
    payload = {"code": code, "message": message}
    payload.update(result)
    return _envelope(
        "unavailable",
        app=app,
        technique=technique,
        result=payload,
        limitations=[message],
    )


# ── vetores ─────────────────────────────────────────────────────────────────


def _vector(value: Any, *, code: str = "invalid_vector") -> list[float]:
    if not isinstance(value, list) or not value:
        raise _ToolError(code, "o vetor deve ser uma lista não vazia de números.")
    if len(value) > MAX_VECTOR_DIM:
        raise _ToolError("limit_exceeded", f"vetor acima de {MAX_VECTOR_DIM} dimensões.")
    out: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise _ToolError(code, "o vetor contém valor não numérico.")
        number = float(item)
        if not math.isfinite(number):
            raise _ToolError(code, "o vetor contém número não finito.")
        out.append(number)
    return out


def _finite(value: Any, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _ToolError("invalid_payload", f"{field} deve ser numérico.")
    number = float(value)
    if not math.isfinite(number):
        raise _ToolError("invalid_payload", f"{field} deve ser finito.")
    return number


def _stats(vector: list[float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vector))
    return {
        "dimension": len(vector),
        "l2_norm": round(norm, 6),
        "mean": round(sum(vector) / len(vector), 6),
        "min": round(min(vector), 6),
        "max": round(max(vector), 6),
    }


# ── PNG (stdlib, sem Pillow) ────────────────────────────────────────────────


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _png_gray(data: bytes) -> tuple[int, int, list[float]]:
    """Decodifica PNG 8 bits não entrelaçado e devolve cinza em 0..255."""
    if not data.startswith(_PNG_SIGNATURE):
        raise _ToolError("unsupported_image_format", "a entrada não é um PNG.")

    position = len(_PNG_SIGNATURE)
    header: bytes | None = None
    compressed = bytearray()
    saw_end = False

    while position + 8 <= len(data):
        length = struct.unpack(">I", data[position:position + 4])[0]
        tag = data[position + 4:position + 8]
        start = position + 8
        end = start + length
        if end + 4 > len(data):
            raise _ToolError("invalid_image", "chunk PNG truncado.")
        payload = data[start:end]
        crc = struct.unpack(">I", data[end:end + 4])[0]
        if zlib.crc32(tag + payload) & 0xFFFFFFFF != crc:
            raise _ToolError("invalid_image", "CRC de chunk PNG inválido.")
        position = end + 4
        if tag == b"IHDR":
            header = payload
        elif tag == b"IDAT":
            compressed.extend(payload)
        elif tag == b"IEND":
            saw_end = True
            break

    if header is None or len(header) != 13 or not saw_end:
        raise _ToolError("invalid_image", "PNG sem IHDR/IEND válidos.")
    if not compressed:
        raise _ToolError("invalid_image", "PNG sem dados IDAT.")

    width, height, depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", header)
    )
    if width == 0 or height == 0:
        raise _ToolError("invalid_image", "dimensões PNG inválidas.")
    if width > MAX_IMAGE_DIM or height > MAX_IMAGE_DIM:
        raise _ToolError("limit_exceeded", f"imagem acima de {MAX_IMAGE_DIM}x{MAX_IMAGE_DIM}.")
    if depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
        raise _ToolError(
            "unsupported_image_format",
            "PNG suportado apenas em 8 bits, sem entrelaçamento.",
        )
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise _ToolError("unsupported_image_format", "tipo de cor PNG não suportado.")

    stride = width * channels
    expected = height * (stride + 1)
    try:
        decompressor = zlib.decompressobj()
        raw = decompressor.decompress(bytes(compressed), expected + 1)
    except zlib.error as exc:
        raise _ToolError("invalid_image", "IDAT PNG não descompacta.") from exc
    if len(raw) != expected or not decompressor.eof or decompressor.unused_data:
        raise _ToolError("invalid_image", "tamanho de pixel PNG inconsistente.")

    previous = bytearray(stride)
    gray: list[float] = []
    cursor = 0

    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor:cursor + stride])
        cursor += stride

        if filter_type == 0:
            pass
        elif filter_type == 1:
            for index in range(channels, stride):
                row[index] = (row[index] + row[index - channels]) & 0xFF
        elif filter_type == 2:
            for index in range(stride):
                row[index] = (row[index] + previous[index]) & 0xFF
        elif filter_type == 3:
            for index in range(stride):
                left = row[index - channels] if index >= channels else 0
                row[index] = (row[index] + ((left + previous[index]) >> 1)) & 0xFF
        elif filter_type == 4:
            for index in range(stride):
                left = row[index - channels] if index >= channels else 0
                upper = previous[index]
                upper_left = previous[index - channels] if index >= channels else 0
                row[index] = (row[index] + _paeth(left, upper, upper_left)) & 0xFF
        else:
            raise _ToolError("invalid_image", "filtro PNG desconhecido.")

        if color_type == 0:
            gray.extend(float(value) for value in row)
        elif color_type == 4:
            gray.extend(float(value) for value in row[0::2])
        elif color_type == 2:
            for index in range(0, stride, 3):
                gray.append(
                    0.299 * row[index] + 0.587 * row[index + 1] + 0.114 * row[index + 2]
                )
        else:
            for index in range(0, stride, 4):
                gray.append(
                    0.299 * row[index] + 0.587 * row[index + 1] + 0.114 * row[index + 2]
                )

        previous = row

    return width, height, gray


def _pixels_gray(pixels: Any) -> tuple[int, int, list[float]]:
    if not isinstance(pixels, list) or not pixels:
        raise _ToolError("invalid_pixels", "pixels deve ser uma matriz não vazia.")
    if len(pixels) > MAX_IMAGE_DIM:
        raise _ToolError("limit_exceeded", f"matriz acima de {MAX_IMAGE_DIM} linhas.")

    width: int | None = None
    flat: list[float] = []
    for row in pixels:
        if not isinstance(row, list) or not row:
            raise _ToolError("invalid_pixels", "cada linha deve ser uma lista não vazia.")
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _ToolError("invalid_pixels", "linhas com larguras diferentes.")
        if width > MAX_IMAGE_DIM:
            raise _ToolError("limit_exceeded", f"matriz acima de {MAX_IMAGE_DIM} colunas.")
        for item in row:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise _ToolError("invalid_pixels", "pixels contém valor não numérico.")
            number = float(item)
            if not math.isfinite(number) or number < 0 or number > 255:
                raise _ToolError("invalid_pixels", "pixels deve estar em 0..255.")
            flat.append(number)
    assert width is not None
    return width, len(pixels), flat


def _resample(values: list[float], width: int, height: int,
              out_width: int = FEATURE_SIDE, out_height: int = FEATURE_SIDE) -> list[float]:
    result: list[float] = []
    for out_y in range(out_height):
        y0 = (out_y * height) // out_height
        y1 = max(y0 + 1, ((out_y + 1) * height + out_height - 1) // out_height)
        y1 = min(y1, height)
        for out_x in range(out_width):
            x0 = (out_x * width) // out_width
            x1 = max(x0 + 1, ((out_x + 1) * width + out_width - 1) // out_width)
            x1 = min(x1, width)
            total = 0.0
            count = 0
            for y in range(y0, y1):
                base = y * width
                for x in range(x0, x1):
                    total += values[base + x]
                    count += 1
            result.append(total / count)
    return result


def _feature_vector(gray: list[float], width: int, height: int) -> list[float]:
    resampled = _resample(gray, width, height)
    return [round(min(1.0, max(0.0, value / 255.0)), 6) for value in resampled]


def _image_feature(image_base64: str | None, pixels: Any) -> tuple[list[float], str]:
    if image_base64 is not None:
        if not isinstance(image_base64, str) or not image_base64:
            raise _ToolError("invalid_image", "image_base64 deve ser texto não vazio.")
        if len(image_base64) > (MAX_IMAGE_BYTES * 4 // 3) + 8:
            raise _ToolError("payload_too_large", f"imagem acima de {MAX_IMAGE_BYTES} bytes.")
        try:
            data = base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise _ToolError("invalid_image", "image_base64 não é base64 válido.") from exc
        if len(data) > MAX_IMAGE_BYTES:
            raise _ToolError("payload_too_large", f"imagem acima de {MAX_IMAGE_BYTES} bytes.")
        width, height, gray = _png_gray(data)
        return _feature_vector(gray, width, height), sha256_hex(data)

    if pixels is not None:
        width, height, gray = _pixels_gray(pixels)
        canonical = json.dumps(pixels, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return _feature_vector(gray, width, height), sha256_hex(canonical)

    raise _ToolError("missing_input", "informe image_base64 (PNG) ou pixels.")


# ── catálogo ────────────────────────────────────────────────────────────────


def _app_catalog(app: str, actions: list[str], available: list[str],
                 unavailable: list[str]) -> dict[str, Any]:
    return {
        "app": app,
        "actions": actions,
        "available_actions": available,
        "unavailable_actions": unavailable,
        "source_html_sha256": SOURCE_HTML_SHA256,
        "source_bundle_sha256": SOURCE_BUNDLES[app],
        "limitations": APP_LIMITATIONS[app],
    }


def catalog() -> dict[str, Any]:
    """Lista aplicações, ações e limites; não acessa rede."""
    apps = [
        _app_catalog(
            "HDR",
            ["validate", "preprocess", "recognize", "compare", "export"],
            ["validate", "preprocess", "compare", "export"],
            ["recognize"],
        ),
        _app_catalog(
            "RSIR",
            ["validate", "features", "analyze", "classify"],
            ["validate", "features"],
            ["analyze", "classify"],
        ),
        _app_catalog(
            "VRP",
            ["validate", "solve", "upload"],
            ["validate", "solve"],
            ["upload"],
        ),
    ]
    return _envelope(
        "success",
        technique="static-analysis-catalog",
        result={
            "apps": apps,
            "network": False,
            "credentials_required": False,
            "server": SERVER_NAME,
        },
    )


# ── HDR ─────────────────────────────────────────────────────────────────────


def hdr_handler(
    action: str | None = None,
    image_base64: str | None = None,
    pixels: Any = None,
    image_path: str | None = None,
    left: Any = None,
    right: Any = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Handler HDR: valida, pré-processa, compara e declara indisponibilidade."""
    del metadata  # aceito no contrato, sem efeito local
    if image_path is not None:
        return _error(
            "path_not_allowed",
            "image_path não é aceito; use image_base64 ou pixels.",
            app="HDR",
            technique="canvas-processing",
        )
    if not action:
        return _error("missing_action", "action é obrigatória.", app="HDR")
    if action not in {"validate", "preprocess", "recognize", "compare", "export"}:
        return _error("invalid_action", f"action desconhecida: {action}.", app="HDR")

    try:
        if action == "recognize":
            return _unavailable(
                "provider_not_implemented",
                "Backend QNN não observado; nenhum dígito é inferido localmente.",
                app="HDR",
                technique="QNN-handler",
                result={"digit": None, "confidence": None, "processed_image": None},
            )

        if action == "validate":
            provided = [
                name for name, value in (
                    ("image_base64", image_base64), ("pixels", pixels),
                    ("left", left), ("right", right),
                ) if value is not None
            ]
            return _envelope(
                "success",
                app="HDR",
                technique="canvas-processing",
                result={"valid": True, "provided": provided, "actions": [
                    "validate", "preprocess", "recognize", "compare", "export"]},
            )

        if action in {"preprocess", "export"}:
            vector, digest = _image_feature(image_base64, pixels)
            result: dict[str, Any] = {
                "feature_dim": FEATURE_DIM,
                "feature_vector": vector,
                "input_sha256": digest,
            }
            if action == "export":
                result.update({"format": "json", "persisted": False})
            return _envelope(
                "success",
                app="HDR",
                technique="canvas-processing",
                result=result,
            )

        # compare
        if left is None or right is None:
            raise _ToolError("missing_input", "compare exige left e right.")
        first = _vector(left)
        second = _vector(right)
        if len(first) != len(second):
            raise _ToolError("dimension_mismatch", "left e right têm dimensões diferentes.")
        l1 = sum(abs(a - b) for a, b in zip(first, second))
        l2 = math.sqrt(sum((a - b) ** 2 for a, b in zip(first, second)))
        norm_first = math.sqrt(sum(a * a for a in first))
        norm_second = math.sqrt(sum(b * b for b in second))
        dot = sum(a * b for a, b in zip(first, second))
        cosine = 0.0 if norm_first == 0 or norm_second == 0 else dot / (norm_first * norm_second)
        return _envelope(
            "success",
            app="HDR",
            technique="vector-comparison",
            result={
                "dimension": len(first),
                "l1": round(l1, 6),
                "l2": round(l2, 6),
                "cosine": round(cosine, 6),
            },
        )
    except _ToolError as exc:
        return _error(exc.code, exc.message, app="HDR")
    except (TypeError, ValueError) as exc:
        return _error("invalid_payload", str(exc), app="HDR")


# ── RSIR ────────────────────────────────────────────────────────────────────


def rsir_handler(
    action: str | None = None,
    features: Any = None,
    expected_dim: int = 768,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Handler RSIR: valida vetor e declara modelo indisponível."""
    del metadata
    if not action:
        return _error("missing_action", "action é obrigatória.", app="RSIR")
    if action not in {"validate", "features", "analyze", "classify"}:
        return _error("invalid_action", f"action desconhecida: {action}.", app="RSIR")

    if action in {"analyze", "classify"}:
        technique = "ViT-inference" if action == "analyze" else "QViT-inference"
        return _unavailable(
            "provider_not_implemented",
            "Modelo ViT/QViT não observado; nenhum rótulo é inferido localmente.",
            app="RSIR",
            technique=technique,
            result={"class_label": None, "probabilities": None, "quantum_enhanced": None},
        )

    try:
        if action == "validate":
            return _envelope(
                "success",
                app="RSIR",
                technique="signal-validation",
                result={"valid": True, "expected_dim": expected_dim,
                        "actions": ["validate", "features", "analyze", "classify"]},
            )
        if isinstance(expected_dim, bool) or not isinstance(expected_dim, int):
            raise _ToolError("invalid_payload", "expected_dim deve ser inteiro.")
        if expected_dim < 1 or expected_dim > MAX_VECTOR_DIM:
            raise _ToolError("limit_exceeded", f"expected_dim fora de 1..{MAX_VECTOR_DIM}.")
        vector = _vector(features)
        if len(vector) != expected_dim:
            raise _ToolError(
                "dimension_mismatch",
                f"vetor com {len(vector)} dimensões; esperado {expected_dim}.",
            )
        return _envelope(
            "success",
            app="RSIR",
            technique="signal-features",
            result=_stats(vector),
        )
    except _ToolError as exc:
        return _error(exc.code, exc.message, app="RSIR")


# ── VRP ─────────────────────────────────────────────────────────────────────


def _normalize_vrp(
    nodes: Any,
    vehicles: Any,
    depot: Any,
    n_vehicles: Any,
    capacity: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if not isinstance(nodes, list) or not nodes:
        raise _ToolError("invalid_payload", "nodes deve ser uma lista não vazia.")
    if len(nodes) > MAX_VRP_NODES:
        raise _ToolError("limit_exceeded", f"nodes acima de {MAX_VRP_NODES}.")

    normalized_nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise _ToolError("invalid_payload", "cada nó deve ser um objeto.")
        raw_id = node.get("id")
        if raw_id is None:
            raise _ToolError("invalid_payload", "nó sem id.")
        node_id = str(raw_id)
        if node_id in seen:
            raise _ToolError("invalid_payload", f"id de nó duplicado: {node_id}.")
        seen.add(node_id)
        demand = _finite(node.get("demand", 0), field=f"demand do nó {node_id}")
        if demand < 0:
            raise _ToolError("invalid_payload", f"demand negativa no nó {node_id}.")
        normalized_nodes.append({
            "id": node_id,
            "x": _finite(node.get("x"), field=f"x do nó {node_id}"),
            "y": _finite(node.get("y"), field=f"y do nó {node_id}"),
            "demand": demand,
        })

    if vehicles is None:
        if n_vehicles is None or capacity is None:
            raise _ToolError("invalid_payload", "informe vehicles ou n_vehicles+capacity.")
        if isinstance(n_vehicles, bool) or not isinstance(n_vehicles, int) or n_vehicles < 1:
            raise _ToolError("invalid_payload", "n_vehicles deve ser inteiro positivo.")
        if n_vehicles > MAX_VRP_VEHICLES:
            raise _ToolError("limit_exceeded", f"n_vehicles acima de {MAX_VRP_VEHICLES}.")
        capacity_value = _finite(capacity, field="capacity")
        if capacity_value <= 0:
            raise _ToolError("invalid_payload", "capacity deve ser positiva.")
        vehicles = [
            {"id": f"v{index + 1}", "capacity": capacity_value}
            for index in range(n_vehicles)
        ]

    if not isinstance(vehicles, list) or not vehicles:
        raise _ToolError("invalid_payload", "vehicles deve ser uma lista não vazia.")
    if len(vehicles) > MAX_VRP_VEHICLES:
        raise _ToolError("limit_exceeded", f"vehicles acima de {MAX_VRP_VEHICLES}.")

    normalized_vehicles: list[dict[str, Any]] = []
    for index, vehicle in enumerate(vehicles):
        if not isinstance(vehicle, dict):
            raise _ToolError("invalid_payload", "cada veículo deve ser um objeto.")
        vehicle_id = str(vehicle.get("id", f"v{index + 1}"))
        vehicle_capacity = _finite(
            vehicle.get("capacity"), field=f"capacity do veículo {vehicle_id}"
        )
        if vehicle_capacity <= 0:
            raise _ToolError("invalid_payload", f"capacity inválida no veículo {vehicle_id}.")
        normalized_vehicles.append({"id": vehicle_id, "capacity": vehicle_capacity})

    depot_id = str(depot) if depot is not None else normalized_nodes[0]["id"]
    if depot_id not in seen:
        raise _ToolError("invalid_payload", f"depot inexistente: {depot_id}.")
    return normalized_nodes, normalized_vehicles, depot_id


def _distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    return math.hypot(first["x"] - second["x"], first["y"] - second["y"])


def _two_opt(route: list[str], by_id: dict[str, dict[str, Any]]) -> list[str]:
    best = list(route)
    improved = True
    passes = 0
    while improved and passes < 50:
        improved = False
        passes += 1
        for start in range(1, len(best) - 2):
            for end in range(start + 1, len(best) - 1):
                a = by_id[best[start - 1]]
                b = by_id[best[start]]
                c = by_id[best[end]]
                d = by_id[best[end + 1]]
                delta = (
                    _distance(a, c) + _distance(b, d)
                    - _distance(a, b) - _distance(c, d)
                )
                if delta < -1e-9:
                    best[start:end + 1] = reversed(best[start:end + 1])
                    improved = True
    return best


def _route_distance(route: list[str], by_id: dict[str, dict[str, Any]]) -> float:
    return sum(
        _distance(by_id[first], by_id[second])
        for first, second in zip(route, route[1:])
    )


def _solve_vrp(
    nodes: list[dict[str, Any]],
    vehicles: list[dict[str, Any]],
    depot_id: str,
) -> dict[str, Any]:
    by_id = {node["id"]: node for node in nodes}
    depot_node = by_id[depot_id]
    unvisited = [node for node in nodes if node["id"] != depot_id]
    routes: list[dict[str, Any]] = []

    for vehicle in vehicles:
        route = [depot_id]
        load = 0.0
        current = depot_node
        while True:
            candidates = [
                node for node in unvisited
                if load + node["demand"] <= vehicle["capacity"] + 1e-9
            ]
            if not candidates:
                break
            chosen = min(candidates, key=lambda node: (_distance(current, node), node["id"]))
            route.append(chosen["id"])
            load += chosen["demand"]
            current = chosen
            unvisited.remove(chosen)
        route.append(depot_id)
        improved = _two_opt(route, by_id)
        routes.append({
            "vehicle_id": vehicle["id"],
            "node_ids": improved,
            "load": round(load, 6),
            "distance": round(_route_distance(improved, by_id), 6),
        })

    unserved = sorted(node["id"] for node in unvisited)
    total_distance = round(sum(route["distance"] for route in routes), 6)
    return {
        "backend": "classical-heuristic",
        "quantum": False,
        "optimality": "not_proven",
        "feasible": not unserved,
        "routes": routes,
        "total_distance": total_distance,
        "unserved": unserved,
        "served_nodes": len(nodes) - 1 - len(unserved),
    }


def vrp_handler(
    action: str | None = None,
    nodes: Any = None,
    vehicles: Any = None,
    depot: Any = None,
    n_vehicles: Any = None,
    capacity: Any = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Handler VRP: valida CVRP e resolve com heurística clássica determinística."""
    del metadata
    if not action:
        return _error("missing_action", "action é obrigatória.", app="VRP")
    if action not in {"validate", "solve", "upload"}:
        return _error("invalid_action", f"action desconhecida: {action}.", app="VRP")

    if action == "upload":
        return _unavailable(
            "provider_not_implemented",
            "Upload de dataset não é implementado; envie nodes/vehicles no payload.",
            app="VRP",
            technique="dataset-upload",
            result={"persisted": False},
        )

    try:
        normalized_nodes, normalized_vehicles, depot_id = _normalize_vrp(
            nodes, vehicles, depot, n_vehicles, capacity
        )
        total_demand = sum(node["demand"] for node in normalized_nodes)
        total_capacity = sum(vehicle["capacity"] for vehicle in normalized_vehicles)
        largest_demand = max(node["demand"] for node in normalized_nodes)
        max_capacity = max(vehicle["capacity"] for vehicle in normalized_vehicles)

        if action == "validate":
            return _envelope(
                "success",
                app="VRP",
                technique="cvrp-validation",
                result={
                    "n_nodes": len(normalized_nodes),
                    "n_vehicles": len(normalized_vehicles),
                    "total_demand": round(total_demand, 6),
                    "capacity": round(total_capacity, 6),
                    "feasible_precheck": (
                        total_demand <= total_capacity and largest_demand <= max_capacity
                    ),
                },
            )

        solved = _solve_vrp(normalized_nodes, normalized_vehicles, depot_id)
        limitations = []
        if not solved["feasible"]:
            limitations.append(
                "Instância inviável com a frota informada; nós não atendidos foram listados."
            )
        return _envelope(
            "success",
            app="VRP",
            technique="classical-heuristic",
            result=solved,
            limitations=limitations,
        )
    except _ToolError as exc:
        return _error(exc.code, exc.message, app="VRP")


# ── servidor ────────────────────────────────────────────────────────────────


def create_server() -> FastMCP:
    """Cria o servidor FastMCP com as quatro ferramentas locais."""
    server = FastMCP(SERVER_NAME)
    read_only = ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, openWorldHint=False
    )

    @server.tool(name="tiangong_catalog", annotations=read_only)
    def tiangong_catalog() -> dict[str, Any]:
        """Lista HDR/RSIR/VRP, ações disponíveis e limites; não acessa rede."""
        return catalog()

    @server.tool(name="hdr_handler", annotations=read_only)
    def hdr_tool(
        action: str,
        image_base64: str | None = None,
        pixels: Any = None,
        image_path: str | None = None,
        left: Any = None,
        right: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """HDR: validate, preprocess (PNG/pixels), compare, export; recognize indisponível."""
        return hdr_handler(
            action=action,
            image_base64=image_base64,
            pixels=pixels,
            image_path=image_path,
            left=left,
            right=right,
            metadata=metadata,
        )

    @server.tool(name="rsir_handler", annotations=read_only)
    def rsir_tool(
        action: str,
        features: Any = None,
        expected_dim: int = 768,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """RSIR: validate/features locais; analyze/classify indisponíveis."""
        return rsir_handler(
            action=action,
            features=features,
            expected_dim=expected_dim,
            metadata=metadata,
        )

    @server.tool(name="vrp_handler", annotations=read_only)
    def vrp_tool(
        action: str,
        nodes: Any = None,
        vehicles: Any = None,
        depot: Any = None,
        n_vehicles: Any = None,
        capacity: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """VRP: validate/solve com heurística clássica; upload indisponível."""
        return vrp_handler(
            action=action,
            nodes=nodes,
            vehicles=vehicles,
            depot=depot,
            n_vehicles=n_vehicles,
            capacity=capacity,
            metadata=metadata,
        )

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
