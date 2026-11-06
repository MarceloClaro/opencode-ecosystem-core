# Molambudos — fontes versionadas e artefatos locais

**Obra:** *Molambudos — O Diário do Paciente 1.260*  
**Autor:** Marcelo Dias de Carvalho Filho  
**Edição canônica:** `Molambudos_VictoriaRegia` — 435 pp, 160×230 mm, KDP PT-BR.

Este mapa cobre também artefatos presentes apenas na máquina de produção.
Um clone do Git contém fontes e documentação, as capas selecionadas 422/436 pp
e provas pequenas rastreadas; **não** contém os PDFs dos miolos, EPUBs, áudio,
vídeo, ZIPs nem o caderno PDF de provas. A regra de entrada é uma allowlist
em [`.gitignore`](../../.gitignore); ignorar não equivale a auditar segredos.
Ver [política e edição](../../README.md#o-que-entra-no-git-e-o-que-fica-local).

## Mapa

| Caminho | Conteúdo |
|---|---|
| `Molambudos_VictoriaRegia/` | fontes da edição canônica PT/EN/ZH/TRI e dossiê; PDF de 435 pp, capas anteriores e release completo são locais |
| `release/2026-11-05/` | pacote local: PDFs PT/EN/ZH/TRI, capas, metadados e checksums |
| `release/2026-11-05/epub/` | EPUB de leitura, fonte Markdown, CSS e manifesto |
| `release/2026-11-05/preflight/` | preflight KDP local com status FAIL documentado |
| `reports/r1073/` | parecer, manifesto e hash dos itens excluídos em 2026-11-05 |
| `reports/r1074/` | EPUB, preflight KDP e estado do PDF tagged |
| `Molambudos_Revisada_R1075/` | edição revista e redesenhada: 421 pp, DOC −18,3%, CONT 7, LUC 23, 6 pranchas |
| `reports/r1075/` | manifesto, EPUB e relatório da edição revista |
| `Molambudos_Print_R1077/` | fontes da variante print-safe: PDF local de 422 pp, sem fundo, imagens ≥300 DPI, TAC 11,7% |
| `reports/r1077/` | manifesto de tinta, CMYK e qualidade de impressão |
| `capas/molambudos_final/` | capa selecionada preta/ouro: PDFs 422/436 pp, 300 DPI, fontes embutidas e manifesto; nome `436p` não confirma compatibilidade com o miolo canônico de 435 pp |
| `capas/piranesi_pencz_2026-11-05/` | alternativa Piranesi/Pencz: capas, tríptico, masters 600 DPI e manifesto |
| `reports/r1081/` | direção de arte Piranesi/Pencz e provas determinísticas |
| `reports/r1082/` | 6 pranchas de prova, caderno de 8 pp, preflight, revisão e perfil local |
| `podcast/producao/` | 26 episódios + piloto R550, pacotes, slides, infográficos, feed, trailer e deploy |
| `auditorias/` | revisão antiga, banca, cultural-episteme, Book Studio e catálogo |
| `capas/` | capa frontal e contracapa corrigidas |
| `scripts/` | scripts de cânon, índice, rotas, selo e normalização |
| `specs/` | specs históricas do Molambudos |
| `meta/` | reflexão metacognitiva da obra |
| `REVISAO_FINAL.md` | parecer editorial e decisão de acervo |

## Comandos

Da raiz do repositório, consulte o diagnóstico **sem gerar nem alterar** miolos:

```bash
python3 -m marceloclaro.bookstudio status
python3 -m marceloclaro.cli doctor
git ls-files literatura/molambudos/capas/molambudos_final/
```

O build com `marceloclaro.book_studio` exige conferir dependências, fontes e
licenças antes da execução; as saídas não são artefatos presentes em clones.

## Estado

- PDF KDP canônico: 435 pp, 160×230 mm, 15 fontes embutidas, metadados completos.
- SHA-256 do PDF canônico: `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`.
- PDF antigo `77aabe2e` excluído definitivamente; hash preservado em `reports/r1073/`.
- 84 fragmentos + epílogo; 0 grupos de parágrafos duplicados.
- 12 aspas retas corrigidas; 0 restantes.
- Podcast: 26/26 episódios + piloto R550; produção NotebookLM; feed e pacote editorial.
- `Molambudos_v2`, `Molambudos_v2_Diario`, o arquivo histórico e o template antigo foram excluídos definitivamente em 2026-11-05, por decisão do autor; hashes em `reports/r1073/`.
- Release local em `release/2026-11-05/`; registro em `reports/r1073/DELETION.md`.
- EPUB de leitura canônico: 84 fragmentos, 5 partes, 105 links no TOC (0 quebrados), 7 imagens; validação estrutural local. O EPUB revisado R1075/R1076 passou EPUBCheck 5.4.0 (0 erros/0 avisos) e Ace 1.4.6 (26 pass/0 fail).
- Preflight KDP da capa canônica antiga: **FAIL** — capa a ~163 DPI, reserva de barras 2,15×0,95 in e posição inferior esquerda. A capa selecionada R1082 foi refeita em 300 DPI (422/436 pp), mas ainda não tem CMYK/PDF-X, prova física ou confirmação KDP.
- PDF tagged: bloqueado pelo toolchain (`luaotfload` ausente; `tagpdf` aborta); nenhum PDF/UA produzido.
- Edição revista R1075 + design R1076: 421 pp, 84 fragmentos, DOC −18,3%, CONT 7, LUC 23; 6 pranchas e legenda de códigos. Não substitui a canônica; capa/lombada a recalcular; sem nova ISBN.
- Variante print-safe R1077: 422 pp, sem fundo sépia, aberturas tipográficas, imagens ≥300 DPI, TAC médio 11,7%. Há capa selecionada R1082 a 300 DPI; CMYK/PDF-X e prova física pendentes.
- R1082 — capa selecionada preta/ouro: PDFs 422/436 pp, 300 DPI, fontes embutidas; 6 pranchas de prova a 316–345 DPI no tamanho final de 86 mm; 2× a 300 DPI não atingido (158–173 DPI), sem upscale; caderno de provas de 8 pp e preflight com TAC máximo 117,9%.
- A capa denominada `436p_canonica` é provisória frente ao miolo canônico **435 pp**; confirmar paginação e recalcular lombada antes de qualquer uso gráfico/KDP. A variante R1076 (421 pp) é digital/sensorial; R1077 (422 pp) é print-safe, ambas separadas da canônica.
- Perfil literário `romance-psicologico-molambudos` registrado e configurado para `ollama-local/gemma4:e2b-tuned`, sem fallback OpenCode Go; a inferência local não foi comprovada.
- Geração de imagem: OpenAI sem créditos e Gemini com cota zero; nenhuma arte nova gerada.
- `Tagged: no` no PDF canônico é gap conhecido; o EPUB revisado tem EPUBCheck/Ace.
- Nenhuma publicação, envio à KDP ou validação externa.
