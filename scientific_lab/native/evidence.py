"""Evidence Graph nativo v4.2."""
from __future__ import annotations
from pathlib import Path
from .common import dump, load, now, sha256_file, uid

def annotate(workspace: Path, project_id: str, claim_id: str, study_id: str,
             relation: str, locator: str, text: str, annotator: str, *,
             claim_text: str | None = None, status: str = "candidate",
             source_file: Path | None = None, human: bool = False,
             verbatim: bool = False) -> Path:
    if status not in {"candidate","verified","rejected"}: raise ValueError("status inválido")
    if status=="verified" and (not human or source_file is None):
        raise ValueError("verified exige decisão humana e source_file para provenance")
    source_sha=sha256_file(source_file) if source_file else None
    obj={"schema_version":"1.0","annotation_id":uid("EANN",12),"project_id":project_id,
         "claim_id":claim_id,"claim_text":claim_text,"study_id":study_id,"relation":relation,
         "locator":locator,"excerpt_or_paraphrase":text,"verbatim":bool(verbatim),
         "source_sha256":source_sha,"verification_status":status,"annotator":annotator,
         "created_at":now(),"limitations":[] if status=="verified" else ["Candidato; não usar como evidência até verificação humana."]}
    out=workspace/"09_provenance/evidence_annotations"/f"{obj['annotation_id']}.json"; dump(out,obj); return out

def build(workspace: Path, project_id: str) -> Path:
    nodes={}; edges=[]
    for p in (workspace/"01_sources/systematic_review/studies").glob("*.json"):
        st=load(p); sid=st["study_id"]
        nodes[sid]={"id":sid,"kind":"study","label":st.get("canonical_title") or sid,"attrs":{"doi":(st.get("identifiers") or {}).get("doi"),"integrity_status":st.get("integrity_status"),"included_in_synthesis":st.get("included_in_synthesis")}}
    for p in (workspace/"09_provenance/evidence_annotations").glob("*.json"):
        ann=load(p); cid=ann["claim_id"]
        nodes.setdefault(cid,{"id":cid,"kind":"claim","label":ann.get("claim_text") or cid,"attrs":{}})
        eid="EVIDENCE:"+ann["annotation_id"]
        nodes[eid]={"id":eid,"kind":"evidence","label":ann["excerpt_or_paraphrase"][:240],"attrs":{"study_id":ann["study_id"],"locator":ann["locator"],"source_sha256":ann.get("source_sha256")}}
        status=ann["verification_status"]
        edges.append({"source":cid,"target":eid,"relation":ann["relation"],"status":status,"annotation_id":ann["annotation_id"]})
        edges.append({"source":eid,"target":ann["study_id"],"relation":"derived_from","status":status,"annotation_id":ann["annotation_id"]})
    obj={"schema_version":"1.0","graph_id":uid("EGRAPH",12),"project_id":project_id,"generated_at":now(),
         "nodes":list(nodes.values()),"edges":edges,"verified_edge_count":sum(e["status"]=="verified" for e in edges),
         "candidate_edge_count":sum(e["status"]=="candidate" for e in edges),
         "epistemic_policy":"candidate_edges_are_not_evidence_until_verified",
         "limitations":["O grafo registra relações auditáveis; não prova causalidade nem qualidade metodológica por si só."]}
    out=workspace/"07_artifacts/evidence_graph/research-evidence-graph.json"; dump(out,obj); return out
