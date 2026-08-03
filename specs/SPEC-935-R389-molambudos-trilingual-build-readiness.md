---
spec_id: SPEC-935-R389
title: Corrige bugs reais de compilação encontrados ao preparar a edição trilíngue para publicação
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r362_molambudos_route_a_pagination_preflight.py
---

# SPEC-935-R389 — Prontidão Técnica da Edição Trilíngue

**Data:** 2026-08-03
**Motivação:** o usuário pediu para "preparar a obra trilíngue pronta para
publicação literária". Ao tentar de fato compilar as 5 edições (PT, EN, ZH,
TRI, KDP trilíngue 160×230mm) via `scripts/audit_r362_pdf_layout.py --build`
pela primeira vez desde as edições de prosa dos ciclos R386/R387/R388, o
preflight R362 revelou 3 bugs reais de compilação que nunca haviam sido
detectados porque o pipeline nunca havia sido rodado de fim a fim após
essas edições — nenhum dos 5 PDFs publicados refletia o texto atual.

## 1. Glifo Unicode não suportado trava o build PT (`fragmentos/mem/MEM-27.tex`)

`\subsection*{╳ ESCALA DE CONTAMINAÇÃO --- DESTRUIÇÃO}` — o caractere
`╳` (U+2573, BOX DRAWINGS LIGHT DIAGONAL CROSS), presente no cabeçalho
original em `projetos/molambudos/molambudos.md` (linha 7981), quebra a
compilação de duas formas diferentes conforme o motor:

- **pdfLaTeX** (edição PT, `main.tex`): `LaTeX Error: Unicode character
  ╳ (U+2573) not set up for use with LaTeX` — erro fatal com
  `-halt-on-error`, build inteiro falha, nenhum PDF é produzido.
- **XeLaTeX** (edição `tri`, que monta o mesmo fragmento via
  `\tribody`/`\triinput`): `Missing character: There is no ╳ (U+2573)
  in font EB Garamond SemiBold` — não é erro fatal, mas o glifo
  simplesmente **desaparece silenciosamente** do PDF final (defeito de
  impressão não detectável sem inspeção manual).

**Correção:** substituído por `$\times$` (símbolo `×`, seguro nos dois
motores, sem depender de cobertura de glifo da fonte) em
`fragmentos/mem/MEM-27.tex` — o único arquivo do corpus com esse
caractere (confirmado por varredura de codepoints não-ASCII incomuns em
todos os fragmentos PT/EN/ZH). `molambudos.md` **não foi alterado** — o
glifo original é markdown legítimo; só a conversão para `.tex` precisa
ser segura. `scripts/build_miolo.py::inline_md_to_latex()` recebeu a
mesma regra (`text.replace('╳', r'$\times$')`) para que regenerações
futuras a partir do `.md` não reintroduzam o bug.

## 2. Tabelas de 2 colunas sem quebra de linha estouram a página

5 fragmentos (`fragmentos/cont/CONT-03.tex`, `fragmentos/luc/LUC-Escolha.tex`,
`fragmentos/cont/CONT-07.tex` PT/EN/ZH) usavam `\begin{tabular}{|l|l|}`
cru — colunas de largura natural, sem `p{largura}` — gerado por
`scripts/build_miolo.py::md_table_to_latex()`, que nunca aplica quebra de
linha a tabelas markdown. Sentenças de diagnóstico longas ("Leitor
contaminado. Lúcia escolheu. Você também já fez a sua escolha --- mesmo
que não saiba qual foi.") estouravam a largura da página, confirmado no
preflight: 9 violações "fora do MediaBox/CropBox" na tabela PT
"ATUALIZAÇÃO 1", 4 na PT "ATUALIZAÇÃO 3", 10 na EN "UPDATE 3" — refletido
com mais intensidade na edição KDP de 160×230mm (48 violações).

Tabelas de 3-6 colunas do projeto já haviam recebido esse retrofit em
ciclo(s) anterior(es), usando os ambientes `moltablethree/four/five/six`
(`supertabular` + `p{largura}` + `\footnotesize`, definidos em
`misc/options.sty` e `misc/options_zh.sty`) — mas não existia variante de
2 colunas, deixando essas 5 tabelas descobertas.

**Correção:** adicionado `\newenvironment{moltabletwo}` (mesmo padrão:
`p{0.25\textwidth}|p{0.65\textwidth}`, `\footnotesize`,
`\arraystretch{1.12}`, `\tabcolsep{2.5pt}`) em `misc/options.sty` e
`misc/options_zh.sty`; as 5 tabelas convertidas de `tabular` cru para
`moltabletwo`. `build_miolo.py::md_table_to_latex()` **não foi
alterado** — mesmo as tabelas de 3-6 colunas nunca foram
auto-geradas como `moltableN` (sempre foi retrofit manual pós-geração);
manter esse padrão evita inconsistência com o precedente já
estabelecido no projeto.

## 3. 12 fragmentos PT com links de rota em texto puro, sem `\rota{}`

`\newcommand{\rota}[1]{\hyperlink{#1}{\textbf{#1}}\,{\footnotesize(p.~\pageref{frag:#1})}}`
insere hyperlink clicável **e** número de página automático. 12
fragmentos PT (`CONT-03/05/06/07/08/09/10/11/12/13`, `MEM-27`,
`LUC-Escolha`) — todos de ciclos de expansão/restauração recentes
(R376/R377 para CONT, R384 para MEM-27/LUC-Escolha) — usavam a linha de
navegação em texto puro (`\noindent \textbf{↪ Links:} CONT-04 | MEM-05`),
sem o macro. As versões EN/ZH irmãs desses mesmos 12 fragmentos já
usavam `\rota{}`/`\rotasep` corretamente. Consequência dupla:

1. **Leitor de PT** perde o hyperlink clicável e o número de página
   nessas 12 passagens de navegação — presentes normalmente em EN/ZH.
2. **Pipeline de auditoria R362** só conta ocorrências de `\rota{}` via
   regex — essas 12 passagens eram **invisíveis** à validação de rotas,
   e a contagem real de rotas por idioma divergia: PT=167, EN=192,
   ZH=192 (esperado: as três iguais).

**Correção:** as 12 linhas convertidas para o padrão já usado nos outros
72 fragmentos modernos do corpus (`\noindent\textit{\textbf{↪ Rotas:}
\rota{X} \rotasep \rota{Y}}`), preservando os alvos de rota já
existentes em cada arquivo PT — **não copiados cegamente do EN**: em
`MEM-27`, o EN aponta para `CONT-05` como terceiro link, mas o PT
manteve `CONT-07` (decisão editorial já presente no PT, não alterada
sem necessidade). Rótulo também normalizado de "Links" (obsoleto) para
"Rotas" (convenção atual), igualando os outros 72 usos.

**Incidente durante a correção:** a primeira tentativa usou
`re.sub(pattern, replacement, text)` com `replacement` contendo `\n`,
`\t`, `\r` literais (para `\noindent`, `\textit`, `\rota`) — bug clássico
do Python: `re.sub` reprocessa essas sequências como escapes de verdade
(newline/tab/carriage-return) dentro do argumento `repl`, não como texto
literal. Isso corrompeu as 12 linhas, quebrando o balanceamento de
chaves (detectado por `_brace_balance` ficando negativo, o mesmo
verificador usado no R358). Corrigido com uma segunda passada segura
(concatenação explícita de `chr(92)`, sem `re.sub`) e remoção das linhas
residuais deixadas pela corrupção; balanceamento de chaves confirmado
zero nos 12 arquivos ao final.

## 4. Invariante de contagem de rotas: mesmo problema de número mágico do R358

Após a correção #3, a contagem de rotas por idioma passou a bater
(PT=EN=ZH=192), mas `scripts/audit_r362_pdf_layout.py::_route_report()`
ainda exigia `by_language == {"pt": 180, "en": 180, "zh": 180}` — um
número mágico desatualizado pelo mesmo motivo já corrigido no R358 para
a contagem de fragmentos (o corpus cresce entre ciclos). Substituído por
uma invariante auto-verificável: as três contagens devem ser iguais entre
si (`len(set(by_language.values())) == 1`) e positivas; `expected`/`total`
derivados dessa contagem × 3, não mais fixados em 540.
`tests/test_r362_molambudos_route_a_pagination_preflight.py::test_r362_route_report_validates_all_540_trilingual_routes`
recebeu a mesma correção.

## 5. Duplicidade de build `main_kdp_print_160x230mm.pdf` (raiz vs `tri/`)

Havia dois artefatos com o mesmo nome de arquivo em locais diferentes:
`main_kdp_print_160x230mm.pdf` na raiz (433 páginas, stale, compilado do
wrapper **legado só-PT** `main_kdp_print_160x230mm.tex`
→ `\input{main.tex}`) e `tri/main_kdp_print_160x230mm.pdf` (1135
páginas, de um build manual anterior com `-output-directory=tri`,
documentado em `evolution/cycles.json` num ciclo predecessor). O
wrapper trilíngue real é `tri/main_kdp_print_160x230mm.tex` →
`\input{tri/main_tri.tex}`, e é esse que
`scripts/audit_r362_pdf_layout.py::EDITIONS["kdp_tri"]` já referenciava
corretamente como fonte — o script roda com `cwd=BOOK` (raiz), então o
PDF de saída legitimamente aparece na raiz (comportamento padrão do
TeX: saída vai para o diretório de trabalho, não para o diretório do
arquivo de entrada). Após recompilação completa (que corrigiu #1-#3
acima), o PDF da raiz passou a ter 1141 páginas — conteúdo trilíngue
correto. Os artefatos órfãos em `tri/` (`.aux/.log/.out/.pdf/.toc`, não
referenciados por nenhum script) foram removidos; `tri/main_kdp_print_
160x230mm.tex` (a fonte, ainda necessária) foi preservado.

## 6. Sincronização com a árvore canônica separada

`projetos/molambudos/fragmentos/` é uma árvore-espelho canônica separada
de `projetos/molambudos/Molambudos_VictoriaRegia/fragmentos/`, verificada
byte-a-byte para um subconjunto de arquivos por
`tests/test_r384_molambudos_extended_regen_editorial_notes.py`. As
correções #1-#3 acima (aplicadas primeiro na árvore VictoriaRegia) foram
espelhadas manualmente nos 12 arquivos correspondentes da árvore
canônica (`CONT-03/05/06/07/08/09/10/11/12/13`, `MEM-27`,
`LUC-Escolha`) — inclusive nos 9 sem verificação automatizada explícita,
para não reintroduzir a mesma classe de dualidade que o usuário pediu
para eliminar nos ciclos anteriores desta sessão.

## 7. Critérios de aceitação

1. As 5 edições (PT, EN, ZH, TRI, KDP trilíngue) compilam com 2 passadas,
   0 erros fatais, 0 caracteres ausentes, 0 violações de layout —
   confirmado por `scripts/audit_r362_pdf_layout.py --build --jobs 5`.
2. `overall_internal_spec_passed: true` no preflight R362
   (`validacao_externa/cultural_episteme/molambudos_r362_preflight.json`).
3. Contagem de rotas `\rota{}` idêntica entre PT/EN/ZH (192 cada,
   576 = 192×3 na montagem `tri`), sem número mágico desatualizado na
   checagem.
4. Nenhuma correção de conteúdo criativo decidida unilateralmente sem
   base no que já existia no próprio arquivo PT (ex.: alvo de rota do
   `MEM-27` preservado, não copiado do EN).
5. `molambudos.md` não foi tocado nesta correção — apenas os `.tex`
   publicados e o gerador `build_miolo.py` (para não reintroduzir os
   bugs em regenerações futuras).
6. Árvore canônica separada (`projetos/molambudos/fragmentos/`)
   sincronizada com as mesmas correções, sem nova dualidade.
7. Suíte completa sem novas regressões: mesmas ~31 falhas pré-existentes
   e não relacionadas (módulos auxjuris/deep_diagnose/r129/r205/r211/
   r212/r213/r238/r239/r240/r242/r262/r266/r267/r268/sdd_tdd — nenhuma
   delas toca conteúdo, tabelas ou build LaTeX do Molambudos alterados
   aqui); `test_r362` 16/16 e `test_r384` 9/9 verdes.

## 8. O que continua explicitamente fora de alcance (não fabricado)

O preflight R362 mede apenas conformidade técnica interna — nunca
validação histórica, cultural, editorial ou de qualidade literária, e
`release_gate` permanece `"blocked"` por design
(`external_validation: false`, `human_review_required: true`,
`quality_verdict_allowed: false`). Continuam pendentes, e não podem ser
resolvidos por mim: revisão beta real (os artefatos existentes se
autodeclaram simulações analíticas), revisão de sensibilidade
recomendada por relatórios anteriores e nunca feita, revisão profissional
de tradução nativa para EN/ZH, confirmação real do ISBN
(`9798189170492`) numa conta KDP, e prova física — o próprio checklist
de KDP do projeto diz para nunca publicar sem ela.
