---
spec_id: SPEC-935-R381
title: Integração do gate de rigor de manuscrito (R369) ao pipeline científico principal
component: marceloclaro/orchestrator.py::scientific_discovery_pipeline
status: verified
test_file: tests/test_r381_manuscript_rigor_gate_integration.py
---

# SPEC-935-R381 — Integração do Gate de Rigor de Manuscrito

**Data:** 2026-08-02
**Motivação:** auditoria de unificação pedida pelo usuário ("unifique o
ecossistema em um sistema único e funcional, rigoroso na pesquisa"). Ao
investigar se as camadas construídas em R363–R373 estão de fato conectadas
ao orquestrador principal (não apenas testadas isoladamente), encontrei:

- **Já unificado (confirmado, não precisa de ação):** a Camada Epistêmica de
  Roteamento (R363) já está viva no caminho real — `transformer/attention.py
  ::AttentionRouter` importa e usa `transformer.semantic_matcher.
  semantic_matcher` (que embute `SkillHandbook.match()` com peso epistêmico)
  na cabeça de confiança do roteamento por atenção. Nenhuma mudança
  necessária.
- **Gap real de unificação:** `marceloclaro.orchestrator.py::
  scientific_discovery_pipeline()` — o pipeline principal que executa
  EvoSci→DeepResearch→PeerReview→Revision→Composer — **nunca chama**
  `reasoning.production_scaffolds.audit_scientific_manuscript()` (R369),
  apesar do R105 (`compose_paper`) já produzir `sections: Dict[str, str]`
  com texto real — exatamente o formato que o auditor espera. O gate de
  rigor científico existe, é testado, mas é uma função de biblioteca que
  ninguém no caminho principal chama.

**Por que não os gates R370–R373 também:** esses exigem dados que o
pipeline genérico não produz por padrão (grupos de amostra brutos, pares
r/n de correlação, protocolo pré-registrado explícito) — forçá-los
significaria inventar dados sintéticos só para preencher a assinatura, o
que violaria a própria disciplina anti-fabricação do projeto. Ficam como
capacidades **opt-in** para quem tiver dados reais (ver Seção 4).

## 1. Novo estágio `r381` — Auditoria de Rigor do Manuscrito

Após o estágio R105 (Paper Composer) em `scientific_discovery_pipeline()`:

1. Se `r105["sections"]` for um dict não vazio: chama
   `audit_scientific_manuscript(r105["sections"])`.
2. Se `r105` falhou (`status == "error"`) ou `sections` vazio/ausente:
   **não fabrica um audit vazio** — registra
   `stages["r381"] = {"status": "skipped", "reason": "..."}`
   explicitamente, sem levantar exceção (o auditor exige mapeamento não
   vazio — `ContractError` seria incorreto aqui, pois a ausência de seções
   é um estado válido de pipeline, não um erro de chamada).
3. Resultado do audit (quando executado) entra em `stages["r381"]`
   integralmente (findings, moves_presentes, human_gate, disclaimer).
4. Confiança calibrada via `mci.confidence_calibrator.calibrate_confidence`
   (mesmo padrão dos demais estágios): `succeeded = not high_severity`
   (nenhum achado `severity="high"`).
5. Traço metacognitivo (`_trace`) registrado como os demais estágios.
6. **Não bloqueia o pipeline** (diferente do gate R103 obrigatório): o resultado já
   foi composto; descartá-lo pós-hoc seria pior que reportar o achado.
   Isso é consistente com R104d/R105, que também não bloqueiam.
7. Campo de conveniência no retorno de nível superior:
   `result["manuscript_rigor_gate"]` — resumo
   `{"human_gate", "high_severity_findings", "moves_ausentes"}` para quem
   não quiser navegar `stages["r381"]["findings"]`.

## 2. Contrato de saída (adição, não quebra)

Todos os campos hoje retornados por `scientific_discovery_pipeline`
permanecem inalterados. Adiciona-se apenas:
- `stages["r381"]` (novo).
- `calibrated_confidences["r381"]` (novo, mesmo padrão dos demais).
- `result["manuscript_rigor_gate"]` (novo, resumo de conveniência,
  presente apenas quando `status == "completed"`).

## 3. Critérios de aceitação

1. Pipeline real (não mockado) com `max_rounds=1`: quando completa com
   sucesso, `stages["r381"]` existe e tem a forma de
   `audit_scientific_manuscript` (schema_version, moves_presentes,
   findings, human_gate, disclaimer).
2. `audit_scientific_manuscript` é chamado com exatamente
   `r105["sections"]` (verificado via spy/monkeypatch — não fabricação
   de conteúdo alternativo).
3. R105 com `sections` vazio ou pipeline com `status="blocked"`/`"error"`
   antes de R105: `stages["r381"] = {"status": "skipped", ...}`,
   sem exceção.
4. `result["manuscript_rigor_gate"]` presente e coerente com
   `stages["r381"]["human_gate"]` quando o pipeline completa.
5. Pipeline nunca é bloqueado pelo estágio `r381` (`status` permanece `"completed"`
   mesmo com achados `high`).
6. Traço metacognitivo do estágio `r381` presente em
   `metacognitive_report` quando o audit roda.
7. Zero regressão em `test_r108_marceloclaro_scientific_fusion.py` e no
   restante da suíte.

## 4. Fora de escopo (documentado, não fabricado)

Gates R370 (estatística), R371 (triangulação multidisciplinar) e R372
(pré-registro) **não** são acionados automaticamente pelo pipeline
genérico — exigem dados que só o CHAMADOR possui (amostras brutas, pares
r/n, protocolo). Ficam expostos como métodos de `OrchestratorReviewer`
(já implementados em R370–R373) para uso explícito por quem tiver esses
dados reais. Candidato a exposição como parâmetros opcionais de
`scientific_discovery_pipeline` em ciclo futuro (R382+), se houver caso de
uso concreto.
