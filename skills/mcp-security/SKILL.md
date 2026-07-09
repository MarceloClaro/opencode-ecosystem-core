# MCP-Security Skill

**Camada de Segurança para MCP — R100 MCP Security Hardening**

Baseado no modelo MCPGuard + AuditLogger, este skill implementa
controle de acesso, auditoria, rate limiting e validação para ferramentas MCP.

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/security-audit <tool>` | Auditoria de chamadas de ferramenta |
| `/security-guard <config>` | Configura MCPGuard |
| `/security-report` | Relatório de segurança |

## Uso

```
/security-audit su_generate
/security-guard '{"rate_limit": 10, "allowed_roles": ["researcher"]}'
/security-report
```

## Exemplo de saída

```
MCPGuard: Ativo | Ferramentas protegidas: 11
AuditLog: 47 chamadas registradas, 0 violações
ToolVetter: Schema validation ativo
RateLimiter: 10 req/min por tool
```

## Dependências

- Python ≥ 3.10
- `synthetic_university.mcp_security` (core OpenCode Ecosystem)
