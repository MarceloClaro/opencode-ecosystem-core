from __future__ import annotations
import hashlib, json
from pathlib import Path
import pytest

from scientific_lab.native import evidence, research as native_research, review
from scientific_lab.runtime import NATIVE_COMMANDS, native_status
from research.downloader import PaperDownloader
from research.searchers import PaperRecord


def rec(**kw):
    base=dict(title="Open science test",authors=["A"],year=2026,doi="10.1234/test.1",arxiv_id=None,url="https://example.org",pdf_url=None,abstract="",venue="J",source="crossref",citations=10,extra={})
    base.update(kw); return PaperRecord(**base)

class FakeSearcher:
    def __init__(self, platforms=None): self.platforms=platforms
    def search(self, query, limit_per_platform=5):
        return [
            rec(title="OA A",source="openalex",pdf_url="https://repo/a.pdf",doi="10.1/a",citations=20),
            rec(title="Metadata B",source="crossref",pdf_url=None,doi="10.1/b",citations=100),
            rec(title="Repo",source="github",doi="",extra={"type":"repository"}),
        ]

class FakeResult:
    def __init__(self, record, ok=True):
        self.record=record; self.ok=ok; self.pdf_path="/tmp/a.pdf" if ok else None; self.method="openalex_oa"; self.error=""
        self.extra={"resolved_pdf_url":"https://repo/a.pdf","rights_basis":"open_access","license":"cc-by","downloaded_at":"2026-09-08T00:00:00Z","sha256":"a"*64,"bytes":123,"content_type":"application/pdf","validation":["magic_bytes_%PDF-","sha256_recorded"],"limitations":[]}
class FakeDownloader:
    def __init__(self, output): self.output=output
    def download(self, records): return [FakeResult(r, ok=(i==0)) for i,r in enumerate(records)]

def test_native_commands_core_first():
    assert {"research","articles","review","evidence"} <= NATIVE_COMMANDS

def test_search_prioritizes_oa_and_excludes_repository(tmp_path):
    path, records, manifest=native_research.search("tema",tmp_path,searcher_factory=FakeSearcher)
    assert path.exists(); assert len(records)==2
    assert manifest["results"][0]["source"]=="openalex"
    assert all(x["source"]!="github" for x in manifest["results"])
    assert manifest["policy"]=="open_science_only"

def test_harvest_writes_receipt(tmp_path):
    out=native_research.harvest("tema",tmp_path,searcher_factory=FakeSearcher,downloader_factory=FakeDownloader,max_downloads=2)
    assert out["downloads_attempted"]==2 and out["downloads_ok"]==1
    receipts=list((tmp_path/"09_provenance/articles").glob("ADL-*.json")); assert len(receipts)==2
    data=json.loads(receipts[0].read_text()); assert data["rights_basis"]=="open_access" and data["sha256"]=="a"*64

def test_downloader_has_no_removed_bypass_runtime():
    source=Path(__file__).resolve().parents[1]/"research/downloader.py"
    text=source.read_text(encoding="utf-8").casefold()
    assert "scihub" not in text
    assert "subprocess" not in text

def test_downloader_direct_oa_records_hash(monkeypatch,tmp_path):
    import research.downloader as dlmod
    monkeypatch.setattr(dlmod,"_download_bytes",lambda url,timeout:(b"%PDF-1.7\nabc","application/pdf",url))
    dl=PaperDownloader(str(tmp_path)); r=rec(source="openalex",pdf_url="https://repo/a.pdf")
    result=dl.download([r])[0]
    assert result.ok; assert result.extra["sha256"]==hashlib.sha256(b"%PDF-1.7\nabc").hexdigest(); assert result.extra["rights_basis"]=="open_access"

def test_downloader_rejects_html(monkeypatch,tmp_path):
    import research.downloader as dlmod
    monkeypatch.setattr(dlmod,"_download_bytes",lambda url,timeout:(b"<html>paywall</html>","text/html",url))
    dl=PaperDownloader(str(tmp_path)); r=rec(source="openalex",pdf_url="https://repo/a")
    result=dl.download([r])[0]; assert not result.ok; assert not list(tmp_path.glob("*.pdf"))

def test_downloader_closed_metadata_without_resolver_is_not_open(monkeypatch,tmp_path):
    dl=PaperDownloader(str(tmp_path),email=None)
    monkeypatch.setattr(dl,"_resolve_openalex",lambda doi:None)
    monkeypatch.setattr(dl,"_resolve_europepmc",lambda doi:None)
    dl.email=None
    result=dl.download([rec(source="crossref",pdf_url="https://publisher/full.pdf")])[0]
    assert not result.ok; assert result.extra["rights_basis"]=="not_verified_open"

def test_review_ingest_dedup_by_doi(tmp_path):
    manifest={"results":[{"article_id":"ART-0001","title":"A","doi":"10.1/a","authors":[],"year":2026,"venue":"J","source":"openalex","record_url":"x"},{"article_id":"ART-0002","title":"A duplicate","doi":"10.1/a","authors":[],"year":2026,"venue":"J","source":"crossref","record_url":"y"}]}
    p=tmp_path/"manifest.json"; p.write_text(json.dumps(manifest))
    out=review.ingest(tmp_path,p); assert out["unique_studies"]==1 and out["duplicates_removed"]==1

def test_screening_requires_human(tmp_path):
    with pytest.raises(ValueError): review.screen(tmp_path,"SRP-X","STUDY-12345678","full_text","R1","include","ok",human=False)

def test_verified_evidence_requires_human_and_source(tmp_path):
    with pytest.raises(ValueError): evidence.annotate(tmp_path,"PRJ","CLAIM-1","STUDY-1","supports","p.1","texto","R1",status="verified")

def test_evidence_graph_separates_candidate_verified(tmp_path):
    studies=tmp_path/"01_sources/systematic_review/studies"; studies.mkdir(parents=True)
    st={"study_id":"STUDY-1","canonical_title":"A","identifiers":{"doi":"10.1/a"},"integrity_status":"unchecked","included_in_synthesis":True}; (studies/"STUDY-1.json").write_text(json.dumps(st))
    evidence.annotate(tmp_path,"PRJ","CLAIM-1","STUDY-1","supports","p.1","candidate","bot",status="candidate")
    src=tmp_path/"source.pdf"; src.write_bytes(b"%PDF-test")
    evidence.annotate(tmp_path,"PRJ","CLAIM-1","STUDY-1","supports","p.2","verified","R1",status="verified",source_file=src,human=True)
    g=json.loads(evidence.build(tmp_path,"PRJ").read_text())
    assert g["candidate_edge_count"]==2 and g["verified_edge_count"]==2
    assert g["epistemic_policy"]=="candidate_edges_are_not_evidence_until_verified"

def test_native_schemas_are_valid_json_schema():
    jsonschema=pytest.importorskip("jsonschema")
    root=Path(__file__).resolve().parents[1]/"scientific_lab/schemas"
    for p in root.glob("*.schema.json"):
        schema=json.loads(p.read_text()); jsonschema.Draft202012Validator.check_schema(schema)
