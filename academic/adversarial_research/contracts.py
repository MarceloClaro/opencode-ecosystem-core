from dataclasses import dataclass,field,asdict
from typing import Any

@dataclass
class ResearchClaim:
    claim_id: str
    statement: str
    claim_type: str
    source_refs: list[str]
    evidence_status: str
    limitations: list[str]
    reviewer_agent_ids: list[str]
    attributes: dict[str,Any]=field(default_factory=dict)
    declared_evidence_status: str=''

@dataclass
class AdversarialObjection:
    objection_id: str
    target_claim_ids: list[str]
    question: str
    scientific_rationale: str
    required_evidence: str
    severity: str
    uncertainty: str
    source_refs: list[str]
    responsible_agent: str
    code: str=''

@dataclass
class ResearchReview:
    research_id: str
    spec_id: str
    reviewed_artifact_hash: str
    claims: list[dict]
    objections: list[dict]
    unresolved_gaps: list[dict]
    recommended_actions: list[str]
    evidence_manifest: list[dict]
    review_status: str
    human_review_required: bool=True

def as_json(value): return asdict(value)
