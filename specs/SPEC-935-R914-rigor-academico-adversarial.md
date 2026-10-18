---
spec_id: SPEC-935-R914
title: Rigor acadêmico adversarial e banca persistente
component: academic.adversarial_research
status: implemented
test_file: tests/test_r914_academic_rigor.py
---

# R914 — Rigor acadêmico adversarial

Derivação autorizada de SPEC-OCRE-ACADEMIC-RIGOR v1.0, fornecida pelo usuário,
SHA256 4639ff390b630fb42548f5ce83da59fab44bdc5cd2cb3ae634c03a0a2d3ae854.
Preservar a fonte em docs/academic-rigor/SPEC-OCRE-ACADEMIC-RIGOR-v1-user.md.

## Critérios de aceitação executáveis

- `R914-AC1` — Casos científicos positivos/negativos preservam evidências, contradições e bloqueios proporcionais.
- `R914-AC2` — Perfis validados executam contratos pelo primário, com A2A/MetaBus e sem autoelevação de confiança.
- `R914-AC3` — Banca exige respostas efetivas, rubrica documentada e controle de versão do artefato e da rubrica.
- `R914-AC4` — CLI/MCP compartilham a fachada, e nenhuma saída local representa aprovação científica externa.

## Escopo e critérios de aceitação

1. Reutilizar MarceloClaro, Blackboard, MetaBus, SpecVerifier e RigorousBoard.
   Nenhum segundo orquestrador. Perfis passam pela API de ciclo de vida R894.
   Piloto de oito especialistas antes da expansão a 34, com permissões de leitura.
2. Contratos ResearchClaim, AdversarialObjection e ResearchReview; oito famílias
   de questões e roteamento por desenho. Só alegações explicitamente submetidas
   são avaliadas. Fontes têm hash, localizador e escopo da inspeção.
3. Integridade física não promove alegação ou referência a verdade comprovada.
   Alegações críticas sem evidência bloqueiam liberação científica; G6 exige
   revisão humana. Não há equivalência medida a banca ou calibração externa.
4. Fluxo: intake → ledger → especialistas → exame → RigorousBoard legado
   (heurístico, não vinculante) → remediação → SpecVerifier → humano.
   Falhas, cancelamento, limite de passos e truncamento produzem relatório parcial.
5. Banco persistente de banca: uma pergunta por vez, resposta efetivamente
   recebida antes da réplica. Turnos idempotentes, hashes e bloqueio de versão
   alterada. Rubrica só com documento/hash/localizador; notas declaradas exigem
   resposta observada, justificativa e avaliador. Não autenticar instituição.
6. CLI e MCP usam a mesma fachada primária. Produção acadêmica existente anexa
   preflight e mantém aceite computacional separado de aprovação científica.
7. Pelo menos os 16 testes especificados, com casos positivos/negativos sobre
   originalidade, categorias, corpus, causalidade, ética, métricas e banca.
   Histórico RED real, GREEN, regressão e diagnóstico. Não fabricar RED passado.
8. Registro evolutivo sem nota ou auditoria externa fictícia. Fase de avaliação
   humana e métricas de falsos positivos/negativos permanecem pendentes até dados.

## Não objetivos

Não produzir parecer ético/jurídico, comprovar novidade por ausência de busca,
consultar automaticamente URLs privadas ou transformar respostas sintéticas em
desempenho de candidato. Regras locais e perfis de especialistas têm escopos
distintos; registrar perfil ou atribuição não equivale a executar inferência.
