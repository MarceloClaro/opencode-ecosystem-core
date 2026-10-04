---
id: minizinc-mcp
name: minizinc-mcp
description: >-
  Ponte orquestrável do MiniZinc Constraint Solver MCP Server
  (r33drichards/minizinc-mcp, MIT): modelagem CSP/COP via tool
  solve_constraint (solver gecode). Monta payloads, checa solver + deps
  e emite config stdio/SSE.
type: integration
round: R646
spec: SPEC-935-R646-minizinc-mcp.md
trust: 0.9
---

# minizinc-mcp — MiniZinc Constraint Solver (ponte MCP)

Ponte orquestrável (não resolve no Core): servidor FastMCP com tool única
`solve_constraint(model, data?, solver, all_solutions, timeout)`.

## Capacidades

- `minizinc_available()` / `minizinc_version()` — binário do solver.
- `python_deps_status()` / `mcp_available()` — deps `mcp/pydantic/minizinc`.
- `build_solve_payload(...)` — dict no schema ConstraintModel (puro).
- `mcp_config()` / `hosted_sse()` — stdio local / URL SSE hospedada.
- `doctor_check()` — pass só com deps + solver; warn indicando a peça.
- CLI `/minizinc status|config|payload|solvers|doctor|install`.

## Limites (anti-overclaim R110)

- Resolução externa; `status` do servidor (`OPTIMAL`, `SATISFIED`,
  `UNSATISFIABLE`) deve ser citado, não presumido.
- Requer MiniZinc 2.8+ para modo local; modo SSE dispensa solver local.
