# SPEC-027: EVOLVE PIPELINE — Routing de Subcomandos + Integração E2E

**Versão:** 1.0.0  
**Data:** 2026-06-08  
**Status:** Em implementação  
**Dependências:** SPEC-025 (Frontmatter), SPEC-026 (Pipeline Review)

---

## 1. Objetivo

Transformar o pipeline `/evolve` de uma documentação estática em um sistema de subcomandos funcional com:

1. **Routing** — cada subcomando (`discover`, `install`, `verify`, `update`, `learn`, `status`) dispara uma fase específica
2. **Integração E2E** — pipeline completo testável em modo dry-run
3. **Remoção de órfão** — `addyosmani/agent-skills` removido

---

## 2. Especificação de Subcomandos (SDD)

### 2.1 `/evolve` (sem argumentos)
Executa o pipeline completo: SENSE → DISCOVER → VERIFY → EVOLVE → LEARN.

### 2.2 `/evolve status`
**Contrato:** Exibe diagnóstico do ecossistema.
**Ações:**
- Ler `installed.json` → listar skills instaladas com status
- Ler `memory.json` → health score atual e histórico
- Executar `test_evolve_pipeline.py` → resultado dos 10 CTs
- Gerar relatório formatado

**Pós-condição:** Relatório com total de skills, health score, CTs pass/fail

### 2.3 `/evolve discover`
**Contrato:** Busca novas skills no GitHub trending + marketplaces.
**Ações:**
- GitHub API: `search/repositories?q=topic:agent-skills&sort=stars`
- GitHub API: `search/repositories?q=topic:claude-code-skills&sort=stars`
- Filtrar skills já instaladas (por nome em `installed.json`)
- Retornar top 5 descobertas não instaladas

**Pós-condição:** `discoveries[{name, url, stars, description}]`

### 2.4 `/evolve install <name>`
**Contrato:** Instala uma skill descoberta.
**Ações:**
- Validar `stars >= 10` (segurança)
- Baixar `SKILL.md` do repositório
- Salvar em `skills/<categoria>/<nome>/`
- Registrar em `installed.json`

**Pós-condição:** SKILL.md no disco + entrada em installed.json

### 2.5 `/evolve verify`
**Contrato:** Executa validação completa do ecossistema.
**Ações:**
- Executar `test_frontmatter_validator.py` (SPEC-025)
- Executar `test_evolve_pipeline.py` (SPEC-026)
- Verificar binários: `browser-use doctor`, `ralph-tui --version`
- Verificar MCPs: health check

**Pós-condição:** Relatório de health check com PASS/FAIL

### 2.6 `/evolve update`
**Contrato:** Atualiza skills instaladas.
**Ações:**
- Comparar versões instaladas vs. upstream
- Atualizar skills com versão > instalada
- Fazer backup antes de atualizar
- Registrar em `installed.json` com `updated_at`

**Pós-condição:** Skills atualizadas ou relatório "sem atualizações pendentes"

### 2.7 `/evolve learn`
**Contrato:** Analisa sessão atual e atualiza memória evolutiva.
**Ações:**
- Coletar métricas da sessão (tools usadas, latências, erros)
- Atualizar ranking de utilidade (`frequency × success × recency`)
- Identificar skills pouco usadas
- Salvar em `memory.json`

**Pós-condição:** `memory.json.healthHistory` incrementado

---

## 3. Testes E2E (TDD)

> Suite: `specs/test_evolve_e2e.py`

### 3.1 CT-E2E-001: Pipeline sequencial dry-run
- **Dado:** ecossistema instalado
- **Quando:** executa SENSE → VERIFY → LEARN (dry-run)
- **Então:** cada fase retorna resultado; sem erros fatais

### 3.2 CT-E2E-002: Status report formatado
- **Dado:** installed.json + memory.json válidos
- **Quando:** gera status report
- **Então:** contém healthScore, total_skills, timestamp

### 3.3 CT-E2E-003: Discover retorna resultados
- **Dado:** acesso à internet
- **Quando:** busca GitHub trending agent-skills
- **Então:** lista não vazia de repositórios com stars > 0

### 3.4 CT-E2E-004: Verify integrado (SPEC-025 + SPEC-026)
- **Dado:** test_frontmatter_validator.py + test_evolve_pipeline.py
- **Quando:** executa ambos em sequência
- **Então:** ambos retornam 100% PASS

### 3.5 CT-E2E-005: Install registra em installed.json
- **Dado:** uma skill descoberta válida
- **Quando:** executa install (dry-run)
- **Então:** não sobrescreve skills existentes; não instala < 10 stars

### 3.6 CT-E2E-006: Update detecta versões
- **Dado:** installed.json com skills
- **Quando:** compara versões com upstream
- **Então:** identifica skills com atualização pendente (ou relata "todas atualizadas")

### 3.7 CT-E2E-007: Learn persiste métricas
- **Dado:** memory.json existente
- **Quando:** executa learn com métricas simuladas
- **Então:** healthHistory incrementado em 1

### 3.8 CT-E2E-008: Órfão removido
- **Dado:** installed.json com órfão `addyosmani/agent-skills`
- **Quando:** executa limpeza de órfãos
- **Então:** órfão removido; installed.json sem status "orphan-404"

---

## 4. Refatoração de Componentes

### 4.1 `agents/autoevolve.md`
- Substituir documentação narrativa por **máquina de estados com routing**
- Cada subcomando → hook de fase específico
- Adicionar dry-run mode (`--dry-run`)

### 4.2 `command/evolve.md`
- Expandir de 37 linhas para documentação completa
- Adicionar exemplos de uso
- Adicionar tabela de subcomandos com parâmetros

### 4.3 `installed.json`
- Remover entrada `addyosmani/agent-skills` (órfão 404)

---

## 5. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Subcomandos implementados | 6/6 (status, discover, install, verify, update, learn) |
| CTs E2E passando | 8/8 |
| Órfãos em installed.json | 0 |
| Health score pós-evolve | >= 95 |
