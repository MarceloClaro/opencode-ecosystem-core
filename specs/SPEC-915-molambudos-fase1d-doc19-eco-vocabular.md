# SPEC-915 — Molambudos Fase 1D: DOC-19, referência externa e eco vocabular

## Objetivo
Revisar `DOC-19` para remover transcrição direta de obra externa real, reduzir risco de direito autoral/overclaim de autorização e transformar o fragmento em nota documental própria da ficção. Em paralelo, executar uma primeira auditoria objetiva de eco vocabular nos fragmentos do livro para orientar futuras passadas de leitura linear.

## Escopo
- Projeto: `projetos/molambudos/Molambudos_VictoriaRegia`.
- Alvo principal: `fragmentos/doc/DOC-19.tex`.
- Contexto narrativo imediato: `DOC-18`, `DOC-02`, `MEM-06`, `MEM-16`.
- Auditoria automatizada de repetições nos arquivos `fragmentos/**/*.tex`, sem reescrever a obra inteira nesta fase.

## Critérios de aceitação
1. `DOC-19` não deve conter transcrição direta atribuída a livro, autora ou obra real.
2. `DOC-19` não deve afirmar “transcrição autorizada” ou autorização externa não comprovada.
3. O fragmento deve manter a função histórica: conectar Joaquim ao Hospital Colônia, aos mortos sem registro e à ambiguidade testemunho/delírio.
4. O título e o cabeçalho de `DOC-19` devem evitar apropriação de título de obra real como se fosse parte autorizada do livro.
5. O texto deve soar como nota arquivística/relatório institucional ficcional, não ensaio explicativo.
6. Links finais de leitura devem permanecer preservados.
7. Deve existir uma auditoria de eco vocabular com achados e recomendações, sem necessidade de corrigir todos os ecos nesta fase.
8. O PDF deve compilar em duas passagens sem erro fatal, sem destinos duplicados, sem font warnings e sem regressão de `overfull hbox`.

## Verificação
- Leitura manual de `DOC-19` após alteração.
- Busca por termos problemáticos no alvo: `Holocausto Brasileiro`, `Daniela Arbex`, `Transcrição autorizada`, `Trecho do livro`.
- Auditoria automatizada de frases recorrentes em `fragmentos/**/*.tex`.
- Compilação dupla: `pdflatex -interaction=nonstopmode main.tex`.
- Contagem no `main.log`: `LaTeX Error`, `Fatal error`, `Overfull \hbox`, `Overfull \vbox`, `destination with the same identifier`, `Font Warning`.
