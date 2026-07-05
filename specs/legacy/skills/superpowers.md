# Specs: Skills — Superpowers

**Categoria:** superpowers | **Total:** 12 skills | **Revisao:** 2026-05-27

---

## ai-engineering-harness (v1.0.0) ✅ SPEC INLINE
Framework Agent Harness: Git checkpoint obrigatorio, worktree isolada, SDD+TDD. 5 regras + checklist anti-vibe-coding.

## maintenance-first (v1.0.0) ✅ SPEC INLINE
Design patterns para manutencao: Repository, Strategy, Observer, Singleton, Factory Method. Arquitetura 3 camadas. SWEBOK.

## using-git-worktrees (v2.0.0) ✅ SPEC INLINE
Protocolo de seguranca commit-before-AI. Worktree isolation. Branches com convencao semantica.

## test-driven-development (v1.0.0) ✅ SPEC INLINE
Verificacao: toda funcao tem teste, teste falha antes, codigo minimo, bordas cobertas.

## subagent-driven-development (v1.0.0) ✅ SPEC INLINE
Regras: nunca pular review, nunca comecar na main, nao disparar implementadores paralelos.

## verification-before-completion (v1.0.0) ✅ SPEC INLINE
Checklist: testes passam, build OK, sem lint errors, bordas testadas, docs atualizados.

## writing-plans (v1.0.0)
### 1. Comportamento
Diretrizes para criar planos de implementacao estruturados com fases, tarefas e dependencias.
### 2. Criterios
- [ ] Plano gerado com fases sequenciais claras
- [ ] Cada task tem criterio de aceitacao verificavel
- [ ] Dependencias entre tasks explicitas

## executing-plans (v1.0.0)
### 1. Comportamento
Executa plano de implementacao passo a passo, verificando cada etapa.
### 2. Criterios
- [ ] Execucao sequencial das fases do plano
- [ ] Verificacao apos cada fase
- [ ] Rollback se fase falhar

## brainstorming (v1.0.0)
### 1. Comportamento
Sessao estruturada de brainstorming para gerar e refinar ideias antes de implementar.
### 2. Criterios
- [ ] Geracao de ideias com criterios de avaliacao
- [ ] Refinamento iterativo
- [ ] Output estruturado (pros/cons/riscos)

## requesting-code-review (v1.0.0)
### 1. Comportamento
Solicita revisao de codigo estruturada com contexto e escopo definidos.
### 2. Criterios
- [ ] Review solicitada com diff e contexto
- [ ] Criterios de revisao definidos (seguranca, performance, estilo)

## finishing-a-development-branch (v1.0.0)
### 1. Comportamento
Checklist para finalizar branch: testes passam, docs atualizados, merge pronto.
### 2. Criterios
- [ ] Verificacao pre-merge completa
- [ ] Limpeza de worktree se usada
- [ ] Branch deletada apos merge

## systematic-debugging (v1.0.0)
### 1. Comportamento
Metodo sistematico de debugging: reproduzir → isolar → hipotetizar → verificar → corrigir.
### 2. Criterios
- [ ] Bug reproduzido antes de corrigir
- [ ] Causa raiz identificada (nao sintoma)
- [ ] Teste adicionado para prevenir regressao
