# R1078 — Piloto PDF/UA: Typst 0.15.1 vs WeasyPrint 67.0

**Status:** piloto técnico executado; **sem certificação PDF/UA**.
**Não é validação externa, não é parecer de acessibilidade e não é nota 10/10.**

## 1. Documento de teste

Um único documento de 6 × 9 in com:

- título e seção;
- parágrafo com link externo;
- tabela com `<th scope="col">` e legenda;
- figura com texto alternativo e legenda;
- nota de rodapé.

Fontes: Liberation Serif. O mesmo conteúdo foi gerado em HTML (WeasyPrint) e
Typst.

## 2. Métricas observadas

| Métrica | WeasyPrint 67.0 (`pdf/ua-1`) | Typst 0.15.1 (`--pdf-standard ua-1`) |
|---|---|---|
| Página | 432 × 648 pt (6 × 9 in) | 432 × 648 pt (6 × 9 in) |
| Tamanho | 20.009 bytes | 38.938 bytes |
| `Tagged` | sim | sim |
| `/StructTreeRoot` | sim | sim |
| `/MarkInfo` | `/Marked true` | `/Marked true`, `/Suspects false` |
| `/Lang` | **`pt-BR`** | `pt` |
| `/ViewerPreferences` | `DisplayDocTitle true` | `DisplayDocTitle true`, `Direction /L2R` |
| XMP `pdfuaid` | sim | sim |
| `/Outlines` | sim | sim |
| Elementos de estrutura | **58** | 39 |
| Entradas `/Alt` | 1 | 1 |
| `/RoleMap` | não | sim |
| `/ParentTree` | sim | sim |
| Fontes embutidas | 3 | 2 |
| Texto extraível | sim | sim |

## 3. Leitura

- **WeasyPrint 67** entrega o idioma `pt-BR` no `/Lang`, mais nós de estrutura
  (58 vs 39), legenda de tabela e alt text. É a melhor escolha para o piloto de
  PDF/UA e para documentos baseados em HTML/CSS.
- **Typst 0.15.1** também entrega PDF tagged e XMP PDF/UA, com `RoleMap` e
  `Direction /L2R`. O `/Lang` ficou `pt` (não `pt-BR`) e o número de nós é menor.
  É excelente para composição rápida e variantes, mas exige ajuste de idioma e
  de mapeamento de papéis para o padrão brasileiro.
- **Nenhum dos dois foi validado pelo veraPDF.** A presença de
  `/StructTreeRoot`, `/MarkInfo` e XMP `pdfuaid` é condição necessária, não
  certificação. A validação formal e a revisão manual de ordem de leitura, alt
  text e tabelas continuam pendentes.

## 4. O que falta para conformidade

1. Rodar **veraPDF** com perfil PDF/UA-1 nos dois PDFs (ferramenta não instalada
   nesta rodada).
2. Revisar manualmente a **ordem de leitura** e a associação de cabeçalhos da
   tabela.
3. Confirmar que todas as imagens têm alt text significativo (o piloto tem uma).
4. Verificar links, notas e metadados de título no leitor de tela.
5. Corrigir o `/Lang` do Typst para `pt-BR` ou aceitar `pt` com justificativa.
6. Repetir o piloto com um capítulo real do Molambudos, não só com uma página.

## 5. Recomendação

**WeasyPrint 67** para o piloto de PDF/UA do Book Studio, com uma etapa
obrigatória de veraPDF. **Typst 0.15.1** permanece como motor de composição
rápida e de variantes; para PDF/UA, precisa de ajuste de idioma e de uma rodada
de validação formal.

## 6. Arquivos

| Caminho | Conteúdo |
|---|---|
| `pilot.html` | fonte HTML do piloto |
| `pilot.typ` | fonte Typst do piloto |
| `pilot.png` | imagem de teste |
| `weasyprint_ua.pdf` | PDF/UA gerado pelo WeasyPrint |
| `typst_ua.pdf` | PDF/UA gerado pelo Typst |
