# SPEC-986 (local) — Auditoria e preparação editorial do artigo sobre inclusão escolar de estudantes com TEA

**Status:** em execução
**Origem:** `C:\Users\marce\Downloads\ARTIGO - Maria do Socorro Araujo Martins Leite.md`
**Cópia imutável:** `00_ORIGINAL.md` (SHA-256 em `00_ORIGINAL.sha256`)
**Autora:** Maria do Socorro Araujo Martins Leite
**Execução:** 2026-11-05

## 1. Objetivo

Produzir um pacote editorial auditável do artigo, com (a) diagnóstico técnico, (b) versão corrigida que preserva a autoria e a argumentação, (c) versão reestruturada em padrão metodológico de artigo de revisão, (d) verificação das referências em base indexada, (e) relatório dos cinco scanners e (f) DOCX/PDF em formatação ABNT.

## 2. Não objetivos e anti-overclaim

- Não declarar o artigo como "Qualis A1", "aprovado", "aceito" ou "verificado" por pares. "Qualis A1" designa, aqui, apenas **alvo de estrutura e rigor**, não classificação alcançada.
- Não inventar dados bibliográficos, DOI, volume, página, editora ou local.
- Não inventar protocolo de busca sistemática que a autora não executou. A versão reestruturada declara-se **revisão narrativa** e descreve o corpus efetivamente disponível.
- Não alterar o sentido das citações para fazer o texto parecer mais sustentado do que é.
- Referências não localizadas em base indexada permanecem com os dados da autora e são sinalizadas no relatório de auditoria, não silenciadas.

## 3. Escopo

1. Preservar o original e registrar hash.
2. Auditar estrutura, coesão, citações e referências (ABNT NBR 6023/10520).
3. Corrigir a versão ABNT com intervenção mínima.
4. Reestruturar uma versão de revisão narrativa com metodologia, síntese temática, discussão integrativa e limitações.
5. Verificar referências via Crossref e páginas editoriais; registrar DOI e divergências.
6. Executar os cinco scanners do `/diagnose` sobre a versão final.
7. Gerar DOCX e PDF ABNT e verificar os artefatos.

## 4. Entregáveis

| Arquivo | Conteúdo |
|---|---|
| `00_ORIGINAL.md` + `.sha256` | original imutável |
| `01_ARTIGO_CORRIGIDO_ABNT.md` | correção mínima, texto da autora preservado |
| `02_ARTIGO_QUALIS_A1.md` | versão reestruturada (revisão narrativa) |
| `01_...pdf` / `.docx` | versão corrigida compilada |
| `02_...pdf` / `.docx` | versão final compilada |
| `RELATORIO_AUDITORIA.md` | achados, decisões e pendências |
| `RELATORIO_REFERENCIAS.md` | verificação Crossref/páginas editoriais |
| `RELATORIO_SCANNERS.md` | cinco scanners |
| `SHA256SUMS.txt` | hashes de todos os artefatos |

## 5. Critérios de aceitação (verificáveis)

1. `00_ORIGINAL.md` confere com o hash registrado.
2. Zero citações órfãs: toda citação no corpo tem entrada na lista e toda entrada é citada.
3. Zero ocorrências de `Silva et al., 2015`, `De Paula Nunes`, `De Oliveira Fam`, `Mendonça e Oliveira (2017)`, `Do Nascimento e Da Cruz`, `p 0`.
4. `Nunes et al.` datado de **2013**; `Nascimento e Cruz` datado de **2015**; `Bezerra e Pantoni (2022)` substitui a referência misatribuída.
5. Versão reestruturada contém: resumo, abstract, introdução com pergunta e objetivo, metodologia declarada, três eixos de síntese, discussão integrativa, considerações finais com limitações e 14 referências.
6. Contagem de palavras da versão reestruturada entre 4.500 e 7.000.
7. PDF compila sem erro, A4 (595×842 pt), margens 3/2/3/2 cm, texto extraível e sem glifos ausentes.
8. DOCX abre, com Times New Roman 12, espaçamento 1,5 e margens ABNT.
9. Relatório dos scanners contém os cinco scanners e a ressalva `candidato_a_inspecao`/`exige_validacao_externa`.
10. `SHA256SUMS.txt` cobre todos os entregáveis.

## 6. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Referência não indexada ser tratada como inexistente | status "não localizada", não "falsa"; decisão humana |
| Correção de metadados alterar o argumento | registrar cada substituição e justificar |
| PDF com fonte substituída | usar TeX Gyre Termes (clone Times) e conferir `pdffonts` |
| Scanners tratarem artigo como ecossistema | interpretar saída como heurística, não como avaliação editorial |
| Overclaim de qualidade | linguagem de alvo estrutural; nenhuma nota atribuída |

## 7. Registro de decisões

- A referência "Mendonça e Oliveira (2017), Revista Ensaio, v. 25, n. 96" não corresponde a obra localizável; o título exato pertence a Bezerra e Pantoni (2022), *Educitec*, v. 8, e182622. A versão corrigida adota a obra verificada e sinaliza a substituição.
- "De Paula Nunes et al. (2021)" é, na verdade, Nunes, Azevedo e Schmidt (2013), *Revista Educação Especial*, v. 26, n. 47.
- "Do Nascimento e Da Cruz (2017)" é Nascimento e Cruz (2015), *Revista Polyphonía*, v. 25, n. 2.
- "Silva et al. (2015)" é órfã; substituída por Silva e Oliveira (2016), já presente no corpus.
- "Mendonça (2022)" não é citada; retirada da lista.
