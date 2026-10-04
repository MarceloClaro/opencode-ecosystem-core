# SPEC-935-R646 — Ponte MiniZinc MCP Server (r33drichards/minizinc-mcp)

**Ronda:** R646
**Status:** em implementação
**Data:** 2026-10-03
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Ponte externa orquestrável (espelho de R645 colab-mcp)

## Objetivo

Tornar o **MiniZinc Constraint Solver MCP Server**
(`r33drichards/minizinc-mcp`, MIT) orquestrável pelo OpenCode Ecosystem Core
como **ponte externa** — sem executar o protocolo MCP no Core e sem declarar
resultados como "verificados" sem validação (anti-overclaim R110).

O servidor expõe uma tool única e poderosa:

- `solve_constraint(model, data?, solver="gecode", all_solutions=false,
  timeout?) -> SolveResult {solutions, status, solve_time, num_solutions, error}`

## Fonte de verdade (anti-overclaim)

README oficial `r33drichards/minizinc-mcp@main` (lido em 2026-10-03 via raw):
- Stack: Python 3.11+, MiniZinc 2.8+ (minizinc.org/software.html), deps
  `pydantic`, `mcp` (FastMCP), `minizinc` (`requirements.txt`, 3 linhas).
- `main.py`: `FastMCP` + `ConstraintModel/Solution/SolveResult/SolverInfo` +
  `solve_constraint_core` (async, `minizinc.Solver.lookup` + `Instance` +
  `solve_async`, `time_limit=timedelta(seconds=timeout)`).
- 3 modos: (1) hospedado SSE `https://minizinc-mcp.up.railway.app/sse`
  (recomendado); (2) Docker self-host (`docker build/run`, porta 8000);
  (3) local (`pip install -r requirements.txt && python main.py`).
- Clientes: Claude connectors (`Add Custom Connector`, nome "minizinc mcp",
  URL SSE) e Claude Code (`claude mcp add minizinc -t sse <URL>`).
- Exemplos: 4-Queens, knapsack, `x+y=15, x<y`.
- Licença: MIT (compatível com o Core).
- Layout: `main.py`, `requirements.txt`, `Dockerfile`, `tests/`,
  `test_server.py`, `test_simple.py`, `pytest.ini`.

## Escopo

- `integrations/minizinc_mcp.py`: presença (`minizinc` binário + deps Python
  `mcp/pydantic/minizinc`), versão do solver, `build_solve_payload()` (puro,
  sem rede), `mcp_config()` (stdio local) + `hosted_sse()`, doctor, install,
  CLI `main()`.
- `agents/catalog/minizinc-mcp.md`: Agent Card A2A.
- `marceloclaro/doctor.py`: entrada `minizinc` em `EXTERNAL_CLIS`.
- `integrations/opencode_cli.py`: comando `/minizinc`.
- `.opencode/skills/minizinc-mcp/SKILL.md`: guia de uso.
- `tests/test_r646_minizinc_mcp.py` (unit, mocks).
- Ciclo de evolução R646.

## Critérios de aceitação

1. `minizinc_available()` usa `shutil.which("minizinc")` (tolerante).
2. `minizinc_version()` extrai semver de `minizinc --version`; `None` se
   ausente/falha; nunca lança.
3. `python_deps_status()` retorna `{mcp, pydantic, minizinc: bool}` via
   `importlib.util.find_spec`, sem importar os pacotes.
4. `mcp_available()` = deps Python presentes (solver binário é check separado).
5. `build_solve_payload(model, data, solver, all_solutions, timeout)` valida:
   `model` não vazio → dict no schema `ConstraintModel`; erro vira
   `ValueError` com mensagem em português.
6. `mcp_config()` retorna stdio local; `hosted_sse()` retorna a URL SSE.
7. `doctor_check()`: `pass` só com deps + binário; `warn` caso contrário
   indicando a peça faltante (NUNCA fail).
8. `install_instructions()` documenta pré-requisitos (Python 3.11+, MiniZinc
   2.8+), pip, Docker e SSE hospedado + `claude mcp add`.
9. `main()`: `status|config|doctor|install|payload|solvers` + `--help`;
   comando desconhecido → exit 2.
10. Gate TDD: `pytest tests/test_r646_minizinc_mcp.py` → 100% verdes (mocks,
    sem binário/rede).
11. Doctor global 0 fail; `minizinc` ausente entra como warn.
12. `/minizinc` presente no `opencode.json` regenerado + Agent Card.
13. Ciclo R646 registrado.

## Estratégia de validação

- Unit (mocks): `which` mapeado; `subprocess.run` fake para `--version`;
  `find_spec` fake para deps; payload válido/inválido; config local vs SSE;
  doctor nos 3 estados (full/deps-sem-binário/sem-deps); exit codes.
- Sem rede nos testes: SSE é string constante, nunca sondada.
- Solver real (`minizinc --solvers`, `solve_async`) fora do Core — pertence ao
  operador (documentado, não executado pela ponte).

## Decisões registradas

- Ponte, não executor: ao contrário do `colab_cli` (que dispara `colab`
  via subprocess), aqui o Core monta payloads e configs; a resolução
  (`gecode` etc.) roda no servidor do operador — evita acoplar o Core a
  binário de solver + rede.
- `mcp_available` não exige o binário: o modo hospedado SSE resolve sem
  MiniZinc local; o doctor distingue as peças para mensagem precisa.
- Sem auto-instalação de solver (instalador do SO / minizinc.org) e sem
  chamada ao SSE no doctor (privacidade + latência).
