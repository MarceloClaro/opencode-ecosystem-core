---
spec_id: SPEC-935-R388
title: Elimina dualidade de conteúdo entre molambudos.md e o corpus .tex publicado
component: projetos/molambudos/molambudos.md
status: verified
test_file: tests/test_r270_molambudos_full_literary_scan.py
---

# SPEC-935-R388 — Elimina Dualidade `.md` × `.tex`

**Data:** 2026-08-03
**Motivação:** o usuário pediu explicitamente para "corrigir e limpar para não
ter dualidades no projeto literário", após a sessão descobrir (nos ciclos
R383/R384) que `molambudos.md` — nominalmente a fonte canônica desde a
decisão autoral do R376 — havia ficado para trás em relação a revisões
editoriais reais aplicadas diretamente nos arquivos `.tex` publicados.

## 1. Levantamento completo (antes de corrigir, não durante)

Comparação sistemática entre os 74 fragmentos parseados de `molambudos.md`
e seus `.tex` correspondentes (via regeneração em memória, nunca
sobrescrevendo nada): **68 dos 74 fragmentos** mostravam alguma
divergência lexical; após filtrar ruído cosmético (estilo de aspas
`\textquotedbl` vs `\textquotedblleft/right`, formato antigo de rotas
`\rota{}`/`\rotasep` vs `↪ Links:`), **31 fragmentos** tinham divergência
de conteúdo real — variando de uma única nota editorial (poucas palavras)
a reescrita substancial de cena (dezenas de linhas).

**Achado que mudou o plano original:** a hipótese inicial era "o `.tex`
só tem pequenas notas a mais". Isso era **falso** para vários casos:

- **CONT-04**: a cena "Noite 3" inteira foi reescrita e reestruturada no
  `.tex`, substituindo uma versão mais antiga e diferente que permanecia
  no `.md`.
- **MEM-02**: a cena da morte do pai foi reescrita para ser mais ambígua
  ("ele parou debaixo de um juazeiro seco... ficam para trás" em vez de
  "ele morreu... as pessoas morrem").
- **MEM-04/MEM-02**: correção geográfica dos ciclos R374/R375 ("sertão de
  Quixeramobim" → "rota de Senador Pompeu a Fortaleza") nunca propagada
  ao `.md`.
- **MEM-05, MEM-10**: cenas inteiras novas (a coruja; o enfermeiro e o
  menino) existiam só no `.tex`.
- **DOC-02, DOC-17, DOC-07, DOC-18**: correções **anti-overclaim reais**
  — o `.tex` já havia trocado alegações que soavam como documento
  histórico genuíno ("Documento original arquivado... Arquivo Público
  Mineiro, 2023", "8.240 internados, 7.912 mortos") por linguagem que
  deixa claro tratar-se de reconstituição ficcional — e essa correção
  nunca chegou ao `.md`.

Diante disso, o usuário foi consultado (`AskUserQuestion`) sobre a direção
da correção, dado o risco real de transcrição em obra de terceiro; optou
por transcrever tudo do `.tex` (mais maduro) para o `.md`.

## 2. Convenção de transcrição (LaTeX → Markdown)

Seguindo a lógica inversa de `scripts/build_miolo.py::md_to_latex()`:
- `\textit{X}` → `*X*`; `\textbf{X}` → `**X**`.
- `\textquotedbl{}X\textquotedbl{}` / `\textquotedblleft/right` → `"X"`
  (aspas retas, como o `.md` já usa em todo o resto do texto).
- `---` inline → `—`; bloco `\vspace...\rule...\vspace` → `---` isolado.
- `\NE{conteúdo}` (nota de rodapé do editor, `\newcommand{\NE}` em
  `main.tex`: `\footnote{\footnotesize\textbf{[N.E.]} #1}`) → novo
  parágrafo **"Nota do Editor:** conteúdo" — o `.md` não tinha
  convenção prévia para isso; esta é nova e documentada aqui.

**Não sincronizado, documentado como exceção estrutural (não é
"dualidade" de conteúdo):** `LUC-02`, `LUC-04`, `LUC-12`, `DOC-03`
(parcial), `DOC-09` contêm inclusão de imagem LaTeX
(`\includegraphics`, `\caption`, ambiente `figure`) e nomes de arquivo
de fotografia — não representáveis como prosa em markdown plano. O
conteúdo textual (legendas, texto ao redor) desses fragmentos já está
sincronizado; só a marcação de imagem em si permanece exclusiva do
`.tex`, como esperado.

## 3. Verificação (mesma disciplina do R383/R384/R386)

Para cada um dos 26 fragmentos com divergência de prosa real
(`CONT-01/02/03/04/10/11/13`, `MEM-02/03/04/05/06/07/10/16/18/20/26/27`,
`DOC-01/02/07/08/17/18/19`, `LUC-Escolha`), após editar `molambudos.md`:
regeneração em memória via `fragment_to_tex()` e comparação de conjunto
de palavras (≥5 caracteres, ignorando ruído cosmético conhecido) contra
o `.tex` publicado — **zero divergência real restante em todos os 26**.

**Nenhum arquivo `.tex` foi modificado nesta correção** — apenas
`molambudos.md`. Consequência direta: as cadeias de proveniência
(R360/R361/R362, que fixam hash de arquivos `.tex`) são **inteiramente
não afetadas** — verificado programaticamente (manifesto R362: 0
problemas).

## 4. Critérios de aceitação

1. Levantamento completo (74 fragmentos) documentado antes de qualquer
   edição, não durante.
2. Direção da correção (`.tex` → `.md`, não o inverso, dado que o `.tex`
   está mais maduro) decidida explicitamente pelo usuário, não
   presumida.
3. 26 fragmentos com divergência de prosa real sincronizados; cada um
   verificado individualmente por regeneração e comparação de palavras.
4. 3 correções anti-overclaim reais (DOC-02, DOC-17, DOC-07 + DOC-18)
   propagadas ao `.md` — não apenas notas de sabor narrativo.
5. Zero arquivo `.tex` tocado; zero impacto nas cadeias de proveniência
   R360/R361/R362 (verificado programaticamente).
6. Zero regressão: 30/30 testes das suítes R270-R276, suíte completa
   sem novas falhas.
7. Exceções estruturais (figuras/fotos em `LUC-02/04/12`, `DOC-03/09`)
   documentadas explicitamente, não silenciosamente ignoradas.
