# -*- coding: utf-8 -*-
"""
EvidenceGraph — Memória Epistemológica para o Pipeline Científico.

Rastreia claims científicos ao longo do tempo com:
- Histórico de versões por claim_id
- Evidência a favor/contra acumulada
- Confiança calibrada histórica (Brier, ECE)
- Condições de validade
- Reprodutibilidade tracking

Inexistente no SuperHuman (Google DeepMind) — diferencial central.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple


class EvidenceGraph:
    """
    Grafo epistemológico que mantém a memória de todas as claims científicas,
    suas evidências, confianças e histórico de revisões.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "evidence_graph.json"
        )
        self._graph: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Carrega o grafo do disco."""
        if os.path.exists(self.storage_path):
            try:
                if os.path.getsize(self.storage_path) > 0:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        self._graph = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._graph = {}

    def _save(self) -> None:
        """Persiste o grafo em disco."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self._graph, f, indent=2, ensure_ascii=False)

    def register_claim(self, claim: Dict[str, Any]) -> str:
        """
        Registra uma nova claim ou atualiza versão existente.
        Retorna o claim_id.
        """
        claim_id = claim.get("claim_id", f"clm-{uuid.uuid4().hex[:8]}")

        if claim_id not in self._graph:
            self._graph[claim_id] = {
                "claim_id": claim_id,
                "versions": [],
                "evidence_for": [],
                "evidence_against": [],
                "confidence_history": [],
                "brier_scores": [],
                "ece_history": [],
                "verdict_history": [],
                "reproducibility_history": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "tags": [],
                "conditions_of_validity": [],
                "replication_attempts": 0,
                "replication_successes": 0,
            }

        entry = self._graph[claim_id]

        # Adiciona versão
        version_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hypothesis": claim.get("hypothesis", ""),
            "null_hypothesis": claim.get("null_hypothesis", ""),
            "p_value": claim.get("p_value"),
            "effect_size": claim.get("effect_size"),
            "confidence_interval": claim.get("confidence_interval"),
            "bayes_factor": claim.get("bayes_factor"),
            "calibrated_confidence": claim.get("calibrated_confidence"),
            "reproducibility_score": claim.get("reproducibility_score", 0.0),
            "final_verdict": claim.get("final_verdict", "inconclusive"),
        }
        entry["versions"].append(version_entry)

        # Atualiza históricos
        if claim.get("calibrated_confidence") is not None:
            entry["confidence_history"].append({
                "timestamp": version_entry["timestamp"],
                "value": claim["calibrated_confidence"]
            })

        if claim.get("final_verdict"):
            entry["verdict_history"].append({
                "timestamp": version_entry["timestamp"],
                "value": claim["final_verdict"]
            })

        if claim.get("reproducibility_score") is not None:
            entry["reproducibility_history"].append({
                "timestamp": version_entry["timestamp"],
                "value": claim["reproducibility_score"]
            })

        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._graph[claim_id] = entry
        self._save()
        return claim_id

    def add_evidence(
        self,
        claim_id: str,
        evidence_type: str,
        description: str,
        confidence_impact: float,
        source: str = "auto"
    ) -> bool:
        """
        Adiciona evidência a favor (for) ou contra (against) uma claim.
        Retorna True se a claim existe.
        """
        if claim_id not in self._graph:
            return False

        evidence_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": evidence_type,
            "description": description,
            "confidence_impact": confidence_impact,
            "source": source,
        }

        if confidence_impact >= 0:
            self._graph[claim_id]["evidence_for"].append(evidence_entry)
        else:
            self._graph[claim_id]["evidence_against"].append(evidence_entry)

        self._graph[claim_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return True

    def record_replication(
        self,
        claim_id: str,
        success: bool,
        details: str = ""
    ) -> bool:
        """Registra uma tentativa de replicação."""
        if claim_id not in self._graph:
            return False

        self._graph[claim_id]["replication_attempts"] += 1
        if success:
            self._graph[claim_id]["replication_successes"] += 1

        rep_key = f"replication_{self._graph[claim_id]['replication_attempts']}"
        if "replication_log" not in self._graph[claim_id]:
            self._graph[claim_id]["replication_log"] = {}

        self._graph[claim_id]["replication_log"][rep_key] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": success,
            "details": details,
        }
        self._graph[claim_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return True

    def get_claim_history(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Retorna todo o histórico de uma claim."""
        return self._graph.get(claim_id)

    def get_consolidated_confidence(self, claim_id: str) -> Optional[float]:
        """
        Retorna a confiança consolidada (média ponderada das versões recentes).
        Quanto mais versões e replicações, maior o peso.
        """
        entry = self._graph.get(claim_id)
        if not entry or not entry["confidence_history"]:
            return None

        history = entry["confidence_history"]
        # Peso maior para versões mais recentes
        weights = [1.0 + i * 0.1 for i in range(len(history))]
        weighted_sum = sum(h["value"] * w for h, w in zip(history, weights))
        total_weight = sum(weights)
        return round(weighted_sum / total_weight, 4)

    def get_reproducibility_rate(self, claim_id: str) -> Optional[float]:
        """Taxa de replicação bem-sucedida para uma claim."""
        entry = self._graph.get(claim_id)
        if not entry or entry["replication_attempts"] == 0:
            return None
        return entry["replication_successes"] / entry["replication_attempts"]

    def find_contradictions(self) -> List[Dict[str, Any]]:
        """
        Encontra claims contraditórias no grafo.
        Duas claims são contraditórias se suas hipóteses são opostas
        e ambas têm suporte estatístico.
        """
        contradictions = []
        claims = list(self._graph.keys())

        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                c1 = self._graph[claims[i]]
                c2 = self._graph[claims[j]]

                latest_v1 = c1["versions"][-1] if c1["versions"] else {}
                latest_v2 = c2["versions"][-1] if c2["versions"] else {}

                v1 = latest_v1.get("final_verdict", "")
                v2 = latest_v2.get("final_verdict", "")

                # Se ambas são "supported" mas hipóteses conflitam semanticamente
                if v1 == "supported" and v2 == "supported":
                    h1 = latest_v1.get("hypothesis", "").lower()
                    h2 = latest_v2.get("hypothesis", "").lower()
                    # Heurística simples: detecta negação
                    negation_markers = ["não", "nunca", "sem", "menos", "reduz"]
                    if any(m in h1 and m not in h2 for m in negation_markers) or \
                       any(m in h2 and m not in h1 for m in negation_markers):
                        contradictions.append({
                            "claim_a": claims[i],
                            "claim_b": claims[j],
                            "hypothesis_a": latest_v1.get("hypothesis", ""),
                            "hypothesis_b": latest_v2.get("hypothesis", ""),
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        })

        return contradictions

    def get_all_claim_ids(self) -> List[str]:
        """Lista todos os IDs de claims registradas."""
        return list(self._graph.keys())

    def purge_claim(self, claim_id: str) -> bool:
        """Remove uma claim do grafo (uso administrativo)."""
        if claim_id in self._graph:
            del self._graph[claim_id]
            self._save()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas resumidas do grafo."""
        total = len(self._graph)
        if total == 0:
            return {"total_claims": 0}

        supported = sum(
            1 for c in self._graph.values()
            if c["versions"] and c["versions"][-1].get("final_verdict") == "supported"
        )
        refuted = sum(
            1 for c in self._graph.values()
            if c["versions"] and c["versions"][-1].get("final_verdict") == "refuted"
        )
        inconclusive = total - supported - refuted

        total_rep_attempts = sum(c["replication_attempts"] for c in self._graph.values())
        total_rep_successes = sum(c["replication_successes"] for c in self._graph.values())

        return {
            "total_claims": total,
            "supported": supported,
            "refuted": refuted,
            "inconclusive": inconclusive,
            "total_replication_attempts": total_rep_attempts,
            "total_replication_successes": total_rep_successes,
            "overall_reproducibility": round(
                total_rep_successes / total_rep_attempts, 4
            ) if total_rep_attempts > 0 else None,
            "contradictions_found": len(self.find_contradictions()),
        }

    def to_dataframe_compatible(self) -> Dict[str, List]:
        """Exporta dados para análise tabular (compatível com pandas)."""
        data = {
            "claim_id": [],
            "latest_verdict": [],
            "latest_confidence": [],
            "latest_p_value": [],
            "latest_effect_size": [],
            "num_versions": [],
            "num_evidence_for": [],
            "num_evidence_against": [],
            "replication_rate": [],
            "created_at": [],
        }
        for cid, entry in self._graph.items():
            latest = entry["versions"][-1] if entry["versions"] else {}
            data["claim_id"].append(cid)
            data["latest_verdict"].append(latest.get("final_verdict", ""))
            data["latest_confidence"].append(latest.get("calibrated_confidence"))
            data["latest_p_value"].append(latest.get("p_value"))
            data["latest_effect_size"].append(latest.get("effect_size"))
            data["num_versions"].append(len(entry["versions"]))
            data["num_evidence_for"].append(len(entry["evidence_for"]))
            data["num_evidence_against"].append(len(entry["evidence_against"]))
            rate = self.get_reproducibility_rate(cid)
            data["replication_rate"].append(rate)
            data["created_at"].append(entry.get("created_at", ""))

        return data


# Singleton para uso global no pipeline
_global_graph: Optional[EvidenceGraph] = None


def get_global_evidence_graph() -> EvidenceGraph:
    """Retorna a instância global do EvidenceGraph (singleton)."""
    global _global_graph
    if _global_graph is None:
        _global_graph = EvidenceGraph()
    return _global_graph


def reset_global_evidence_graph() -> None:
    """Reseta a instância global (útil em testes)."""
    global _global_graph
    _global_graph = None
