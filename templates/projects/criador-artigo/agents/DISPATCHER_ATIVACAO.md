<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# DISPATCHER DE ATIVAÇÃO MULTIAGENTE v4.0 (ITERATIVO)
# Multi-Agent Scientific Writing Operating System (MASWOS V4)
# 45 Agentes Especializados (A0–A45) · 8 Fases · Ecossistema Integrado

---

## Arquitetura do Sistema V4 (Loop Fechado)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                     A0 · EDITOR-CHEFE PhD (AUTORIDADE)                    │
│           Abre/Fecha Fases · Arbitra Conflitos · Homologa 10/10           │
└──────────────┬──────────────────────────────────────────────┬─────────────┘
               │                                              │
      ┌────────▼────────┐                            ┌────────▼────────┐
      │ FASE 1: DIAGN.  │──→ FASE 2: BUSCA ──→ FASE 3: ESTRUTURA       │
      └────────┬────────┘                            └────────┬────────┘
               │                                              │
      ┌────────▼────────┐                            ┌────────▼────────┐
      │ FASE 4: PRODUÇÃO│←─── Loop de Correção ────→ │ FASE 4A: NÚCLEO │
      │ (A5-A11)        │      (A44 + A45)           │ ANALÍTICO (DATA)│
      └────────┬────────┘                            └────────┬────────┘
               │                                              │
      ┌────────▼────────┐                            ┌────────▼────────┐
      │ FASE 5: INTEGRA.│←── FASE 6: PEER REV. ←── FASE 7: DEFESA/SLID.│
      └─────────────────┘    (A31 + V4 Loop)         └─────────────────┘
```

---

## Regras de Sincronização V4

1. **Gate de Nota 10/10:** Nenhuma fase ou capítulo é aprovado com nota inferior a 10/10 na `rubrica_avaliacao.md`.
2. **Ativação Automática do Módulo de Correção:** Sempre que A13 (QA) ou A14 (Consistência) detectarem falhas, os agentes **A44 (Forma)** e **A45 (Conteúdo)** são ativados antes do escalonamento ao A0.
3. **Retroalimentação de Pesquisa:** Se A44/A45 identificarem falta de lastro, reativam **A2/A3** (Módulo de Pesquisa) para nova coleta.
4. **Handoff Estrito:** O uso do `TEMPLATE_HANDOFF.md` é obrigatório para manter a memória do ecossistema.
5. **Sincronia de Idioma:** 100% Português Brasileiro (PT-BR) em todos os agentes, exceto onde especificado (Abstract).

---

## ⚠️ DIRETIVA GLOBAL — SISTEMA DE 3 NÍVEIS DE PUBLICAÇÃO (3-TIER PUBLISHABLE SYSTEM)

> A partir da V3, o ecossistema processa demandas em três malhas de profundidade distintas.
> **Todo agente, template e validador DEVE adaptar sua verbosidade, uso de tokens, rigor analítico
> e chamadas de subprocessos ao Nível de Publicação escolhido pelo Usuário Principal
> (Editor-Chefe Hominídeo) na abertura da Fase 1.**

| Nível | Alvo | Agentes Ativos | Política de Tokens |
|:---:|---|:---:|---|
| 🥇 **1 — Magnum / Tese / Qualis A1** | Teses, livros, State-of-the-Art (+100 páginas) | **45** (cascata total, A0–A45) | **Nenhuma economia** — rigor máximo, Loop A44/A45 até 10/10 |
| 🥈 **2 — Standard Paper / Q1-Q2** | Artigos de periódico (15–30 páginas) | **~20** (Núcleo Analítico Fast-Track) | Eficiência de tempo exigida; sem anexos massivos |
| 🥉 **3 — Short Communication / Congresso** | Resumos expandidos, Policy Briefs (5–10 páginas) | **≤ 10** (Pipeline Expresso) | Economia máxima; IMRAD condensado; sem blind-review pesado |

> **Instrução de ativação:** A0 (Editor-Chefe PhD) registra o Nível em `decisao_editor_fase_1.md`
> antes de qualquer outra ação. Este arquivo é lido por todos os agentes antes de iniciar sua etapa.

---

## ═══════════════════════════════════════════════════════════════
## FASE 1 — DIAGNÓSTICO E DEFINIÇÃO (ECOSSISTEMA V4)
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Congelar a fundação científica do artigo.

### Pipeline
```
A0 (abre) → A1 → A40 → A39 → A14 (Valida) → [A44/A45 se nota < 10] → A0 (fecha)
```

| Passo | Agente | Ação | Saída |
|---|---|---|---|
| 1.1 | A0 Editor-Chefe | Abrir fase, definir Nível de Publicação (1, 2 ou 3) | `decisao_editor_fase_1.md` |
| 1.2 | A1 Diagnóstico | Problema, lacuna, gap, hipóteses, objetivos | `diagnostico_fundacao.md` |
| 1.3 | A40 Marcos Teóricos | Classificar corrente teórica e método de interpretação | `marco_teorico_classificado.md` |
| 1.4 | A39 Metodologia | Classificar paradigma (Quanti/Quali/Misto/DSR) | `classificacao_paradigmatica.md` |
| 1.5 | **A14 Consistência** | **Gate de Validação V4** | OK ou Ativa A44/A45 |
| 1.6 | A0 Editor-Chefe | Homologação final da Fase 1 | Aprovação formal |

---

## ═══════════════════════════════════════════════════════════════
## FASE 2 — BUSCA E EVIDÊNCIAS (MÓDULO DE PESQUISA)
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Lastro bibliográfico auditável.

### Pipeline
```
A0 (abre) → A2 → A3 → A12 → A33 → A14 (Valida) → [A44/A45] → A0 (fecha)
```

| Passo | Agente | Ação | Saída |
|---|---|---|---|
| 2.1 | A2 Busca/Curadoria | Busca sistemática (Scopus, WoS, etc.) | `log_busca.md`, `triagem_fontes.md` |
| 2.2 | A3 Evidências | Mapa de citações com DOI e justificativa | `matriz_evidencias.md`, `mapa_citacoes.md` |
| 2.3 | A12 Auditoria ABNT | Conferir norma (ABNT/APA/Vancouver) | `relatorio_abnt.md` |
| 2.4 | A14 Consistência | Validação do lastro documental | OK ou Loop de Correção |

---

## ═══════════════════════════════════════════════════════════════
## FASE 4 — PRODUÇÃO E LOOP DE CORREÇÃO V4
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Redação dos capítulos com densidade 10/10.

### Pipeline de Produção (Iterativo)
```
A0 (abre) → [A5|A6|A7|A8|A9|A10|A11] → A14 (Valida) → A13 (QA)
                                          ↓ (Se < 10/10)
                                    Módulo de Correção (A44 + A45)
                                          ↓ (Se falta evidência)
                                    Módulo de Pesquisa (A2 + A3)
                                          ↓
                                    A0 (Homologa 10/10)
```

### Agentes de Produção (Fase 4):
- **A5 (Revisão Literatura):** Redação teórica profunda.
- **A6 (Metodologia):** Detalhamento procedimental.
- **A9 (Resultados):** Exposição de achados.
- **A10 (Discussão):** Diálogo crítico (Sincronizado com A45).
- **A11 (Conclusão):** Síntese e contribuições.

### Módulo de Correção Ativa (Novo V4):
- **A44 (Correção Textual):** Garante a estrutura de 6 frases por parágrafo e densidade Qualis.
- **A45 (Refinamento Argumentativo):** Injeta debate teórico e profundidade analítica.

---

## ═══════════════════════════════════════════════════════════════
## FASE 4A — NÚCLEO ANALÍTICO REPRODUTÍVEL
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Produção de dados, código e evidência empírica.

### Pipeline
```
A35 (Coleta Real) → A43 (Satelite/Bio) → A17 (Env) → A18 (Data) → A32 (Etica) → 
A19 (Auditoria) → A20/A21 (Estat/Mat) → [A22-A27 Domínio] → A28 (Bench) → A42 (Dev) → A0
```

---

## ═══════════════════════════════════════════════════════════════
## FASE 6 — PEER REVIEW E VALIDAÇÃO FINAL
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Stress test do manuscrito completo.

### Pipeline
```
A0 (abre) → A31 (Blind Review) → [A44/A45 se críticas Major] → A29 (Conf. Int.) → A0 (fecha)
```

---

## MAPA COMPLETO: 45 AGENTES × 8 FASES (ECOSSISTEMA V4)

| ID | Nome do Agente | Fases Ativas |
|---|---|---|
| A0 | Editor-Chefe PhD | TODAS (Gatekeeper) |
| A1 | Diagnóstico de Escopo | 1, 3 |
| A2 | Busca e Curadoria | 2, 4 (Loop) |
| A3 | Evidências e Citações | 2, 4 (Loop) |
| A4 | Estrutura Argumentativa | 3 |
| A5 | Revisão de Literatura | 4.1 |
| A6 | Metodologia | 4.2 |
| A7 | Estatística e Análise | 4.2, 4.4 |
| A8 | Visualização Gráfica | 4.2, 4.4, 5 |
| A9 | Resultados | 4.4 |
| A10 | Discussão e Contribuição | 4.5 |
| A11 | Conclusão e Coerência | 4.6 |
| A12 | Auditoria ABNT | 2, 5 |
| A13 | QA Qualis A1 | 4.5, 5, 6 |
| A14 | Consistência Interna | TODAS (Validador) |
| A15 | Resumo/Abstract | 4.7 |
| A16 | Integração Editorial | 5 |
| A17 | Framework Reprodutível | 4A |
| A18 | Engenharia de Dados | 4A |
| A19 | Auditoria de Código | 4A |
| A20 | Estatística Avançada | 4A |
| A21 | Matemática Aplicada | 4A |
| A22 | Machine Learning/DL | 4A |
| A23 | Bioinformática/Ômicas | 4A |
| A24 | Quimioinformática | 4A |
| A25 | Ciências Sociais Quant. | 4A |
| A26 | Visão Computacional | 4A |
| A27 | Computação Quântica | 4A |
| A28 | Benchmark/Ablação | 4A |
| A29 | Conformidade Internacional | 6 |
| A30 | Tradução Nativa | 5 |
| A31 | Blind Peer Review | 6 |
| A32 | Ética e Open Science | 4A |
| A33 | Multi-Norma | 2, 5 |
| A34 | Conflitos/Similaridade | 5 |
| A35 | Coleta de Dados Reais | 4A |
| A36 | Exportação LaTeX/PDF | 5 |
| A37 | Slides para Banca | 7 |
| A38 | Montagem Final | 5 |
| A39 | Metodologia Multi-Paradigma | 1, 4.2 |
| A40 | Marcos Teóricos | 1, 4.1, 4.4, 4.5 |
| A41 | GIS/Geoprocessamento | 4.2, 4A |
| A42 | Desenvolvedor/Cientista | 4A, 5, 7 |
| A43 | Satélite/Bioinformática | 4A |
| **A44** | **Correção Textual Qualis** | **4, 5, 6 (Loop)** |
| **A45** | **Refinamento Argumentação** | **4, 5, 6 (Loop)** |

---
**Status do Ecossistema:** 100% Ativo, Síncrono e Funcional.
