# Anexo B (M7) — Auditoria de citações e referências

**Projeto**: artigo IA e Direito → Educação Por Escrito
**Data da auditoria**: 17 set. 2026
**Auditor**: marceloclaro (orquestrador) com verificações automatizadas via Crossref e HTTP

## 1. Método de auditoria

- DOI: consulta à API pública do Crossref (`api.crossref.org/works/{DOI}`) — confere existência, título, autores, periódico, volume/páginas e ano.
- URL oficial: requisição HTTP (status 200/403/000 interpretados conforme bloqueio de bot).
- Tipos de fonte: artigo, revisão, norma, guia institucional, página de diretrizes editoriais.
- Status: `verificada` (metadados confirmados em fonte primária/repositório oficial), `verificada com ressalva` (http 000 por bloqueio de bot; conteúdo confirmado via indexação oficial), `excluída` (falha de verificação).

## 2. Tabela de auditoria das referências do manuscrito

| # | Referência | Identificador | Status | O que foi conferido |
|---|---|---|---|---|
| 1 | ALMADA; ZANATTA (2024), Revista USP | DOI 10.11606/issn.2316-9036.i141p51-64 | ✅ verificada | Crossref: título, autores, periódico, n. 141, p. 51-64, 2024; página do periódico (revistas.usp.br/revusp/article/view/247075) |
| 2 | BARROSO; PERRONE CAMPOS MELLO (2024), Rev. Direito e Práxis | DOI 10.1590/2179-8966/2024/84479 | ✅ verificada | Crossref: título, autores, v. 15, n. 4, 2024; página oficial do periódico (Qualis A1 Direito, confirmado no site); PDF integral baixado (45 p.) e citado com paginação |
| 3 | BORGESANO et al. (2025), EJIM | DOI 10.1108/ejim-01-2025-0117 | ✅ verificada | Crossref: título, autores (Borgesano, De Maio, Laghi, Musmanno), v. 28, p. 349-385, 2025 |
| 4 | BRASIL. PL 2.338/2023 | URL camara.leg.br (idProposicao=2403886) | ✅ verificada | HTTP 200 na ficha de tramitação da Câmara |
| 5 | BRASIL. Resolução CNE/CES 5/2018 (DCN Direito) | gov.br/mec/pt-br/cne/resolucoes/resolucoes-cne-ces-2018 | ✅ verificada | Conteúdo confirmado via indexação oficial gov.br (lista as resoluções de 2018, incl. nº 5 de 17/12/2018) e ABMES (PDF do texto integral) |
| 6 | BRASIL. Resolução CNE/CES 2/2021 (alteração art. 5º DCN) | abmes.org.br/legislacoes/detalhe/3502 | ✅ verificada | Conteúdo confirmado via indexação (título e objeto da resolução); inclui Parecer CNE/CES 757/2020 |
| 7 | BRASIL. MEC. Inteligência Artificial na Educação Básica (2025) | gov.br/mec/pt-br/escolas-conectadas/arquivos/ia-educacao-basica.pdf | ⚠️ verificada com ressalva | Conteúdo (título, seções, contexto normativo e curricular) confirmado via indexação oficial do Portal gov.br; HTTP 000 no ambiente por bloqueio de bot — conferir em navegador antes da submissão |
| 8 | CNJ. Resolução 332/2020 | atos.cnj.jus.br/atos/detalhar/3429 | ✅ verificada | HTTP 200 no portal de atos do CNJ |
| 9 | CNJ. Resolução 615/2025 | atos.cnj.jus.br/atos/detalhar/6001 | ✅ verificada | HTTP 200 no portal de atos do CNJ |
| 10 | EDUCAÇÃO POR ESCRITO. Diretrizes para Autores | revistaseletronicas.pucrs.br/porescrito/about/submissions | ✅ verificada | Página oficial acessada em 17 set. 2026: extensão 15–20 p., resumo PT/EN, folha de rosto, declaração de IA, Qualis A4 (Ensino, 2021–2024), dossiê "Avaliação em tempos de IA Generativa" |
| 11 | KIM; YI; PARK (2025), PLOS ONE | DOI 10.1371/journal.pone.0326028 | ✅ verificada | Crossref: título, autores, v. 20, n. 6, e0326028, 2025; PMC (artigo em acesso aberto) |
| 12 | LONG; MAGERKO (2020), CHI | DOI 10.1145/3313831.3376727 | ✅ verificada | Crossref: título, autores, conferência CHI 2020 |
| 13 | NG et al. (2021), CEAIA | DOI 10.1016/j.caeai.2021.100041 | ✅ verificada | Crossref: título, periódico Computers and Education: Artificial Intelligence, v. 2, 2021 |
| 14 | UNESCO. AI and education (2021) | DOI 10.54675/PCSP7350 | ✅ verificada | Crossref: título "AI and education: guidance for policy-makers", 2021 |
| 15 | UNESCO. Recommendation Ethics of AI (2021) | unesdoc.unesco.org/ark:/48223/pf0000379920 | ✅ verificada | HTTP 200 no repositório oficial UNESCO (UNESDOC) |
| 16 | UNIÃO EUROPEIA. AI Act (Reg. UE 2024/1689) | eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX:32024R1689 | ✅ verificada | HTTP 200 no portal oficial EUR-Lex |

## 3. Referências excluídas por falha de verificação

| Referência candidata | Motivo |
|---|---|
| OCDE. Artificial Intelligence and the Future of Skills, v. 1 (2021) — DOI 10.1787/ee75f4ae-en | Crossref e doi.org retornaram falha/404 → excluída (não consta no manuscrito) |

## 4. Verificação de citações (correspondência bidirecional)

- Cada referência listada é citada ao menos uma vez no corpo do manuscrito (verificado manualmente na versão 0.1; re-checagem obrigatória após edições).
- Citações diretas do artigo-âncora conferidas contra o PDF oficial baixado (paginação: p. 15, p. 16, p. 27 nota 42, p. 33).
- Não há referência não citada nem citação sem referência nesta versão.
- Não há frases distintivas copiadas de outras fontes além das citações diretas curtas, entre aspas e com paginação, do artigo-âncora (uso permitido pela licença CC BY 4.0 da Revista Direito e Práxis, com atribuição).

## 5. Pendências para a submissão

1. Autoria, afiliações, ORCID e folha de rosto (bloco desidentificado a remover).
2. Reconfirmar o acesso à URL do MEC (item 7) em navegador.
3. Preenchimento da declaração oficial de IA e tecnologias da revista (@editora.pucrs.br) com a ferramenta exata.
4. Conversão para .docx e checagem de extensão (15–20 páginas) e das normas de formatação da revista.
5. Verificação de similaridade (Turnitin) recomendada pela revista — executar antes da submissão.