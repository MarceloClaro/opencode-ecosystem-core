"""Revisão sistemática mínima nativa v4.2, com inclusão/exclusão humana."""
from __future__ import annotations
import re
from pathlib import Path
from .common import dump, load, now, uid

def _key(row: dict) -> str:
    doi = (row.get("doi") or "").strip().lower()
    if doi: return "doi:" + re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    return "title:" + re.sub(r'\W+', '', (row.get("title") or "").casefold())[:180]

def init_protocol(workspace: Path, project_id: str, title: str, question: str,
                  *, sources=None, approved_by: str | None = None, human: bool = False) -> Path:
    if human and not approved_by: raise ValueError("--human exige approved_by")
    protocol_id = "SRP-" + re.sub(r'[^A-Z0-9-]', '-', project_id.upper())[:40]
    obj = {
        "schema_version":"1.0","protocol_id":protocol_id,"project_id":project_id,
        "title":title,"question":question,
        "eligibility":{"include":["Atende à pergunta/protocolo"],"exclude":["Não atende à pergunta/protocolo"],"date_from":None,"date_to":None,"languages":[],"study_types":[]},
        "search_plan":{"sources":list(sources or ["openalex","crossref"]),"query_strategy":[question],"snowballing":True,"search_date":None},
        "screening":{"title_abstract":"assisted","full_text":"manual","independent_reviewers":2},
        "integrity_policy":{"check_retractions":True,"check_corrections":True,"check_versions":True},
        "synthesis_plan":{"narrative":True,"meta_analysis":"conditional_on_homogeneity_and_human_protocol"},
        "reporting_standard":"PRISMA_2020","human_review_required":True,
        "status":"approved" if human else "draft", "approved_by":approved_by if human else None,
    }
    path=workspace/"00_contract/systematic-review-protocol.json"; dump(path,obj); return path

def ingest(workspace: Path, manifest_path: Path) -> dict:
    manifest=load(manifest_path); rows=manifest.get("results",[]); seen={}; dup=0; outdir=workspace/"01_sources/systematic_review/studies"
    created=[]
    for row in rows:
        key=_key(row)
        if not key or key in seen: dup += 1; continue
        seen[key]=True
        sid="STUDY-"+uid("",8).strip('-').upper()
        rec={
            "schema_version":"1.0","study_id":sid,"canonical_title":row.get("title") or "",
            "identifiers":{"doi":row.get("doi"),"openalex":row.get("record_url") if row.get("source")=="openalex" else None,"pmid":None,"arxiv":None},
            "authors":row.get("authors") or [],"year":row.get("year"),"venue":row.get("venue"),
            "versions":[{"version_id":row.get("article_id"),"kind":"retrieved_record","source":row.get("source"),"url":row.get("record_url"),"pdf_path":None}],
            "source_records":[row.get("article_id")],"integrity_status":"unchecked",
            "screening_status":"pending","included_in_synthesis":False,"exclusion_reason":None,
            "created_at":now(),"updated_at":now(),
        }
        p=outdir/f"{sid}.json"; dump(p,rec); created.append(str(p))
    audit={"records_identified":len(rows),"unique_studies":len(created),"duplicates_removed":dup,"created":created}
    dump(workspace/"09_provenance/systematic_review/ingest-summary.json",audit); return audit

def screen(workspace: Path, protocol_id: str, study_id: str, stage: str, reviewer: str,
           decision: str, reason: str, *, human: bool = False) -> Path:
    if stage not in {"title_abstract","full_text"}: raise ValueError("stage inválido")
    if decision not in {"include","exclude","uncertain"}: raise ValueError("decision inválida")
    if not human: raise ValueError("Decisão de screening final exige --human")
    obj={"schema_version":"1.0","decision_id":uid("SCR",12),"protocol_id":protocol_id,
         "study_id":study_id,"stage":stage,"reviewer":reviewer,"decision":decision,
         "reason":reason,"decided_at":now(),"human_decision":True,"assistant_suggestion":None,"evidence_refs":[]}
    out=workspace/"09_provenance/systematic_review/screening"/f"{obj['decision_id']}.json"; dump(out,obj)
    candidates=list((workspace/"01_sources/systematic_review/studies").glob(f"{study_id}.json"))
    if candidates:
        st=load(candidates[0]); st["screening_status"]=f"{stage}:{decision}"; st["updated_at"]=now()
        if stage=="full_text":
            st["included_in_synthesis"] = decision=="include"
            st["exclusion_reason"] = reason if decision=="exclude" else None
        dump(candidates[0],st)
    return out

def prisma(workspace: Path, protocol_id: str, *, human_verified: bool = False) -> Path:
    studies=list((workspace/"01_sources/systematic_review/studies").glob("*.json"))
    decisions=[load(p) for p in (workspace/"09_provenance/systematic_review/screening").glob("*.json")]
    full=[d for d in decisions if d.get("stage")=="full_text"]
    ta=[d for d in decisions if d.get("stage")=="title_abstract"]
    ingest_summary=workspace/"09_provenance/systematic_review/ingest-summary.json"
    ing=load(ingest_summary) if ingest_summary.exists() else {"records_identified":len(studies),"duplicates_removed":0}
    reasons={}
    for d in full:
        if d.get("decision")=="exclude": reasons[d.get("reason") or "não especificado"]=reasons.get(d.get("reason") or "não especificado",0)+1
    obj={"schema_version":"1.0","flow_id":uid("PRISMA",12),"protocol_id":protocol_id,"generated_at":now(),
         "identification":{"records_identified":int(ing.get("records_identified",0)),"duplicates_removed":int(ing.get("duplicates_removed",0)),"records_from_databases":int(ing.get("records_identified",0)),"records_from_other_methods":0},
         "screening":{"records_screened":len(ta),"records_excluded":sum(d.get("decision")=="exclude" for d in ta),"reports_sought":sum(d.get("decision")=="include" for d in ta),"reports_not_retrieved":0,"reports_assessed":len(full),"reports_excluded":sum(d.get("decision")=="exclude" for d in full)},
         "included":{"studies_included":sum(load(p).get("included_in_synthesis") is True for p in studies),"reports_included":sum(load(p).get("included_in_synthesis") is True for p in studies)},
         "exclusion_reasons":reasons,"reporting_standard":"PRISMA_2020","human_verified":bool(human_verified),
         "limitations":["Fluxo derivado de ledgers locais; confira manualmente antes de publicação."]}
    out=workspace/"07_artifacts/systematic_review/prisma-flow.json"; dump(out,obj); return out
