# -*- coding: utf-8 -*-
"""Auditoria bibliográfica — SPEC-935-R408.

Gera outputs/citation_audit.csv a partir da lista de referências únicas do
manuscrito. Status conservador: sem resolução página a página das fontes,
nenhuma alegação específica é confirmada como 'confirmed'; apenas a
identidade da obra e a presença de DOI/URL são registradas como metadados
verificáveis no artefato.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

AUDIT_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = AUDIT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# chave, autor, obra, ano, doi_verificado, url, status, pertinencia_alegacao,
# observacao
REFERENCES = [
    ("ABRUCIO2016", "ABRUCIO; SEGGATTO; PEREIRA", "O modelo cearense de educação (capítulo)", 2016,
     "sem_doi", "capítulo em livro", "not_verified", "not_verified",
     "Capítulo sem DOI; conteúdo não acessado — alegação sobre Ceará/IDEB não verificada página a página."),
    ("ACEMOGLU_GALLEGO2014", "ACEMOGLU; GALLEGO; ROBINSON", "Institutions, human capital, and development", 2014,
     "10.1146/annurev-economics-080213-041119", "doi.org", "partial", "partial",
     "DOI bem formado e obra canônica; alegação específica (IVs reduzem efeito causal) consistente com a tese do artigo, mas páginas não verificadas."),
    ("ACEMOGLU_ROBINSON2012", "ACEMOGLU; ROBINSON", "Why nations fail", 2012,
     "sem_doi", "livro Crown Business", "partial", "partial",
     "Obra canônica; alegação sobre Argentina/reversão de prosperidade consistente com a tese, sem verificação de página."),
    ("AIYAR2018", "AIYAR et al.", "Growth slowdowns and the middle-income trap", 2018,
     "10.1016/j.japwor.2018.07.001", "doi.org", "partial", "partial",
     "DOI válido (versão em periódico 2018); manuscrito cita também IMF WP 2013 — dupla versão não esclarecida."),
    ("BARRO_LEE2013", "BARRO; LEE", "A new data set of educational attainment 1950-2010", 2013,
     "10.1016/j.jdeveco.2012.10.001", "doi.org", "partial", "partial",
     "DOI válido; alegação de interpolação linear de quinquenais é decisão do manuscrito, não da fonte."),
    ("BREIMAN2001", "BREIMAN", "Random forests", 2001,
     "10.1023/A:1010933404324", "doi.org", "partial", "partial",
     "DOI válido; fundamento metodológico do RF confirmado em nível genérico."),
    ("CEPAL2024", "CEPAL", "Development traps in Latin America and the Caribbean", 2024,
     "sem_doi", "https://www.cepal.org", "not_verified", "not_verified",
     "Relatório oficial; alegação específica das quatro armadilhas e 'US$ 100 bi' não verificada página a página."),
    ("COHEN1988", "COHEN", "Statistical power analysis for the behavioral sciences", 1988,
     "sem_doi", "livro Lawrence Erlbaum", "partial", "partial",
     "Obra canônica; convenções η²/d são padrão na literatura (p. 20-283 citadas)."),
    ("EASTERLY2001", "EASTERLY", "The middle class consensus and economic development", 2001,
     "10.1023/A:1012786330095", "doi.org", "partial", "partial",
     "DOI válido; nota: obra trata de consenso de classe média, não diretamente da crítica causal educação-crescimento atribuída — pertinência parcial."),
    ("EICHENGREEN2012", "EICHENGREEN; PARK; SHIN", "When fast growing economies slow down", 2012,
     "10.1162/ASEP_a_00118", "doi.org", "partial", "partial",
     "DOI válido; limiares US$10-16k citados são consistentes com o artigo."),
    ("EICHENGREEN2013", "EICHENGREEN; PARK; SHIN", "Growth slowdowns redux (NBER WP 18673)", 2013,
     "10.3386/w18673", "doi.org", "partial", "partial",
     "DOI válido para NBER WP."),
    ("FAUL2007", "FAUL et al.", "G*Power 3", 2007,
     "10.3758/BF03193146", "doi.org", "partial", "partial",
     "DOI válido; software de poder estatístico — alegação 'n mínimo = 38 para AUC = 0,97' requer cálculo reproduzido, não verificado."),
    ("FELIPE2012", "FELIPE; ABDON; KUMAR", "Tracking the middle-income trap", 2012,
     "10.2139/ssrn.2049330", "doi.org", "partial", "partial",
     "DOI válido (SSRN); critério 28/14 anos citado é consistente com o WP."),
    ("FIELD2018", "FIELD", "Discovering statistics using IBM SPSS Statistics", 2018,
     "sem_doi", "livro SAGE 5. ed.", "partial", "partial",
     "Texto-padrão; recomendações de Shapiro-Wilk/Levene/Welch são consistentes com o conteúdo do livro."),
    ("GILL_KHARAS2007", "GILL; KHARAS", "An East Asian renaissance", 2007,
     "sem_doi", "https://openknowledge.worldbank.org", "partial", "partial",
     "Obra seminal da ARM; número '101 países / 13 escaparam até 2008' citado como p. 17 NÃO verificado na página — requer confirmação na fonte."),
    ("GLEWWE2023", "GLEWWE et al.", "What explains Vietnam's exceptional performance in education?", 2023,
     "sem_doi", "working paper Univ. Minnesota", "not_verified", "not_verified",
     "Working paper sem DOI; página 34-45 citada não verificada."),
    ("GRINDLE2004", "GRINDLE", "Despite the odds: the contentious politics of education reform", 2004,
     "sem_doi", "livro Princeton UP", "not_verified", "not_verified",
     "Livro sem DOI; alegação sobre sindicatos/fragmentação não verificada página a página."),
    ("HANUSHEK_WOESSMANN2010", "HANUSHEK; WOESSMANN", "Education and economic growth (enciclopédia)", 2010,
     "10.1016/B978-0-08-044894-7.01227-6", "doi.org", "partial", "partial",
     "DOI corrigido (antes 01316-X, de outro capítulo) para o capítulo 'Education and economic growth', v. 2, p. 245-252; alegação '1 DP ≈ 1 p.p. crescimento' consistente com a linha de pesquisa, e a página 247-248 citada fica dentro do intervalo do capítulo — verificação página a página pendente."),
    ("IM_ROSENBLATT2015", "IM; ROSENBLATT", "Middle-income traps: a conceptual and empirical survey", 2015,
     "10.1142/S1793993315500131", "doi.org", "partial", "partial",
     "DOI válido; alegação '38 artigos revisados' consistente com o survey."),
    ("LEE2013", "LEE", "Schumpeterian analysis of economic catch-up", 2013,
     "sem_doi", "livro Cambridge UP", "not_verified", "not_verified",
     "Livro sem DOI; framework path-creating/path-following citado sem verificação de página."),
    ("LUCAS1988", "LUCAS", "On the mechanics of economic development", 1988,
     "10.1016/0304-3932(88)90168-7", "doi.org", "partial", "partial",
     "DOI válido; fundamento teórico do capital humano como motor endógeno."),
    ("MANKIW1992", "MANKIW; ROMER; WEIL", "A contribution to the empirics of economic growth", 1992,
     "10.2307/2118477", "doi.org", "partial", "partial",
     "DOI válido; alegação 'R²=0,78' citada como p. 416-422 NÃO verificada na página."),
    ("OECD2023", "OECD", "PISA 2022 Results — Volume I", 2023,
     "10.1787/53f23881-en", "doi.org", "partial", "partial",
     "DOI válido; scores PISA 2022 citados (BRA 379, KOR 505, SGP 527) são valores oficiais conhecidos; páginas não verificadas."),
    ("PRITCHETT2001", "PRITCHETT", "Where has all the education gone?", 2001,
     "10.1093/wber/15.3.367", "doi.org", "partial", "partial",
     "DOI válido; tese 'schooling ain't learning' consistente com a obra."),
    ("PSACHAROPOULOS2018", "PSACHAROPOULOS; PATRINOS", "Returns to investment in education", 2018,
     "10.1080/09645292.2018.1484426", "doi.org", "partial", "partial",
     "DOI válido; alegação 'retorno médio 9,0% a.a.' consistente com a revisão, não verificada página a página."),
    ("RODRIK2016", "RODRIK", "Premature deindustrialization", 2016,
     "10.1007/s10887-015-9122-3", "doi.org", "partial", "partial",
     "DOI válido; tese de desindustrialização prematura consistente com o artigo."),
    ("ROMER1990", "ROMER", "Endogenous technological change", 1990,
     "10.1086/261725", "doi.org", "partial", "partial",
     "DOI válido; fundamento do capital humano em P&D como motor de crescimento."),
    ("STROBL2007", "STROBL et al.", "Bias in random forest variable importance measures", 2007,
     "10.1186/1471-2105-8-25", "doi.org", "partial", "partial",
     "DOI válido; viés da importância de Gini documentado na obra."),
    ("TAN2018", "TAN; STEINBACH; KUMAR", "Introduction to data mining", 2018,
     "sem_doi", "livro Pearson 2. ed.", "partial", "partial",
     "Texto-padrão; fórmula de similaridade de cosseno é conteúdo conhecido do livro."),
    ("VANDENBUSSCHE2006", "VANDENBUSSCHE; AGHION; MEGHIR", "Growth, distance to frontier and composition of human capital", 2006,
     "10.1007/s10887-006-9002-y", "doi.org", "partial", "partial",
     "DOI válido; tese de educação ótima conforme distância à fronteira consistente."),
    ("VIRTANEN2020", "VIRTANEN et al.", "SciPy 1.0", 2020,
     "10.1038/s41592-019-0686-2", "doi.org", "partial", "partial",
     "DOI válido; citação de software científico."),
    ("WORLDBANK_WDR2024", "WORLD BANK", "World Development Report 2024: The Middle-Income Trap", 2024,
     "10.1596/978-1-4648-2078-6", "doi.org", "partial", "partial",
     "DOI corrigido (antes 2017-4, inexistente) para 10.1596/978-1-4648-2078-6 (hdl 10986/41919), confirmado no Open Knowledge Repository e no PDF oficial; modelo das três transições citado é tema central do WDR 2024."),
    ("WORLDBANK_WDI2024", "WORLD BANK", "World Development Indicators 2024", 2024,
     "sem_doi", "https://databank.worldbank.org", "not_verified", "not_verified",
     "Base de dados oficial; repositório da coleta original (17 mar. 2026) não fornecido — dados recalculados no snapshot R408."),
]


def main() -> None:
    df = pd.DataFrame(
        REFERENCES,
        columns=[
            "chave", "autor", "obra", "ano", "doi_verificado", "url",
            "status", "pertinencia_alegacao", "observacao",
        ],
    )
    df["referencia_unica"] = df["chave"]
    df.to_csv(OUT_DIR / "citation_audit.csv", index=False)
    print(f"citation_audit.csv gerado: {len(df)} referências únicas")
    print(df.groupby("status").size().to_string())


if __name__ == "__main__":
    main()
