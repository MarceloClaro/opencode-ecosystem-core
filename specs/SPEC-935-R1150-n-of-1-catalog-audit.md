# SPEC-935-R1150 — N-of-1 unificado e auditoria de catálogo

**Status:** implementação local; sem hardware
**Data:** 2026-11-10
**Depende de:** R1132, R1148, R1149

## 1. Objetivo

Fechar duas lacunas de consolidação:

1. eliminar a duplicação entre `core_cognition.n_of_1` (validador) e
   `mci.n_of_1` (runner/SCED);
2. criar auditoria executável de duplicidade para 374 agentes e 35 MCPs,
   comparando catálogo, `opencode.json`, prompts, comandos e descrições.

## 2. Requisitos

- **R1.** `core_cognition.n_of_1` é a fonte única: validador de protocolo +
  runner com randomização, lock, adesão, eventos adversos, NAP, PEM, Tau-U,
  autocorrelação e permutação.
- **R2.** `mci.n_of_1` é shim de compatibilidade: reexporta as funções
  canônicas; não contém segunda implementação.
- **R3.** `integrations/catalog_audit.py` audita:
  - ids canônicos (nome do arquivo), ids declarados, nomes e descrições;
  - prompts repetidos em agentes diferentes;
  - comandos/URLs de MCP repetidos;
  - drift catálogo ↔ `opencode.json`;
  - spec/test ausentes.
- **R4.** O auditor não remove nem funde nada; emite relatório com SHA-256.
- **R5.** `agent_id` legado divergente do nome do arquivo é reportado como
  `metadata_id_mismatch`, sem alterar o baseline de ciclo de vida.

## 3. Critérios de aceitação

- `mci.n_of_1.run_n_of_1 is core_cognition.n_of_1.run_n_of_1`;
- validador ABAB e runner SCED coexistem no mesmo módulo;
- fixture de catálogo detecta id declarado repetido, prompt repetido,
  comando/URL de MCP repetido e descrição quase idêntica;
- catálogo real: 374 arquivos/ids, 374 agentes, 35 MCPs;
- duplicatas de id/nome/prompt/MCP: 0;
- drift: 0; artefatos ausentes: 0;
- divergências de `agent_id` não resolvidas: 0; 2 legados preservados por
  baseline com hash conferido;
- quase-duplicatas não revisadas: 0; 1 par revisado com justificativa;
- `opencode_cli --check` continua OK.

## 4. Limites

Auditoria textual/estrutural; não prova equivalência funcional, qualidade ou
trust. O par `gjq-backend-guoji-04` × `-07` é quase idêntico por descrição, mas
representa backends distintos; não deve ser fundido sem revisão. A migração dos
dois `agent_id` legados exige atualização explícita de
`agents/lifecycle_baseline.json`.
