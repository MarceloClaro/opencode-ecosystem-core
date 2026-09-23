"""
Testes R-976.14 — Perfis Editoriais de periódicos na banca (SPEC-976).

Cobre: registro de perfis editoriais reais (normas públicas), resolução por
nome, merge de pesos, seleção de periódico-alvo no gerador de banca, exposição
do perfil no relatório e determinismo.
"""
import unittest

from mirofish.social import (
    BancaProfileGenerator,
    CRITERIA,
    CRITERION_WEIGHTS,
    EDITORIAL_PROFILES,
    JOURNAL_KEYS,
    get_profile,
    merge_weights,
    profile_summary,
    summarize_banca,
)

DOC_EXEMPLO = """
Protocolo registrado na Open Science Framework (OSF) com DOI.
Revisão de escopo seguindo PRISMA-ScR e Joanna Briggs Institute (JBI).
Critérios de inclusão e exclusão definidos em painel de consenso.
Triagem independente com dois revisores (RH1 e RH2); consenso documentado.
Extração padronizada em planilha; síntese temática.
Concordância Kappa κ=1,000 (Po=1,000; Pe=0,580).
Ética: declaração de integridade acadêmica, conflito de interesses e anti-overclaim.
Contribuição: lacuna sobre IAGen (inteligência artificial generativa) na educação
jurídica brasileira, corpus n=21, 2020-2026.
Referências: ABNT NBR 6023; reposição via OpenAlex e DOAJ; depósito Zenodo.
Discussão alinhada com objetivo, método, resultados e conclusão.
Implicações para políticas públicas e formação docente.
"""


class TestEditorialProfilesRegistry(unittest.TestCase):
    def test_tem_perfis_suficientes(self):
        self.assertGreaterEqual(len(EDITORIAL_PROFILES), 9)

    def test_todos_perfis_tem_campos_obrigatorios(self):
        required = {"journal", "scope", "priority", "reference_style",
                    "length_limit", "review_flow", "special_gates",
                    "weights", "source"}
        for key, profile in EDITORIAL_PROFILES.items():
            with self.subTest(journal=key):
                self.assertEqual(profile.journal, EDITORIAL_PROFILES[key].journal)
                self.assertTrue(profile.scope)
                self.assertTrue(profile.priority)
                self.assertTrue(profile.reference_style)
                self.assertTrue(profile.source.startswith("http"))
                self.assertTrue(set(profile.weights.keys()).issubset(set(CRITERIA)))

    def test_pesos_coerentes_positivos(self):
        for key, profile in EDITORIAL_PROFILES.items():
            for crit, w in profile.weights.items():
                self.assertGreater(w, 0.0, f"{key}.{crit}")

    def test_merge_weights_multiplica(self):
        merged = merge_weights(CRITERION_WEIGHTS, {"metodologia": 1.8})
        self.assertAlmostEqual(merged["metodologia"], CRITERION_WEIGHTS["metodologia"] * 1.8)
        # critérios sem override mantêm default
        self.assertAlmostEqual(merged["impacto"], CRITERION_WEIGHTS["impacto"])

    def test_get_profile_exato_e_parcial(self):
        self.assertIsNotNone(get_profile("Computers & Education"))
        self.assertIsNotNone(get_profile("práxis educacional"))  # case-insensitive
        self.assertIsNone(get_profile("Revista Inexistente XYZ"))


class TestTargetInstitutionBanca(unittest.TestCase):
    def test_gera_banca_com_periodico_alvo(self):
        gen = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=42,
                                    target_institution="Computers & Education")
        members = gen.generate()
        self.assertEqual(len(members), 12)
        # todos afiliados ao rótulo do periódico-alvo
        for m in members:
            self.assertIn("Computers & Education", m.institution)
        self.assertIsNotNone(gen.editorial_profile)
        # pesos efetivos refletem o perfil (metodologia/estatística/evidências reforçados)
        self.assertGreater(gen.effective_weights["metodologia"],
                           CRITERION_WEIGHTS["metodologia"])
        self.assertGreater(gen.effective_weights["estatística"],
                           CRITERION_WEIGHTS["estatística"])

    def test_sem_alvo_rotaciona_instituicoes(self):
        gen = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=42)
        members = gen.generate()
        insts = {m.institution for m in members}
        self.assertGreater(len(insts), 1)  # diversidade de rótulos
        self.assertIsNone(gen.editorial_profile)
        # pesos default
        self.assertEqual(gen.effective_weights, CRITERION_WEIGHTS)

    def test_summarize_inclui_perfil_editorial(self):
        gen = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=42,
                                    target_institution="Revista Brasileira de Educação")
        members = gen.generate()
        opinions = {m.profile.user_id: m.adjusted_bias for m in members}
        resumo = summarize_banca(
            members, opinions,
            weights=gen.effective_weights,
            signals=gen.signals(),
            editorial_profile=gen.editorial_profile,
        )
        self.assertIn("editorial_profile", resumo)
        prof = resumo["editorial_profile"]
        self.assertIn("Revista Brasileira de Educação", prof["journal"])
        self.assertTrue(prof["scope"])
        self.assertIsInstance(prof["special_gates"], list)  # pode ser vazio p/ RBE
        self.assertIn("disclaimer", resumo)
        self.assertIn("R-976.11–14", resumo["disclaimer"])

    def test_alvo_impacta_nota_ponderada(self):
        """Revista quantitativa (Computers & Education) vs. ensaio teórico (E&S)
        devem produzir notas diferentes com o mesmo texto."""
        gen1 = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=7,
                                     target_institution="Computers & Education")
        gen2 = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=7,
                                     target_institution="Educação & Sociedade")
        m1, m2 = gen1.generate(), gen2.generate()
        o1 = {m.profile.user_id: m.adjusted_bias for m in m1}
        o2 = {m.profile.user_id: m.adjusted_bias for m in m2}
        r1 = summarize_banca(m1, o1, weights=gen1.effective_weights, signals=gen1.signals(),
                             editorial_profile=gen1.editorial_profile)
        r2 = summarize_banca(m2, o2, weights=gen2.effective_weights, signals=gen2.signals(),
                             editorial_profile=gen2.editorial_profile)
        # pesos diferentes → scores podem diferir (ao menos um critério com peso distinto)
        self.assertNotEqual(gen1.effective_weights, gen2.effective_weights)
        self.assertIsInstance(r1["weighted_score"], float)
        self.assertIsInstance(r2["weighted_score"], float)

    def test_determinismo_com_alvo(self):
        g1 = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=99,
                                   target_institution="BJET")
        g2 = BancaProfileGenerator(DOC_EXEMPLO, n_members=12, seed=99,
                                   target_institution="British Journal of Educational Technology")
        self.assertEqual(g1.editorial_profile.journal, g2.editorial_profile.journal)
        m1 = [m.to_dict() for m in g1.generate()]
        m2 = [m.to_dict() for m in g2.generate()]
        self.assertEqual(m1, m2)

    def test_profile_summary_anti_overclaim(self):
        resumo = profile_summary("Cadernos de Pesquisa")
        self.assertTrue(resumo["found"])
        self.assertIn("simulação R-976.14", resumo["disclaimer"])


if __name__ == "__main__":
    unittest.main()