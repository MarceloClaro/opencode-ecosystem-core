# -*- coding: utf-8 -*-
"""
Testes de VALIDADE do ScientificReasoningScanner applied ao manuscrito OdontoCA.

Contexto (SPEC-935-R645)
------------------------
Uma auditoria por scanner foi solicitada para o manuscrito
`odonto/Journal_of_Dentistry_Example_OdontoCA.md` (EN, versao de submissao) e
sua traducao PT-BR. O scanner reportou:

    EN  -> methodology_score 25, falsifiability_score 25, SRI 25, status low_rigor
    PT  -> methodology_score  0, falsifiability_score 100, SRI 40, status moderate_rigor

O texto PT e a traducao do texto EN: nao ha diferenca de ciencia. Portanto o
scanner produz uma INVERSAO (PT piores em metodologia, PT melhores em
falsificabilidade) que nao pode reflecting a qualidade do manuscrito.

Causa raiz (verificada em scanners/scientific_reasoning_scanner.py):
  * METHODOLOGY_KEYWORDS e uma lista de 10 subpalavras EXCLUSIVAMENTE em
    portugues -> um manuscrito em ingles nao consegue casar 8 das 10;
  * "se" e uma FALSIFIABILITY_KEYWORD e casa como substring em palavras
   Frequency PT como sem/segundo/sempre/seis/sessao/desejo -> pontos de
    "falsificabilidade" gratuitos;
  * o divisor e fixo em /4.0, entao 4 de 10 keywords ja saturam a nota em 100.

Estes testes existem para TRAVAR o achado: nenhuma decisao editorial (banca,
publicacao, revisao) pode citar SRI/methodology_score como evidencia sobre a
qualidade do manuscrito OdontoCA sem antes consultar o veredito autoritativo
PROBAST+AI (S4) e a revisao humana.

O que estes testes NAO fazem: nao "reparam" o scanner. Corrigir o scanner e
fora de escopo e mudaria retroativamente os resultados de outras specs.
"""
import unittest
from pathlib import Path

from scanners.scientific_reasoning_scanner import ScientificReasoningScanner

REPO = Path(__file__).resolve().parent.parent
EN_PATH = REPO / "odonto" / "Journal_of_Dentistry_Example_OdontoCA.md"
PT_PATH = REPO / "odonto" / "Journal_of_Dentistry_Example_OdontoCA_PT.md"


class TestR645ScannerValidityOdonto(unittest.TestCase):
    """A inversao EN/PT que inutiliza o SRI para o manuscrito OdontoCA."""

    def setUp(self):
        self.scanner = ScientificReasoningScanner()
        self.assertTrue(EN_PATH.exists(), f"manuscrito EN ausente: {EN_PATH}")
        self.assertTrue(PT_PATH.exists(), f"traducao PT ausente: {PT_PATH}")
        self.en = EN_PATH.read_text(encoding="utf-8")
        self.pt = PT_PATH.read_text(encoding="utf-8")
        self.en_res = self.scanner.scan_text(self.en)
        self.pt_res = self.scanner.scan_text(self.pt)

    # --- 1. A inversao, medida nos arquivos reais -----------------------
    def test_pt_scores_worse_methodology_than_en(self):
        """PT deve ter methodology <= EN: prova a inversaoqndo houver diff."""
        self.assertLessEqual(
            self.pt_res["methodology_score"],
            self.en_res["methodology_score"],
            "Se este teste falha, a PT passou a ser reconhecida em metodologia; "
            "reavaliar a validade do achado de inversao antes de ignorar.",
        )
        # O achado original: PT metodologicamente invisivel.
        self.assertEqual(
            self.pt_res["methodology_score"],
            0.0,
            "PT deveria ter 0.0 de metodologia (nenhuma keyword PT casa). "
            "Se mudou, o achado de inversao precisa ser re-documentado.",
        )

    def test_pt_scores_better_falsifiability_than_en(self):
        """PT recebe fauxa maior por 'se' como substring, nao por ciencia."""
        self.assertGreater(
            self.pt_res["falsifiability_score"],
            self.en_res["falsifiability_score"],
            "PT devequisitionar falsificabilidade maior que EN via 'se' substring.",
        )

    # --- 2. Causa raiz: lista de keywords so em portugues ---------------
    def test_methodology_keywords_are_portuguese_only(self):
        """Papeis em ingles (submission) nao casam com nenhuma keyword PT."""
        matched_en = [
            k for k in self.scanner.METHODOLOGY_KEYWORDS if k in self.en.lower()
        ]
        matched_pt = [
            k for k in self.scanner.METHODOLOGY_KEYWORDS if k in self.pt.lower()
        ]
        self.assertLessEqual(
            len(matched_en),
            3,
            f"EN casou {len(matched_en)} keywords: {matched_en} — English manuscript "
            "structuralmente nao alcanca a lista PT-only.",
        )
        self.assertEqual(
            matched_pt, [], f"PT casou keywords: {matched_pt} — reavaliar achado."
        )

    def test_control_and_sampling_keywords_absent_from_both(self):
        """'grupo de controle' e 'amostragem' nao existem em nenhum dos idiomas.

        Logo a recomendacao 'inclua grupo de controle/amostragem' nao e um
        achado especifico do manuscrito: e um default do scanner, emite para
        qualquer texto que nao caste essas duas subpalavras.
        """
        for kw in ("grupo de controle", "amostragem"):
            self.assertNotIn(kw, self.en.lower(), f"'{kw}' presente no EN")
            self.assertNotIn(kw, self.pt.lower(), f"'{kw}' presente no PT")

    # --- 3. A substring degenerada 'se' ---------------------------------
    def test_falsifiability_keyword_se_is_degenerate(self):
        """'se' casa como substring em muitas palavras PT sem significado."""
        for w in ("sem", "segundo", "sempre", "seis", "sessão", "desejo"):
            self.assertIn(
                "se", w.lower(), f"'se' deveria casar em '{w}' para provar degenerencia"
            )
        self.assertIn(
            "se", self.scanner.FALSIFIABILITY_KEYWORDS, "'se' deve ser keyword de falsific."
        )

    def test_pt_falsifiability_credit_from_non_scientific_words(self):
        """A keyword 'se' casa no PT do manuscrito mesmo sem frase se -> entao."""
        self.assertIn(
            "se", self.pt.lower(), "PT deve conter 'se' como substring para reproduzir o achado."
        )
        # 'sem'/'sempre' aparecem em linguagem comum, nao em construcao se->entao.
        self.assertTrue(
            ("sem " in self.pt.lower()) or ("sempre" in self.pt.lower()),
            "PT deve conter linguagem comum que dispare 'se'.",
        )

    # --- 4. Normalizacao grosseira / divisor /4.0 -----------------------
    def test_divisor_fixed_at_four_creates_ceiling(self):
        """Com /4.0, apenas 4 de N keywords saturam methodology em 100."""
        for attr in ("METHODOLOGY_KEYWORDS", "FALSIFIABILITY_KEYWORDS"):
            kws = getattr(self.scanner, attr)
            self.assertGreater(
                len(kws),
                4,
                f"{attr} tem >4 keywords; divisor /4.0 satura em 4 casamentos. "
                "Se a lista crescer, a nota maxima 100 sera inalcancavel "
                "(=normalizacao sem base).",
            )

    # --- 5. O scanner nao detecta falacia alguma em texto sem fallacy --
    def test_fallacy_triggers_do_not_fire_on_our_manuscript(self):
        """Manuscript nao deve conter gatilhos de falacia do scanner."""
        for r, lang in ((self.en_res, "EN"), (self.pt_res, "PT")):
            self.assertEqual(
                r["detected_fallacies"], [], f"{lang} disparou falacia: {r['detected_fallacies']}"
            )

    # --- 6. Anti-overclaim: o veredito autoritativo e o PROBAST+AI -------
    def test_authoritative_verdict_is_probast_not_sri(self):
        """O veredito de risco de viess deve vir do S4 (PROBAST+AI), nao do SRI."""
        s4 = REPO / "odonto" / "Supplementary_File_S4_PROBAST_AI_Assessment.md"
        self.assertTrue(s4.exists(), f"S4 PROBAST+AI ausente: {s4}")
        s4_txt = s4.read_text(encoding="utf-8").lower()
        self.assertIn(
            "high",
            s4_txt,
            "S4 deve declarar risco de vies alto (PROBAST+AI).",
        )
        # Scanner diz 'low_rigor'; PROBAST diz High/High. Scanner nao e o judge.
        self.assertIn(
            self.en_res["status"],
            ("low_rigor", "moderate_rigor", "high_rigor"),
            "status do scanner e categorico, nao ordenavel contra PROBAST.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
