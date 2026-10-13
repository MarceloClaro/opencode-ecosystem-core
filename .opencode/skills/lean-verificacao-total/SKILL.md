---
name: lean-verificacao-total
description: Verificação total fail-closed em Lean 4 com Mathlib para o Core; exige contrato mínimo, bloqueia sorry/admit/axiom não declarado e nunca alega prova total sem compilador. Use para verificar teoremas, auditar provas e exportar .lean com hash.
---

# Lean Verificação Total (SPEC-935-R747)

## Quando acionar

Quando houver pedido de verificação, prova, correção ou auditoria em Lean 4.

## Contrato mínimo

Exigir sempre: enunciado PT-BR, premissas, código `.lean`, imports Mathlib, versão Lean/lake, log do verificador, SHA-256.

Sem contrato completo: produzir protocolo, nunca veredito.

## Mapa tática → uso

| Tática | Uso típico | Cuidado |
|---|---|---|
| `ring` | identidades em anéis comutativos | não prova desigualdades |
| `linarith` | desigualdades lineares | precisa hipóteses lineares |
| `omega` | Nat/Int Presburger | não usa Real |
| `simp` | simplificação canônica | pode ocultar lema; registrar |
| `rw` | reescrita por igualdade | citar igualdade usada |
| `exact`/`apply` | fechamento por termo/lema | lema deve existir nos imports |

## Bloqueadores fail-closed

- `sorry` ou `admit` em qualquer ponto → `is_valid=False`, `status=incomplete_sorry`.
- `axiom` sem declaração explícita e auditoria → `axiom_nao_declarado`.
- Sem binário `lean`/`lake` → máximo `syntax_verified`; escrever `não validado por compilador`.
- Palavras como prova total, correção garantida, Qualis ou superhuman só com `machine_checked` + validação externa explícita.

## Ferramentas

MCP `integrations/lean_proof_mcp.py`: `lean_verify`, `lean_export`, `lean_autoformalize`, `lean_saturate`.
Agentes: `49_agente_lean_verificacao_total`, `50_agente_lean_matematica_formal`, `52_agente_lean_software_critico`.
