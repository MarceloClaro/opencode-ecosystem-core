"""
Testes R-976.19 — Perfis editoriais de Computação Quântica e Direito (SPEC-976).

Guias de submissão OFICIAIS consultados em 24/09/2026:
- npj Quantum Information (Nature Portfolio): peer-reviewed open access CC BY;
  escopo quantum computing/communication/information theory/metrology/sensing/
  cryptography; 1ª decisão mediana ~5 dias; reporting summary; deduplicação
  contra arXiv; checklists editoriais obrigatórios.
- Quantum (quantum-journal.org): overlay journal, submissão via arXiv (quant-ph),
  sem taxas, sem limite de formato/comprimento; altamente seletiva; critérios de
  avaliação explícitos (technical correctness, significance, clarity/
  reproducibility, honest claims, scope); contributions obrigatórias; disclosure
  de uso de LLM na submissão.
- Quantum Science and Technology (IOP): highly selective — "essential reading
  for a particular sub-field and of interest to the broader quantum science and
  technology community with the expectation for lasting scientific and
  technological impact"; Letters (outstanding concise; justification statement;
  priority review), Papers (significant advance), Topical reviews (invited),
  Roadmaps (coleção de perspectivas 2–3 páginas); single anonymous.
- IEEE Transactions on Quantum Engineering (TQE): gold open access, sem page
  limit, all-electronic; APC USD 1.995 (efetivo 01/01/2024; desconto IEEE members
  5%, Society members 20%, não combináveis); regular/review/tutorial; escopo:
  engenharia de fenômenos quânticos + supercondutividade, magnética, micro-ondas,
  fotônica, processamento de sinais.
- ACM Transactions on Quantum Computing (TQC): desde 01/01/2026 submissões via
  Manuscript Central; expectativa de revised manuscritos dentro de 30 dias para
  minor revisions; transição 100% Open Access em 01/01/2026 (APC com waivers/
  discounts); revisão EIC → seção → Senior Associate Editors; templates ACM;
  ORCID obrigatório.
- Quantum Information Processing (Springer): single-blind; abstract 150–250
  palavras; fonte editável + PDF obrigatórios; recomenda template LaTeX;
  cobertura: computação quântica, informação, comunicação, criptografia,
  simulação, algoritmos, hardware/software.
- Revista Direito GV (FGV): Qualis A1; desk review (ine ditismo, adequação
  temático-metodológica, requisitos formais); duplo-cego → SIMPLES-cego quando
  há preprint (revisor conhece autoria); 5 palavras-chave em PT/EN/ES;
  desidentificação obrigatória; resenhas ≤2.000 palavras (incluindo referências);
  ScholarOne; sem taxas; software de similaridade.
- Revista Direito e Práxis (UERJ): Qualis A1; trilíngue (PT/EN/ES); desk review
  (autores informados em até 30 dias) + duplo-cega com 2 avaliadores ad hoc;
  declaração rigorosa de conflito de interesses; 3º avaliador se divergência;
  preprints permitidos (SciELO/arXiv/bioRxiv/medRxiv); sem APC.
- Revista de Direito Administrativo (RDA, FGV): Qualis A1; desde 1945; desk
  review ≤15 dias; 2–3 pareceristas doutores por área; titulação mínima doutor;
  máximo 2 autores (1 com doutorado); sem inclusão de autor após submissão;
  ABNT; CC BY-NC-ND 4.0; autores mantêm direitos autorais; primeira publicação
  (não exclusiva) cedida à FGV Direito Rio.
- Seqüência (UFSC): Qualis A1; avaliação duplo-cega; iThenticate para plágio;
  CC BY 4.0; sem taxas; ABNT; fluxo contínuo.
- Revista de Estudos Empíricos em Direito (REED): foco em pesquisa empírica
  jurídica; duplo-cega; avaliação média ~6 meses; parecerista tem ~1 mês;
  exogenia de pareceristas ≥75%; nomes de avaliadores publicados (ciência
  aberta); ORCID; formatos .doc/.docx/.odt.
- Suprema — Revista de Estudos Constitucionais (STF): semestral; duplo-cega com
  ≥2 pareceristas externos; 3º parecerista se impasse; até 3 coautores (titulação
  de doutor primordial); aceita PT/EN/ES/FR/IT; fluxo contínuo.
"""
import unittest

from mirofish.social import (
    CRITERIA,
    EDITORIAL_PROFILES,
    JOURNAL_KEYS,
    get_profile,
    profile_summary,
)

PERFIS_QUANTUM = [
    "npj Quantum Information",
    "Quantum",
    "Quantum Science and Technology",
    "IEEE Transactions on Quantum Engineering",
    "ACM Transactions on Quantum Computing",
    "Quantum Information Processing",
]

PERFIS_DIREITO = [
    "Revista Direito GV",
    "Revista Direito e Práxis",
    "Revista de Direito Administrativo",
    "Seqüência (UFSC)",
    "Revista de Estudos Empíricos em Direito",
    "Suprema (STF)",
]

PERFIS_R589 = PERFIS_QUANTUM + PERFIS_DIREITO


class TestPerfisQuantumDireito(unittest.TestCase):
    def test_perfis_registrados(self):
        for nome in PERFIS_R589:
            self.assertIn(nome, EDITORIAL_PROFILES, f"perfil ausente: {nome}")
            self.assertIn(nome, JOURNAL_KEYS)

    def test_campos_obrigatorios(self):
        for nome in PERFIS_R589:
            p = EDITORIAL_PROFILES[nome]
            self.assertTrue(p.scope, nome)
            self.assertTrue(p.priority, nome)
            self.assertTrue(p.reference_style, nome)
            self.assertTrue(p.review_flow, nome)
            self.assertTrue(p.length_limit, nome)
            self.assertIsInstance(p.special_gates, list, nome)
            self.assertTrue(p.source.startswith("http"), nome)
            self.assertTrue(set(p.weights.keys()).issubset(set(CRITERIA)), nome)
            for w in p.weights.values():
                self.assertGreater(w, 0.0, nome)

    # ── npj Quantum Information (Nature Portfolio) ───────────────
    def test_npjqi_escopo_real(self):
        p = EDITORIAL_PROFILES["npj Quantum Information"]
        texto = (p.scope + " " + p.priority).lower()
        self.assertIn("quântica", texto)
        self.assertIn("open access", (p.review_flow + " " + " ".join(p.special_gates)).lower(),
                      "OA explícito")

    def test_npjqi_gates_real(self):
        p = EDITORIAL_PROFILES["npj Quantum Information"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("nature portfolio", p.review_flow.lower() or " ".join(p.special_gates).lower(),
                      "políticas Nature Portfolio")
        self.assertIn("arxiv", texto, "deduplicação/consistência com arXiv")

    # ── Quantum (overlay journal) ────────────────────────────────
    def test_quantum_overlay_real(self):
        p = EDITORIAL_PROFILES["Quantum"]
        texto = (p.review_flow + " " + " ".join(p.special_gates)).lower()
        self.assertIn("arxiv", texto, "submissão via arXiv (quant-ph)")
        self.assertIn("sem taxas", texto, "sem taxas/APC")
        self.assertIn("sem limite", p.length_limit.lower(), "sem limite de formato/comprimento")

    # ── Quantum Science and Technology (IOP) ─────────────────────
    def test_qst_seletividade_real(self):
        p = EDITORIAL_PROFILES["Quantum Science and Technology"]
        texto = (p.scope + " " + p.priority).lower()
        self.assertIn("essential reading", texto, "exigência 'essential reading'")
        self.assertIn("duradouro", texto, "expectativa de impacto duradouro")
        self.assertIn("single anonymous", p.review_flow.lower(), "peer review single anonymous")

    def test_qst_tipos_real(self):
        p = EDITORIAL_PROFILES["Quantum Science and Technology"]
        texto = (p.length_limit + " " + " ".join(p.special_gates)).lower()
        self.assertIn("letters", texto, "Letters com justification statement")
        self.assertIn("justification", texto, "Letters exigem justification statement")
        self.assertIn("topical review", texto, "Topical reviews convidadas")

    # ── IEEE TQE ─────────────────────────────────────────────────
    def test_ieee_tqe_oa_real(self):
        p = EDITORIAL_PROFILES["IEEE Transactions on Quantum Engineering"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("gold open access", texto, "gold OA")
        self.assertIn("page limit", texto, "sem page limit")
        self.assertIn("1.995", p.review_flow.lower(), "APC USD 1.995")

    def test_ieee_tqe_escopo_real(self):
        p = EDITORIAL_PROFILES["IEEE Transactions on Quantum Engineering"]
        texto = (p.scope + " " + p.priority).lower()
        self.assertIn("engenharia", texto, "escopo engineering")
        self.assertIn("fotônica", texto, "photonics no escopo")
        self.assertIn("sinais", texto, "signal processing no escopo")

    # ── ACM TQC ──────────────────────────────────────────────────
    def test_acm_tqc_real(self):
        p = EDITORIAL_PROFILES["ACM Transactions on Quantum Computing"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("open access", texto, "transição 100% OA")
        self.assertIn("orcid", texto, "ORCID obrigatório")
        self.assertIn("30 dias", p.review_flow.lower(), "revisão minor em 30 dias")

    # ── Quantum Information Processing (Springer) ────────────────
    def test_qip_real(self):
        p = EDITORIAL_PROFILES["Quantum Information Processing"]
        texto = (p.review_flow + " " + " ".join(p.special_gates)).lower()
        self.assertIn("single-blind", texto, "single-blind review")
        self.assertIn("150", p.length_limit.lower(), "abstract 150–250 palavras")
        self.assertIn("editável", texto, "fonte editável obrigatória")

    # ── Revista Direito GV (FGV) ─────────────────────────────────
    def test_direito_gv_real(self):
        p = EDITORIAL_PROFILES["Revista Direito GV"]
        texto = (p.review_flow + " " + " ".join(p.special_gates)).lower()
        tudo = (p.length_limit + " " + texto).lower()
        self.assertIn("duplo-cego", texto, "duplo-cego")
        self.assertIn("simples-cego", texto, "preprint → simples-cego")
        self.assertIn("2.000", tudo, "resenhas ≤2.000 palavras")
        self.assertIn("5 palavras-chave", tudo, "5 keywords PT/EN/ES")

    # ── Revista Direito e Práxis (UERJ) ──────────────────────────
    def test_direito_praxis_real(self):
        p = EDITORIAL_PROFILES["Revista Direito e Práxis"]
        texto = (p.review_flow + " " + " ".join(p.special_gates)).lower()
        self.assertIn("ad hoc", texto, "2 avaliadores ad hoc")
        self.assertIn("30 dias", p.review_flow.lower(), "resposta desk review em 30 dias")
        self.assertIn("conflito", texto, "declaração de conflito de interesses")

    # ── RDA (FGV) ────────────────────────────────────────────────
    def test_rda_real(self):
        p = EDITORIAL_PROFILES["Revista de Direito Administrativo"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("doutor", texto, "titulação mínima doutor")
        self.assertIn("2 autores", texto, "máximo 2 autores")
        self.assertIn("cc by-nc-nd", texto, "licença CC BY-NC-ND")
        self.assertIn("abnt", p.reference_style.lower(), "ABNT")

    # ── Seqüência (UFSC) ─────────────────────────────────────────
    def test_sequencia_real(self):
        p = EDITORIAL_PROFILES["Seqüência (UFSC)"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("duplo-cega", texto, "avaliação duplo-cega")
        self.assertIn("ithenticate", texto, "iThenticate antiplágio")
        self.assertIn("cc by", texto, "CC BY 4.0")
        self.assertIn("abnt", p.reference_style.lower(), "ABNT")

    # ── REED ─────────────────────────────────────────────────────
    def test_reed_real(self):
        p = EDITORIAL_PROFILES["Revista de Estudos Empíricos em Direito"]
        texto = (p.scope + " " + " ".join(p.special_gates)).lower()
        self.assertIn("empíric", texto, "foco em pesquisa empírica")
        self.assertIn("orcid", texto, "ORCID")
        self.assertIn("6 meses", p.review_flow.lower(), "avaliação ~6 meses")
        self.assertIn("exogenia", " ".join(p.special_gates).lower(), "exogenia ≥75%")

    # ── Suprema (STF) ────────────────────────────────────────────
    def test_suprema_real(self):
        p = EDITORIAL_PROFILES["Suprema (STF)"]
        texto = (p.review_flow + " " + " ".join(p.special_gates)).lower()
        self.assertIn("duplo-cega", texto, "duplo-cega")
        self.assertIn("3", p.review_flow.lower(), "3º parecerista se impasse")
        self.assertIn("3 coautores", texto, "máximo 3 coautores")
        self.assertIn("semestral", p.scope.lower(), "periodicidade semestral")

    # ── anti-overclaim ───────────────────────────────────────────
    def test_profile_summary_anti_overclaim(self):
        for nome in PERFIS_R589:
            s = profile_summary(nome)
            self.assertTrue(s["found"], nome)
            self.assertIn("simulação", s["disclaimer"].lower(), nome)

    # ── aliases ──────────────────────────────────────────────────
    def test_get_profile_por_alias(self):
        pares = {
            "npjqi": "npj Quantum Information",
            "npj qi": "npj Quantum Information",
            "quantum": "Quantum",
            "qst": "Quantum Science and Technology",
            "tqe": "IEEE Transactions on Quantum Engineering",
            "ieee tqe": "IEEE Transactions on Quantum Engineering",
            "tqc": "ACM Transactions on Quantum Computing",
            "acm tqc": "ACM Transactions on Quantum Computing",
            "qip": "Quantum Information Processing",
            "direito gv": "Revista Direito GV",
            "direito e praxis": "Revista Direito e Práxis",
            "rda": "Revista de Direito Administrativo",
            "sequencia": "Seqüência (UFSC)",
            "sequencia ufsc": "Seqüência (UFSC)",
            "reed": "Revista de Estudos Empíricos em Direito",
            "suprema": "Suprema (STF)",
            "suprema stf": "Suprema (STF)",
        }
        for alias, canone in pares.items():
            p = get_profile(alias)
            self.assertIsNotNone(p, alias)
            self.assertEqual(p.journal, EDITORIAL_PROFILES[canone].journal, alias)


if __name__ == "__main__":
    unittest.main()