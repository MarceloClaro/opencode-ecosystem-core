# -*- coding: utf-8 -*-
"""R1012 — roteamento de artefatos federados pela quinta cabeça de atenção.

Reutiliza ``transformer.harness_head.HarnessAttentionHead`` (semântica,
capacidade, maturidade, licença) sobre os cartões normalizados. É determinístico
e devolve a decomposição do score — não há caixa-preta.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .store import load_items


def route(
    repo_root: Path,
    description: str,
    required_capabilities: Optional[Sequence[str]] = None,
    *,
    top_k: int = 5,
    include_non_admitted: bool = False,
) -> Dict[str, Any]:
    items = load_items(repo_root)
    if not include_non_admitted:
        items = [item for item in items if item.status == "admitted"]
    if not items:
        return {"status": "empty", "task": description, "considered": 0, "ranking": []}

    from transformer.harness_head import HarnessAttentionHead

    head = HarnessAttentionHead()
    cards = [item.card() for item in items]
    explanation = head.explain(description, list(required_capabilities or []), cards)
    index = {item.item_id: item for item in items}
    ranking: List[Dict[str, Any]] = []
    for item_id, score in explanation["ranking"][: max(1, int(top_k))]:
        item = index.get(item_id)
        if item is None:
            continue
        ranking.append({
            "item_id": item_id,
            "score": round(float(score), 6),
            "name": item.name,
            "ecosystem": item.ecosystem,
            "kind": item.kind,
            "license": item.license or "(não declarada)",
            "install_mode": item.install_mode,
            "status": item.status,
            "source_uri": item.source_uri,
            "source_path": item.source_path,
        })
    return {
        "status": "ok",
        "task": description,
        "required_capabilities": list(required_capabilities or []),
        "considered": len(items),
        "weights": explanation["weights"],
        "ranking": ranking,
    }
