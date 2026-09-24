"""
Testes R-976.15 — Perfil editorial Journal of Dentistry (SPEC-976).

Baseado no template oficial de Review Article do Journal of Dentistry (Elsevier),
compartilhado pelo autor em Google Docs (2026-09-24): abstract estruturado com
Clinical significance, protocolo registrado, quadro PCC, PRISMA-ScR, seleção
dupla independente, extração padronizada, referências numeradas com DOI,
declarações obrigatórias (CRediT, competição, ética, dados, IA generativa) e
anti-overclaim explícito ("não implicar registro sem registro").
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

TEXTO_SCORING_REVIEW = """
Protocolo registrado na Open Science Framework (OSF) com DOI.
Revisão de escopo seguindo PRISMA-ScR e Joanna Briggs Institute (JBI).
Quadro PCC: população, conceito e contexto definidos.
Triagem independente por dois revisores (RH1 e RH2); concordância κ=1,000.
Extração padronizada; síntese descritiva com contagens e proporções.
Declarações: CRediT, conflito de interesses, ética, disponibilidade de dados
e uso de IA generativa.
Implicações proporcionais à evidência; novidade verificada na literatura.
"""


class TestJournalOfDentistryProfile(unittest.TestCase):
    def test_perfil_registrado(self):
        self.assertIn("Journal of Dentistry", EDITORIAL_PROFILES)
        self.assertIn("Journal of Dentistry", JOURNAL_KEYS)

    def test_campos_obrigatorios(self):
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        self.assertTrue(p.scope)
        self.assertTrue(p.priority)
        self.assertTrue(p.reference_style)
        self.assertTrue(p.review_flow)
        self.assertTrue(p.length_limit)
        self.assertIsInstance(p.special_gates, list)
        self.assertTrue(p.source.startswith("http"))
        self.assertTrue(set(p.weights.keys()).issubset(set(CRITERIA)))

    def test_fonte_modelo_google_docs(self):
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        self.assertIn("docs.google.com", p.source)

    def test_gates_editoriais_jod(self):
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        # gate de IA generativa (o template exige declaração de IA)
        self.assertTrue(any("IA" in g or "generative AI" in g or "generativa" in g
                            for g in p.special_gates))

    def test_gates_rigor_edital_oficial(self):
        """Gates derivados do Guide for Authors oficial (Elsevier, acesso 2026-09-24)."""
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        conj = " ".join(p.special_gates).lower()
        # tipos de artigo rejeitados
        self.assertIn("case reports", conj)
        # consort/icmje para ensaios
        self.assertIn("consort", conj)
        self.assertIn("icmje", conj)
        # seção de IA antes das referências
        self.assertTrue(
            any(frase in conj for frase in ("antes das referências", "before references")),
            "declaração de IA deve exigir seção própria antes das referências",
        )

    def test_length_limit_edital_oficial(self):
        """Limites por tipo conforme guia oficial (review ≈ 10 pp impressas)."""
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        self.assertIn("10", p.length_limit)
        self.assertIn("33", p.length_limit)

    def test_review_flow_timeline_edital(self):
        """Timeline e fases de decisão do guia oficial."""
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        self.assertIn("5 dias", p.review_flow)
        self.assertIn("29 dias", p.review_flow)
        self.assertIn("74 dias", p.review_flow)

    def test_reference_style_numerado_com_doi(self):
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        self.assertIn("DOI", p.reference_style)
        self.assertIn("[", p.reference_style)  # estilo numerado []

    def test_alias_jod(self):
        self.assertEqual(get_profile("Journal of Dentistry").journal,
                         get_profile("journal of dentistry").journal)
        self.assertEqual(get_profile("jod").journal,
                         EDITORIAL_PROFILES["Journal of Dentistry"].journal)
        self.assertIsNotNone(JOURNAL_ALIASES.get("jod"))

    def test_pesos_positivos_e_merge(self):
        p = EDITORIAL_PROFILES["Journal of Dentistry"]
        for w in p.weights.values():
            self.assertGreater(w, 0.0)
        merged = merge_weights(CRITERION_WEIGHTS, p.weights)
        self.assertAlmostEqual(
            merged["metodologia"], CRITERION_WEIGHTS["metodologia"] * p.weights["metodologia"])

    def test_banca_afiliada_ao_jod(self):
        gen = BancaProfileGenerator(TEXTO_SCORING_REVIEW, n_members=12, seed=42,
                                    target_institution="Journal of Dentistry")
        members = gen.generate()
        self.assertEqual(len(members), 12)
        for m in members:
            self.assertIn("Journal of Dentistry", m.institution)
        self.assertIsNotNone(gen.editorial_profile)
        # perfil reforça metodologia/evidências/reprodutibilidade
        self.assertGreater(gen.effective_weights["metodologia"], CRITERION_WEIGHTS["metodologia"])
        self.assertGreater(gen.effective_weights["evidências"], CRITERION_WEIGHTS["evidências"])
        self.assertGreater(gen.effective_weights["reprodutibilidade"],
                           CRITERION_WEIGHTS["reprodutibilidade"])

    def test_summarize_com_perfil_jod(self):
        gen = BancaProfileGenerator(TEXTO_SCORING_REVIEW, n_members=12, seed=42,
                                    target_institution="Journal of Dentistry")
        members = gen.generate()
        opinions = {m.profile.user_id: m.adjusted_bias for m in members}
        resumo = summarize_banca(
            members, opinions,
            weights=gen.effective_weights,
            signals=gen.signals(),
            editorial_profile=gen.editorial_profile,
        )
        self.assertIn("editorial_profile", resumo)
        self.assertIn("Journal of Dentistry", resumo["editorial_profile"]["journal"])
        self.assertIn("disclaimer", resumo)

    def test_profile_summary_anti_overclaim(self):
        resumo = profile_summary("Journal of Dentistry")
        self.assertTrue(resumo["found"])
        self.assertIn("simulação", resumo["disclaimer"])
        self.assertIn("Journal of Dentistry", resumo["journal"])

    def test_determinismo_com_alvo_jod(self):
        g1 = BancaProfileGenerator(TEXTO_SCORING_REVIEW, n_members=12, seed=7,
                                   target_institution="Journal of Dentistry")
        g2 = BancaProfileGenerator(TEXTO_SCORING_REVIEW, n_members=12, seed=7,
                                   target_institution="jod")
        m1 = [m.to_dict() for m in g1.generate()]
        m2 = [m.to_dict() for m in g2.generate()]
        self.assertEqual(m1, m2)


if __name__ == "__main__":
    unittest.main()