# SDD Onboarding: Criando uma Nova Skill com Spec-First

> "Spec antes de codigo. O agente implementa o que foi especificado." — Cap. 6

Este documento define o fluxo obrigatorio para criar qualquer nova skill no ecossistema OpenCode. Baseado no Cap. 6 (SDD) e na ADR-006.

---

## Fluxo SDD Completo

```
1. SPEC   → spec da skill (5 dimensoes)
2. REVIEW → spec revisada (agente reviewer ou humano)
3. SKILL  → implementar SKILL.md conforme spec
4. TEST   → testes validam criterios de aceitacao
5. REGIST → component-registry.md atualizado
6. CI     → pipeline valida tudo
```

## 1. SPEC — Template de 5 Dimensoes

Criar arquivo `SPEC.md` no diretorio da skill:

```markdown
# Spec: [nome-da-skill]

**Versao:** 0.1.0 (draft)
**Status:** proposed
**SWEBOK:** [evolutiva | adaptativa | corretiva | preventiva]

## 1. Comportamento
O que esta skill faz?
- Funcionalidade principal: [1-2 frases]
- Fluxo feliz: [passo 1] → [passo 2] → [resultado]
- O que NAO faz: [comportamentos excluidos]

## 2. Usuarios e Contexto
Quem usa e em que condicoes?
- Gatilho: [quando a skill e carregada/ativada]
- Usuarios: [agentes | humanos | ambos]
- Carga: [frequencia de uso]
- Dependencias: [skills, MCPs, arquivos]

## 3. Restricoes
Limites obrigatorios?
- Token budget: [max tokens no SKILL.md]
- Latencia: [tempo maximo de execucao]
- Compatibilidade: [modelos, plataformas]
- Seguranca: [restricoes de acesso]

## 4. Casos de Borda
O que acontece quando algo sai do esperado?
- Entrada invalida: [comportamento]
- Dependencia offline: [fallback]
- Timeout: [comportamento]
- Estado inconsistente: [recuperacao]

## 5. Criterios de Aceitacao
Como verificar que funciona?
- [ ] Criterio 1: [descricao verificavel]
- [ ] Criterio 2: [descricao verificavel]
- [ ] Criterio 3: [descricao verificavel]
- [ ] Testes cobrem todos os criterios? [sim/nao]
```

## 2. REVIEW — Checklist de Revisao

Antes de implementar, a spec deve ser revisada:

- [ ] As 5 dimensoes estao preenchidas? (sem "TBD" ou "—")
- [ ] O comportamento esta claro para quem nao escreveu a spec?
- [ ] As restricoes sao realistas? (token budget, latencia)
- [ ] Os casos de borda cobrem falhas comuns?
- [ ] Os criterios de aceitacao sao testaveis?
- [ ] Nao duplica funcionalidade de skill existente? (consultar component-registry.md)
- [ ] As dependencias estao corretas? (skills existem, MCPs disponiveis)

## 3. SKILL — Implementacao

Criar `SKILL.md` usando o template canonico (`skills/SKILL_TEMPLATE.md`), garantindo:

- [ ] Frontmatter com name, description (<120 chars), version, category
- [ ] Corpo do SKILL.md <= 2.500 tokens
- [ ] References em `references/` (carregadas sob demanda)
- [ ] Instrucoes claras para o agente que vai usar a skill
- [ ] Secao de integracao listando dependencias reais

## 4. TEST — Validacao

Criar testes que validam CADA criterio de aceitacao da spec:

- [ ] Teste para criterio 1
- [ ] Teste para criterio 2
- [ ] Teste para criterio 3
- [ ] Teste para caso de borda 1 (ex: dependencia offline)
- [ ] Teste para caso de borda 2 (ex: entrada invalida)

## 5. REGIST — Atualizar Registry

Adicionar entrada em `specs/component-registry.md`:

```markdown
| skill-[nome] | [nome] | 1.0.0 | active | [SWEBOK] | [deps] | SPEC.md |
```

## 6. CI — Validacao Automatica

Apos push, o CI pipeline (ADR-007) verifica:

- [ ] Lint: SKILL.md e references passam no linter
- [ ] Spec: SPEC.md existe e tem as 5 dimensoes
- [ ] Registry: componente esta registrado
- [ ] Tests: testes passam

---

## Exemplo: Spec da Skill "maintenance-first"

### 1. Comportamento
Fornece diretrizes de design patterns (Repository, Strategy, Observer, Singleton, Factory Method) e arquitetura em camadas para agentes gerarem codigo mantivel.

### 2. Usuarios
- Gatilho: quando o usuario pede codigo ou o agente vai gerar codigo
- Usuarios: agentes de codigo (coder-agent, web-developer) e humanos
- Dependencias: ai-engineering-harness, test-driven-development, code-review

### 3. Restricoes
- Token budget: max 2.500 tokens no SKILL.md
- Nao executa codigo (so fornece diretrizes)
- Compatibilidade: qualquer LLM com contexto >= 100K tokens

### 4. Casos de Borda
- Agente ignora as diretrizes: checklist de verificacao detecta
- Skill conflita com outra diretriz: ai-engineering-harness tem precedencia
- Design pattern nao aplicavel: agente deve justificar por que nao usou

### 5. Criterios
- [ ] Agente gera codigo em 3 camadas quando instruido com esta skill
- [ ] Agente usa Repository para acesso a dados
- [ ] Agente usa Strategy para 3+ variacoes de comportamento
- [ ] Checklist de manutenibilidade tem 8 itens verificaveis
- [ ] SKILL.md <= 2.500 tokens
