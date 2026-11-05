# Relatório de auditoria de DOI — TCC Marcelo Claro Laranjeira

**TCC:** Dupla excepcionalidade no Brasil: autismo, altas habilidades/superdotação e desafios de identificação
**Regra:** a literatura científica citada deve ter **DOI ativo e auditável**.
**Data:** 5 de novembro de 2026.
**Registro bruto:** `dados/doi_audit_final_20.json` (20 referências finais) e `dados/doi_audit.json` (triagem inicial).

---

## 1. Método

Para cada referência científica:

1. o DOI foi resolvido em `https://doi.org/<doi>`;
2. o registro foi conferido na API Crossref;
3. a página do editor foi consultada quando necessário.

Foram considerados **auditáveis** os DOIs registrados no Crossref e com resolução válida. Quando o editor bloqueou o acesso automatizado (HTTP 403), o DOI foi mantido apenas se o registro Crossref estivesse confirmado; a ocorrência foi anotada.

---

## 2. Referências aceitas (20)

| # | Referência | DOI | HTTP | Crossref | Observação |
|---|---|---|---|---|---|
| 1 | Assouline, Foley Nicpon e Dockery (2012) | 10.1007/s10803-011-1403-x | 200 | Confirmado | — |
| 2 | Baum e Schader (2021) | 10.4324/9781003239345-2 | 200 | Confirmado | Capítulo de livro |
| 3 | Barcelos da Costa, Picharillo e Chamel Elias (2025) | 10.46943/x.conedu.2024.gt10.011 | 200 | Confirmado | Trabalho em anais |
| 4 | Cabral e Marin (2017) | 10.1590/0102-4698142079 | 200 | Confirmado | — |
| 5 | Cipriano, Zaqueu e Silva (2024) | 10.48209/978-65-5417-208-7 | 200 | Confirmado | Capítulo de livro |
| 6 | Hughes (2021) | 10.4324/9781003239345-8 | 200 | Confirmado | Capítulo de livro |
| 7 | Madaus et al. (2022) | 10.3389/fpsyg.2022.995356 | 200 | Confirmado | — |
| 8 | McFadden (2017) | 10.62608/2164-1102.1055 | 200 | Confirmado | — |
| 9 | Nunes, Azevedo e Schmidt (2013) | 10.5902/1984686X10178 | 200 | Confirmado | Crossref indica v. 29, n. 56; a página editorial indica v. 26, n. 47. O TCC adota a página editorial. |
| 10 | Paulino Braz e Rangni (2024) | 10.46943/ix.conedu.2023.gt10.009 | 200 | Confirmado | Trabalho em anais |
| 11 | Reis et al. (2022) | 10.1177/00400599221108899 | 403 | Confirmado | SAGE bloqueia acesso automatizado; DOI registrado |
| 12 | Reis e Renzulli (2025) | 10.3390/bs15060834 | 403 | Confirmado | MDPI bloqueia acesso automatizado; DOI registrado |
| 13 | Ribeiro (2025) | 10.29327/1662710.1-2 | 200 | Confirmado | Trabalho em anais |
| 14 | Schmidt et al. (2016) | 10.15348/1980-6906/psicologia.v18n1p222-235 | 403 | Confirmado | Editor bloqueia acesso automatizado; DOI registrado |
| 15 | Bezerra e Pantoni (2022) | 10.31417/educitec.v8.1826 | 200 | Confirmado | — |
| 16 | Couto et al. (2019) | 10.5216/ree.v21.55954 | 200 | Confirmado | — |
| 17 | Fam et al. (2021) | 10.33448/rsd-v10i6.15912 | 200 | Confirmado | — |
| 18 | Ferreira e Howell (2023) | 10.4324/9781003334033-3 | 200 | Confirmado | Capítulo de livro |
| 19 | Maia, Bataglion e Mazo (2020) | 10.36311/2674-8681.2020.v21n1.02.p15 | 200 | Confirmado | — |
| 20 | Togashi e Walter (2016) | 10.1590/S1413-65382216000300004 | 200 | Confirmado | — |

**Resumo:** 17 DOIs resolvem diretamente (HTTP 200); 3 estão registrados no Crossref e redirecionam para editores que bloqueiam acesso automatizado (HTTP 403), mas permanecem auditáveis.

---

## 3. Referência excluída na triagem

| Referência | DOI | Motivo |
|---|---|---|
| Souza e Tavares (2023). Diagnóstico tardio da dupla excepcionalidade em autismo e altas habilidades | 10.29327/5256902.1-10 | DOI não registrado: HTTP 404 no resolvedor e no Crossref. Não foi citada no TCC. |

---

## 4. Fontes primárias sem DOI — exceção declarada

A regra de DOI foi aplicada à **literatura científica**. As fontes oficiais e a legislação não possuem DOI e foram mantidas como fontes primárias, com URL de acesso:

### 4.1 Sinopses do INEP

- Sinopse Estatística da Educação Básica 2021 — `https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2021.zip`
- Sinopse Estatística da Educação Básica 2022 — `https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_2022.zip`
- Sinopse Estatística da Educação Básica 2023 — `https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2023.zip`
- Sinopse Estatística da Educação Básica 2024 — `https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2024.zip`

### 4.2 Legislação

- Constituição Federal de 1988 — `http://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm`
- LDB 9.394/1996 — `http://www.planalto.gov.br/ccivil_03/leis/l9394.htm`
- Lei 12.764/2012 — `http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12764.htm`
- Lei 13.146/2015 — `http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm`
- PNEEPEI 2008 — `http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf`

**Ressalva:** se a regra "só DOI" for interpretada como aplicável também a fontes primárias, o TCC precisará substituir as Sinopses e a legislação por artigos com DOI que as discutam — com perda da ancoragem estatística e normativa direta.

---

## 5. Conclusão

O TCC cumpre a regra de DOI ativo e auditável para as 20 referências científicas citadas. Três DOIs são registrados no Crossref e resolvem para editores que bloqueiam acesso automatizado; a auditoria optou por mantê-los por serem rastreáveis. A única referência candidata com DOI inválido (Souza e Tavares, 2023) foi excluída e não aparece no texto. As Sinopses do INEP e a legislação são fontes primárias oficiais, com URL, e estão declaradas como exceção.
