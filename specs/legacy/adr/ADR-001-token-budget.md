# ADR-001: Token Budget Rigido para Skills

**Status:** active
**Data:** 2026-05-27
**Autor:** ecosystem (baseado no Cap. 5 — Agent Skills)
**Inspirado por:** Livro "Engenharia de Software com Agentes Inteligentes" (Sandeco, 2026)

## Contexto

O ecossistema OpenCode opera com agentes que consomem contexto de janela limitada (200K tokens). Skills sao carregadas no contexto do modelo antes da execucao. Sem controle de tamanho, skills grandes consomem tokens que deveriam ser usados para raciocinio. Alem disso, multiplas skills carregadas simultaneamente causam colapso de contexto.

## Decisao

Estabelecer limite rigido de token budget para toda skill carregavel:

1. **SKILL.md**: maximo 2.500 tokens (~500 linhas)
2. **Diretorio completo da skill**: maximo 10.000 tokens
3. **Skills simultaneas carregadas**: maximo 4
4. **Description no frontmatter**: maximo 120 caracteres (~30 tokens)

Arquivos alem do SKILL.md sao acessados via progressive disclosure (carregados sob demanda, nunca automaticamente).

## Alternativas Consideradas

| Alternativa | Rejeitada porque |
|-------------|-----------------|
| Skills sem limite de tamanho | Estouro de contexto, degradacao de qualidade |
| Carregar todas as references sempre | Consome tokens desnecessarios (referencias so precisam ser carregadas quando a tarefa corresponde) |
| Um unico SKILL.md monolitico de 10K tokens | Violaria progressive disclosure: o agente receberia informacao irrelevante para a tarefa atual |

## Consequencias

- **Positivas**: Contexto eficiente, respostas mais precisas, menos alucinacoes por sobrecarga
- **Negativas**: Skills complexas precisam ser bem decompostas em references. Custo inicial de design maior.
- **Riscos**: Skills mal decompostas podem perder contexto entre references

## Referencias

- `skills/evolution/progressive-disclosure-design.md` — especificacao detalhada
- `skills/SKILL_TEMPLATE.md` — template com limites
