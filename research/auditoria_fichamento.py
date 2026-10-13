# -*- coding: utf-8 -*-
"""SPEC-978 — Pasta de auditoria por artigo com fichamento ABNT obrigatório (stdlib-only)."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List

_BLOCKED = ("sci-hub", "scihub")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _norm_doi(doi: str) -> str:
    v = str(doi or "").strip().lower()
    v = re.sub(r"^https?://(dx\.)?doi\.org/", "", v)
    v = re.sub(r"^doi:\s*", "", v)
    return v


def slug_doi(doi: str) -> str:
    n = _norm_doi(doi)
    if not n.startswith("10.") or "/" not in n:
        raise ValueError(f"DOI inválido: {doi!r}")
    s = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return s[:120] or "doi"


def _abnt_ref(meta: Dict) -> str:
    autores = meta.get("autores") or []
    parts = []
    for a in autores[:10]:
        a = str(a).strip()
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            ini = " ".join(f"{p[0].upper()}." for p in first.split() if p)
            parts.append(f"{last.upper()}, {ini}".rstrip(", "))
        else:
            px = a.split()
            if len(px) == 1:
                parts.append(px[0].upper())
            else:
                ini = " ".join(f"{p[0].upper()}." for p in px[:-1] if p)
                parts.append(f"{px[-1].upper()}, {ini}".rstrip(", "))
    aut = "; ".join(parts) if parts else "AUTOR DESCONHECIDO"
    titulo = str(meta.get("titulo") or "[Sem título]").rstrip(".")
    venue = str(meta.get("venue") or meta.get("fonte") or "[S.l.: s.n.]")
    ano = str(meta.get("ano") or "[s.d.]")
    doi = _norm_doi(str(meta.get("doi") or ""))
    ref = f"{aut} {titulo}. **{venue}**, {ano}."
    if doi.startswith("10."):
        ref += f" DOI: https://doi.org/{doi}."
    return ref


def _check_blocked(url: str | None) -> None:
    s = str(url or "").lower()
    for b in _BLOCKED:
        if b in s:
            raise PermissionError(f"blocked: unauthorized_source {url!r}")


def criar_pasta_auditoria(base_dir: str, meta: Dict, pdf_bytes: bytes | None = None,
                          runner_allowed=None) -> str:
    doi = _norm_doi(str(meta.get("doi") or ""))
    if not doi.startswith("10.") or "/" not in doi:
        raise ValueError("meta.doi inválido")
    _check_blocked(meta.get("pdf_url"))
    if runner_allowed is None:
        try:
            from .legal_oa_pipeline import is_download_allowed
            g = is_download_allowed({"license": meta.get("licenca"), "pdf_url": meta.get("pdf_url")})
        except Exception:
            g = {"allowed": False}
    else:
        g = runner_allowed(meta)
    allowed = bool(g.get("allowed"))
    slug = slug_doi(doi)
    pasta = Path(base_dir) / slug
    pasta.mkdir(parents=True, exist_ok=True)
    data = _now()
    pdf_sha = None
    if allowed:
        if pdf_bytes is None or not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("PDF OA ausente ou sem magic %PDF-")
        (pasta / "artigo.pdf").write_bytes(pdf_bytes)
        pdf_sha = hashlib.sha256(pdf_bytes).hexdigest()
    else:
        rota = {"reason": str(g.get("reason") or "closed_access"),
                "rota_institucional": "Assinatura institucional, empréstimo interbibliotecário ou contato com os autores."}
        (pasta / "sem_pdf.json").write_text(json.dumps(rota, ensure_ascii=False, indent=2), encoding="utf-8")
    met = {"doi": doi, "titulo": meta.get("titulo"), "autores": meta.get("autores"),
           "ano": meta.get("ano"), "fonte": meta.get("fonte"), "licenca": meta.get("licenca"),
           "pdf_url": meta.get("pdf_url"), "pdf_sha256": pdf_sha,
           "data_consulta": data,
           "hash_resposta": hashlib.sha256(f"{doi}|{data}".encode()).hexdigest(),
           "allowed": allowed}
    (pasta / "metadados.json").write_text(json.dumps(met, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "recortes.json").write_text("[]", encoding="utf-8")
    fich = [f"# Fichamento — {doi}", "", _abnt_ref(meta), "",
            "## 1. Recortes citados (NBR 10520:2023 — AUTOR, ano, p.)", "",
            "_Nenhum recorte registrado._", "",
            "## 2. Síntese crítica", "",
            "_A preencher com análise vinculada ao tema._", "",
            f"_Proveniência: {met['fonte']} | {met['licenca']} | {data}_"]
    (pasta / "fichamento.md").write_text("\n".join(fich), encoding="utf-8")
    return str(pasta)


def adicionar_recorte(pasta: str, rec: Dict) -> Dict:
    trecho = str(rec.get("trecho_literal") or "")
    pagina = str(rec.get("pagina") or "").strip()
    autor = str(rec.get("autor") or "").strip()
    ano = rec.get("ano")
    just = str(rec.get("justificativa_relevancia") or "")
    mid = str(rec.get("id_trecho_manuscrito") or "").strip()
    if not trecho or len(trecho) > 400:
        raise ValueError("trecho_literal deve ter 1..400 caracteres")
    if not pagina or not autor or not mid:
        raise ValueError("pagina/autor/id_trecho_manuscrito obrigatórios")
    try:
        ano_i = int(ano)
    except Exception:
        raise ValueError("ano obrigatório")
    if len(just.strip()) < 20:
        raise ValueError("justificativa_relevancia mínima 20 caracteres")
    p = Path(pasta)
    rp = p / "recortes.json"
    atual: List[Dict] = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else []
    novo = {"trecho_literal": trecho, "pagina": pagina, "autor": autor, "ano": ano_i,
            "justificativa_relevancia": just.strip(), "id_trecho_manuscrito": mid}
    atual.append(novo)
    rp.write_text(json.dumps(atual, ensure_ascii=False, indent=2), encoding="utf-8")
    fp = p / "fichamento.md"
    txt = fp.read_text(encoding="utf-8")
    bloco = f"\n> {trecho}\n\n— {autor}, {ano_i}, p. {pagina}\n\n**Relevância:** {just.strip()}\n\n**Citada em:** {mid}\n\n---\n"
    if "_Nenhum recorte registrado._" in txt:
        txt = txt.replace("_Nenhum recorte registrado._", bloco.strip())
    else:
        txt += "\n" + bloco
    fp.write_text(txt, encoding="utf-8")
    return novo


def auditar_pasta(pasta: str, citacoes_manuscrito: List[str]) -> Dict:
    p = Path(pasta)
    if not p.is_dir():
        return {"aprovado": False, "motivo": "pasta ausente"}
    if not (p / "metadados.json").exists() or not (p / "fichamento.md").exists():
        return {"aprovado": False, "motivo": "metadados ou fichamento ausente"}
    try:
        recs = json.loads((p / "recortes.json").read_text(encoding="utf-8"))
    except Exception:
        return {"aprovado": False, "motivo": "recortes.json ilegível"}
    cobertos = {str(r.get("id_trecho_manuscrito")) for r in recs}
    faltantes = [c for c in (citacoes_manuscrito or []) if str(c) not in cobertos]
    if faltantes:
        return {"aprovado": False, "motivo": f"citações sem recorte: {faltantes}"}
    return {"aprovado": True, "total_recortes": len(recs)}
