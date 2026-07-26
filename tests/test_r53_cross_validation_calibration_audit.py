#!/usr/bin/env python3
"""
Testes TDD para CrossValidator, CalibrationLayer e AuditTrail (SPEC-966)
=========================================================================
RED phase: testes falham antes da implementação.
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════
# CrossValidator
# ═══════════════════════════════════════════════════════════════

class TestCrossValidator:
    """Validação cruzada entre fontes de dados."""

    def test_module_exists(self):
        from skills.tooling.data_knowledge_hub.validation import CrossValidator
        assert CrossValidator is not None

    def test_validate_match(self):
        """Fontes concordando = validação aprovada com confiança alta."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        result = cv.validate("IPCA", [
            {"source": "bcb", "value": 0.38, "unit": "%"},
            {"source": "ibge", "value": 0.38, "unit": "%"},
        ])
        assert result["status"] == "match"
        assert result["confidence"] >= 0.90

    def test_validate_slight_discrepancy(self):
        """Discrepância pequena dentro da tolerância = match."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        result = cv.validate("IPCA", [
            {"source": "bcb", "value": 0.38, "unit": "%"},
            {"source": "ibge", "value": 0.39, "unit": "%"},
        ])
        # Tolerância IPCA = 0.1 pp → diferença 0.01 está dentro
        assert result["status"] == "match"
        assert result["confidence"] > 0.85

    def test_validate_discrepancy(self):
        """Discrepância > tolerância = discrepância detectada."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        # IPCA com diferença de 2% (muito acima da tolerância 0.1pp)
        result = cv.validate("IPCA", [
            {"source": "bcb", "value": 0.38, "unit": "%"},
            {"source": "ibge", "value": 2.50, "unit": "%"},
        ])
        assert result["status"] == "discrepancy"
        assert result["confidence"] < 0.50

    def test_validate_currency_conversion(self):
        """Validação com normalização de moeda (BRL ↔ USD)."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        # PIB Brasil: BCB em BRL, World Bank em USD
        # (R$ 2.892T / ~5.0 = ~$578B — mas WB diz $2.175T? discrepância!)
        result = cv.validate("PIB Brasil", [
            {"source": "bcb", "value": 2892.0, "unit": "BRL_billion"},
            {"source": "world_bank", "value": 2175.0, "unit": "USD_billion"},
        ])
        # Se a taxa de câmbio implícita (2892/2175 = 1.33) não é realista
        assert result["status"] in ("match", "discrepancy")
        assert "details" in result

    def test_validate_single_source(self):
        """Apenas uma fonte disponível = validação parcial."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        result = cv.validate("taxa_selic", [
            {"source": "bcb", "value": 10.50, "unit": "%"},
        ])
        assert result["status"] == "single_source"
        assert result["confidence"] < 0.90  # sem consenso, confiança menor

    def test_validate_multiple_match(self):
        """3+ fontes concordando = confiança muito alta."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        result = cv.validate("PETR4", [
            {"source": "yfinance", "value": 38.52, "unit": "BRL"},
            {"source": "alpha_vantage", "value": 38.51, "unit": "BRL"},
            {"source": "bcb", "value": 38.53, "unit": "BRL"},
        ])
        assert result["status"] == "match"
        assert result["confidence"] >= 0.95  # consenso entre 3 fontes

    def test_cross_validator_get_stats(self):
        """CrossValidator expõe estatísticas."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator

        cv = CrossValidator()
        cv.validate("IPCA", [{"source": "bcb", "value": 1.0, "unit": "%"}])
        stats = cv.get_stats()
        assert stats["total_validations"] >= 1
        assert "matches" in stats


# ═══════════════════════════════════════════════════════════════
# CalibrationLayer
# ═══════════════════════════════════════════════════════════════

class TestCalibrationLayer:
    """Camada de calibração de confiança."""

    def test_module_exists(self):
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer
        assert CalibrationLayer is not None

    def test_authority_score(self):
        """Fontes têm scores de autoridade pré-definidos."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()
        assert cal.get_authority("bcb") >= 0.90
        assert cal.get_authority("ibge") >= 0.90
        assert cal.get_authority("yfinance") >= 0.70
        assert cal.get_authority("wikipedia") >= 0.60
        assert cal.get_authority("conceptnet") >= 0.40

    def test_freshness_decay(self):
        """Dados frescos têm peso maior que dados antigos."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()
        now = time.time()

        # 1 minuto atrás vs 1 semana atrás
        fresh = cal._freshness_weight(now - 60, domain="financeiro")
        stale = cal._freshness_weight(now - 604800, domain="financeiro")  # 7 dias

        assert fresh > stale, "Dados frescos devem ter peso maior"

    def test_consensus_bonus(self):
        """Consenso entre fontes aumenta confiança."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()

        # Sem consenso
        single = cal.calibrate(
            source="bcb",
            domain="financeiro",
            consensus_score=0.5,  # sem pares
        )

        # Com consenso total
        consensus = cal.calibrate(
            source="bcb",
            domain="financeiro",
            consensus_score=1.0,  # 3 fontes concordam
        )

        assert consensus["confidence"] >= single["confidence"]

    def test_calibrate_returns_components(self):
        """Calibração retorna componentes individuais."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()
        result = cal.calibrate("bcb", "financeiro", 0.8)
        assert "authority" in result
        assert "freshness" in result
        assert "consensus" in result
        assert "confidence" in result

    def test_calibrate_specific_values(self):
        """Valores específicos de calibração para BCB."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()
        result = cal.calibrate("bcb", "financeiro", 1.0)
        # BCB = autoridade 1.0, financeiro TTL=1h, consenso 1.0
        assert result["authority"] == 1.0
        assert result["confidence"] >= 0.95

    def test_calibrate_low_authority(self):
        """Fonte de baixa autoridade tem confiança reduzida."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer

        cal = CalibrationLayer()
        result = cal.calibrate("conceptnet", "conhecimento", 0.5)
        # ConceptNet = autoridade baixa
        assert result["confidence"] <= 0.7


# ═══════════════════════════════════════════════════════════════
# AuditTrail
# ═══════════════════════════════════════════════════════════════

class TestAuditTrail:
    """Log imutável e auditável de decisões de dados."""

    def test_module_exists(self):
        from skills.tooling.data_knowledge_hub.audit import AuditTrail
        assert AuditTrail is not None

    def test_record_entry(self):
        """Registra entrada no audit trail."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        entry_id = audit.record(
            query="IPCA 2024",
            domain="financeiro",
            source="bcb",
            confidence=0.95,
            decision_context="orchestrator:route_agent",
        )
        assert entry_id is not None
        assert entry_id.startswith("audit_")

    def test_entries_immutable(self):
        """Entradas registradas não podem ser modificadas no audit trail."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        entry_id = audit.record(
            query="teste", domain="generico", source="mock",
            confidence=0.5,
        )
        entry = audit.get(entry_id)
        # Modificar a cópia não afeta o registro interno (append-only)
        entry["_modified"] = True
        # Recuperar novamente mostra que o original não mudou
        same_entry = audit.get(entry_id)
        assert "_modified" not in same_entry, "Entrada original foi alterada!"

    def test_get_entry(self):
        """Recupera entrada por ID."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        eid = audit.record(
            query="PETR4", domain="financeiro", source="yfinance",
            confidence=0.85,
        )
        entry = audit.get(eid)
        assert entry["query"] == "PETR4"
        assert entry["domain"] == "financeiro"
        assert entry["source"] == "yfinance"

    def test_get_nonexistent_entry(self):
        """Entrada inexistente retorna None."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        assert audit.get("nonexistent_id") is None

    def test_list_entries(self):
        """Lista entradas com paginação."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        audit.record("q1", "financeiro", "bcb", 0.9)
        audit.record("q2", "conhecimento", "wikipedia", 0.8)
        entries = audit.list(limit=10)
        assert len(entries) == 2

    def test_search_entries(self):
        """Busca entradas por query ou domínio."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        audit.record("IPCA", "financeiro", "bcb", 0.9)
        audit.record("machine learning", "conhecimento", "wikipedia", 0.7)

        found = audit.search("IPCA")
        assert len(found) >= 1
        assert found[0]["query"] == "IPCA"

        found = audit.search(query="machine learning")
        assert len(found) >= 1

    def test_export_json(self):
        """Exporta audit trail como JSON Lines."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        audit.record("query1", "financeiro", "bcb", 0.9)
        audit.record("query2", "dataset", "zenodo", 0.8)

        exported = audit.export_json()
        lines = exported.strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            data = json.loads(line)
            assert "timestamp" in data
            assert "query" in data

    def test_hash_integrity(self):
        """Audit trail armazena hash SHA-256 dos resultados."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        raw_result = {"value": 0.38, "unit": "%"}
        eid = audit.record(
            query="IPCA", domain="financeiro", source="bcb",
            confidence=0.95, raw_result=raw_result,
        )
        entry = audit.get(eid)
        expected_hash = hashlib.sha256(
            json.dumps(raw_result, sort_keys=True).encode()
        ).hexdigest()
        assert entry["result_hash"] == expected_hash

    def test_audit_stats(self):
        """Audit trail expõe estatísticas."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail

        audit = AuditTrail()
        audit.record("q1", "financeiro", "bcb", 0.9)
        audit.record("q2", "conhecimento", "wikipedia", 0.8)
        stats = audit.get_stats()
        assert stats["total_entries"] >= 2
        assert "domains" in stats


# ═══════════════════════════════════════════════════════════════
# Integração no DataKnowledgeHub
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    """CrossValidator + CalibrationLayer + AuditTrail integrados."""

    def test_hub_has_validation(self):
        """DataKnowledgeHub tem cross_validator, calibration, audit."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        assert hasattr(hub, "cross_validator"), "Sem cross_validator"
        assert hasattr(hub, "calibration"), "Sem calibration"
        assert hasattr(hub, "audit"), "Sem audit"

    def test_hub_search_returns_confidence(self):
        """Hub.search() retorna confidence e audit_id."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("teste")
        assert "confidence" in result
        assert "audit_id" in result
        assert result["confidence"] >= 0.0

    def test_hub_search_cross_validates(self):
        """Hub faz validação cruzada quando múltiplas fontes disponíveis."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        result = hub.search("IPCA")
        assert "cross_validated" in result
        assert "validation_details" in result

    def test_audit_trail_records_every_search(self):
        """Toda busca no hub gera entrada no audit trail."""
        from skills.tooling.data_knowledge_hub import DataKnowledgeHub

        hub = DataKnowledgeHub()
        before = hub.audit.get_stats()["total_entries"]
        hub.search("PETR4")
        hub.search("machine learning")
        after = hub.audit.get_stats()["total_entries"]
        assert after == before + 2

    def test_calibration_via_reduction_layer(self):
        """LLMReductionLayer.search_data retorna confiança calibrada."""
        from skills.tooling.llm_reduction import get_reduction_layer

        layer = get_reduction_layer()
        result = layer.search_data("teste de calibração")
        assert "confidence" in result


# ═══════════════════════════════════════════════════════════════
# Performance
# ═══════════════════════════════════════════════════════════════

class TestPerformance:
    """Todas as camadas devem ser rápidas."""

    def test_cross_validate_under_5ms(self):
        """Validação cruzada deve levar < 5ms."""
        from skills.tooling.data_knowledge_hub.validation import CrossValidator
        import time

        cv = CrossValidator()
        data = [
            {"source": "bcb", "value": 1.0, "unit": "%"},
            {"source": "ibge", "value": 1.0, "unit": "%"},
        ]
        start = time.time()
        for _ in range(100):
            cv.validate("IPCA", data)
        elapsed_ms = (time.time() - start) * 10
        assert elapsed_ms < 5, f"Muito lento: {elapsed_ms:.2f}ms"

    def test_calibrate_under_2ms(self):
        """Calibração deve levar < 2ms."""
        from skills.tooling.data_knowledge_hub.calibration import CalibrationLayer
        import time

        cal = CalibrationLayer()
        start = time.time()
        for _ in range(100):
            cal.calibrate("bcb", "financeiro", 0.8)
        elapsed_ms = (time.time() - start) * 10
        assert elapsed_ms < 2, f"Muito lento: {elapsed_ms:.2f}ms"

    def test_audit_record_under_1ms(self):
        """Registro no audit trail deve levar < 1ms."""
        from skills.tooling.data_knowledge_hub.audit import AuditTrail
        import time

        audit = AuditTrail()
        start = time.time()
        for _ in range(100):
            audit.record("q", "d", "s", 0.5)
        elapsed_ms = (time.time() - start) * 10
        assert elapsed_ms < 1, f"Muito lento: {elapsed_ms:.2f}ms"
