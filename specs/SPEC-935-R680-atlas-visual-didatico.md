# SPEC-935-R680 — Atlas Visual Didático: Mapas, Fluxogramas e Diagramas por Elemento e Arquitetura

**Status:** proposta (orquestrador marceloclaro) — 05 out. 2026
**Escopo:** `livro-core/mod-16-mapas-fluxogramas.tex` + inclusão em `main.tex`
**Problema:** auditoria 05/10/2026 mostra cobertura irregular de diagramas: `mod-02` tem 8 `flowch`, mas `mod-00a/00b/15` (camada didática nova), `mod-01c`, `mod-09/09a`, `mod-10/12/13/14` têm 0. Leitor leigo perde-se sem mapa; técnico perde-se sem fluxo verificável.
**Estado-alvo:** atlas com ≥10 fluxogramas TikZ compiláveis cobrindo cada camada/elemento-arquétipo, leitura F-S-T-R, sem novos pacotes, com ajuda do NotebookLM quando autorizada.

## 1. Critérios de aceitação

1. [CA1] Arquivo `livro-core/mod-16-mapas-fluxogramas.tex` criado; `main.tex` ganha `\part{Atlas Visual}` + `\input{mod-16-mapas-fluxogramas}` antes do epílogo.
2. [CA2] ≥10 ambientes `flowch` (uso canônico `\begin{flowch}[titulo]{fonte}`), estilos `fn/fns/fne/fde/seta` de `macros.tex`, `matrix of nodes` com `ampersand replacement=\&`. Mapas: (M1) mestre 8 camadas didático; (M2) ciclo PERCEBE-DELEGA-EXECUTA-REFLETE; (M3) Blackboard A2A; (M4) MCI/MetaBus; (M5) SDD/TDD fail-closed; (M6) roteamento por atenção; (M7) instalação/doctor; (M8) FAIR + 12 passos; (M9) jornada 4 estações Ana/Bruno; (M10) ativação E1-E7.
3. [CA3] Cada mapa tem parágrafo de leitura funcional + onde mora no código + limite (sem prometer desempenho). Nenhum `flowch` com `[a][b]`; nenhum `\text{}` (usar `\mbox`); nenhum `_` cru fora de math/`\pth`; sem emoji; chaves balanceadas.
4. [CA4] NotebookLM: consulta `notebook_list` executada (225 notebooks, 05/10/2026); tentativa de `notebook_create` registrada como `blocked: explicit_operation_confirmation_required`; atlas segue local até confirmação do operador. Proveniência documentada neste SPEC e no capítulo.
5. [CA5] Verde: `python3 livro-core/check.py` exit 0; `pdflatex main.tex` com `grep -c "^!" == 0`; `main.pdf` regenerado com capítulo 16.
6. [CA6] Anti-overclaim: diagramas rotulados como modelo explicativo, não pipeline universal; contagens datadas como fotografia.

## 2. Execução

Perceber (auditoria acima + MetaBus) → Especificar (esta SPEC) → Executar (1 arquivo + 1 edição `main.tex`) → Verificar (check + pdflatex + contagem `flowch`) → Refletir (ciclo evolução + memória).
