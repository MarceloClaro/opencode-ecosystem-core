# Plano R910 — Deduções locais do livro

> Executar no contexto atual com editores paralelos em arquivos distintos e revisão independente.

**Objetivo:** aproximar cada dedução da proposição efetivamente aceita pelo Lean.
**Arquitetura:** blocos locais em TeX, nomes auditados e índice de dependências gerado.
**Tecnologias:** LaTeX, Python/pytest, Lean 4.34.1/Mathlib fixados.
**Spec:** specs/SPEC-935-R910-deducoes-locais-livro-lean.md.

## Restrições e foco de revisão

- Hipóteses de independência, faixas e denominadores não podem desaparecer.
- Prova de aritmética não comprova a ocorrência do dado; F27 fica fora do domínio formal.
- Nomes citados precisam existir no recibo e representar a fórmula apresentada.
- Catálogo gerado deve sobreviver à regeneração; texto longo deve caber nas margens.
- Recibos ficam obsoletos ao editar fontes: recompilar após congelar os arquivos.

## Execução

- [ ] Criar teste editorial RED dos pares família/fonte e de nomenclatura.
- [ ] Implementar ambiente local e validador, com mutações negativas de rastreabilidade.
- [ ] Revisar capítulos científicos e de fundamentos com editor validado.
- [ ] Revisar orquestração/memória/integrações com editor validado.
- [ ] Root integra catálogo/geradores, seção de fundamentos e tabela de axiomas por declaração.
- [ ] Revisão independente, correções e testes editoriais selecionados.
- [ ] Congelar fontes; recompilar Lean e livro, inspecionar páginas e margens.
- [ ] Registrar evidências, evolução e publicar commit na branch atual.
