# -*- coding: utf-8 -*-
"""Testes de regressão — SPEC-935-R384.

Estende a regeneração de fragmentos Molambudos (R383/build_miolo fix) para
CONT-03, MEM-27 e LUC-Escolha — recuperando conteúdo real presente em
molambudos.md mas ausente do .tex publicado há tempos — e prova que duas
notas editoriais e um parágrafo narrativo que só existem no .tex (nunca
existiram no .md) foram preservados manualmente na regeneração.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VIC_FRAG = ROOT / "projetos/molambudos/Molambudos_VictoriaRegia/fragmentos"
CANON_FRAG = ROOT / "projetos/molambudos/fragmentos"


class TestNotasEditoriaisPreservadas:
    def test_cont03_preserva_nota_do_editor(self):
        text = (VIC_FRAG / "cont/CONT-03.tex").read_text(encoding="utf-8")
        assert r"\NE{Nota do Editor" in text
        assert "protocolos de contaminação aqui descritos são simulações formais" in text

    def test_mem27_preserva_nota_do_editor(self):
        text = (VIC_FRAG / "mem/MEM-27.tex").read_text(encoding="utf-8")
        assert r"\NE{O editor registra" in text
        assert "análise espectrográfica não consegue datar com precisão" in text

    def test_luc_escolha_preserva_paragrafo_quarta_opcao(self):
        text = (VIC_FRAG / "luc/LUC-Escolha.tex").read_text(encoding="utf-8")
        assert "Mas havia uma quarta opção" in text
        assert "a diferença entre afogar-se e mergulhar" in text

    def test_canon_frag_espelha_vic_frag(self):
        for rel in ("cont/CONT-03.tex", "mem/MEM-27.tex", "luc/LUC-Escolha.tex"):
            vic = (VIC_FRAG / rel).read_text(encoding="utf-8")
            canon = (CANON_FRAG / rel).read_text(encoding="utf-8")
            assert vic == canon, f"{rel}: árvore canônica divergente da VictoriaRegia"


class TestConteudoRecuperado:
    def test_cont03_recupera_escala_atualizacao_2(self):
        text = (VIC_FRAG / "cont/CONT-03.tex").read_text(encoding="utf-8")
        assert "ESCALA DE CONTAMINAÇÃO --- ATUALIZAÇÃO 2" in text

    def test_mem27_recupera_epilogo_destruicao(self):
        text = (VIC_FRAG / "mem/MEM-27.tex").read_text(encoding="utf-8")
        assert "DESTRUIÇÃO" in text

    def test_luc_escolha_recupera_escala_atualizacao_1(self):
        text = (VIC_FRAG / "luc/LUC-Escolha.tex").read_text(encoding="utf-8")
        assert "ESCALA DE CONTAMINAÇÃO --- ATUALIZAÇÃO 1" in text


class TestProvenienciaIntacta:
    """Reexecuta a mesma verificação de cadeia usada no R383, agora sobre o
    estado pós-extensão da regeneração (CONT-03/MEM-27/LUC-Escolha)."""

    def test_cadeias_r360_r361_r362_resolvem_sem_problema(self):
        drift_path = ROOT / "validacao_externa/cultural_episteme/molambudos_r361_provenance_drift.json"
        r362_path = ROOT / "validacao_externa/cultural_episteme/molambudos_r362_change_manifest.json"
        drift_records = json.loads(drift_path.read_text())["records"] if drift_path.exists() else []
        r362_records = json.loads(r362_path.read_text())["records"] if r362_path.exists() else []
        reviews = json.loads(
            (ROOT / "validacao_externa/cultural_episteme/molambudos_r360_reviews.json").read_text()
        )

        problems = []
        for review in reviews["reviews"]:
            for locator_role, locator in review["source_locators"].items():
                relative_path = locator["path"]
                corpus_file = ROOT / relative_path
                if not corpus_file.is_file():
                    continue
                digest = hashlib.sha256(corpus_file.read_bytes()).hexdigest()
                if locator["sha256"] == digest:
                    continue
                predecessor_matches = [
                    r for r in drift_records
                    if r["path"] == relative_path
                    and r["old_sha256"] == locator["sha256"]
                    and any(
                        item["review_id"] == review["review_id"]
                        and item["locator_role"] == locator_role
                        for item in r["affected_reviews"]
                    )
                ]
                direct = [r for r in predecessor_matches if r["new_sha256"] == digest]
                chained = [
                    (r, s) for r in predecessor_matches for s in r362_records
                    if s["path"] == relative_path
                    and s["old_sha256"] == r["new_sha256"]
                    and s["new_sha256"] == digest
                ]
                inherited = [
                    s for s in r362_records
                    if s["path"] == relative_path
                    and s["old_sha256"] == locator["sha256"]
                    and s["new_sha256"] == digest
                    and any(
                        item["review_id"] == review["review_id"]
                        and item["locator_role"] == locator_role
                        for item in s.get("affected_reviews", [])
                    )
                ]
                if len(direct) + len(chained) + len(inherited) != 1:
                    problems.append((review["review_id"], locator_role, relative_path))

        assert not problems, f"cadeias de proveniência quebradas: {problems}"

    def test_r362_change_manifest_hashes_batem(self):
        r362_path = ROOT / "validacao_externa/cultural_episteme/molambudos_r362_change_manifest.json"
        records = json.loads(r362_path.read_text())["records"]
        mismatches = []
        for record in records:
            path = ROOT / record["path"]
            if not path.is_file():
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != record["new_sha256"]:
                mismatches.append(record["path"])
        assert not mismatches, f"hashes do manifesto R362 divergentes: {mismatches}"
