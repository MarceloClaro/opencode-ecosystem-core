"""
Testes R-976.18 — Editais de submissão dos perfis editoriais originais (SPEC-976).

Guias de submissão OFICIAIS consultados em 24/09/2026:
- RBE (ANPEd/SciELO OJS): artigos 40.000–70.000 caracteres com espaços INCLUINDO
  refs, notas, título, resumo e palavras-chave nos 3 idiomas; resumo ≤1.000
  caracteres por idioma (PT/EN/ES; +FR se original em francês); Espaço Aberto
  30–50 mil; resenhas ≤10 mil; referências ABNT obrigatórias (senão não
  consideradas); notas de rodapé exclusivamente explicativas; duplo-cego;
  Times New Roman 12; cessão integral de direitos.
- Educação & Sociedade (CEDES/SciELO): Similarity Check (plágio/autoplágio/
  republicação/falsificação); tamanho de referência ~45.000 caracteres; avaliação
  aberta opcional (open evaluation); declaração de ética obrigatória; CC BY 4.0.
- Cadernos de Pesquisa (FCC): iThenticate 2.0 como scanner antiplágio; desk
  review; duplo-anônimo; open peer review experimental; fluxo em 8 etapas.
- Práxis Educacional (UESB): ABNT (NBR 6022/6028/10520); desk review; duplo-cega;
  divergência → 3º parecerista ad hoc ou parecer de consolidação editorial;
  máx. 3 autores (4 excepcional justificado); ≥1 doutor; contribuições declaradas.
- Computers & Education (Elsevier): double anonymized; ≥2 revisores; artigos
  ≤8.000 palavras excluindo refs/apêndices; declaração de IA generativa
  obrigatória; revisores/editores PROIBIDOS de submeter manuscrito a IA;
  arquivos editáveis (.doc/.docx/.tex, PDF não é fonte aceitável); title page +
  manuscrito anônimo em arquivos separados.
- BJET (BERA/Wiley): Original/Review 5.000–6.000 palavras excl. refs/abstracts/
  practitioner notes/apêndices/suplementares, INCLUINDO tabelas/figuras/footnotes;
  double-anonymised; Free Format; leeway >6000 mediante email ao editor;
  decisão final sobre GenAI com o editor.
- EIT (Springer/IFIP TC3): NÃO permite mudança de autoria após submissão;
  arquivos editáveis obrigatórios em toda submissão/revisão (senão → não
  considerado); NÃO aceita mais review papers (literature/systematic/
  bibliometric reviews); double-anonymous; ORCID; IF 7.2; 1ª decisão ~29 dias.
- IRE (UNESCO UIL/Springer): Articles ≤6.000 palavras (excl. abstract e
  bibliografia); Research notes ≤3.000; Book reviews ≤1.000 (EN/FR); double-blind
  (artigos e research notes; book reviews excluídas); abstract 150–250 palavras;
  4–6 keywords; .docx/Times New Roman 12; IF 1.9; 1ª decisão mediana 97 dias.
- Práxis Educativa (UEPG): artigos 20–28 páginas; resenhas 4–7 páginas (livros
  últimos 5 anos); resumo ≤10 linhas (150 palavras) com 3 palavras-chave em
  PT/EN/ES; sem identificação de autoria; APA; ética CNS 466/2012 + 510/2016 +
  CNPq; controle de plágio/autoplágio; 2 pareceristas (opiniões contraditórias →
  outros pareceristas); atualmente NÃO aceita submissões.
- Estudos em Avaliação Educacional (FCC): duplo anônimo; ≥2 pareceristas ad hoc;
  preprint → avaliação simples anônimo (revisor conhece autoria); parecer
  consolidado do Comitê Editorial; CC BY 4.0; e-ISSN 1984-932X; fluxo contínuo.
- Educação (PUCRS): APA; folha de rosto separada obrigatória; declaração de IA
  obrigatória (omissão = infração ética); Turnitin; análise de forma com 8
  critérios de rejeição; ≥2 pareceristas; prazo 30 dias p/ reformulações;
  máx. 20 páginas; ≤4 autores (3 resenhas/traduções); titulação ≥ doutorado em
  andamento; CC BY 4.0; sem APCs; e-ISSN 1981-2582.
"""
import unittest

from mirofish.social import (
    CRITERIA,
    EDITORIAL_PROFILES,
    JOURNAL_KEYS,
    get_profile,
    profile_summary,
)

PERFIS_ORIGINAIS = [
    "Revista Brasileira de Educação",
    "Educação & Sociedade",
    "Cadernos de Pesquisa",
    "Práxis Educacional",
    "Computers & Education",
    "British Journal of Educational Technology",
    "Education and Information Technologies",
    "International Review of Education",
    "Práxis Educativa",
    "Estudos em Avaliação Educacional",
    "Educação (PUCRS)",
]


class TestEditaisPerfisOriginais(unittest.TestCase):
    def test_perfis_registrados(self):
        for nome in PERFIS_ORIGINAIS:
            self.assertIn(nome, EDITORIAL_PROFILES, f"perfil ausente: {nome}")
            self.assertIn(nome, JOURNAL_KEYS)

    def test_campos_obrigatorios(self):
        for nome in PERFIS_ORIGINAIS:
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

    # ── RBE (ANPEd) ─────────────────────────────────────────────
    def test_rbe_length_real(self):
        p = EDITORIAL_PROFILES["Revista Brasileira de Educação"]
        self.assertIn("70.000", p.length_limit.lower())
        self.assertIn("40.000", p.length_limit.lower())

    def test_rbe_gates_real(self):
        p = EDITORIAL_PROFILES["Revista Brasileira de Educação"]
        texto = " | ".join(p.special_gates).lower()
        tudo = (p.length_limit + " " + texto).lower()
        self.assertIn("abnt", p.reference_style.lower())
        self.assertIn("1.000 caracteres", texto, "exige resumo ≤1.000 caracteres")
        self.assertIn("espaço aberto", tudo, "seção Espaço Aberto (30–50 mil)")
        self.assertIn("nota", texto, "notas de rodapé explicativas")

    # ── Educação & Sociedade (CEDES) ─────────────────────────────
    def test_ees_gates_real(self):
        p = EDITORIAL_PROFILES["Educação & Sociedade"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("similarity check", p.review_flow.lower())
        self.assertIn("integridade", texto, "declaração de integridade")
        self.assertIn("conflito", texto, "conflito de interesses")
        self.assertIn("45.000", p.length_limit.lower(), "tamanho ~45.000 caracteres")

    # ── Cadernos de Pesquisa (FCC) ───────────────────────────────
    def test_cadernos_gates_real(self):
        p = EDITORIAL_PROFILES["Cadernos de Pesquisa"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("ithenticate", texto, "iThenticate 2.0 como scanner")
        self.assertIn("desk", p.review_flow.lower(), "desk review")
        self.assertIn("anônimo", p.review_flow.lower(), "duplo-anônimo")
        self.assertIn("8 etapas", p.review_flow.lower(), "fluxo em 8 etapas")

    # ── Práxis Educacional (UESB) ────────────────────────────────
    def test_praxis_educacional_gates_real(self):
        p = EDITORIAL_PROFILES["Práxis Educacional"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("autor", texto, "limite de autores + titulação")
        self.assertIn("contribuições", texto, "contribuições declaradas")
        self.assertIn("abnt", p.reference_style.lower())
        self.assertIn("consolidação", p.review_flow.lower(), "parecer de consolidação")

    # ── Computers & Education (Elsevier) ─────────────────────────
    def test_ce_length_real(self):
        p = EDITORIAL_PROFILES["Computers & Education"]
        self.assertIn("8.000", p.length_limit.lower())
        self.assertIn("double anonymized", p.review_flow.lower())

    def test_ce_gates_real(self):
        p = EDITORIAL_PROFILES["Computers & Education"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("generativa", texto, "declaração de IA generativa")
        self.assertIn("revisores", texto, "revisores proibidos de usar IA")
        self.assertIn("editáveis", texto, "arquivos editáveis obrigatórios")

    # ── BJET (BERA/Wiley) ────────────────────────────────────────
    def test_bjet_length_real(self):
        p = EDITORIAL_PROFILES["British Journal of Educational Technology"]
        self.assertIn("5.000", p.length_limit.lower())
        self.assertIn("6.000", p.length_limit.lower())

    def test_bjet_gates_real(self):
        p = EDITORIAL_PROFILES["British Journal of Educational Technology"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("double", p.review_flow.lower(), "double-anonymised")
        self.assertIn("anonym", p.review_flow.lower(), "double-anonymised")

    # ── EIT (Springer/IFIP TC3) ──────────────────────────────────
    def test_eit_gates_real(self):
        p = EDITORIAL_PROFILES["Education and Information Technologies"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("autoria", texto, "sem mudança de autoria após submissão")
        self.assertIn("editáveis", texto, "arquivos editáveis obrigatórios")
        self.assertIn("double-anonymous", p.review_flow.lower(), "double-anonymous")

    def test_eit_review_papers_rejected(self):
        p = EDITORIAL_PROFILES["Education and Information Technologies"]
        texto = (p.priority + " " + p.scope).lower()
        self.assertIn("não aceita", texto, "declara restrição a review papers")
        self.assertIn("review papers", texto, "menciona review papers na restrição")

    # ── IRE (UNESCO UIL/Springer) ────────────────────────────────
    def test_ire_length_real(self):
        p = EDITORIAL_PROFILES["International Review of Education"]
        self.assertIn("6.000", p.length_limit.lower())

    def test_ire_gates_real(self):
        p = EDITORIAL_PROFILES["International Review of Education"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("research notes", texto, "research notes ≤3.000")
        self.assertIn("book reviews", texto, "book reviews ≤1.000")
        self.assertIn("150", texto, "abstract 150–250 palavras")
        self.assertIn("keywords", texto, "4–6 keywords")

    # ── Práxis Educativa (UEPG) ──────────────────────────────────
    def test_praxis_educativa_length_real(self):
        p = EDITORIAL_PROFILES["Práxis Educativa"]
        self.assertIn("20", p.length_limit.lower())
        self.assertIn("28", p.length_limit.lower())

    def test_praxis_educativa_gates_real(self):
        p = EDITORIAL_PROFILES["Práxis Educativa"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("apa", p.reference_style.lower())
        self.assertIn("ética", texto, "Res. CNS 466/2012 e 510/2016")
        self.assertIn("plágio", texto, "controle de plágio/autoplágio")
        self.assertIn("não aceita", texto.lower(), "não aceita submissões no momento")

    # ── Estudos em Avaliação Educacional (FCC) ───────────────────
    def test_eae_gates_real(self):
        p = EDITORIAL_PROFILES["Estudos em Avaliação Educacional"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("ad hoc", p.review_flow.lower(), "≥2 pareceristas ad hoc")
        self.assertIn("consolidado", p.review_flow.lower(), "parecer consolidado")
        self.assertIn("preprint", texto, "preprint → simples anônimo")
        self.assertIn("cc by", texto, "licença CC BY 4.0")

    # ── Educação (PUCRS) ─────────────────────────────────────────
    def test_pucrs_gates_real(self):
        p = EDITORIAL_PROFILES["Educação (PUCRS)"]
        texto = " | ".join(p.special_gates).lower()
        self.assertIn("turnitin", texto, "Turnitin para plágio")
        self.assertIn("declaração de ia", texto, "declaração de IA obrigatória")
        self.assertIn("20", p.length_limit.lower(), "máx. 20 páginas")
        self.assertIn("folha de rosto", texto, "folha de rosto separada")
        self.assertIn("apa", p.reference_style.lower(), "referência APA")

    def test_profile_summary_anti_overclaim(self):
        for nome in PERFIS_ORIGINAIS:
            s = profile_summary(nome)
            self.assertTrue(s["found"], nome)
            self.assertIn("simulação", s["disclaimer"].lower(), nome)

    def test_get_profile_por_alias(self):
        pares = {
            "rbe": "Revista Brasileira de Educação",
            "ees": "Educação & Sociedade",
            "cadernos": "Cadernos de Pesquisa",
            "ce": "Computers & Education",
            "bjet": "British Journal of Educational Technology",
            "eit": "Education and Information Technologies",
            "ire": "International Review of Education",
            "educacao pucrs": "Educação (PUCRS)",
            "estudos em avaliacao": "Estudos em Avaliação Educacional",
        }
        for alias, canone in pares.items():
            p = get_profile(alias)
            self.assertIsNotNone(p, alias)
            self.assertEqual(p.journal, EDITORIAL_PROFILES[canone].journal, alias)


if __name__ == "__main__":
    unittest.main()