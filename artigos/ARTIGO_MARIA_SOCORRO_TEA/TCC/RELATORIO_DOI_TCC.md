# Relatório de auditoria de DOI — TCC

**Artefato:** `TCC_MARIA_SOCORRO.pdf` / `.docx`
**Regra adotada:** aceitar, na literatura científica, **apenas citações com DOI ativo e auditável**.
**Data da auditoria:** 5 de novembro de 2026.
**Registro bruto:** `doi_audit.json`.

---

## 1. Método

Para cada referência científica, o DOI foi:

1. resolvido em `https://doi.org/<doi>` (HTTP 301/302/200);
2. conferido na API Crossref (`https://api.crossref.org/works/<doi>`);
3. confrontado com a página do editor ou repositório.

Foram considerados **ativos** os DOIs registrados no Crossref e com resolução válida. O bloqueio de acesso automatizado por parte do editor (HTTP 403) não invalida o registro; foi anotado caso a caso.

---

## 2. Referências aceitas (8)

| Referência | DOI | Resolução | Crossref |
|---|---|---|---|
| Bezerra e Pantoni (2022) | 10.31417/educitec.v8.1826 | HTTP 200 | Confirmado |
| Cabral e Marin (2017) | 10.1590/0102-4698142079 | HTTP 200 | Confirmado |
| Couto et al. (2019) | 10.5216/ree.v21.55954 | HTTP 200 | Confirmado |
| Fam et al. (2021) | 10.33448/rsd-v10i6.15912 | HTTP 200 | Confirmado |
| Maia, Bataglion e Mazo (2020) | 10.36311/2674-8681.2020.v21n1.02.p15 | HTTP 200 | Confirmado |
| Nunes, Azevedo e Schmidt (2013) | 10.5902/1984686X10178 | HTTP 200 | Confirmado |
| Schmidt et al. (2016) | 10.15348/1980-6906/psicologia.v18n1p222-235 | HTTP 302 → editor; 403 a bots | Confirmado |
| Togashi e Walter (2016) | 10.1590/S1413-65382216000300004 | HTTP 200 | Confirmado |

**Observação sobre Schmidt et al. (2016):** o DOI está registrado no Crossref e resolve para a página do editor. A página retorna HTTP 403 a requisições automatizadas, mas o registro é auditável e o artigo é acessível a humanos. Por isso, foi mantido.

---

## 3. Referências excluídas (6)

| Referência | Motivo da exclusão |
|---|---|
| Costa (2016) | Dissertação no repositório da UFSM sem DOI. A página institucional não registra DOI. |
| Nascimento e Cruz (2015) | O DOI impresso (10.5216/rp.v25i2.38149) **não está registrado**: retorna HTTP 404 no resolvedor e 404 no Crossref. |
| Nunes (2018) | Trabalho em anais do CBEE 2018 sem DOI localizado. |
| Ribeiro (2019) | Trabalho em anais do CONEDU 2019 sem DOI; além disso, o Google Acadêmico atribui o título a MCCA Menezes, e a autoria não foi confirmada. |
| Santos e Lopes (2021) | Artigo na Revista Educação Pública sem DOI localizado. |
| Silva e Arantes (2020) | Artigo na REIN sem DOI localizado. A página do artigo não exibe DOI. |

Essas obras **não são citadas no texto do TCC**. As passagens que dependiam delas foram reescritas com as obras aceitas ou convertidas em afirmações analíticas sem atribuição.

---

## 4. Fontes primárias (5) — exceção declarada

A legislação brasileira não possui DOI. Ela foi mantida como **fonte primária**, com URL oficial, por ser o fundamento normativo do objeto de estudo:

| Fonte | URL oficial |
|---|---|
| Constituição Federal de 1988 | http://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm |
| Lei 9.394/1996 (LDB) | http://www.planalto.gov.br/ccivil_03/leis/l9394.htm |
| Lei 12.764/2012 | http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12764.htm |
| Lei 13.146/2015 (LBI) | http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm |
| PNEEPEI (2008) | http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf |

**Ressalva:** se a regra “só DOI ativo” for interpretada como aplicável também às fontes primárias, o TCC precisará remover as citações legais e substituí-las por artigos com DOI que discutam as normas. Isso reduziria a ancoragem jurídica do trabalho. A decisão é da autora/orientação.

---

## 5. Impacto no texto

- O corpus científico passou de **14 para 8 obras**.
- As seções 2.1, 2.2, 2.3, 4.2, 4.3, 4.4, 5.1 e 5.2 foram ajustadas para retirar as citações às obras excluídas.
- O Quadro 2 (caracterização do corpus) foi reduzido de 14 para 8 linhas.
- O registro da auditoria está neste relatório e em `doi_audit.json`; o TCC não inclui apêndice com esse quadro.
- O resumo e o abstract informam “oito obras com DOI ativo”.
- A metodologia declara a regra e a redução do corpus.

---

## 6. Renderização

| Item | Situação |
|---|---|
| PDF | 27 páginas, A4 (595,28 × 841,89 pt) |
| Margens | 2,5 cm em todos os lados (conforme o manual) |
| Fonte | TeX Gyre Termes 12 pt (clone métrico de Times New Roman) |
| Espaçamento | 1,5 |
| Pré-textuais | Capa, folha de rosto, resumo, abstract e lista de abreviaturas sem numeração |
| Paginação | Arábica a partir da introdução (página 1) |
| Sumário | 32 entradas, com títulos e páginas |
| Tabelas | 4 quadros, com título acima e fonte abaixo |
| Overfull boxes | Nenhuma acima de 10 pt |
| DOCX | 2,5 cm, Times New Roman 12, 1,5; 206 parágrafos, 6 tabelas |

---

## 7. Pendências

1. Capa e folha de rosto preenchidas com FACUMINAS, Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica, Brasília e título de especialista; linha do orientador removida a pedido.
2. Confirmar se a legislação pode permanecer como fonte primária sem DOI ou se deve ser substituída por artigos com DOI.
3. Revisar o TCC com o orientador(a) antes da submissão.

---

## 8. Conclusão

O TCC cumpre a regra de **DOI ativo e auditável** para toda a literatura científica citada. A única exceção são os cinco documentos legais, tratados como fontes primárias com URL oficial. As seis obras sem DOI ativo foram excluídas e não aparecem como citações no corpo do texto; este relatório registra a auditoria e os motivos.
