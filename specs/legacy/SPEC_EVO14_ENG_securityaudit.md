# SPEC_EVO14_ENG_securityaudit — SecurityAuditEngine Skill

## Metadata
- **Evolucao**: Round 14 (Agency Engineering)
- **Fonte**: agency-agents/engineering/engineering-security-engineer.md
- **Categoria**: agency/engineering
- **Versao**: 1.0.0

## Descricao
Motor de auditoria de seguranca estatica. Analisa codigo-fonte para detectar vulnerabilidades OWASP Top 10, secrets hardcoded, SQL injection, XSS, e padroes de autenticacao inseguros. Opera offline com stdlib Python 3.12.

## CTs (Criterios de Aceitacao)

### CT-01: Deteccao de Secrets Hardcoded
- **Dado**: codigo com `API_KEY = "sk-abc123"`, `password = "admin123"`, `token = "ghp_xxx"`
- **Quando**: `engine.detect_secrets(source_code)` e chamado
- **Entao**: retorna `SecretsReport` com `secrets` listando cada ocorrencia com `line`, `variable`, `pattern`, `severity="HIGH"`

### CT-02: Deteccao de SQL Injection
- **Dado**: codigo com `f"SELECT * FROM users WHERE id = {user_input}"`, string concatenation em queries
- **Quando**: `engine.detect_sql_injection(source_code)` e chamado
- **Entao**: retorna `InjectionReport` com `vulnerabilities` listando linhas com queries concatenadas/interpoladas

### CT-03: Deteccao de XSS
- **Dado**: codigo com `innerHTML`, `dangerouslySetInnerHTML`, `document.write()` com user input
- **Quando**: `engine.detect_xss(source_code)` e chamado
- **Entao**: retorna `XSSReport` com `vulnerabilities` listando sinks XSS com `line`, `sink`, `severity`

### CT-04: Auditoria de Autenticacao
- **Dado**: codigo com senhas em plain text, JWT sem expiracao, cookies sem HttpOnly/Secure
- **Quando**: `engine.audit_authentication(source_code)` e chamado
- **Entao**: retorna `AuthAudit` com `issues` e `score` (0-100), listando deficiencias

## API Contract

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SecretsReport:
    secrets: list[dict]  # [{line, variable, pattern, severity}]
    count: int
    available: bool = True

@dataclass
class InjectionReport:
    vulnerabilities: list[dict]  # [{line, type, snippet, severity}]
    count: int
    available: bool = True

@dataclass
class XSSReport:
    vulnerabilities: list[dict]  # [{line, sink, context, severity}]
    count: int
    available: bool = True

@dataclass
class AuthAudit:
    issues: list[dict]  # [{line, category, description, severity}]
    score: int  # 0-100, higher = better
    available: bool = True

class SecurityAuditEngine:
    @property
    def available(self) -> bool: ...

    def detect_secrets(self, source: str) -> SecretsReport: ...
    def detect_sql_injection(self, source: str) -> InjectionReport: ...
    def detect_xss(self, source: str) -> XSSReport: ...
    def audit_authentication(self, source: str) -> AuthAudit: ...
```
