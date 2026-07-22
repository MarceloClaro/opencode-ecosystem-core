# SPEC-911 — Molambudos Fase 0: viabilização editorial e pré-flight

## Objetivo
Executar a Fase 0 da avaliação best-seller de `Molambudos — O Diário do Paciente 1.260`, corrigindo lacunas editoriais e técnicas críticas que impedem a obra de ser tratada como produto publicável.

## Escopo
- Projeto-alvo: `projetos/molambudos/Molambudos_VictoriaRegia/`.
- Corrigir front/back matter comercial sem inventar dados legais inexistentes.
- Remover placeholders editoriais visíveis ao leitor.
- Reduzir warnings técnicos críticos de LaTeX.
- Unificar inconsistências nominais de Lúcia.
- Preservar a proposta imersiva: horror psicológico/sensorial em que o leitor se aproxima do Paciente 1.263.

## Fora de escopo
- Registrar ISBN real, solicitar CIP real ou autorizar uso de obra de terceiros: essas tarefas dependem de decisões/serviços externos.
- Reescrever estruturalmente os fragmentos CONT/LUC (Fase 1).
- Redesign profissional da capa e conversão gráfica para CMYK/bleed (Fase 2).

## Critérios de aceitação
1. `frontmatter/backpage.tex` não deve conter `Lorem ipsum` nem texto placeholder genérico.
2. `frontmatter/copyrightpage.tex` deve usar formulação comercial de direitos reservados e marcar ISBN/CIP como pendentes, sem inventar números.
3. Uma página de ficha catalográfica provisória deve existir e ser incluída no frontmatter, com aviso claro de substituição por ficha emitida por bibliotecário.
4. Todas as ocorrências de `Lúcia Mendes` e `Lúcia M.` devem ser unificadas para `Lúcia Menezes`, salvo usos deliberadamente abreviados e coerentes.
5. `misc/options.sty` deve corrigir `headheight` para eliminar warnings recorrentes de `fancyhdr`.
6. O PDF deve compilar em duas passagens com `pdflatex -interaction=nonstopmode main.tex` e sem erro fatal (`^!`).
7. O log deve reduzir warnings críticos de pré-flight em relação ao estado inicial da avaliação; itens remanescentes devem ser documentados como Fase 1/Fase 2.
8. O relatório da Fase 0 deve registrar mudanças feitas e pendências não executáveis sem decisão externa.

## Verificação
- Busca textual por `Lorem ipsum`, `Lúcia Mendes`, `Lúcia M.`, `ISBN:}` vazio e `headheight is too small`.
- Compilação dupla de `main.tex` no diretório `Molambudos_VictoriaRegia`.
- Leitura do sumário/frontmatter via `pdftotext` para confirmar inclusão da ficha provisória e ausência de placeholder.
