"""
Testes R-976.17 — Perfis de periódicos odontológicos e de outras áreas reais (SPEC-976).

Guia de autores oficiais consultados em 24/09/2026:
- JDR (IADR/Sage): CSE 9ª ed.; Original Research 3.200 palavras (excl. abstract/ack/legends/
  refs), 5 fig./tab., 40 refs, abstract 300 palavras; Critical Reviews 4.000 palavras, 6
  fig./tab., refs até ~60; Clinical Reviews (antigas Concise Reviews); Letters 250; Discovery!
  apenas por convite; 1ª decisão ~17-18 dias; COPE; ICMJE Uniform Requirements.
- Clinical Oral Investigations (Springer): single-blind; Original 4.000 palavras (excl.
  abstract/refs/tab/fig), 6 tab/fig, 60 refs; abstract estruturado 150-250 palavras com
  Objective/Methods/Results/Conclusions/Clinical Relevance; Opinion 1.500-3.000 palavras;
  Case Reports desencorajados; 1ª decisão ~6 dias; IF 3.6.
- Medical Image Analysis (Elsevier/MICCAI): single anonymized; ≥2 revisores; escopo
  processamento/análise de imagens médicas e biológicas (computer vision, VR, robótica);
  CiteScore 25.8, IF 14.0; coluna única (word/tex).
- Artificial Intelligence in Medicine (Elsevier): exige NOVIDADE metodológica/teórica em IA
  e Ciência da Computação (mera aplicação de algoritmos conhecidos NÃO é aceita); declaração
  de IA generativa obrigatória; revisores/editores proibidos de submeter manuscrito a IA.
- Journal of Biomedical Informatics (Elsevier/AMIA): periódico de metodologia; métodos novos
  com aplicação geral; single anonymized; ≥2 revisores; APC USD 3.550; timeline 2 dias desk /
  49 dias pós-review / 142 dias até aceite; CiteScore 10.8, IF 5.9.
- npj Digital Medicine (Nature Portfolio): sem limites estritos de palavras (online); Article
  com abstract ≤150 palavras; refs ~60; CONSORT obrigatório p/ RCTs; Data Availability
  Statement obrigatório; title ≤15 palavras; cover letter obrigatório; 1ª decisão ~5 dias;
  IF 12.4; sistemáticas/escopo/meta submetidas como Article.
"""
import unittest

from mirofish.social import (
    BancaProfileGenerator,
    CRITERIA,
    CRITERION_WEIGHTS,
    EDITORIAL_PROFILES,
    JOURNAL_KEYS,
    JOURNAL_ALIASES,
    get_profile,
    merge_weights,
    profile_summary,
    summarize_banca,
)

NOVOS_PERIODICOS = [
    "Journal of Dental Research",
    "Clinical Oral Investigations",
    "Medical Image Analysis",
    "Artificial Intelligence in Medicine",
    "Journal of Biomedical Informatics",
    "npj Digital Medicine",
]

TEXTO_METODOLOGICO = """
Método original com fundamentação teórica explícita (modelagem formal e
justificativa frente ao estado da arte). Protocolo registrado com DOI.
Validação reprodutível: código e dados disponíveis; seeds e ambiente
documentados. Avaliação comparativa contra baseline com métricas e
intervalos de confiança; análise estatística adequada ao desenho.
Declarações: conflito de interesses, ética, disponibilidade de dados e
uso de IA generativa. Implicações proporcionais à evidência.
"""


class TestPerfisPeriodicosReais(unittest.TestCase):
    def test_perfis_registrados(self):
        for nome in NOVOS_PERIODICOS:
            self.assertIn(nome, EDITORIAL_PROFILES, f"perfil ausente: {nome}")
            self.assertIn(nome, JOURNAL_KEYS)

    def test_campos_obrigatorios(self):
        for nome in NOVOS_PERIODICOS:
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

    def test_aliases(self):
        pares = {
            "jdr": "Journal of Dental Research",
            "journal of dental research": "Journal of Dental Research",
            "coi": "Clinical Oral Investigations",
            "clinical oral investigations": "Clinical Oral Investigations",
            "mia": "Medical Image Analysis",
            "medical image analysis": "Medical Image Analysis",
            "aiim": "Artificial Intelligence in Medicine",
            "artificial intelligence in medicine": "Artificial Intelligence in Medicine",
            "jbi": "Journal of Biomedical Informatics",
            "journal of biomedical informatics": "Journal of Biomedical Informatics",
            "npj digital medicine": "npj Digital Medicine",
        }
        for alias, canone in pares.items():
            self.assertEqual(
                get_profile(alias).journal,
                EDITORIAL_PROFILES[canone].journal,
                f"alias {alias} -> {canone}",
            )
            self.assertIsNotNone(JOURNAL_ALIASES.get(alias))

    def test_jdr_rigor_guia(self):
        """JDR: CSE 9ª ed., limites por tipo, ICMJE, 1ª decisão ~17-18 dias."""
        p = EDITORIAL_PROFILES["Journal of Dental Research"]
        conj_flow = p.review_flow.lower()
        self.assertIn("cse", p.reference_style.lower() or conj_flow)
        self.assertIn("3.200", p.length_limit or "")
        self.assertIn("icmje", conj_flow)
        self.assertIn("17", conj_flow)
        # gates editoriais essenciais
        conj = " ".join(p.special_gates).lower()
        self.assertIn("300", conj)          # abstract 300 palavras p/ originais
        self.assertTrue(any("convite" in g or "invitation" in g.lower() for g in p.special_gates))

    def test_coi_rigor_guia(self):
        """COI: single-blind, abstract 150-250 com Clinical Relevance, 4.000 palavras."""
        p = EDITORIAL_PROFILES["Clinical Oral Investigations"]
        conj = " ".join(p.special_gates).lower()
        self.assertIn("clinical relevance", conj)
        self.assertIn("150", conj)
        self.assertIn("250", conj)
        self.assertIn("single-blind", p.review_flow.lower())
        self.assertIn("4.000", p.length_limit or "")
        # Case Reports desencorajados
        self.assertTrue(any("case report" in g.lower() for g in p.special_gates))

    def test_mia_rigor_guia(self):
        """Medical Image Analysis: single anonymized, ≥2 revisores, MICCAI."""
        p = EDITORIAL_PROFILES["Medical Image Analysis"]
        conj = " ".join(p.special_gates).lower()
        self.assertIn("single anonymized", p.review_flow.lower())
        self.assertTrue(
            any(frase in conj for frase in ("dois revisores", "2 revisores", "≥2 revisores")),
            "deve exigir ao menos dois revisores independentes",
        )
        self.assertIn("miccai", p.scope.lower())

    def test_aiim_rigor_guia(self):
        """AIIM: novidade metodológica em IA/CS obrigatória; mera aplicação rejeitada."""
        p = EDITORIAL_PROFILES["Artificial Intelligence in Medicine"]
        conj = " ".join(p.special_gates).lower()
        self.assertIn("novidade", conj)
        self.assertTrue(any("aplicação" in g.lower() and ("não" in g.lower() or "rejeit" in g.lower())
                            for g in p.special_gates))
        # gate de IA generativa obrigatória
        self.assertTrue(any("ia generativa" in g.lower() or "generative ai" in g.lower()
                            for g in p.special_gates))

    def test_jbi_rigor_guia(self):
        """JBI: metodologia com aplicação geral; single anonymized; timeline oficial."""
        p = EDITORIAL_PROFILES["Journal of Biomedical Informatics"]
        conj_flow = p.review_flow.lower()
        self.assertIn("single anonymized", conj_flow)
        self.assertIn("2 dias", conj_flow)
        self.assertIn("49 dias", conj_flow)
        self.assertIn("142 dias", conj_flow)
        conj = " ".join(p.special_gates).lower()
        self.assertIn("metodologia", p.scope.lower() + conj)
        self.assertIn("aplicação geral", p.scope.lower() + conj)

    def test_npj_digital_rigor_guia(self):
        """npj Digital Medicine: abstract ≤150, CONSORT RCTs, Data Availability obrigatório."""
        p = EDITORIAL_PROFILES["npj Digital Medicine"]
        conj = " ".join(p.special_gates).lower()
        self.assertIn("150", conj)
        self.assertIn("consort", conj)
        self.assertIn("data availability", conj)
        # sistemáticas como Article
        self.assertIn("article", conj) or self.assertIn("article", p.priority.lower())

    def test_banca_afiliada_novos(self):
        for nome in NOVOS_PERIODICOS:
            gen = BancaProfileGenerator(TEXTO_METODOLOGICO, n_members=12, seed=42,
                                        target_institution=nome)
            members = gen.generate()
            self.assertEqual(len(members), 12, nome)
            for m in members:
                self.assertIn(nome, m.institution)
            self.assertIsNotNone(gen.editorial_profile, nome)
            self.assertGreater(gen.effective_weights["metodologia"],
                               CRITERION_WEIGHTS["metodologia"], nome)

    def test_summarize_com_perfil_novo(self):
        gen = BancaProfileGenerator(TEXTO_METODOLOGICO, n_members=12, seed=42,
                                    target_institution="Journal of Biomedical Informatics")
        members = gen.generate()
        opinions = {m.profile.user_id: m.adjusted_bias for m in members}
        resumo = summarize_banca(
            members, opinions,
            weights=gen.effective_weights,
            signals=gen.signals(),
            editorial_profile=gen.editorial_profile,
        )
        self.assertIn("editorial_profile", resumo)
        self.assertIn("disclaimer", resumo)

    def test_determinismo_aliases_novos(self):
        g1 = BancaProfileGenerator(TEXTO_METODOLOGICO, n_members=12, seed=7,
                                   target_institution="npj Digital Medicine")
        g2 = BancaProfileGenerator(TEXTO_METODOLOGICO, n_members=12, seed=7,
                                   target_institution="npj")
        m1 = [m.to_dict() for m in g1.generate()]
        m2 = [m.to_dict() for m in g2.generate()]
        self.assertEqual(m1, m2)


if __name__ == "__main__":
    unittest.main()