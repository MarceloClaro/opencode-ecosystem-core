---
spec_id: SPEC-935-R371
title: Triangulação Multidisciplinar — gate de convergência entre domínios independentes
component: mci/multidisciplinary_triangulation.py + agentic_science_v2/review_agent.py
status: verified
test_file: tests/test_r371_multidisciplinary_triangulation.py
---

# SPEC-935-R371 — Triangulação Multidisciplinar

**Data:** 2026-08-02
**Motivação:** o R370 deu convergência estatística (mesma alegação vista por
dois testes independentes). Este ciclo dá a segunda metade do pedido
original: "cruzar informações relevantes e multidisciplinares" — uma
alegação só é tratada como bem sustentada quando **≥2 domínios/disciplinas
independentes** trazem evidência concordante, e **nenhum** domínio a
contesta abertamente.

**Design deliberadamente aditivo:** não modifica `EvidenceGraph`
(`agentic_science_v2/evidence_graph.py`, R102) nem `DataKnowledgeHub`
(`skills/tooling/data_knowledge_hub/`, R52/R55) — ambos são fundacionais e
usados por outras frentes. O contrato de entrada é uma lista simples de
itens de evidência (`{source, domain, stance}`) que qualquer chamador
(EvidenceGraph, DataKnowledgeHub, ou entrada manual) pode popular.

**Limite epistêmico:** triangulação não decide verdade — decide se a
alegação tem corroboração **estruturalmente independente**. Discordância
real entre disciplinas nunca é resolvida por maioria de votos: um único
domínio contestando bloqueia a triangulação (não é "outvoted"), porque
esconder controvérsia real seria o overclaim mais perigoso possível aqui.

## 1. Contrato de entrada

`evidence_item`: `{"source": str, "domain": str, "stance": "supports" |
"contradicts" | "neutral"}`. `domain` é texto livre (não um enum fechado —
disciplinas variam por alegação); sugestões documentadas no docstring
seguem os 5 domínios já existentes no `DataKnowledgeHub`
(`financeiro`, `oficial`, `conhecimento`, `dataset`, `academico`) mais
domínios de disciplina acadêmica quando vier de literatura
(`medicina`, `direito`, `ciencia_dados`, ...). `source` não pode ser vazio;
`stance` restrito às 3 opções; validação fail-closed (`ContractError`).

## 2. `multidisciplinary_triangulation(claim_text, evidence_items) -> dict`

1. Agrupa `evidence_items` por `domain` (normalizado: casefold + strip).
2. Para cada domínio, calcula o veredito do domínio:
   - tem `supports` e nenhum `contradicts` → `"supports"`;
   - tem `contradicts` e nenhum `supports` → `"contradicts"`;
   - tem ambos → `"mixed"`;
   - só `neutral` → `"neutral"`.
3. `contesting_domains` = domínios com veredito `"contradicts"` ou `"mixed"`.
4. `supporting_domains` = domínios com veredito `"supports"`.
5. `triangulated = True` **se e somente se**:
   `len(contesting_domains) == 0` **e** `len(supporting_domains) >= 2`.
6. Achados (mesma forma de `requires_human_review` usada em R364-R366):
   - `contesting_domains` não vazio → achado `CONTESTED_MULTIDISCIPLINARY`
     (severity `high`), um por domínio contestador, com o domínio nomeado.
   - `contesting_domains` vazio e `supporting_domains` tem 0 ou 1 domínio →
     achado `SINGLE_DOMAIN_EVIDENCE` (severity `medium`).
7. Retorna envelope: `schema_version`, `claim_text` (truncado a 200 chars),
   `triangulated`, `supporting_domains`, `contesting_domains`,
   `domain_verdicts` (mapa domínio→veredito), `findings[]`, `human_gate`
   (`required` se houver `high`, senão `recommended`), `disclaimer`.
8. Entrada vazia (`evidence_items == []`) → `triangulated=False`,
   `analysis_status="insufficient_context"`, sem achados fabricados.

## 3. Integração no R103

`OrchestratorReviewer.verify_multidisciplinary_claim(claim_id, evidence_items,
ledger) -> dict` — mesmo padrão de `verify_statistical_claim` (R370):
roda `multidisciplinary_triangulation`, e só chama `ledger.verify_claim(...)`
quando `triangulated=True`; caso contrário adiciona/mantém na
`verification_agenda` com nota dos domínios que discordam ou da
insuficiência de domínios.

## 4. Critérios de aceitação

1. 2 domínios concordantes, nenhum contestando → `triangulated=True`.
2. 1 domínio único (mesmo com múltiplas fontes dentro dele) →
   `triangulated=False`, achado `SINGLE_DOMAIN_EVIDENCE`.
3. 3 domínios concordantes + 1 contestando → `triangulated=False` (a
   controvérsia bloqueia, não é resolvida por maioria) com achado
   `CONTESTED_MULTIDISCIPLINARY` nomeando o domínio.
4. `stance` inválido ou `source` vazio → `ContractError`.
5. Lista vazia → `insufficient_context`, sem achados.
6. Normalização de domínio (`"Medicina"` e `"medicina "` contam como o
   mesmo domínio).
7. `verify_multidisciplinary_claim`: claim só verificada no ledger quando
   `triangulated=True`.
8. Determinismo (função pura, sem aleatoriedade — trivial mas testado).
9. Suíte do ciclo verde; zero regressão em R102/R103/R370.
