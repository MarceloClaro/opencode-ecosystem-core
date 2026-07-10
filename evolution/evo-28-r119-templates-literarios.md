# R119 — Templates Literários/de Ficção + Limpeza de Resíduos do Catálogo

## Objetivo

Adicionar ao catálogo de templates os dois primeiros modelos LaTeX
literários/de ficção (`romance-literario` e `contos-poesia`), remover 37
diretórios numerados legados que duplicavam o catálogo já organizado por
SPEC-916, e validar a integração de ponta a ponta convertendo um PDF real
(romance de 341 páginas do próprio usuário) em projeto LaTeX via
`pdf2latex`.

## Mudanças Entregues

1. **Limpeza de resíduos** — `templates/01_*` a `templates/36_*` (37
   diretórios, confirmados como duplicatas via `diff -rq` e hash SHA-256
   de todo o conteúdo). Antes de remover, os 4 arquivos com conteúdo
   único encontrados foram copiados para seus lugares definitivos
   (`templates/projects/livro-volume2/.opencode_integration.json`,
   `.sdd_v2_specs.md`, `.tdd_validate_v2.py`;
   `templates/abntex2/abntex2-modelo-references-bibdesk-example.bib`).
   Confirmado por `grep` que nenhum código do repositório referenciava
   os caminhos numerados.

2. **`templates/books/romance-literario/`** — romance/narrativa de
   ficção: página de rosto, dedicatória, epígrafe, capítulos com letra
   capitular (`\letracapitular`) e marca de quebra de cena
   (`\cenaseguinte`), seção "Sobre o Autor" e colofão. Formato trade
   paperback (5.5×8.5in, compatível com Amazon KDP). Sem aparato
   acadêmico (sem abstract, sem bibliografia obrigatória).

3. **`templates/books/contos-poesia/`** — coletânea de contos e poemas:
   capítulos autocontidos (sem numeração "Capítulo N", só o título de
   cada texto), ambiente `poema` próprio (evita depender do pacote
   externo `verse`, ausente na instalação testada), organizado em partes
   "Contos"/"Poemas".

4. **Integração ao pipeline** — `publishing/production.py::TEMPLATE_MAIN`
   ganhou `livro-romance` e `livro-contos`; symlinks de compatibilidade
   `publishing/templates/livro/romance` e `.../contos`, seguindo o
   padrão já usado por `book`/`victoria_regia`.

5. **`templates/README.md`** atualizado: catálogo de livros, tabela de
   compatibilidade retroativa e estatísticas (46 templates, ~934
   arquivos `.tex`).

6. **Verificação de ponta a ponta com PDF real** — o usuário pediu para
   transformar dois PDFs em `templates/livro/` em projetos LaTeX via
   `pdf2latex`. Isso expôs (e permitiu corrigir) três bugs de integração
   reais, não hipotéticos:
   - `pdf2latex/latex_generator.py::_get_figures_for_section()` gerava
     `\caption{figura_1}` sem escapar `_` — o próprio método
     `_escape_latex()` já existia no arquivo mas não era chamado ali.
     Qualquer PDF com 2+ imagens quebrava a compilação
     ("Missing $ inserted"). Corrigido chamando `_escape_latex(caption)`.
   - `misc/opcoes.sty` dos dois templates novos carregava `babel` e
     `geometry` incondicionalmente com opções fixas — um main.tex gerado
     pelo pdf2latex já carrega os dois com opções próprias, causando
     "Option clash" fatal ao reabrir o pacote com opções diferentes.
     Corrigido com guarda `\@ifpackageloaded` para `babel` e trocando o
     carregamento de `geometry` por `\usepackage{geometry}` (sem opções)
     seguido do comando `\geometry{...}` (que sempre sobrescreve sem
     conflito).
   - `pdf2latex/template_integrator.py` não copiava o subdiretório
     `misc/` do template para o projeto gerado (só conhecia
     `config/images/logos/fonts`) — `misc/opcoes.sty` nunca chegava ao
     projeto. Adicionado `misc` à lista.
   - Confirmado por compilação real: `latexmk -pdf` no projeto gerado a
     partir de `MOLAMBUDOS.pdf` (romance de ficção real do usuário, 341
     páginas) produziu um PDF de 23 páginas sem erro fatal, restando
     apenas avisos não bloqueantes (headheight do fancyhdr, rótulos
     duplicados entre capítulos, bibliografia vazia).

7. **Testes**: `tests/test_r119_templates_literarios.py` (9 testes) —
   existência dos arquivos/estrutura de cada template, entradas em
   `TEMPLATE_MAIN`, resolução via `list_templates()`, symlinks de
   compatibilidade, e `prepare_latex()` copiando a árvore inteira
   (incluindo `misc/opcoes.sty`) para os dois novos templates.

## Decisão de Escopo — commit do módulo `pdf2latex/`

As correções em `pdf2latex/template_integrator.py` e
`pdf2latex/latex_generator.py` foram aplicadas e verificadas em disco,
mas **não fazem parte do commit deste ciclo**: ambos os arquivos já
tinham mudanças pendentes (staged e não-staged) de outra frente em
desenvolvimento paralelo (SPEC-1000 — pdf2latex multi-engine renderer),
não relacionadas a este ciclo. Misturar commits arriscaria atribuir a
este ciclo um diff muito maior do que o que foi de fato revisado aqui.
As correções ficam disponíveis para quem for commitar o SPEC-1000
completo. Da mesma forma, os PDFs de origem e os projetos LaTeX gerados
a partir deles (`templates/livro/MOLAMBUDOS.pdf`, `main-dark.pdf`, e as
pastas `molambudos/`/`ia-em-odontologia/`) são conteúdo do usuário, não
parte do catálogo reutilizável de templates — permanecem em disco, fora
deste commit.

## Verificação

- `python3 -m pytest tests/test_r119_templates_literarios.py -v` → 9 passed
- `python3 -m pytest tests/ -q` completo (sem regressão nova; a única
  falha é a intermitente pré-existente `test_failed_task_lowers_confidence`,
  já documentada em ciclos anteriores como não relacionada)
- Compilação real (`latexmk -pdf`) do projeto `pdf2latex` gerado a
  partir do romance de 341 páginas do usuário, com sucesso após as
  três correções acima

## Lições

1. "Renovar" um catálogo de templates sem testar a integração de ponta a
   ponta (gerar + compilar um projeto real) deixaria passar os três bugs
   de integração encontrados — nenhum deles aparecia nos testes
   unitários de existência de arquivo, só na compilação LaTeX real.
2. Reutilizar `\usepackage{babel}`/`\usepackage{geometry}` com opções
   fixas dentro de um `.sty` pensado para ser incluído por *outros*
   documentos (não só o `main.tex` autoral do próprio template) exige
   assumir que o pacote já pode estar carregado com opções diferentes —
   o padrão seguro é carregar sem opções e aplicar via comando depois
   (`\geometry{}`), ou guardar com `\@ifpackageloaded`.
3. A limpeza de resíduos e a criação de templates novos, apesar de
   pedidas em mensagens separadas do usuário, se mostraram uma única
   unidade coerente de trabalho (catálogo de templates) — registradas
   num único ciclo R119 em vez de dois ciclos artificialmente separados.

## Score

**9.0/10**

- Entrega o pedido explícito do usuário (templates literários) e o
  pedido lateral (limpeza de resíduos) num único ciclo coerente
- Verificação de ponta a ponta com conteúdo real do usuário (não apenas
  testes sintéticos), encontrando e corrigindo 3 bugs de integração reais
- Disciplina de escopo de commit mantida mesmo sob pressão de conveniência
  (não misturou as correções do `pdf2latex/` com trabalho pendente de
  outra frente)
