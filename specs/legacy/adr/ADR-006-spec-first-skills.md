# ADR-006: Spec-First para Todas as Novas Skills

**Status:** active
**Data:** 2026-05-27
**Autor:** ecosystem (baseado no Cap. 6 — SDD: Spec-Driven Development)
**Inspirado por:** Livro "Engenharia de Software com Agentes Inteligentes" (Sandeco, 2026)

## Contexto

O ecossistema OpenCode cresceu de 9 skills (Maio/2026) para 74+ skills. Skills foram criadas em 12 rodadas de evolucao, muitas sem spec previa documentada. Isso gera os mesmos problemas que o vibe coding: codigo (skill) funcional, mas sem especificacao clara do que deve fazer, para quem, com quais restricoes.

O Cap. 6 do livro estabelece: "O agente implementa o que foi especificado. Se a spec estava errada, o agente implementa o erro com eficiencia impecavel."

## Decisao

Toda nova skill criada no ecossistema DEVE seguir o fluxo SDD:

1. **SPEC** — Escrever spec minima com 5 dimensoes (comportamento, usuarios/contexto, restricoes, casos de borda, criterios de aceitacao)
2. **REVIEW** — Spec revisada por pelo menos 1 outro componente do ecossistema (agente reviewer ou swarm-review)
3. **SKILL** — Implementar a skill conforme a spec
4. **TEST** — Criar testes que validam cada criterio de aceitacao da spec
5. **REGISTER** — Registrar no component registry

Template de spec: `skills/superpowers/references/spec-template-minima.md`

## Alternativas Consideradas

| Alternativa | Rejeitada porque |
|-------------|-----------------|
| Continuar sem spec (status quo) | Skills sem spec = manutencao impossivel. "Codigo que ninguem entende completamente e codigo que ninguem consegue manter com seguranca." (Cap. 2) |
| Spec apenas para skills complexas | Toda skill se torna complexa com o tempo. Limiar arbitrario de "complexo" gera inconsistencia. |
| Spec gerada pela IA sem revisao | O agente alucina suposicoes. Spec precisa de revisao humana ou cross-validation. |

## Consequencias

- **Positivas**: Rastreabilidade completa. Cada skill tem proposito documentado, restricoes conhecidas, criterios de aceitacao verificaveis. Manutencao previsivel.
- **Negativas**: Custo inicial maior (escrever spec antes de codificar). Velocidade de criacao reduzida no curto prazo.
- **Riscos**: Specs desatualizadas (skill evolui, spec nao). Mitigado: spec versionada junto com a skill no mesmo diretorio.

## Verificacao

- [ ] Toda skill em `skills/` tem `SPEC.md` ou spec inline no SKILL.md
- [ ] Spec cobre as 5 dimensoes minimas
- [ ] Existem testes para cada criterio de aceitacao
- [ ] Spec esta registrada no component registry

## Referencias

- `skills/superpowers/references/spec-template-minima.md`
- `skills/superpowers/ai-engineering-harness.md` — Regra 2 (Spec antes de codigo)
- Cap. 6 do livro — Secao 6.2-6.7
