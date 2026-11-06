#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera 01_ARTIGO_CORRIGIDO_ABNT.md a partir do original, com correções rastreadas.

Cada substituição é verificada; se o texto de origem mudar, o script falha em vez
de produzir uma correção silenciosa.
"""
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent
ORIG = BASE / "00_ORIGINAL.md"
DEST = BASE / "01_ARTIGO_CORRIGIDO_ABNT.md"

texto = ORIG.read_text(encoding="utf-8-sig")
linhas = [l.rstrip() for l in texto.splitlines()]
texto = "\n".join(linhas)


def rep(old: str, new: str, esperado: int | None = None) -> None:
    global texto
    n = texto.count(old)
    if n == 0:
        raise SystemExit(f"NÃO ENCONTRADO: {old!r}")
    if esperado is not None and n != esperado:
        raise SystemExit(f"OCORRÊNCIAS {n} != {esperado}: {old!r}")
    texto = texto.replace(old, new)


# 1. Frase quebrada na abertura: dois textos fundidos.
rep(
    "independentemente de suas A inclusão escolar é um dos pilares centrais",
    "independentemente de suas condições. A inclusão escolar é um dos pilares centrais",
    1,
)

# 2. Citação órfã (Silva et al., 2015 não existe nas referências).
rep("(Silva *et al*., 2015)", "(Silva e Oliveira, 2016)", 1)

# 3. Citação com sobrenome e ano incorretos: a obra é de 2013.
rep("De Paula Nunes *et al*. (2021)", "Nunes, Azevedo e Schmidt (2013)", 2)

# 4. Referência misatribuída: o título corresponde a Bezerra e Pantoni (2022).
rep("Mendonça e Oliveira (2017)", "Bezerra e Pantoni (2022)", 1)
rep(
    "(MENDONÇA e OLIVEIRA, 2017 p 01\\)",
    "(Bezerra e Pantoni, 2022)",
    1,
)
rep(
    "(MENDONÇA e OLIVEIRA, 2017 p 03\\)",
    "(Bezerra e Pantoni, 2022)",
    1,
)

# 5. Dois autores não admitem "et al."; sobrenome é Silva.
rep("Silva *et al*. (2016)", "Silva e Oliveira (2016)", 1)

# 6. Formatação de citação no sistema autor-data.
rep("(SANTOS e LOPES, 2021 p 03\\)", "(Santos e Lopes, 2021, p. 3)", 1)

# 7. Sobrenome é Fam, não "De Oliveira Fam".
rep("De Oliveira Fam *et al*. (2021)", "Fam et al. (2021)", 4)

# 8. Sobrenome é Silva, não "Da Silva".
rep("Da Silva e Arantes (2020)", "Silva e Arantes (2020)", 1)

# 9. Schmidt é autor de obra com seis autores; o verbo fica no plural.
rep("Schmidt (2016) sugerem", "Schmidt et al. (2016) sugerem", 1)

# 10. Pontuação e sobrenome.
rep(
    "Maia; Bataglion e Mazo (2020), ressaltam",
    "Maia, Bataglion e Mazo (2020) ressaltam",
    1,
)
rep("Do Nascimento e Da Cruz (2015)", "Nascimento e Cruz (2015)", 1)

# 11. Títulos e numeração.
rep("1. # **INTRODUÇÃO**", "# 1 INTRODUÇÃO", 1)
rep("2. # **DESENVOLVIMENTO**", "# 2 DESENVOLVIMENTO", 1)
rep(
    "   1. ## INCLUSÃO ESCOLAR E POLÍTICAS EDUCACIONAIS",
    "## 2.1 INCLUSÃO ESCOLAR E POLÍTICAS EDUCACIONAIS",
    1,
)
rep("2. ## TRANSTORNO DO ESPECTRO AUTISTA (TEA)", "## 2.2 TRANSTORNO DO ESPECTRO AUTISTA (TEA)", 1)
rep(
    "3. ## PRÁTICAS PEDAGÓGICAS INCLUSIVAS NOS ANOS INICIAIS",
    "## 2.3 PRÁTICAS PEDAGÓGICAS INCLUSIVAS NOS ANOS INICIAIS",
    1,
)
rep("3. # **CONCLUSÃO**", "# 3 CONCLUSÃO", 1)
rep("4. # **REFERÊNCIAS**", "# REFERÊNCIAS", 1)

# 12. Palavras-chave: capitalização de preposições e do inglês.
rep("Transtorno Do Espectro Autista", "Transtorno do Espectro Autista", 1)
rep("Early Years Of Education", "Early Years of Education", 1)

# 13. Lista de referências reconstruída com os metadados verificados.
NOVAS_REFS = """# REFERÊNCIAS

BEZERRA, Marli de Figueiredo; PANTONI, Rodrigo Palucci. Formação docente para inclusão de alunos com Transtorno do Espectro Autista no Ensino Médio Integrado. **Educitec – Revista de Estudos e Pesquisas sobre Ensino Tecnológico**, Manaus, v. 8, p. e182622, 2022. DOI: 10.31417/educitec.v8.1826.

CABRAL, Cristiane Soares; MARIN, Angela Helena. Inclusão escolar de crianças com transtorno do espectro autista: uma revisão sistemática da literatura. **Educação em Revista**, Belo Horizonte, v. 33, p. e142079, 2017. DOI: 10.1590/0102-4698142079.

COSTA, Luciane Silva da. **Escolarização de crianças com transtorno do espectro autista: a concepção do educador numa perspectiva inclusiva**. 2016. 53 f. Dissertação (Mestrado em Educação) – Universidade Federal de Santa Maria, Santa Maria, 2016.

COUTO, Cirleine Costa; FURTADO, Maria Cândida de Carvalho; ZILLY, Adriana; SILVA, Marta Angélica Iossi. Experiências de professores com o autismo: impacto no diagnóstico precoce e na inclusão escolar. **Revista Eletrônica de Enfermagem**, Goiânia, v. 21, p. e55954, 2019. DOI: 10.5216/ree.v21.55954.

FAM, Antônio Eustáquio de Oliveira; REIS, Sérgio Pereira dos; BARBOSA, Rosemary Pereira Costa e. O brincar no espaço escolar como estratégia de inclusão de alunos com Transtorno do Espectro Autista (TEA). **Research, Society and Development**, [s. l.], v. 10, n. 6, p. e49010615912, 2021. DOI: 10.33448/rsd-v10i6.15912.

MAIA, Juliana; BATAGLION, Giandra Anceski; MAZO, Janice Zarpellon. Alunos com transtorno do espectro autista na escola regular: relatos de professores de educação física. **Revista da Associação Brasileira de Atividade Motora Adaptada**, Marília, v. 21, n. 1, 2020. DOI: 10.36311/2674-8681.2020.v21n1.02.p15.

NASCIMENTO, Fabiana Ferreira do; CRUZ, Mara Lucia Reis Monteiro da. Da realidade à inclusão: uma investigação acerca da aprendizagem e do desenvolvimento do/a aluno/a com transtornos do espectro autista – TEA nas séries iniciais do I segmento do ensino fundamental. **Revista Polyphonía**, Goiânia, v. 25, n. 2, p. 51-66, 2015. DOI: 10.5216/rp.v25i2.38149.

NUNES, Débora Regina de Paula; AZEVEDO, Mariana Queiroz Orrico de; SCHMIDT, Carlo. Inclusão educacional de pessoas com autismo no Brasil: uma revisão da literatura. **Revista Educação Especial**, Santa Maria, v. 26, n. 47, p. 557-572, set./dez. 2013. DOI: 10.5902/1984686X10178.

NUNES, Vera Lucia Mendonça. Práticas pedagógicas na inclusão do aluno com TEA: uma revisão sistemática. In: CONGRESSO BRASILEIRO DE EDUCAÇÃO ESPECIAL, 8., 2018, São Carlos. **Anais [...].** Campinas: Galoá, 2018.

RIBEIRO, Mariana Laura Queiroz. Intervenções neuropsicopedagógicas em casos de autismo. In: **Anais do VI Congresso Nacional de Educação**. [S. l.]: CONEDU, 2019.

SANTOS, Renata Cristina; LOPES, Fábio Augusto. Abordagens neuropsicopedagógicas no processo ensino: uma revisão bibliográfica entre os anos de 2010 e 2021. **Revista Educação Pública**, [s. l.], v. 17, n. 3, p. 123-138, 2021.

SCHMIDT, Carlo *et al*. Inclusão escolar e autismo: uma análise da percepção docente e práticas pedagógicas. **Psicologia: Teoria e Prática**, São Paulo, v. 18, n. 1, p. 222-235, 2016. DOI: 10.15348/1980-6906/psicologia.v18n1p222-235.

SILVA, Hanna Christina da; ARANTES, Adlene Silva. Inclusão dos estudantes com transtorno do espectro autista (TEA): percepções docentes. **REIN – Revista Educação Inclusiva**, v. 4, n. 1, p. 86-103, 2020. Disponível em: https://revista.uepb.edu.br/REIN/article/view/218. Acesso em: 5 nov. 2026.

TOGASHI, Cláudia Miharu; WALTER, Cátia Crivelenti de Figueiredo. As contribuições do uso da comunicação alternativa no processo de inclusão escolar de um aluno com transtorno do espectro do autismo. **Revista Brasileira de Educação Especial**, Marília, v. 22, n. 3, p. 351-366, 2016. DOI: 10.1590/S1413-65382216000300004.
"""

cabeca, _ = texto.split("# REFERÊNCIAS", 1)
texto = cabeca.rstrip() + "\n\n" + NOVAS_REFS

# 14. Normalização de parágrafos: o export do Google Docs deixou parágrafos
#     em linhas consecutivas, que o Markdown fundiria em um único bloco.
linhas = [l.strip() for l in texto.splitlines()]
saida: list[str] = []
for linha in linhas:
    if linha == "":
        saida.append("")
    else:
        if saida and saida[-1] != "":
            saida.append("")
        saida.append(linha)
texto = "\n".join(saida)
texto = re.sub(r"\n{3,}", "\n\n", texto)

# 15. Limpeza final de espaços e barras remanescentes em fim de linha.
texto = "\n".join(l.rstrip() for l in texto.splitlines())
if "\\. " in texto or texto.count("\\") > 0:
    sobras = [i + 1 for i, l in enumerate(texto.splitlines()) if "\\" in l]
    raise SystemExit(f"barras invertidas remanescentes nas linhas {sobras}")

DEST.write_text(texto.rstrip() + "\n", encoding="utf-8")
print(f"OK: {DEST} ({len(texto)} chars)")
