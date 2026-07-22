# SPEC-935-R53 — Nano-Orquestração para Manuscritos de Grande Escala

**Versão**: 1.0.0  
**Status**: Especificada  
**Data**: 2026-07-22  
**Autor**: Marcelo Claro (OpenCode Ecosystem Core)  
**Rótulos**: `nano-orchestration`, `coherence`, `large-scale`, `writing`, `fusion`
**Score-alvo**: 99.5/100

---

## 1. Visão Geral

Sistema de nano-orquestração que decompõe manuscritos de grande escala (até 500 laudas / ~750K tokens) em milhares de **nanoblocos** (~80-120 linhas, ~300 tokens cada), escreve cada um em paralelo via pool de agentes LiteRT-LM, e funde o resultado em 3 passagens de coerência para produzir um texto coeso, coerente e fluente com qualidade mínima de 99.5/100.

---

## 2. Arquitetura do Pipeline

```
[Entrada: tema + especificação]
         ↓
┌────────────────────────────────────────────┐
│ 1. NanoPlanner                             │
│    • Decompõe 500 laudas → 5000 nanoblocos │
│    • Gera grafo de dependência entre blocos │
│    • Estima tokens por bloco                │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 2. NanoSDD Engine                          │
│    • Gera mini-SDD para cada nanobloco     │
│    • 3-5 critérios de aceitação por bloco  │
│    • Contexto mínimo necessário             │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 3. ContextWindowManager                    │
│    • Seleciona apenas o contexto relevante  │
│    • Vizinhos imediatos + citações-chave    │
│    • Maximiza 300 tokens por bloco          │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 4. NanoWriter Pool (paralelo)              │
│    • Qwen3 0.6B: blocos descritivos        │
│    • Gemma4 2B: blocos argumentativos      │
│    • Gemma4 4B: blocos analíticos          │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 5. Quality Checker                         │
│    • Valida contra mini-SDD                │
│    • Falha → reescreve (escala modelo)     │
│    • 3 tentativas máximas                  │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 6. CoherenceEngine (3 passagens)           │
│    • Passada 1: Consistência local (2 viz) │
│    • Passada 2: Coerência global (seções)  │
│    • Passada 3: Fluidez de leitura (todo)  │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 7. CrossValidator                          │
│    • Valida transições entre blocos        │
│    • Verifica consistência terminológica   │
│    • Score de coesão > 9.5                 │
└────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────┐
│ 8. Quality Gates                           │
│    • SDD Gate: 100% dos critérios          │
│    • Coerência Gate: score médio > 9.5     │
│    • Trust Gate: consistência > 9.0        │
│    • CrossVal Gate: coesão > 9.5           │
└────────────────────────────────────────────┘
         ↓
[Manuscrito Final: 500 laudas coesas]
```

---

## 3. Critérios de Aceitação (SDD)

### 3.1. NanoPlanner (CA-001 a CA-006)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-001 | Decompõe entrada em nanoblocos de 80-120 linhas (±10%) | Precisão ≥ 90% | 5 |
| CA-002 | Gera grafo de dependência direcionado entre blocos | 100% dos blocos têm arestas | 4 |
| CA-003 | Estima tokens por bloco com erro < 20% | RMSE < 60 tok | 4 |
| CA-004 | Atribui tipo a cada bloco (descritivo/argumentativo/analítico) | Precisão ≥ 85% | 3 |
| CA-005 | Ordena blocos topologicamente segundo dependências | Ordem válida (sem ciclos) | 5 |
| CA-006 | Escala para 5000 blocos em < 30s | Tempo < 30s | 3 |

### 3.2. NanoSDD Engine (CA-007 a CA-011)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-007 | Gera 3-5 critérios de aceitação por nanobloco | 100% dos blocos | 4 |
| CA-008 | Extrai contexto mínimo do bloco e vizinhos | Tamanho < 400 tok | 4 |
| CA-009 | Critérios são verificáveis automaticamente | 95% TRUE pos | 5 |
| CA-010 | Cada critério tem peso (1-5) | Válido em 100% | 3 |
| CA-011 | Gera template de saída esperada (tipo, tom, extensão) | 100% dos blocos | 3 |

### 3.3. ContextWindowManager (CA-012 a CA-015)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-012 | Contexto por bloco nunca excede 400 tokens | Sem outliers | 5 |
| CA-013 | Inclui sempre o bloco anterior e posterior | 100% dos casos | 4 |
| CA-014 | Inclui citações de referências citadas no bloco | Recall ≥ 90% | 4 |
| CA-015 | Remove contexto duplicado entre blocos vizinhos | Redundância < 5% | 3 |

### 3.4. NanoWriter Pool (CA-016 a CA-020)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-016 | Bloco descritivo usa Qwen3 0.6B (rápido) | 100% dos descritivos | 3 |
| CA-017 | Bloco argumentativo usa Gemma 4 2B/4B | 100% dos argumentativos | 4 |
| CA-018 | Bloco analítico usa Gemma 4 4B | 100% dos analíticos | 4 |
| CA-019 | Timeout por bloco: 30s (descritivo), 60s (argumentativo), 120s (analítico) | Respeitado 100% | 3 |
| CA-020 | Pool executa N blocos em paralelo (N configurável, default 5) | Throughput ≥ 5 | 4 |

### 3.5. Quality Checker (CA-021 a CA-025)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-021 | Valida cada bloco contra seus critérios SDD | 100% dos critérios | 5 |
| CA-022 | Se falha, reescreve escalando modelo (Qwen→2B→4B) | Escalonamento correto | 5 |
| CA-023 | Máximo 3 tentativas por bloco | Respeitado 100% | 4 |
| CA-024 | Se falha após 3 tentativas, marca para revisão manual | Sinalizado | 3 |
| CA-025 | Score geral do checker ≥ 9.5 | Média ≥ 9.5 | 5 |

### 3.6. CoherenceEngine — Passada 1: Local (CA-026 a CA-029)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-026 | Verifica transição com bloco anterior | Suave em 95% | 5 |
| CA-027 | Verifica transição com bloco posterior | Suave em 95% | 5 |
| CA-028 | Reescreve abertura/fechamento se necessário | Melhora score | 4 |
| CA-029 | Mantém conteúdo original (não altera meio do bloco) | Fidelidade ≥ 95% | 4 |

### 3.7. CoherenceEngine — Passada 2: Global (CA-030 a CA-033)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-030 | Agrupa blocos em seções (10 blocos = 1 seção) | Agrupamento correto | 4 |
| CA-031 | Reescreve abertura e fechamento de cada seção | 100% das seções | 5 |
| CA-032 | Verifica consistência terminológica intra-seção | Termos consistentes | 4 |
| CA-033 | Score de coerência global > 8.5 | Score ≥ 8.5 | 5 |

### 3.8. CoherenceEngine — Passada 3: Fluidez (CA-034 a CA-037)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-034 | Leitura completa do manuscrito (agora em ~20 blocos de 40K tok) | Leitura integral | 5 |
| CA-035 | Refina tom e voz para consistência global | Tom uniforme | 4 |
| CA-036 | Remove repetições e redundâncias | Redundância < 3% | 5 |
| CA-037 | Score de fluidez de leitura > 9.0 | Score ≥ 9.0 | 5 |

### 3.9. CrossValidator (CA-038 a CA-042)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-038 | Valida transições entre N blocos consecutivos | Amostra ≥ 10% | 4 |
| CA-039 | Verifica consistência de termos técnicos no manuscrito inteiro | Desvio < 2% | 5 |
| CA-040 | Detecta contradições entre blocos distantes | 0 contradições | 5 |
| CA-041 | Score de coesão geral > 9.5 | Score ≥ 9.5 | 5 |
| CA-042 | Relatório de validação exportável (JSON) | 100% dos cenários | 3 |

### 3.10. Orquestrador (CA-043 a CA-047)

| CA# | Descrição | Métrica | Peso |
|-----|-----------|---------|------|
| CA-043 | Pipeline executa as 7 fases em ordem | Ordem correta | 5 |
| CA-044 | Checkpoints salvos a cada fase (retomável) | 100% das fases | 4 |
| CA-045 | Relatório final com scores de cada gate | Scores reportados | 3 |
| CA-046 | Tempo total para 500 laudas < 120 min | Tempo < 120 min | 4 |
| CA-047 | Taxa de sucesso geral (blocos válidos) > 98% | Sucesso > 98% | 5 |

---

## 4. Métricas de Validação

| Métrica | Alvo | Peso no Score |
|---------|------|---------------|
| Cobertura de critérios SDD | 100% | 20% |
| Score de coerência (médio) | ≥ 9.5 | 20% |
| Score de coesão (cross-val) | ≥ 9.5 | 15% |
| Taxa de sucesso de escrita | > 98% | 15% |
| Tempo total (500 laudas) | < 120 min | 10% |
| Fidelidade ao conteúdo original | ≥ 95% | 10% |
| Consistência terminológica | ≥ 98% | 10% |

**Score composto = Σ(métrica_normalizada × peso)**

Para atingir **99.5/100**: todas as métricas individuais devem estar no percentil 99% dos alvos.

---

## 5. Dependências

- `nano_orchestration/planner.py` — NanoPlanner
- `nano_orchestration/nano_sdd.py` — NanoSDD Engine
- `nano_orchestration/context_window.py` — ContextWindowManager
- `nano_orchestration/writer.py` — NanoWriter + Pool
- `nano_orchestration/quality_checker.py` — Quality Checker
- `nano_orchestration/coherence.py` — CoherenceEngine
- `nano_orchestration/cross_validator.py` — CrossValidator
- `nano_orchestration/orchestrator.py` — Orquestrador principal
- LiteRT-LM server rodando em `localhost:9379`
- Modelos: Qwen3 0.6B, Gemma 4 E2B, Gemma 4 4B
- `specs/SPEC-935-R210-litertlm-plugin-provider.md` — Provider LiteRT-LM

---

## 6. Risco e Mitigação

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Modelo LiteRT-LM não sustenta qualidade analítica | Média | Escalonamento automático para modelo maior no Quality Checker |
| Contexto de 300 tok por bloco é insuficiente | Baixa | ContextWindowManager pode expandir até 600 tok com aviso |
| CoherenceEngine introduce inconsistências | Média | CrossValidator detecta e sinaliza |
| Pool paralelo sobrecarrega servidor | Alta | Rate limiter + fila configurável (default 5 paralelos) |
| Tempo total excede 120 min | Média | Checkpoints permitem retomada |

---

## 7. Histórico de Revisão

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0.0 | 2026-07-22 | Spec inicial — 47 critérios de aceitação |
