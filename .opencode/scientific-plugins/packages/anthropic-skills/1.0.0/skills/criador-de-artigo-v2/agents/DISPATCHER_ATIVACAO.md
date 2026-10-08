# DISPATCHER DE ATIVAÇÃO MULTIAGENTE v3.0
# Multi-Agent Scientific Writing Operating System (MASWOS)
# 43 Agentes Especializados (A0–A43) · 8 Fases · Pipeline 100% Acoplado

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                   A0 · EDITOR-CHEFE PhD (GERENTE)                   │
│           Autoridade máxima · Abre e fecha TODA fase                │
│    Decisão: APROVAR | APROVAR COM RESSALVAS | REPROVAR E DEVOLVER  │
└────────────┬────────────────────────────────────────────┬───────────┘
             │                                            │
     ┌───────▼───────┐                          ┌─────────▼─────────┐
     │ FASE 1        │──→ FASE 2 ──→ FASE 3 ──→ │ FASE 4/4A/4B      │
     │ Diagnóstico   │   Evidências  Estrutura   │ Produção          │
     └───────────────┘                           └─────────┬─────────┘
                                                           │
     ┌───────────────┐    ┌───────────────┐     ┌──────────▼────────┐
     │ FASE 7        │←── │ FASE 6        │←──  │ FASE 5            │
     │ Slides/Defesa │    │ Peer Review   │     │ Integração Final  │
     └───────────────┘    └───────────────┘     └───────────────────┘
```

---

## Regra Central

1. **A0 ABRE toda fase** emitindo `decisao_editor_fase_N.md`.
2. **A0 FECHA toda fase** com gate de saída verificado.
3. **Nenhum agente inicia** sem que o anterior tenha completado seu handoff.
4. **Paralelização** só é permitida dentro do mesmo bloco, nunca entre fases.
5. **Escalamento imediato** ao A0 em caso de conflito, lacuna ou incoerência.

---

## ═══════════════════════════════════════════════════════════════
## FASE 1 — DIAGNÓSTICO E DEFINIÇÃO DO ESTUDO
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Congelar problema, lacunas, objetivos, hipóteses e fronteira.

### Pipeline (sequencial estrito)
```
A0 (abre) → A1 → A40 → A39 → A14 → A0 (fecha)
```

| Passo | Agente | Ação | Entrada | Saída |
|---|---|---|---|---|
| 1.1 | A0 Editor-Chefe | Abrir fase, definir alvo e escopo | Prompt do usuário | `decisao_editor_fase_1.md` |
| 1.2 | A1 Diagnóstico | Problema, lacuna, gap, hipóteses, objetivos | decisao_editor | `diagnostico_fundacao.md`, `plano_paginas.md` |
| 1.3 | A40 Marcos Teóricos | Classificar corrente teórica, tipo de pesquisa, método de interpretação | diagnostico_fundacao | `marco_teorico_classificado.md` |
| 1.4 | A39 Metodologia Multi-Paradigma | Classificar paradigma (quanti/quali/misto/fenomenológico/DSR etc.), configurar critérios de rigor | diagnostico + marco_teorico | `classificacao_paradigmatica.md` |
| 1.5 | A14 Consistência | Validação cruzada: problema ↔ hipóteses ↔ marco ↔ paradigma | todos os anteriores | OK ou DEVOLVER |
| 1.6 | A0 Editor-Chefe | Gate: aprovar ou devolver fase 1 | todos os artefatos | Aprovação formal |

**Gate de saída (6 artefatos obrigatórios):**
- `diagnostico_fundacao.md`
- `plano_paginas.md`
- `marco_teorico_classificado.md`
- `classificacao_paradigmatica.md`
- `decisao_editor_fase_1.md`
- Aprovação A0

**BLOCK:** Não avançar sem paradigma classificado E marco teórico definido.

---

## ═══════════════════════════════════════════════════════════════
## FASE 2 — BUSCA, TRIAGEM E EVIDÊNCIAS
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Produzir lastro bibliográfico auditável e mapa de citações.

### Pipeline
```
A0 (abre) → A2 → A3 → A12 → A33 → A14 → A0 (fecha)
```

| Passo | Agente | Ação | Entrada | Saída |
|---|---|---|---|---|
| 2.1 | A0 | Abrir fase 2 | Fase 1 aprovada | `decisao_editor_fase_2.md` |
| 2.2 | A2 Busca/Curadoria | Busca sistemática em bases | diagnostico + marco | `log_busca.md`, `triagem_fontes.md` |
| 2.3 | A3 Evidências | Mapa de citações com justificativa e DOI | triagem | `matriz_evidencias.md`, `mapa_citacoes.md` |
| 2.4 | A12 Auditoria ABNT | Conferir norma bibliográfica (ABNT/APA/Vancouver) | mapa_citacoes | `relatorio_abnt.md` |
| 2.5 | A33 Multi-Norma | Converter para norma do periódico-alvo (se ≠ ABNT) | mapa_citacoes | `referencias_formatadas.md` |
| 2.6 | A14 Consistência | Citações ↔ afirmações do texto | todos | OK ou DEVOLVER |
| 2.7 | A0 | Gate | todos | Aprovação |

**Paralelização permitida:** A2 e A3 podem sobrepor parcialmente.

**Gate de saída:** `log_busca.md` + `mapa_citacoes.md` + `matriz_evidencias.md` + norma OK

---

## ═══════════════════════════════════════════════════════════════
## FASE 3 — ESTRUTURA ARGUMENTATIVA
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Congelar espinha argumentativa e papel de cada capítulo.

### Pipeline
```
A0 (abre) → A4 → A1 (revisão cruzada) → A14 → A0 (fecha)
```

| Passo | Agente | Ação |
|---|---|---|
| 3.1 | A0 | Abrir fase 3 |
| 3.2 | A4 Estrutura | Esqueleto argumentativo, fluxo de capítulos |
| 3.3 | A1 Diagnóstico | Revisão cruzada: estrutura ↔ lacunas ↔ hipóteses |
| 3.4 | A14 Consistência | Validar coerência ponta a ponta |
| 3.5 | A0 | Gate: `estrutura_artigo.md` aprovada |

**Gate de saída:** `estrutura_artigo.md` + validação cruzada + aprovação A0

---

## ═══════════════════════════════════════════════════════════════
## FASE 4 — PRODUÇÃO DOS CAPÍTULOS CENTRAIS
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Redigir todos os capítulos com rigor analítico, código e visualização.

### BLOCO 4.1 — TEÓRICO
```
A0 (abre) → A5 → A3 → A14 → A0 (valida)
```
| Agente | Ação |
|---|---|
| A5 Revisão de Literatura | Redigir referencial teórico usando marco do A40 |
| A3 Evidências | Inserir citações auditáveis |
| A14 Consistência | Validar coerência interna |

### BLOCO 4.2 — METODOLÓGICO
```
A6 → A7 (se quanti) → A8 → A41 (se espacial) → A42 (audita código) → A0 (valida)
```
| Agente | Condição | Ação |
|---|---|---|
| A6 Metodologia | Sempre | Redigir seção metodológica conforme A39/A40 |
| A7 Estatística | Se quantitativo/misto | Análise estatística |
| A8 Visualização | Sempre | Figuras, gráficos, tabelas |
| A41 GIS/Cartografia | Se dimensão espacial | Mapas, análise espacial, cartas |
| A42 Desenvolvedor | Sempre (se houver código) | Auditar e otimizar scripts |

### BLOCO 4.3 — NÚCLEO ANALÍTICO REPRODUTÍVEL (Fase 4A)

**ATIVAR quando houver dados, código, modelos ou análise computacional.**

```
A35 (PRIMEIRO) → A43 (se sat/bio) → A17 → A18 → A32 → A19 →
A20/A21 → [A22|A23|A24|A25|A26|A27] → A28 → A42 (audita) → A0
```

| Passo | Agente | Condição | Ação |
|---|---|---|---|
| 4A.1 | **A35 Coleta Real** | **OBRIGATÓRIO PRIMEIRO** | Coleta dados reais via 151+ APIs, downloads, scraping; valida DOIs |
| 4A.2 | A43 Satélite/Bio | Se satélite, DNA, RNA-Seq, microarray | Coleta especializada GEE, NCBI GEO, deep web acadêmica |
| 4A.3 | A17 Framework | Sempre | Ambiente reprodutível (seeds, versões) |
| 4A.4 | A18 Engenharia | Sempre | Dataset split, proveniência, hash SHA-256 |
| 4A.5 | A32 Ética | Sempre | FAIR, LGPD/GDPR, licenças, comitê de ética |
| 4A.6 | A19 Auditoria | Sempre | Documentação técnica do pipeline |
| 4A.7 | A20/A21 Estatística/Matemática | Conforme paradigma | Inferência ou formalização |
| 4A.8 | Domínio especializado | Conforme área | A22 (ML) / A23 (Bio) / A24 (Quimio) / A25 (Social) / A26 (CV) / A27 (Quântica) |
| 4A.9 | A28 Benchmark | Sempre | Baseline, ablação, robustez, comparação justa |
| 4A.10 | **A42 Desenvolvedor** | **OBRIGATÓRIO ÚLTIMO** | Audita TODO o código: seeds, testes, docs, linting, requirements |
| 4A.11 | A0 Editor-Chefe | Gate | Aprova pipeline completo |

**Roteamento por tipo de estudo:**

| Padrão do estudo | Agentes obrigatórios |
|---|---|
| Regressão, painel, causal (DiD, IV, RDD) | A35 + A17 + A18 + A20 + A28 + A42 |
| Fórmula central, simulação, ODE/PDE | A35 + A17 + A19 + A21 + A28 + A42 |
| ML tabular, NLP, ranking, clustering | A35 + A17 + A18 + A20 + A22 + A28 + A42 |
| Visão computacional / multimodal | A35 + A17 + A18 + A22 + A26 + A28 + A42 |
| Bioinformática / ômicas | A35 + A43 + A17 + A18 + A20 + A23 + A28 + A42 |
| Quimioinformática / molecular | A35 + A17 + A18 + A21 + A24 + A28 + A42 |
| Survey, psicometria, NLP social | A35 + A17 + A18 + A20 + A25 + A28 + A42 |
| Computação quântica | A35 + A17 + A19 + A21 + A27 + A28 + A42 |
| Sensoriamento remoto / GIS | A35 + A43 + A41 + A17 + A18 + A28 + A42 |
| Pesquisa qualitativa pura | A35 (valida refs) + A39 + A40 + A42 (se houver IRaMuTeQ/NVivo) |
| Pesquisa mista (Mixed Methods) | A35 + A39 + A40 + A7 + A42 |
| Revisão Sistemática / Metanálise | A35 (valida DOIs) + A2 + A3 + A7 + A28 + A42 |

**Gate de saída 4A (13 artefatos):**
- `coleta_dados_reais.py` · `datasets/raw/` · `referencias_validadas_api.md`
- `manifesto_reprodutibilidade.md` · `ambiente_execucao.md` · `catalogo_datasets.md`
- `codebook_dados.md` · `registro_experimentos.md` · `relatorio_benchmark_robustez.md`
- `relatorio_auditoria_codigo.md` · `requirements.txt` · `README_CODIGO.md` · `tests/`

### BLOCO 4.4 — EMPÍRICO
```
A9 → A7 → A8 → A40 (interpreta conforme marco) → A14 → A0
```
| Agente | Ação |
|---|---|
| A9 Resultados | Redigir seção de resultados |
| A7 Estatística | Tabelas de resultados, p-valores, tamanho de efeito |
| A8 Visualização | Figuras de evidência gráfica |
| A40 Interpretação | Verificar que resultados são interpretados conforme marco teórico |
| A14 Consistência | Resultados ↔ hipóteses ↔ método |

### BLOCO 4.5 — INTERPRETATIVO
```
A10 → A40 (valida lente) → A14 → A13 (pré-QA) → A0
```
| Agente | Ação |
|---|---|
| A10 Discussão | Redigir discussão com diálogo teórico |
| A40 Marcos Teóricos | Assegurar interpretação conforme corrente |
| A14 Consistência | Discussão ↔ resultados ↔ literatura |
| A13 QA Qualis | Pré-auditoria de qualidade |

### BLOCO 4.6 — FECHAMENTO
```
A11 → A14 → A0
```
| Agente | Ação |
|---|---|
| A11 Conclusão | Redigir conclusão e contribuições |
| A14 Consistência | Conclusão ↔ problema ↔ resultados |

### BLOCO 4.7 — RESUMO E ABSTRACT (FASE 4B)

**Ativar SOMENTE depois do corpo completo e estabilizado.**

```
A15 → A14 → A0
```
| Agente | Ação |
|---|---|
| A15 Resumo/Abstract | Redigir resumo, abstract e palavras-chave |
| A14 Consistência | Abstract ↔ manuscrito integral |

---

## ═══════════════════════════════════════════════════════════════
## FASE 5 — INTEGRAÇÃO EDITORIAL E PACOTE FINAL
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Montar documento ÚNICO, exportar em todos os formatos e gerar pacote de submissão.

### Pipeline
```
A0 (abre) → A12/A33 → A8 → A16 → A38 → A36 → A30 → A34 → A42 → A13 → A0 (fecha)
```

| Passo | Agente | Ação | Saída |
|---|---|---|---|
| 5.1 | A12/A33 Multi-Norma | Formatar referências conforme periódico-alvo | `referencias_formatadas.md` |
| 5.2 | A8 Visualização | Polir figuras finais (300+ DPI, SVG) | `figuras/` |
| 5.3 | A16 Integração | Consolidar seções em sequência editorial | `artigo_completo_consolidado.md` |
| 5.4 | **A38 Montagem Final** | **Montar documento ÚNICO** (capa → apêndice), deduplicar referências, gerar pacote | `artigo_completo_final.md`, `pacote_submissao/`, `README_SUBMISSAO.md` |
| 5.5 | A36 Exportação | Gerar LaTeX (.tex + .bib), PDF compilado, DOCX | `manuscript.tex`, `.pdf`, `.docx` |
| 5.6 | A30 Tradução | Proofreading nativo (se inglês/internacional) | `manuscript_english.tex` |
| 5.7 | A34 Similaridade | Turnitin check, COI, Funding | `declaracao_coi_funding.md` |
| 5.8 | A42 Desenvolvedor | Auditar scripts finais no pacote suplementar | `relatorio_auditoria_final.md` |
| 5.9 | A13 QA Qualis | Auditoria completa Qualis A1 | `auditoria_final_qualis.md` |
| 5.10 | A0 Editor-Chefe | Gate: pacote completo aprovado | Aprovação |

**Gate de saída (14 artefatos):**
- `artigo_completo_final.md` · `pacote_submissao/` · `README_SUBMISSAO.md`
- `manuscript.tex` + `references.bib` · `manuscript.pdf` · `manuscript.docx`
- `manifesto_pacote_final.md` · `declaracao_coi_funding_icmje.md`
- `relatorio_analise_lexica_similaridade.md` · `auditoria_final_qualis.md`
- `relatorio_auditoria_final.md` · Figuras 300+ DPI separadas
- Cover Letter (rascunho) · Data Availability Statement

---

## ═══════════════════════════════════════════════════════════════
## FASE 6 — LIBERAÇÃO FINAL E EMULAÇÃO OPOSITORA (TOP-TIER)
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Submeter o manuscrito a 6 revisores implacáveis antes da banca real.

### Pipeline
```
A0 (abre) → A13 → A14 → A29 → A31 → A0 (decisão final)
```

| Passo | Agente | Ação |
|---|---|---|
| 6.1 | A13 QA Qualis A1 | Auditoria final completa |
| 6.2 | A14 Consistência | Varredura ponta a ponta |
| 6.3 | A29 Conformidade Internacional | STROBE/CONSORT/PRISMA/ARRIVE (se aplicável) |
| 6.4 | A31 Blind Peer Review Emulado | Simula 3-6 Reviewers implacáveis, stress test, Cover Letter final |
| 6.5 | A0 Editor-Chefe | **DECISÃO FINAL**: publicar ou ciclar |

**Único resultado aceitável:**
- Cover Letter gerada e aprovada
- Checklists de conformidade 100% green
- Decisão formal A0: `PUBLICAR` ou `CICLAR PARA FASE N`

---

## ═══════════════════════════════════════════════════════════════
## FASE 7 — APRESENTAÇÃO DE SLIDES PARA BANCA / DEFESA
## ═══════════════════════════════════════════════════════════════

**Objetivo:** Produzir apresentação acadêmica completa.

### Pipeline
```
A0 (abre) → A37 → A8 → A42 → A0 (fecha)
```

| Passo | Agente | Ação | Saída |
|---|---|---|---|
| 7.1 | A37 Slides | Gerar 20-30 slides (Beamer + PPTX) | `slides.tex`, `slides.pdf`, `slides.pptx` |
| 7.2 | A8 Visualização | Polir figuras dos slides | Figuras adaptadas |
| 7.3 | A42 Desenvolvedor | Verificar código de demonstração nos slides | OK |
| 7.4 | A0 Editor-Chefe | Aprovar apresentação | `roteiro_apresentacao.md` |

**Gate de saída:** `slides.pdf` + `slides.pptx` + `roteiro_apresentacao.md` + Aprovação A0

---

## ═══════════════════════════════════════════════════════════════
## REGRAS DE ACOPLAMENTO UNIVERSAL
## ═══════════════════════════════════════════════════════════════

### Handoff Obrigatório (entre TODOS os agentes)
Todo handoff usa `TEMPLATE_HANDOFF.md` e DEVE conter:
1. Status: `APROVADO` | `RESSALVAS` | `REPROVADO`
2. Artefatos entregues (lista com nomes de arquivo)
3. Riscos abertos (se houver)
4. Próximo agente recomendado
5. O que o próximo agente PODE e NÃO PODE alterar

### Paralelização Permitida (dentro da mesma fase)
- A2 ∥ A3 (busca e evidências)
- A6 ∥ A7 (metodologia e estatística)
- A9 ∥ A8 (resultados e visualização)
- A17 ∥ A18 (framework e engenharia de dados)
- A20 ∥ A21 (inferência e formalização, se mesmo estimando)

### Paralelização PROIBIDA (entre fases ou dependências)
- Conclusão antes de Discussão estabilizada
- Resumo antes de manuscrito completo
- Integração editorial antes de ABNT/norma OK
- Benchmark antes de registro de experimentos
- A42 (auditoria) antes de código existir
- Aprovação final antes de QA Qualis A1

### Gatilhos de Escalamento Imediato ao A0
Escalar ao Gerente SEM resolver localmente quando:
- Disputa sobre problema central ou hipóteses
- Discrepância código ↔ fórmula ↔ resultado reportado
- Dataset sem origem, licença ou split confiável
- Resultado sem reprodução mínima ou sem baseline
- Leakage, shift ou viés que comprometa claim central
- Conclusão desalinhada dos resultados
- Alteração de escopo afetando mais de uma fase

---

## ═══════════════════════════════════════════════════════════════
## MAPA COMPLETO: 43 AGENTES × 8 FASES
## ═══════════════════════════════════════════════════════════════

| Agente | Nome | Fases de Atuação |
|---|---|---|
| A0 | Editor-Chefe PhD | **TODAS** (abre e fecha) |
| A1 | Diagnóstico e Escopo | 1, 3 |
| A2 | Busca e Curadoria | 2 |
| A3 | Evidências e Citações | 2, 4.1 |
| A4 | Estrutura Argumentativa | 3 |
| A5 | Revisão de Literatura | 4.1 |
| A6 | Metodologia | 4.2 |
| A7 | Estatística | 4.2, 4.4 |
| A8 | Visualização Gráfica | 4.2, 4.4, 5, 7 |
| A9 | Resultados | 4.4 |
| A10 | Discussão | 4.5 |
| A11 | Conclusão | 4.6 |
| A12 | Auditoria ABNT | 2, 5 |
| A13 | QA Qualis A1 | 4.5, 5, 6 |
| A14 | Consistência Interna | 1, 2, 3, 4.1–4.7, 6 |
| A15 | Resumo/Abstract | 4.7 |
| A16 | Integração Editorial | 5 |
| A17 | Framework Reprodutível | 4A |
| A18 | Engenharia de Dados | 4A |
| A19 | Auditoria Código/Docs Técnica | 4A |
| A20 | Estatística Avançada | 4A |
| A21 | Matemática Aplicada | 4A |
| A22 | ML/DL/Data Mining | 4A |
| A23 | Bioinformática/Ômicas | 4A |
| A24 | Quimioinformática | 4A |
| A25 | Ciências Sociais/NLP | 4A |
| A26 | Visão Computacional | 4A |
| A27 | Computação Quântica | 4A |
| A28 | Benchmark/Ablação | 4A |
| A29 | Conformidade Internacional | 6 |
| A30 | Tradução Nativa | 5 |
| A31 | Blind Peer Review Emulado | 6 |
| A32 | Ética e Open Science | 4A |
| A33 | Multi-Norma | 2, 5 |
| A34 | Conflitos/Similaridade | 5 |
| A35 | Coleta de Dados Reais | **4A (PRIMEIRO)** |
| A36 | Exportação LaTeX/PDF | 5 |
| A37 | Slides para Banca | 7 |
| A38 | Montagem e Entrega Final | 5 |
| A39 | Metodologia Multi-Paradigma | 1, 4.2 |
| A40 | Marcos Teóricos/Interpretação | 1, 4.1, 4.4, 4.5 |
| A41 | GIS/Geoprocessamento | 4.2, 4A |
| A42 | Desenvolvedor/Cientista Computação | 4A, 5, 7 |
| A43 | Satélite/Bioinformática/Ômicas | 4A |

---

## Regra Final do Dispatcher

> **Ativação mínima, acoplamento máximo, rigor absoluto.**
>
> Ative o **mínimo conjunto de agentes** necessário para o tipo de estudo,
> mas NUNCA pule um agente de validação (A14, A13, A42, A0).
>
> O sistema é um loop fechado: a saída de um agente é a entrada do próximo.
> Não há etapas soltas. Não há artefatos órfãos.
> Cada fase produz, cada fase valida, cada fase fecha.
