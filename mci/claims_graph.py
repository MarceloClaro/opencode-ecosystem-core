"""R1148 — grafo de claims com proveniência, prova/contraprova e evidência numérica.

Nós: claim, source, excerpt, test, evidence, theorem, counterproof.
Arestas: supports, contradicts, insufficient, derived_from, tests, proves,
counterproves.

Regras:

- `axiom` é declarado, não provado; warrant limitado.
- `lemma`/`law`/`theory` exigem vínculo formal com teorema **e** contraprova
  kernel-checked para o status `formal_only`.
- `subjective` exige metadados psicométricos; warrant limitado e revisão humana.
- evidência `irreal` (sintética/contrafactual) é descontada e não sustenta
  alegação empírica.
- o grafo liga e contrapõe evidência; não inventa evidência.

Não prova verdade, causalidade, hardware ou vantagem.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LIMITS = (
    "Grafo epistemológico: liga e contrapõe evidência, mas não inventa verdade. "
    "Evidência irreal é sintética/contrafactual e não sustenta alegação "
    "empírica. Warrant não é probabilidade de verdade. Exige revisão humana."
)
CLAIM_KINDS = {"axiom", "lemma", "law", "theory", "hypothesis", "empirical", "subjective"}
RELATIONS = {
    "supports",
    "contradicts",
    "insufficient",
    "derived_from",
    "tests",
    "proves",
    "counterproves",
}
DOMAINS = {"real", "complex", "irreal"}
DOMAIN_WEIGHT = {"real": 1.0, "complex": 1.0, "irreal": 0.3}


class FormalLinkError(ValueError):
    """Certificado formal ausente, não aceito ou sem kernel-checked."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ClaimsGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _prov(self, *, agent: str, activity: str, source=None, **extra) -> dict:
        payload = {
            "agent": str(agent),
            "activity": str(activity),
            "generated_at": self._now(),
            "source": source,
        }
        payload.update(extra)
        return payload

    def _add_node(self, node: dict) -> dict:
        node_id = str(node.get("id", "")).strip()
        if not node_id:
            raise ValueError("nó sem id")
        if node_id in self.nodes:
            raise ValueError(f"nó duplicado: {node_id}")
        self.nodes[node_id] = node
        return node

    def add_claim(
        self,
        claim_id: str,
        proposition: str,
        *,
        kind: str = "empirical",
        polarity: str = "affirm",
        proposition_key: str | None = None,
        falsifier: str = "",
        agent: str = "unknown",
        source_id: str | None = None,
    ) -> dict:
        if kind not in CLAIM_KINDS:
            raise ValueError(f"kind inválido: {kind}")
        if polarity not in {"affirm", "deny"}:
            raise ValueError("polarity deve ser affirm ou deny")
        if not str(proposition).strip():
            raise ValueError("proposition obrigatória")
        if source_id is not None and source_id not in self.nodes:
            raise ValueError(f"source_id ausente: {source_id}")
        return self._add_node({
            "id": str(claim_id),
            "type": "claim",
            "proposition": str(proposition),
            "kind": kind,
            "polarity": polarity,
            "proposition_key": proposition_key or str(claim_id),
            "falsifier": str(falsifier),
            "formal_link": None,
            "psychometric": None,
            "prov": self._prov(
                agent=agent, activity="assert_claim", source=source_id
            ),
        })

    def add_source(
        self,
        source_id: str,
        *,
        title: str,
        doi: str | None = None,
        url: str | None = None,
        license: str | None = None,
        retrieved_at: str | None = None,
        agent: str = "unknown",
    ) -> dict:
        if not (doi or url):
            raise ValueError("source exige doi ou url")
        if not str(title).strip():
            raise ValueError("source exige title")
        return self._add_node({
            "id": str(source_id),
            "type": "source",
            "title": str(title),
            "doi": doi,
            "url": url,
            "license": license,
            "retrieved_at": retrieved_at,
            "prov": self._prov(agent=agent, activity="retrieve_source"),
        })

    def add_excerpt(
        self,
        excerpt_id: str,
        *,
        source_id: str,
        text: str,
        locator: str,
        agent: str = "unknown",
    ) -> dict:
        if source_id not in self.nodes:
            raise ValueError(f"source_id ausente: {source_id}")
        if not str(text).strip() or not str(locator).strip():
            raise ValueError("excerpt exige text e locator")
        return self._add_node({
            "id": str(excerpt_id),
            "type": "excerpt",
            "source_id": str(source_id),
            "text": str(text),
            "locator": str(locator),
            "sha256": hashlib.sha256(str(text).encode("utf-8")).hexdigest(),
            "prov": self._prov(
                agent=agent, activity="extract_excerpt", source=source_id
            ),
        })

    def add_test(
        self,
        test_id: str,
        *,
        test_kind: str,
        result: str,
        n: int | None = None,
        protocol_hash: str | None = None,
        agent: str = "unknown",
    ) -> dict:
        if test_kind not in {"experiment", "simulation", "formal", "survey"}:
            raise ValueError("test_kind inválido")
        if not str(result).strip():
            raise ValueError("test exige result")
        if n is not None and int(n) < 0:
            raise ValueError("n não pode ser negativo")
        return self._add_node({
            "id": str(test_id),
            "type": "test",
            "test_kind": test_kind,
            "result": str(result),
            "n": int(n) if n is not None else None,
            "protocol_hash": protocol_hash,
            "prov": self._prov(agent=agent, activity="run_test"),
        })

    def add_evidence(
        self,
        evidence_id: str,
        *,
        domain: str,
        value,
        units: str | None = None,
        uncertainty: float | None = None,
        source_id: str | None = None,
        synthetic: bool = False,
        scenario: str | None = None,
        agent: str = "unknown",
    ) -> dict:
        if domain not in DOMAINS:
            raise ValueError(f"domain inválido: {domain}")
        if source_id is not None and source_id not in self.nodes:
            raise ValueError(f"source_id ausente: {source_id}")
        if domain == "real":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError("evidência real exige número")
        elif domain == "complex":
            if not isinstance(value, dict) or not {
                "real", "imag"
            } <= set(value):
                raise ValueError("evidência complexa exige {real, imag}")
        else:
            if not synthetic:
                raise ValueError("evidência irreal exige synthetic=True")
            if not str(scenario or "").strip():
                raise ValueError("evidência irreal exige scenario")
        if uncertainty is not None and float(uncertainty) < 0:
            raise ValueError("uncertainty deve ser >= 0")
        return self._add_node({
            "id": str(evidence_id),
            "type": "evidence",
            "domain": domain,
            "value": value,
            "units": units,
            "uncertainty": (
                float(uncertainty) if uncertainty is not None else None
            ),
            "source_id": source_id,
            "synthetic": bool(synthetic),
            "scenario": scenario,
            "prov": self._prov(
                agent=agent, activity="collect_evidence", source=source_id
            ),
        })

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        *,
        weight: float = 1.0,
        rationale: str = "",
        agent: str = "unknown",
    ) -> dict:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("aresta exige nós existentes")
        if relation not in RELATIONS:
            raise ValueError(f"relação inválida: {relation}")
        if not 0.0 <= float(weight) <= 1.0:
            raise ValueError("weight deve estar em [0,1]")
        edge = {
            "source": str(source_id),
            "target": str(target_id),
            "relation": relation,
            "weight": float(weight),
            "rationale": str(rationale),
            "prov": self._prov(agent=agent, activity="link_evidence"),
        }
        self.edges.append(edge)
        return edge

    def add_formal_link(
        self,
        claim_id: str,
        *,
        theorem_id: str,
        counterproof_id: str,
        certificate_path: str | Path,
    ) -> dict:
        if claim_id not in self.nodes or self.nodes[claim_id]["type"] != "claim":
            raise ValueError(f"claim ausente: {claim_id}")
        path = Path(certificate_path)
        if not path.exists():
            raise FormalLinkError(f"certificado ausente: {path}")
        certificate = json.loads(path.read_text(encoding="utf-8"))
        if not certificate.get("gate", {}).get("accepted"):
            raise FormalLinkError("gate do certificado não aceitou")
        axioms = certificate.get("axioms", {})
        for name, label in (
            (theorem_id, "teorema"),
            (counterproof_id, "contraprova"),
        ):
            entry = axioms.get(name)
            if entry is None:
                raise FormalLinkError(f"{label} não reportado: {name}")
            if entry.get("classification") != "kernel_checked":
                raise FormalLinkError(
                    f"{label} não kernel-checked: {name} "
                    f"({entry.get('classification')})"
                )
        for node_id, node_type, lean_name in (
            (theorem_id, "theorem", theorem_id),
            (counterproof_id, "counterproof", counterproof_id),
        ):
            if node_id not in self.nodes:
                self._add_node({
                    "id": node_id,
                    "type": node_type,
                    "lean_name": lean_name,
                    "prov": self._prov(
                        agent="lean", activity="kernel_check"
                    ),
                })
        self.add_edge(theorem_id, claim_id, "proves", rationale="Lean kernel-checked")
        self.add_edge(
            counterproof_id, claim_id, "counterproves", rationale="contraprova Lean"
        )
        link = {
            "theorem": theorem_id,
            "counterproof": counterproof_id,
            "certificate_path": str(path),
            "certificate_sha256": _sha256_file(path),
            "lean_file_sha256": certificate.get("lean_file", {}).get("sha256"),
        }
        self.nodes[claim_id]["formal_link"] = link
        return link

    def add_psychometric(self, claim_id: str, metadata: dict | None) -> dict:
        if claim_id not in self.nodes or self.nodes[claim_id]["type"] != "claim":
            raise ValueError(f"claim ausente: {claim_id}")
        from .ema import validate_psychometrics

        validation = validate_psychometrics(metadata)
        self.nodes[claim_id]["psychometric"] = {
            "valid": validation["valid"],
            "metadata": metadata,
            "warnings": validation["warnings"],
            "missing": validation["missing"],
        }
        return validation

    def _incoming(self, claim_id: str) -> list[dict]:
        return [edge for edge in self.edges if edge["target"] == claim_id]

    def _edge_weight(self, edge: dict) -> float:
        source = self.nodes.get(edge["source"], {})
        weight = float(edge["weight"])
        if source.get("type") == "evidence":
            return weight * DOMAIN_WEIGHT.get(source.get("domain"), 0.2)
        if source.get("type") == "test":
            return weight
        if source.get("type") == "excerpt":
            return weight * 0.5
        return weight

    def warrant(self, claim_id: str) -> dict:
        if claim_id not in self.nodes:
            raise ValueError(f"claim ausente: {claim_id}")
        claim = self.nodes[claim_id]
        if claim["type"] != "claim":
            raise ValueError(f"nó não é claim: {claim_id}")
        support = 0.0
        contradiction = 0.0
        domains = {}
        for edge in self._incoming(claim_id):
            if edge["relation"] == "supports":
                support += self._edge_weight(edge)
            elif edge["relation"] == "contradicts":
                contradiction += self._edge_weight(edge)
            source = self.nodes.get(edge["source"], {})
            if source.get("type") == "evidence":
                domains[source["domain"]] = domains.get(source["domain"], 0) + 1
        formal = claim.get("formal_link") is not None
        psychometric = claim.get("psychometric") or {}
        psychometric_valid = bool(psychometric.get("valid"))
        total = support + contradiction
        empirical_score = (
            0.0
            if total <= 0
            else 0.5 + 0.5 * (support - contradiction) / (total + 1e-9)
        )
        formal_score = 1.0 if formal else 0.0
        warrant = 0.7 * empirical_score + 0.3 * formal_score
        status = "insufficient"
        reasons = []
        if claim["kind"] == "axiom":
            warrant = min(warrant, 0.5)
            status = "declared_axiom"
            reasons.append("axioma é hipótese declarada, não teorema")
        elif claim["kind"] == "subjective":
            if not psychometric_valid:
                warrant = 0.0
                status = "insufficient_psychometric"
                reasons.append("metadados psicométricos ausentes ou inválidos")
            else:
                warrant = min(warrant, 0.6)
                status = "subjective_review"
                reasons.append("autorrelato exige validação clínica")
        elif domains and set(domains) == {"irreal"}:
            warrant = min(warrant, 0.5)
            status = "simulation_only"
            reasons.append("apenas evidência irreal; não sustenta alegação empírica")
        if claim["kind"] in {"lemma", "law", "theory"} and not formal:
            status = "insufficient_formal"
            reasons.append("falta vínculo formal com teorema e contraprova")
        if contradiction > 0 and support == 0:
            status = "contradicted"
        elif support > 0 and contradiction > 0 and abs(support - contradiction) < 0.5:
            status = "conflicted"
        elif formal and total == 0:
            status = "formal_only"
            reasons.append("prova formal cobre apenas o enunciado formal")
        elif status == "insufficient" and warrant >= 0.6:
            status = "supported"
        abstain = status not in {"supported", "formal_only"}
        return {
            "schema_version": 1,
            "claim_id": claim_id,
            "kind": claim["kind"],
            "warrant": float(max(0.0, min(1.0, warrant))),
            "status": status,
            "abstain": bool(abstain),
            "support": float(support),
            "contradiction": float(contradiction),
            "formal": bool(formal),
            "psychometric_valid": psychometric_valid,
            "domains": domains,
            "reasons": reasons,
            "limits": LIMITS,
        }

    def detect_contradictions(self) -> list[dict]:
        findings = []
        claims = [
            node for node in self.nodes.values() if node["type"] == "claim"
        ]
        by_key: dict[str, list[dict]] = {}
        for claim in claims:
            by_key.setdefault(claim["proposition_key"], []).append(claim)
        for key, group in by_key.items():
            affirm = [claim for claim in group if claim["polarity"] == "affirm"]
            deny = [claim for claim in group if claim["polarity"] == "deny"]
            for left in affirm:
                for right in deny:
                    left_warrant = self.warrant(left["id"])
                    right_warrant = self.warrant(right["id"])
                    if (
                        left_warrant["support"] > 0
                        and right_warrant["support"] > 0
                    ):
                        findings.append({
                            "type": "polarity_conflict",
                            "proposition_key": key,
                            "affirm": left["id"],
                            "deny": right["id"],
                            "affirm_support": left_warrant["support"],
                            "deny_support": right_warrant["support"],
                        })
        for claim in claims:
            incoming = self._incoming(claim["id"])
            support = sum(
                self._edge_weight(edge)
                for edge in incoming
                if edge["relation"] == "supports"
            )
            contradiction = sum(
                self._edge_weight(edge)
                for edge in incoming
                if edge["relation"] == "contradicts"
            )
            if support > 0 and contradiction > 0:
                findings.append({
                    "type": "mixed_evidence",
                    "claim": claim["id"],
                    "support": support,
                    "contradiction": contradiction,
                })
        return findings

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "nodes": self.nodes,
            "edges": self.edges,
            "limits": LIMITS,
        }

    def save(self, path: str | Path) -> dict:
        """Persiste o grafo com SHA-256 canônico; não promove confiança."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_dict()
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
        return {
            "path": str(target),
            "sha256": digest,
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }

    @classmethod
    def load(cls, path: str | Path) -> "ClaimsGraph":
        target = Path(path)
        payload = json.loads(target.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("schema_version do grafo deve ser 1")
        graph = cls()
        nodes = payload.get("nodes")
        if not isinstance(nodes, dict):
            raise ValueError("grafo exige nodes como objeto")
        for node_id, node in nodes.items():
            if not isinstance(node, dict):
                raise ValueError(f"nó inválido: {node_id}")
            if node.get("id") != node_id:
                raise ValueError(f"id divergente no nó: {node_id}")
            graph._add_node(node)
        edges = payload.get("edges", [])
        if not isinstance(edges, list):
            raise ValueError("edges deve ser lista")
        for edge in edges:
            if not isinstance(edge, dict):
                raise ValueError("aresta inválida")
            if edge.get("source") not in graph.nodes:
                raise ValueError(f"aresta com fonte ausente: {edge.get('source')}")
            if edge.get("target") not in graph.nodes:
                raise ValueError(f"aresta com alvo ausente: {edge.get('target')}")
            if edge.get("relation") not in RELATIONS:
                raise ValueError(f"relação inválida: {edge.get('relation')}")
            if not 0.0 <= float(edge.get("weight", 0.0)) <= 1.0:
                raise ValueError("peso de aresta fora de [0,1]")
            graph.edges.append(edge)
        return graph

    def audit(self) -> dict:
        claims = [
            node["id"] for node in self.nodes.values()
            if node.get("type") == "claim"
        ]
        warrants = {claim_id: self.warrant(claim_id) for claim_id in claims}
        return {
            "schema_version": 1,
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "claims": len(claims),
            "contradictions": len(self.detect_contradictions()),
            "abstain": sum(
                1 for entry in warrants.values() if entry["abstain"]
            ),
            "warrants": warrants,
            "limits": LIMITS,
        }

    @classmethod
    def from_ledger(cls, path: str | Path) -> "ClaimsGraph":
        """Converte o ledger JSONL do core_cognition em grafo de claims."""
        from core_cognition.claims_ledger import load_ledger

        mapping = {
            "observation": "empirical",
            "inference": "hypothesis",
            "hypothesis": "hypothesis",
            "tested": "empirical",
            "externally_validated": "empirical",
            "refuted": "hypothesis",
        }
        graph = cls()
        for claim in load_ledger(path):
            node = graph.add_claim(
                claim.claim_id,
                claim.text,
                kind=mapping.get(claim.status, "hypothesis"),
                polarity="deny" if claim.status == "refuted" else "affirm",
                proposition_key=claim.claim_id,
                falsifier=claim.falsifier,
                agent="core_cognition.claims_ledger",
            )
            node["ledger_status"] = claim.status
            node["source_sha256"] = claim.source_sha256
            node["external_validation"] = claim.external_validation
            for index, evidence in enumerate(claim.evidence):
                evidence_id = f"{claim.claim_id}-ev{index}"
                value = evidence.get("value") if isinstance(evidence, dict) else None
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    graph.add_evidence(
                        evidence_id, domain="real", value=float(value)
                    )
                else:
                    graph.add_test(
                        evidence_id,
                        test_kind="survey",
                        result=json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                    )
                graph.add_edge(
                    evidence_id,
                    claim.claim_id,
                    "contradicts" if claim.status == "refuted" else "supports",
                    weight=0.5,
                    rationale="evidência importada do claims_ledger",
                )
        return graph

    def to_ledger(self) -> list[dict]:
        """Exporta claims para o formato do core_cognition.claims_ledger."""
        output = []
        for node in self.nodes.values():
            if node.get("type") != "claim":
                continue
            falsifier = str(node.get("falsifier", "")).strip()
            if not falsifier:
                raise ValueError(
                    f"claim {node['id']} sem falsificador; exportação recusada"
                )
            incoming = self._incoming(node["id"])
            evidence = [
                {
                    "source": edge["source"],
                    "relation": edge["relation"],
                    "weight": edge["weight"],
                }
                for edge in incoming
                if edge["relation"] in {"supports", "contradicts"}
            ]
            status = node.get("ledger_status")
            if status is None:
                if node.get("kind") == "hypothesis":
                    status = "refuted" if node.get("polarity") == "deny" else "hypothesis"
                elif evidence:
                    status = "tested"
                else:
                    status = "observation"
            output.append({
                "claim_id": node["id"],
                "text": node["proposition"],
                "status": status,
                "falsifier": falsifier,
                "evidence": evidence,
                "source_sha256": node.get("source_sha256", ""),
                "external_validation": node.get("external_validation"),
                "history": [],
            })
        return output


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Audita/exporta o grafo de claims (R1148)."
    )
    parser.add_argument("--load", type=Path, default=None)
    parser.add_argument("--from-ledger", type=Path, default=None)
    parser.add_argument("--save", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.from_ledger:
        graph = ClaimsGraph.from_ledger(args.from_ledger)
    elif args.load:
        graph = ClaimsGraph.load(args.load)
    else:
        parser.error("informe --load ou --from-ledger")
    result = {"audit": graph.audit()}
    if args.save:
        result["saved"] = graph.save(args.save)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
