# SPEC_EVO14_SPE_MCP_BUILDER -- MCP Builder Engine v1.0

**Domain**: agency-agents/specialized/specialized-mcp-builder
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Parameter Validation
Parametro obrigatorio INTEGER valida corretamente: 50=OK, None=FAIL, "abc"=FAIL.

## CT-02: Tool Registry Uniqueness
Nomes duplicados e com espacos sao rejeitados. Apenas 1 tool registrada.

## CT-03: Validate Tool Call
Validacao completa: chamada valida OK, sem titulo FAIL, enum invalido FAIL, ferramenta inexistente FAIL.

## CT-04: Error Formatting
Formato MCP: isError=True com mensagem; sucesso sem isError com dados.

---

## Implementation
- `scripts/mcp_builder_engine.py`: ParamDef, ToolDef, ToolRegistry, ParamType
- `tests/test_mcp_builder.py`: 4 CTs via pytest
