---
spec_id: SPEC-935-R265
title: Auditoria final Molambudos 160x230mm com scanners e nota honesta
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r265_r279_spec_deliverables.py
---

# SPEC-935-R265 — Auditoria final Molambudos 160 × 230 mm

## Objetivo

Executar uma auditoria final do livro `Molambudos — O Diário do Paciente 1.260`, variante física **160 × 230 mm com folios seguros**, para responder se o livro está completo e qual nota honesta, de 0 a 10, pode ser atribuída antes de envio ao KDP.

## Escopo

- PDF final alvo: `main_miolo_amazon_kdp_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS.pdf`.
- Cópia nomeada: `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS_v2.0_2026-07-26.pdf`.
- Fontes LaTeX e fragmentos em `projetos/molambudos/Molambudos_VictoriaRegia/`.

## Critérios de aceitação para nota 10/10 local

1. O PDF final existe e abre com `pypdf`/PyMuPDF.
2. O PDF possui exatamente 296 páginas de miolo.
3. Todas as páginas têm tamanho 160 × 230 mm, tolerância máxima de 0,5 mm.
4. O PDF não possui criptografia.
5. O PDF não possui anotações/hyperlinks: `/Annots = 0`.
6. O catálogo não contém `/OpenAction`, `/Names`, `/Outlines`, `/PageMode` ou `/AA`.
7. Termos críticos estão presentes no texto extraível: `Molambudos`, `Passaporte`, `MEM-07`, `Nota Histórica`, `9798189170492`.
8. O ISBN canônico no fonte é `9798189170492`.
9. O texto visível do barcode/ISBN é coerente com `9 798189 170492` quando aplicável.
10. Todos os `\input{...}` literários e front/back matter referenciados existem.
11. Todos os arquivos de fragmentos em `fragmentos/**/*.tex` usados pelo livro existem e são alcançáveis pelo `main.tex`.
12. Todas as labels de fragmentos `frag:ID` são únicas.
13. Todas as rotas `\rota{ID}` apontam para labels existentes.
14. Não há labels órfãs críticas causadas por ID duplicado ou destino inexistente.
15. O conjunto esperado de 73 IDs de fragmentos permanece íntegro.
16. O PDF contém folios/números de página em páginas numeráveis suficientes para navegação física.
17. Não há cabeçalhos corridos no topo do miolo físico.
18. Nenhum bloco de texto fica fora do corte da página.
19. Nenhum bloco de texto viola as margens mínimas KDP para 296 páginas: interna 12,7 mm, externa/superior/inferior 6,35 mm.
20. Os scanners do ecossistema não detectam bloqueadores críticos de integridade, rigor ou consistência.
21. A nota 10/10 só pode ser declarada como **nota local de preflight**, não como aprovação externa Amazon/KDP.

## Não escopo

- Não substitui o Amazon KDP Previewer.
- Não valida capa/lombada da versão 296 páginas.
- Não garante revisão humana final de estilo linha a linha.

## Resultado da auditoria local — 2026-07-27

### Miolo 160 × 230 mm `COM-FOLIOS`

Resultado: **10/10 local de preflight do miolo**.

Critérios técnicos verificados:

- 296 páginas;
- página 160 × 230 mm;
- PDF abre em `pypdf`/PyMuPDF;
- sem criptografia;
- `/Annots = 0`;
- catálogo sem `/OpenAction`, `/Names`, `/Outlines`, `/PageMode` ou `/AA`;
- fontes incorporadas (`pdffonts`: 16/16 embutidas);
- termos críticos presentes no texto extraível;
- ISBN `9798189170492` presente no fonte;
- texto visual do barcode `9 798189 170492` presente no fonte;
- 73 IDs reais de navegação;
- 180 rotas;
- 0 destinos ausentes;
- 0 labels duplicadas;
- 0 labels órfãs;
- 72 arquivos de fragmentos usados + epílogo;
- 0 `\input` ausente;
- 263 páginas com folios detectáveis;
- 0 cabeçalhos corridos detectados no topo;
- 0 violações de corte;
- 0 violações de margens mínimas KDP.

### Livro/pacote KDP completo

Resultado: **não pode ser declarado 10/10 como pacote completo**.

Bloqueador: não foi localizada capa/lombada Amazon KDP recalculada para **296 páginas**. As capas KDP localizadas são variantes de **371 páginas**, portanto incompatíveis com o miolo final 160 × 230 mm de 296 páginas.

Formulação honesta: o **miolo** está aprovado localmente em 10/10; o **livro completo para KDP** permanece pendente até gerar e validar capa/lombada compatível com 296 páginas.
