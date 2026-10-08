# -*- coding: utf-8 -*-
"""Parecer técnico sem decidir (SPEC-935-R722).

Só leitura local de clones. Opinião para ratificação titular, nunca decisão.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
from typing import Any, Dict, List

SPEC_ID = "SPEC-935-R722"
GERADOR = "marceloclaro"


def parecer(url: str, clone_path: str, licenca: str, capacidades: List[str]) -> Dict[str, Any]:
    """Pontua maturidade 0-10 e recomenda sem decidir."""
    def existe(*parts: str) -> bool:
        return os.path.exists(os.path.join(clone_path, *parts))
    def arquivo(*parts: str) -> int:
        try:
            return os.path.getsize(os.path.join(clone_path, *parts))
        except OSError:
            return 0
    readme_txt = ""
    for cand in ("README.md", "README.rst", "README"):
        try:
            with open(os.path.join(clone_path, cand), encoding="utf-8", errors="ignore") as fh:
                readme_txt = fh.read()
            if readme_txt.strip():
                break
        except OSError:
            continue
    pontos, riscos, pend = 0, [], []
    if readme_txt.strip():
        pontos += 2
        if len(readme_txt) < 200:
            riscos.append("README < 200 chars")
            pend.append("ampliar evidência documental antes da federação")
    else:
        riscos.append("README ausente ou ilegível")
        pend.append("exigir descrição auditável")
    if any(existe(m) for m in ("LICENSE", "LICENSE.txt", "LICENSE.md")) or (licenca or "").strip():
        pontos += 2
    else:
        riscos.append("licença ausente")
        pend.append("confirmar licença com evidência")
    if existe("tests") or existe("test"):
        pontos += 2
    else:
        riscos.append("sem diretório tests")
        pend.append("avaliar cobertura fora do gate antes de federar")
    if any(existe(m) for m in ("pyproject.toml", "setup.py", "setup.cfg")):
        pontos += 1
    else:
        riscos.append("sem manifesto de pacote")
    if existe("docs"):
        pontos += 1
    if existe("examples"):
        pontos += 1
    if existe("CITATION.cff"):
        pontos += 1
    maturidade = min(10, pontos)
    if not readme_txt.strip() or maturidade <= 3:
        rec = "aguardar_evidencia"
    elif riscos:
        rec = "ratificar_com_ressalvas"
    else:
        rec = "ratificar_com_ressalvas"
    return {"url": url, "maturidade": maturidade, "licenca": licenca or "",
            "capacidades": list(capacidades), "riscos": riscos,
            "pendencias_ratificacao": pend, "recomendacao_tecnica": rec,
            "opiniao_tecnica": True, "ratificacao_titular_pendente": True,
            "readme_chars": len(readme_txt)}


def emitir_pareceres(minutas: List[Dict[str, str]], clones: Dict[str, str], destino_dir: str) -> Dict[str, Any]:
    """Escreve pareceres.json para lista de minutas."""
    os.makedirs(destino_dir, exist_ok=True)
    pareceres = []
    for m in minutas:
        url = str(m["url"])
        pareceres.append(parecer(url, clones.get(url, ""), str(m.get("licenca", "")),
                                 list(m.get("capacidades", []))))
    payload = {"spec_id": SPEC_ID, "gerador": GERADOR,
               "gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "total": len(pareceres), "pareceres": pareceres,
               "rotulo": "candidato_a_inspecao", "nota": "Opiniões para ratificação; nada decidido."}
    alvo = os.path.join(destino_dir, "pareceres.json")
    with open(alvo, "w", encoding="utf-8") as fh:
        json.dump(copy.deepcopy(payload), fh, ensure_ascii=False, indent=2)
    return {"ok": True, "arquivo": alvo, "total": len(pareceres)}
