---
name: lean-tese-provas-auditaveis
description: Estrutura tese com provas Lean auditáveis por capítulo; exige tabela enunciado-código-hash-status e proveniência Mathlib. Use para tese, dissertação, artigo com apêndice formal e defesa com trilha reproduzível.
---

# Lean Tese com Provas Auditáveis (SPEC-935-R747)

## Quando acionar

Quando houver tese, dissertação, TCC ou artigo que alegue prova formal.

## Estrutura de capítulo auditável

1. Enunciado em PT-BR com premissas numeradas.
2. Código `.lean` completo via `lean_export` + SHA-256.
3. Veredito `lean_verify` + `provenance.has_compiler`.
4. Tabela de reconciliação: cada premissa PT-BR ↔ linha Lean correspondente.
5. Riscos e limites: o que não foi provado.

## Checklist de proveniência Mathlib

- [ ] imports listados (`Mathlib.Tactic`, demais usados);
- [ ] versão Lean/lake registrada (ou `ausente → syntax_verified`);
- [ ] cada lema externo com nome completo;
- [ ] nenhum `sorry`/`admit`/`axiom` oculto;
- [ ] hashes de todos os `.lean`.

## Bloqueadores

- Capítulo sem hash/log → incompleto.
- `sorry` em qualquer teorema → capítulo bloqueado.
- Sem compilador → declarar `não validado por compilador`; nunca `prova total`.

## Ferramentas

MCP `integrations/lean_proof_mcp.py`; agentes `51_agente_lean_tese_auditavel`, `53_agente_lean_estudo_teoremas`.
