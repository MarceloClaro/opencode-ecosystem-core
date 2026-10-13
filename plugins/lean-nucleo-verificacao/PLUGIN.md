# Plugin Lean Núcleo Verificação (SPEC-935-R747)

Versão 0.1.0 — pacote auditável do núcleo Lean no Core.

## Componentes

- Agentes (5): `49_agente_lean_verificacao_total`, `50_agente_lean_matematica_formal`, `51_agente_lean_tese_auditavel`, `52_agente_lean_software_critico`, `53_agente_lean_estudo_teoremas`.
- Skills (2): `lean-verificacao-total`, `lean-tese-provas-auditaveis`.
- MCP: `integrations/lean_proof_mcp.py` (`lean_verify`, `lean_export`, `lean_autoformalize`, `lean_saturate`) sobre R444/R445.
- Motores reutilizados, não duplicados: `integrations/deepmind/lean4_verifier.py`, `autoformalizer.py`, `egraph_rewriter.py`.

## Uso

1. Formalize via skill/MCP (`lean_autoformalize` → `lean_export`).
2. Verifique via `lean_verify` (fail-closed `sorry`/`admit`).
3. Audite via tabela enunciado-código-hash-status.
4. Sem compilador `lean`/`lake`: `syntax_verified` no máximo; nunca alegar prova total.

## Licença e limites

Uso interno auditável. Sem validação externa não há alegação de Qualis, nota, aceite, superhuman ou correção garantida. `sorry`/`admit` sempre bloqueiam.
