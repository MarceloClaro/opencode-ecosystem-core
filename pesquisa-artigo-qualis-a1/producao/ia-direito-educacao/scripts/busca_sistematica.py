#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Busca sistemática da revisão de escopo — IA e Direito × letramento/formação (2018–2026).
Executa buscas reais em APIs públicas (DOAJ, ERIC, Crossref), deduplica e gera TSV de triagem.
Data de execução: 2026-09-17
"""
import json, time, urllib.parse, urllib.request, csv, re, html

UA = {"User-Agent": "OpenCodeEcosystemScopingReview/1.0 (contact: research@example.org)"}

def get(url, timeout=120, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            if i == retries - 1:
                print("ERR", url[:80], e); return None
            time.sleep(5)

def clean(t):
    if not t: return ""
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

# ---------- 1. DOAJ ----------
doaj_recs = {}
for q in ['"AI literacy" AND "law"', '"artificial intelligence" AND "legal education"']:
    url = "https://doaj.org/api/search/articles/" + urllib.parse.quote(q) + "?pageSize=100"
    d = get(url)
    if not d: continue
    for it in d.get("results", []):
        b = it.get("bibjson", {})
        doi = ""
        ids = b.get("identifier", [])
        if isinstance(ids, list):
            for i in ids:
                if i.get("type") == "doi": doi = i.get("id", "")
        rec = {
            "fonte": "DOAJ", "doi": doi, "titulo": clean(b.get("title", "")),
            "resumo": clean(b.get("abstract", "")),
            "ano": b.get("year", ""), "periodico": clean((b.get("journal", {}) or {}).get("title", "")),
            "autores": "; ".join((a or {}).get("name", "") for a in (b.get("author") or [])),
        }
        key = doi.lower() if doi else (b.get("title", "")).lower()
        doaj_recs.setdefault(key, rec)

# ---------- 2. ERIC ----------
eric_searches = [
    '"artificial intelligence" AND ("legal education" OR "law schools" OR "law students")',
    '"AI literacy" AND law',
    '"artificial intelligence" AND "legal education"',
    '"generative AI" AND ("law school" OR "legal education")',
]
eric_recs = {}
for q in eric_searches:
    url = "https://api.ies.ed.gov/eric/?search=" + urllib.parse.quote(q) + "&format=json&rows=50"
    d = get(url)
    if not d or "response" not in d: continue
    docs = d["response"].get("docs", [])
    for doc in docs:
        doi = ""
        for ident in (doc.get("identifier") or []):
            if ident.startswith("10."): doi = ident
        rec = {
            "fonte": "ERIC", "doi": doi, "titulo": clean(doc.get("title", "")),
            "resumo": clean((doc.get("description") or [""])[0] if isinstance(doc.get("description"), list) else doc.get("description", "")),
            "ano": str((doc.get("publicationdateyear") or [""])[0] if isinstance(doc.get("publicationdateyear"), list) else (doc.get("publicationdateyear") or "")),
            "periodico": clean((doc.get("publicationtitle") or [""])[0] if isinstance(doc.get("publicationtitle"), list) else doc.get("publicationtitle", "")),
            "autores": "; ".join(doc.get("author") or []),
        }
        key = doi.lower() if doi else rec["titulo"].lower()
        eric_recs.setdefault(key, rec)

# ---------- 3. Crossref ----------
crossref_queries = [
    "AI literacy legal education",
    "artificial intelligence law school curriculum",
    "generative AI legal education teaching assessment",
    "artificial intelligence legal training judicial",
    "inteligência artificial ensino jurídico",
    "inteligencia artificial enseñanza derecho",
]
cross_recs = {}
for q in crossref_queries:
    url = ("https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) +
           "&filter=from-pub-date:2018-01-01,type:journal-article&rows=20&select=DOI,title,author,container-title,issued,abstract")
    d = get(url)
    if not d: continue
    for it in d.get("message", {}).get("items", []):
        doi = it.get("DOI", "").lower()
        if doi in cross_recs: continue
        auth = "; ".join((a.get("family", "") + ", " + a.get("given", "")) for a in (it.get("author") or [])[:6])
        year = ""
        iss = it.get("issued", {}).get("date-parts", [[None]])[0]
        if iss and iss[0]: year = str(iss[0])
        abstract = clean(it.get("abstract", ""))
        abstract = re.sub(r"<[^>]+>", " ", abstract)
        cross_recs[doi] = {
            "fonte": "Crossref", "doi": doi, "titulo": clean((it.get("title") or [""])[0]),
            "resumo": clean(abstract), "ano": year,
            "periodico": clean((it.get("container-title") or [""])[0]),
            "autores": auth,
        }

# ---------- merge + dedupe ----------
all_recs = {}
for d in (doaj_recs, eric_recs, cross_recs):
    for k, v in d.items():
        if k not in all_recs or (len(v.get("resumo","")) > len(all_recs[k].get("resumo",""))):
            all_recs[k] = v

out = "05_busca_registros_triagem.tsv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["fonte", "doi", "ano", "periodico", "titulo", "resumo", "autores"])
    for k, r in sorted(all_recs.items(), key=lambda x: -(int(x[1]["ano"] or 0))):
        w.writerow([r["fonte"], r["doi"], r["ano"], r["periodico"], r["titulo"], r["resumo"], r["autores"]])

print("TOTAIS:", {"DOAJ": len(doaj_recs), "ERIC": len(eric_recs), "Crossref": len(cross_recs), "MERGED_DEDUP": len(all_recs)})