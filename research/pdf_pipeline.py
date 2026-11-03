# -*- coding: utf-8 -*-
"""SPEC-935-R1008 — PDF legal → auditoria → fichamento → resenha → RAG.

O pipeline nunca inventa tradução ou argumento: quando o tradutor/argumentador
não existe ou falha na validação, o campo fica `pending`/`rejected` e o texto
original permanece como única evidência.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from research.auditoria_fichamento import _abnt_ref, criar_pasta_auditoria
from research.oa_resolver import openalex_runner, openalex_work, resolve
from research.source_policy import is_blocked_url

MAX_PDF_BYTES = 52_428_800  # 50 MiB
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")

Translator = Callable[[str, str], str | None]
Argumenter = Callable[[dict[str, Any]], Mapping[str, Any] | None]
Fetcher = Callable[[str], tuple[int, Mapping[str, str], bytes]]


def _now(now: str | None = None) -> str:
    return now or datetime.datetime.now(datetime.timezone.utc).isoformat()


def _clean(text: str) -> str:
    text = str(text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _surname(meta: Mapping[str, Any]) -> str:
    autores = meta.get("autores") or []
    if not autores:
        return "AUTOR"
    first = str(autores[0]).strip()
    if "," in first:
        return first.split(",", 1)[0].strip() or "AUTOR"
    parts = first.split()
    return parts[-1] if parts else "AUTOR"


def citation(meta: Mapping[str, Any], page: int) -> str:
    ano = meta.get("ano") or "[s.d.]"
    return f"({_surname(meta).upper()}, {ano}, p. {page})"


def _numbers(text: str) -> set[str]:
    return set(_NUMBER_RE.findall(str(text or "")))


def validate_translation(source: str, target: str | None) -> tuple[bool, str]:
    """Anti-fabricação: não aceitar números que o original não tem."""
    if not isinstance(target, str) or len(target.strip()) < 10:
        return False, "empty_translation"
    ratio = len(target) / max(1, len(source))
    if not 0.3 <= ratio <= 3.0:
        return False, "length_ratio_out_of_range"
    invented = _numbers(target) - _numbers(source)
    if invented:
        return False, f"fabricated_numbers:{','.join(sorted(invented))}"
    return True, ""


def validate_argumentation(
    arg: Mapping[str, Any] | None, meta: Mapping[str, Any]
) -> tuple[bool, str]:
    if not isinstance(arg, Mapping):
        return False, "not_object"
    just = str(arg.get("justificativa") or "").strip()
    argu = str(arg.get("argumento") or "").strip()
    if len(just) < 40:
        return False, "justificativa_curta"
    if len(argu) < 40:
        return False, "argumento_curto"
    blob = f"{just} {argu}".lower()
    surname = _surname(meta).lower()
    ano = str(meta.get("ano") or "")
    if surname and surname not in blob and "autor" not in blob:
        return False, "autor_ausente"
    if ano and ano not in blob and "ano" not in blob:
        return False, "ano_ausente"
    return True, ""


# ── download e extração ─────────────────────────────────────────────────────


def fetch_pdf(url: str, *, fetcher: Fetcher | None, max_bytes: int = MAX_PDF_BYTES) -> bytes:
    if is_blocked_url(url):
        raise PermissionError(f"blocked: unauthorized_source {url!r}")
    if fetcher is None:
        raise RuntimeError("unavailable: fetcher ausente")
    status, headers, body = fetcher(url)
    if status != 200:
        raise ValueError(f"HTTP {status}")
    if len(body) > max_bytes:
        raise ValueError("PDF acima do limite")
    content_type = str((headers or {}).get("content-type", "")).lower()
    if "application/pdf" not in content_type and not body.startswith(b"%PDF-"):
        raise ValueError("resposta não é PDF")
    if not body.startswith(b"%PDF-"):
        raise ValueError("magic %PDF- ausente")
    return body


def http_fetcher(url: str, timeout: int = 60) -> tuple[int, Mapping[str, str], bytes]:
    """Fetcher padrão via urllib. Só é usado quando escolhido explicitamente."""
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "opencode-core-pdf/1.0", "Accept": "application/pdf"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 — URL já validada
        body = response.read(MAX_PDF_BYTES + 1)
        return response.status, dict(response.headers), body


def extract_pages(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Extrai texto por página; página sem texto é marcada como vazia."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[dict[str, Any]] = []
    for index, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        pages.append({"page": index, "text": _clean(raw), "empty": not raw.strip()})
    return pages


def select_excerpts(
    pages: Sequence[Mapping[str, Any]],
    *,
    max_excerpts: int = 8,
    min_len: int = 80,
    max_len: int = 600,
    keywords: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Seleção determinística de frases citáveis, com página e posição."""
    keys = [k.lower() for k in keywords if str(k).strip()]
    candidates: list[dict[str, Any]] = []
    ordinal = 0
    for page in pages:
        body = " ".join(str(page.get("text") or "").split())
        for sentence in _SENTENCE_RE.split(body):
            text = sentence.strip()
            if not (min_len <= len(text) <= max_len):
                continue
            low = text.lower()
            score = 1.0 + sum(1.0 for k in keys if k in low)
            if re.search(r"\b(19|20)\d{2}\b", text):
                score += 1.0
            if _NUMBER_RE.search(text):
                score += 0.5
            candidates.append(
                {
                    "page": int(page["page"]),
                    "text": text,
                    "score": round(score, 3),
                    "ordinal": ordinal,
                }
            )
            ordinal += 1

    chosen = sorted(candidates, key=lambda c: (-c["score"], c["page"], c["ordinal"]))[:max_excerpts]
    chosen.sort(key=lambda c: (c["page"], c["ordinal"]))
    return chosen


# ── fichamento ──────────────────────────────────────────────────────────────


def enrich_excerpts(
    excerpts: Sequence[Mapping[str, Any]],
    meta: Mapping[str, Any],
    *,
    translator: Translator | None = None,
    argumenter: Argumenter | None = None,
    target_lang: str = "pt-BR",
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []

    for excerpt in excerpts:
        text = str(excerpt["text"])
        page = int(excerpt["page"])

        translation: dict[str, Any]
        if translator is None:
            translation = {"status": "pending", "text": None, "reason": "translator_absent"}
        else:
            try:
                target = translator(text, target_lang)
            except Exception as exc:  # noqa: BLE001
                translation = {"status": "rejected", "text": None, "reason": f"translator_error:{type(exc).__name__}"}
            else:
                ok, reason = validate_translation(text, target)
                translation = {
                    "status": "ok" if ok else "rejected",
                    "text": target if ok else None,
                    "reason": reason,
                }

        argumentation: dict[str, Any]
        if argumenter is None:
            argumentation = {
                "status": "pending",
                "justificativa": None,
                "argumento": None,
                "reason": "argumenter_absent",
            }
        else:
            try:
                arg = argumenter(
                    {
                        "trecho": text,
                        "pagina": page,
                        "citacao": citation(meta, page),
                        "titulo": meta.get("titulo"),
                        "autores": list(meta.get("autores") or []),
                        "ano": meta.get("ano"),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                argumentation = {
                    "status": "rejected",
                    "justificativa": None,
                    "argumento": None,
                    "reason": f"argumenter_error:{type(exc).__name__}",
                }
            else:
                ok, reason = validate_argumentation(arg, meta)
                argumentation = {
                    "status": "ok" if ok else "rejected",
                    "justificativa": str(arg.get("justificativa") or "").strip() if ok else None,
                    "argumento": str(arg.get("argumento") or "").strip() if ok else None,
                    "reason": reason,
                }

        enriched.append(
            {
                "page": page,
                "ordinal": excerpt.get("ordinal"),
                "text": text,
                "citation": citation(meta, page),
                "translation": translation,
                "argumentation": argumentation,
            }
        )

    return enriched


def _pendente(label: str, info: Mapping[str, Any]) -> str:
    reason = info.get("reason") or "não fornecido"
    return f"_Pendente — {label} não validada ({reason}). Nenhum texto foi inventado._"


def write_fichamento(
    pasta: str | Path,
    meta: Mapping[str, Any],
    enriched: Sequence[Mapping[str, Any]],
    *,
    now: str | None = None,
) -> str:
    linhas = [
        f"# Fichamento crítico — {meta.get('titulo') or '[Sem título]'}",
        "",
        f"**Referência (ABNT):** {_abnt_ref(dict(meta))}",
        "",
        f"**DOI:** {meta.get('doi')}  ",
        f"**Licença:** {meta.get('licenca') or 'desconhecida'}  ",
        f"**PDF:** {meta.get('pdf_url') or 'não informado'}  ",
        f"**Coleta:** {_now(now)}",
        "",
        "> Recortes literais com página. Tradução e argumentação só aparecem",
        "> quando passaram pela validação anti-fabricação; caso contrário,",
        "> permanecem explicitamente pendentes.",
        ">",
        "> `trechos.json` guarda os recortes deste pipeline. `recortes.json` é",
        "> reservado ao vínculo com o manuscrito (SPEC-978) e permanece vazio",
        "> até que uma citação do texto seja associada a um recorte.",
        "",
    ]

    for index, item in enumerate(enriched, start=1):
        linhas.extend(
            [
                f"## Recorte {index} — p. {item['page']}",
                "",
                f"> {item['text']}",
                "",
                f"**Citação ABNT:** {item['citation']}",
                "",
            ]
        )
        trad = item["translation"]
        if trad.get("status") == "ok":
            linhas.extend([f"**Tradução (pt-BR):** {trad['text']}", ""])
        else:
            linhas.extend([f"**Tradução (pt-BR):** {_pendente('tradução', trad)}", ""])

        arg = item["argumentation"]
        if arg.get("status") == "ok":
            linhas.extend(
                [
                    f"**Justificativa:** {arg['justificativa']}",
                    "",
                    f"**Argumento:** {arg['argumento']}",
                    "",
                ]
            )
        else:
            linhas.extend([f"**Justificativa/Argumento:** {_pendente('argumentação', arg)}", ""])
        linhas.extend(["---", ""])

    validadas = [i for i in enriched if i["argumentation"].get("status") == "ok"]
    linhas.extend(["## Síntese crítica", ""])
    if validadas:
        for item in validadas:
            linhas.append(f"- {item['argumentation']['argumento']} {item['citation']}")
    else:
        linhas.append(
            "_Nenhuma argumentação validada. A síntese crítica exige leitura humana "
            "ou argumentador com saída verificável._"
        )
    linhas.append("")

    destino = Path(pasta) / "fichamento.md"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return str(destino)


def write_resenha(
    pasta: str | Path,
    meta: Mapping[str, Any],
    enriched: Sequence[Mapping[str, Any]],
    pages: Sequence[Mapping[str, Any]],
) -> str:
    """Resenha estruturada; não afirma o que os recortes não sustentam."""
    limitações = [
        i for i in enriched if re.search(r"\blimitation|\blimita|\bthreat", i["text"], re.IGNORECASE)
    ]
    validadas = [i for i in enriched if i["argumentation"].get("status") == "ok"]

    linhas = [
        f"# Resenha — {meta.get('titulo') or '[Sem título]'}",
        "",
        f"**Referência (ABNT):** {_abnt_ref(dict(meta))}",
        "",
        "## 1. Identificação",
        "",
        f"- DOI: {meta.get('doi')}",
        f"- Autoria: {', '.join(meta.get('autores') or ['não informada'])}",
        f"- Ano: {meta.get('ano') or '[s.d.]'}",
        f"- Veículo: {meta.get('fonte') or '[não informado]'}",
        f"- Páginas extraídas: {len(pages)}",
        "",
        "## 2. Contribuição sustentada por recortes",
        "",
    ]
    if validadas:
        for item in validadas:
            linhas.append(f"- {item['argumentation']['justificativa']} {item['citation']}")
    else:
        linhas.append("_Sem argumentação validada; contribuição não afirmada automaticamente._")

    linhas.extend(["", "## 3. Limitações declaradas no próprio texto", ""])
    if limitações:
        for item in limitações:
            linhas.append(f"- “{item['text']}” {item['citation']}")
    else:
        linhas.append("_Nenhuma limitação explícita localizada nos recortes selecionados._")

    linhas.extend(
        [
            "",
            "## 4. Veredito",
            "",
            "Revisão humana obrigatória. Esta resenha é um rascunho rastreável: "
            "cada afirmação aponta recorte, página e citação. O pipeline não declara "
            "qualidade, aceite editorial ou contribuição original.",
            "",
        ]
    )

    destino = Path(pasta) / "resenha.md"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return str(destino)


# ── pontes com LLM local (opcionais) ────────────────────────────────────────


def _json_object(text: str | None) -> Mapping[str, Any] | None:
    if not text:
        return None
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.DOTALL)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, Mapping) else None


def llm_translator(client: Any, *, max_tokens: int = 900) -> Translator:
    """Tradutor via LLMClient; saída fora dos limites vira `rejected`, não texto."""

    def translate(text: str, target_lang: str = "pt-BR") -> str | None:
        prompt = (
            f"Traduza para {target_lang} o trecho acadêmico abaixo. "
            "Preserve números, nomes próprios, siglas e citações exatamente como no original. "
            "Não acrescente informação. Responda apenas com a tradução.\n\n" + text
        )
        return client.generate(
            prompt,
            system="Você é tradutor acadêmico rigoroso.",
            max_tokens=max_tokens,
        )

    return translate


def llm_argumenter(client: Any, *, max_tokens: int = 700) -> Argumenter:
    """Argumentador que exige JSON; formato inválido não vira argumento."""

    def argue(payload: dict[str, Any]) -> Mapping[str, Any] | None:
        prompt = (
            "Analise o trecho e produza APENAS JSON com as chaves "
            '"justificativa" e "argumento". '
            "A justificativa explica por que o trecho é relevante (>= 40 caracteres). "
            "O argumento conecta o trecho à tese, citando o autor e o ano.\n\n"
            f"Autor(es): {payload.get('autores')}\nAno: {payload.get('ano')}\n"
            f"Trecho: {payload.get('trecho')}"
        )
        return _json_object(
            client.generate(
                prompt,
                system="Você é pesquisador PhD.",
                max_tokens=max_tokens,
            )
        )

    return argue


# ── RAG lexical ─────────────────────────────────────────────────────────────

def _chunk_page(text: str, page: int, *, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
    body = " ".join(text.split())
    if not body:
        return []
    chunks: list[dict[str, Any]] = []
    start = 0
    while start < len(body):
        end = min(len(body), start + chunk_size)
        piece = body[start:end]
        chunks.append(
            {
                "page": page,
                "char_start": start,
                "char_end": end,
                "text": piece,
                "sha256": hashlib.sha256(piece.encode("utf-8")).hexdigest(),
            }
        )
        if end >= len(body):
            break
        start = max(start + 1, end - overlap)
    return chunks


def build_rag(
    pasta: str | Path,
    pages: Sequence[Mapping[str, Any]],
    *,
    chunk_size: int = 800,
    overlap: int = 120,
) -> dict[str, Any]:
    destino = Path(pasta) / "rag"
    destino.mkdir(parents=True, exist_ok=True)

    chunks: list[dict[str, Any]] = []
    for page in pages:
        for chunk in _chunk_page(str(page.get("text") or ""), int(page["page"]), chunk_size=chunk_size, overlap=overlap):
            chunk["chunk_id"] = len(chunks)
            chunks.append(chunk)

    linhas = "".join(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n" for c in chunks)
    (destino / "chunks.jsonl").write_text(linhas, encoding="utf-8")

    df: Counter[str] = Counter()
    postings: dict[str, list[list[int]]] = {}
    lengths: list[int] = []
    for chunk in chunks:
        tokens = re.findall(r"[a-z0-9]+", chunk["text"].lower())
        lengths.append(len(tokens))
        tf = Counter(tokens)
        for token, count in tf.items():
            df[token] += 1
            postings.setdefault(token, []).append([chunk["chunk_id"], count])

    index = {
        "version": 1,
        "chunks": len(chunks),
        "avg_length": (sum(lengths) / len(lengths)) if lengths else 0.0,
        "lengths": lengths,
        "df": dict(sorted(df.items())),
        "postings": postings,
    }
    (destino / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )

    manifest = rag_manifest(str(pasta), write=True)
    return manifest


def rag_manifest(pasta: str | Path, *, write: bool = False) -> dict[str, Any]:
    destino = Path(pasta) / "rag"
    chunks_path = destino / "chunks.jsonl"
    index_path = destino / "index.json"
    payload = chunks_path.read_bytes() if chunks_path.exists() else b""
    manifest = {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "chunks": payload.count(b"\n"),
        "bytes": len(payload),
        "index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest() if index_path.exists() else None,
    }
    if write:
        (destino / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return manifest


def query_rag(pasta: str | Path, query: str, *, k: int = 5) -> list[dict[str, Any]]:
    destino = Path(pasta) / "rag"
    chunks = [
        json.loads(line)
        for line in (destino / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    index = json.loads((destino / "index.json").read_text(encoding="utf-8"))
    n = int(index["chunks"])
    if n == 0:
        return []

    terms = re.findall(r"[a-z0-9]+", query.lower())
    if not terms:
        return []

    k1, b = 1.5, 0.75
    avg = float(index["avg_length"]) or 1.0
    scores: dict[int, float] = {}
    for term in terms:
        df = int(index["df"].get(term, 0))
        if df == 0:
            continue
        idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
        for chunk_id, tf in index["postings"].get(term, []):
            length = int(index["lengths"][chunk_id])
            denom = tf + k1 * (1 - b + b * length / avg)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + idf * tf * (k1 + 1) / denom

    ranked = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))[:k]
    return [
        {
            "chunk_id": chunk_id,
            "score": round(score, 6),
            "page": chunks[chunk_id]["page"],
            "text": chunks[chunk_id]["text"],
            "sha256": chunks[chunk_id]["sha256"],
            "citation": citation(
                json.loads((Path(pasta) / "metadados.json").read_text(encoding="utf-8")),
                int(chunks[chunk_id]["page"]),
            ),
        }
        for chunk_id, score in ranked
    ]


# ── orquestração ────────────────────────────────────────────────────────────


def run(
    doi: str,
    meta: Mapping[str, Any],
    *,
    base_dir: str,
    resolver_runners: Mapping[str, Callable[[str], Any]] | None = None,
    fetcher: Fetcher | None = None,
    translator: Translator | None = None,
    argumenter: Argumenter | None = None,
    max_excerpts: int = 8,
    keywords: Iterable[str] = (),
    now: str | None = None,
    target_lang: str = "pt-BR",
) -> dict[str, Any]:
    resolved = resolve(doi, runners=resolver_runners)
    if resolved["chosen"] is None:
        return {
            "status": "no_legal_pdf",
            "doi": resolved["doi"],
            "rejected": resolved["rejected"],
            "pdf_downloaded": False,
        }

    chosen = resolved["chosen"]
    pdf_bytes = fetch_pdf(chosen["pdf_url"], fetcher=fetcher)
    pages = extract_pages(pdf_bytes)

    meta2 = {**meta, "pdf_url": chosen["pdf_url"], "licenca": chosen["license"]}
    pasta = criar_pasta_auditoria(
        base_dir,
        dict(meta2),
        pdf_bytes,
        runner_allowed=lambda _meta: {"allowed": True},
    )
    pasta_path = Path(pasta)
    (pasta_path / "paginas.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    excerpts = select_excerpts(pages, max_excerpts=max_excerpts, keywords=keywords)
    enriched = enrich_excerpts(
        excerpts,
        meta2,
        translator=translator,
        argumenter=argumenter,
        target_lang=target_lang,
    )
    (pasta_path / "trechos.json").write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_fichamento(pasta_path, meta2, enriched, now=now)
    write_resenha(pasta_path, meta2, enriched, pages)
    rag = build_rag(pasta_path, pages)

    receipt = {
        "status": "ok",
        "doi": resolved["doi"],
        "pasta": str(pasta_path),
        "pdf_downloaded": True,
        "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "pages": len(pages),
        "excerpts": len(enriched),
        "translations_ok": sum(1 for i in enriched if i["translation"]["status"] == "ok"),
        "argumentations_ok": sum(1 for i in enriched if i["argumentation"]["status"] == "ok"),
        "rag": rag,
        "resolver": {"source": chosen["source"], "license": chosen["license"], "host_type": chosen["host_type"]},
        "rejected_sources": resolved["rejected"],
        "retrieved_at": _now(now),
    }
    (pasta_path / "recibo.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: DOI → PDF legal → auditoria → fichamento → resenha → RAG."""
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de PDF legal com auditoria e RAG (SPEC-935-R1008)")
    parser.add_argument("doi")
    parser.add_argument("--base-dir", default="auditoria_fichamentos")
    parser.add_argument("--max-excerpts", type=int, default=8)
    parser.add_argument("--keywords", default="", help="termos separados por vírgula")
    parser.add_argument("--llm-provider", default="ollama", choices=["ollama", "openai", "none"])
    parser.add_argument("--llm-model", default="", help="habilita tradução/argumentação via LLM")
    parser.add_argument("--lang", default="pt-BR")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    try:
        work = openalex_work(args.doi)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "resolution_error", "error": type(exc).__name__, "doi": args.doi}))
        return 1

    meta = {
        "doi": args.doi,
        "titulo": work.get("title"),
        "autores": [a.get("author", {}).get("display_name") for a in (work.get("authorships") or []) if a.get("author")],
        "ano": work.get("publication_year"),
        "fonte": ((work.get("primary_location") or {}).get("source") or {}).get("display_name"),
    }

    translator = argumenter = None
    if args.llm_model:
        from research.llm_client import LLMClient

        client = LLMClient(args.llm_provider, model=args.llm_model, timeout=300)
        translator = llm_translator(client)
        argumenter = llm_argumenter(client)

    receipt = run(
        args.doi,
        meta,
        base_dir=args.base_dir,
        resolver_runners={"openalex": openalex_runner},
        fetcher=http_fetcher,
        translator=translator,
        argumenter=argumenter,
        max_excerpts=args.max_excerpts,
        keywords=keywords,
        target_lang=args.lang,
    )

    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(f"status: {receipt['status']}")
        for key in ("pasta", "pages", "excerpts", "translations_ok", "argumentations_ok"):
            if key in receipt:
                print(f"{key}: {receipt[key]}")
        if receipt.get("rejected"):
            print(f"rejeitados: {receipt['rejected']}")
    return 0 if receipt["status"] == "ok" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
