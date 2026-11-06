# Relatório de auditoria de DOI — TCC (versão ampliada)

**Artefato:** `TCC_MARIA_SOCORRO.pdf` / `.docx`
**Regra adotada:** aceitar, na literatura científica, **apenas citações com DOI ativo e auditável**.
**Data da auditoria:** 6 de novembro de 2026.
**Registro bruto:** `dados/doi_audit_20.json`.

---

## 1. Método

Para cada referência científica, o DOI foi:

1. resolvido em `https://doi.org/<doi>`;
2. conferido na API Crossref (`https://api.crossref.org/works/<doi>`);
3. confrontado com a página do editor ou repositório.

Foram considerados **ativos** os DOIs registrados no Crossref e com resolução válida. O bloqueio de acesso automatizado por parte do editor (HTTP 403) não invalida o registro; foi anotado caso a caso.

A auditoria foi executada pelo script `scripts/auditar_dois_tcc.py`, que registra metadados, status HTTP e URL final. O resultado completo está em `dados/doi_audit_20.json`.

---

## 2. Corpus final (20 obras)

| # | Referência | DOI | HTTP | Crossref | Veículo |
|---|---|---|---|---|---|
| 1 | Harrower e Dunlap (2001) | 10.1177/0145445501255006 | 403 | Confirmado | Behavior Modification |
| 2 | Rotheram-Fuller et al. (2010) | 10.1111/j.1469-7610.2010.02289.x | 403 | Confirmado | Journal of Child Psychology and Psychiatry |
| 3 | Crosland e Dunlap (2012) | 10.1177/0145445512442682 | 403 | Confirmado | Behavior Modification |
| 4 | Koegel et al. (2012) | 10.1016/j.cbpra.2010.11.003 | 200 | Confirmado | Cognitive and Behavioral Practice |
| 5 | Humphrey e Symes (2013) | 10.1080/13603116.2011.580462 | 403 | Confirmado | International Journal of Inclusive Education |
| 6 | Lindsay et al. (2013) | 10.1080/1034912x.2013.846470 | 403 | Confirmado | International Journal of Disability, Development and Education |
| 7 | Nunes, Azevedo e Schmidt (2013) | 10.5902/1984686X10178 | 200 | Confirmado | Revista Educação Especial |
| 8 | Wong et al. (2015) | 10.1007/s10803-014-2351-z | 200 | Confirmado | Journal of Autism and Developmental Disorders |
| 9 | Chang e Locke (2016) | 10.1016/j.rasd.2016.03.010 | 200 | Confirmado | Research in Autism Spectrum Disorders |
| 10 | Schmidt et al. (2016) | 10.15348/1980-6906/psicologia.v18n1p222-235 | 403 | Confirmado | Psicologia: Teoria e Prática |
| 11 | Togashi e Walter (2016) | 10.1590/S1413-65382216000300004 | 200 | Confirmado | Revista Brasileira de Educação Especial |
| 12 | Cabral e Marin (2017) | 10.1590/0102-4698142079 | 200 | Confirmado | Educação em Revista |
| 13 | Couto et al. (2019) | 10.5216/ree.v21.55954 | 200 | Confirmado | Revista Eletrônica de Enfermagem |
| 14 | Maia, Bataglion e Mazo (2020) | 10.36311/2674-8681.2020.v21n1.02.p15 | 200 | Confirmado | Revista da ABAM |
| 15 | Sousa e Menezes (2020) | 10.18554/ifd.v7i3.4979 | 200 | Confirmado | Iniciação & Formação Docente |
| 16 | Fam et al. (2021) | 10.33448/rsd-v10i6.15912 | 200 | Confirmado | Research, Society and Development |
| 17 | Suassuna (2021) | 10.51891/rease.v7i7.1831 | 200 | Confirmado | Revista Ibero-Americana de Humanidades, Ciências e Educação |
| 18 | Hume et al. (2021) | 10.1007/s10803-020-04844-2 | 200 | Confirmado | Journal of Autism and Developmental Disorders |
| 19 | Bezerra e Pantoni (2022) | 10.31417/educitec.v8.1826 | 200 | Confirmado | Educitec |
| 20 | Fang et al. (2023) | 10.1016/j.rasd.2023.102257 | 200 | Confirmado | Research in Autism Spectrum Disorders |

**Resumo:** 20 DOIs registrados no Crossref; 14 resolvem diretamente (HTTP 200) e 6 são bloqueados por editores que restringem acesso automatizado (HTTP 403), mas permanecem auditáveis. Nenhum DOI foi aceito sem confirmação no Crossref.

---

## 3. Composição do corpus

- **10 obras brasileiras:** Nunes, Azevedo e Schmidt (2013); Schmidt et al. (2016); Togashi e Walter (2016); Cabral e Marin (2017); Couto et al. (2019); Maia, Bataglion e Mazo (2020); Sousa e Menezes (2020); Fam et al. (2021); Suassuna (2021); Bezerra e Pantoni (2022).
- **10 obras internacionais:** Harrower e Dunlap (2001); Rotheram-Fuller et al. (2010); Crosland e Dunlap (2012); Koegel et al. (2012); Humphrey e Symes (2013); Lindsay et al. (2013); Wong et al. (2015); Chang e Locke (2016); Hume et al. (2021); Fang et al. (2023).
- **Período:** 2001–2023.
- **Tipos:** todos os 20 são artigos em periódicos.

A ampliação de 8 para 20 obras respondeu à necessidade de cobrir três dimensões que a versão anterior tratava de forma incompleta: (a) práticas baseadas em evidências e mediação por pares; (b) atitudes, conhecimento e desafios de educadores; (c) inclusão social e prontidão escolar na primeira infância.

---

## 4. Fontes primárias (9) — exceção declarada

A legislação brasileira e as Sinopses do INEP não possuem DOI. Elas foram mantidas como **fontes primárias oficiais**, com URL, por serem o fundamento normativo e estatístico do estudo.

| Fonte | URL oficial |
|---|---|
| Constituição Federal de 1988 | http://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm |
| Lei 9.394/1996 (LDB) | http://www.planalto.gov.br/ccivil_03/leis/l9394.htm |
| Lei 12.764/2012 | http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12764.htm |
| Lei 13.146/2015 (LBI) | http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm |
| PNEEPEI (2008) | http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf |
| Sinopse 2021 | https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2021.zip |
| Sinopse 2022 | https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2022.zip |
| Sinopse 2023 | https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2023.zip |
| Sinopse 2024 | https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2024.zip |

**Ressalva:** a regra de DOI foi aplicada à literatura científica. As fontes primárias são identificadas como exceção no corpo do TCC (seção 3.6).

---

## 5. Impacto no texto

- O corpus científico passou de **8 para 20 obras**.
- O TCC incorporou análise de dados secundários do Censo Escolar (2021–2024), com série nacional, decomposição por tipo de classe, distribuição regional, extremos estaduais e cenários exploratórios.
- O resumo e o abstract informam **20 obras** e os principais indicadores.
- A metodologia declara o protocolo de busca, a regra de DOI e a exceção das fontes primárias.
- O TCC passou de 27 para **43 páginas**, com **8 quadros** e **40 entradas** no sumário.

---

## 6. Renderização

| Item | Situação |
|---|---|
| PDF | 43 páginas, A4 (595,28 × 841,89 pt) |
| Margens | 2,5 cm em todos os lados |
| Fonte | TeX Gyre Termes 12 pt (clone métrico de Times New Roman) |
| Espaçamento | 1,5 |
| Pré-textuais | Capa, folha de rosto, resumo, abstract e lista de abreviaturas sem numeração |
| Paginação | Arábica a partir da introdução (página 1) |
| Sumário | 40 entradas, com títulos e páginas |
| Quadros | 8, com título acima e fonte abaixo |
| Overfull boxes | Nenhuma acima de 10 pt |
| DOCX | 2,5 cm, Times New Roman 12, 1,5; 314 parágrafos, 10 tabelas |

---

## 7. Pendências

1. Revisar o texto com a orientação antes da submissão.
2. Confirmar se a legislação e as Sinopses podem permanecer como fontes primárias sem DOI (decisão já adotada e declarada no TCC).
3. Conferir a paginação no Word, se o DOCX for o arquivo de entrega.
4. Atualizar o sumário do DOCX se a paginação mudar.

---

## 8. Conclusão

O TCC cumpre a regra de **DOI ativo e auditável** para as 20 obras científicas citadas. A única exceção são as cinco fontes legais e as quatro Sinopses do INEP, tratadas como fontes primárias com URL oficial. Nenhuma obra sem DOI é citada como literatura científica. O registro da auditoria permite reconstruir cada decisão.
