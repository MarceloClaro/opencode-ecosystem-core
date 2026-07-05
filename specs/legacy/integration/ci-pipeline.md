# Spec: CI Pipeline — Ecossistema OpenCode

**Versao:** 1.0.0
**Status:** proposed (ADR-007)
**Manutencao SWEBOK:** preventiva
**Ultima revisao:** 2026-05-27

---

## 1. Comportamento Esperado

Pipeline CI que valida automaticamente a integridade do ecossistema a cada push/PR. 5 gates sequenciais:

```
PUSH → [Lint] → [Unit Tests] → [Spec Coverage] → [Integration Tests] → [Health Check] → ✅
         ↓            ↓               ↓                  ↓                    ↓
        FAIL        FAIL            FAIL               FAIL                 FAIL
```

Cada gate em falha bloqueia o pipeline e reporta o erro com referencia `file:line`.

## 2. Usuarios e Contexto

- **Usuarios:** Evolver, agentes que modificam o ecossistema, revisores humanos
- **Gatilho:** Push para branch principal, PR aberto, ou comando manual `/ci`
- **Ambiente:** GitHub Actions, Windows 11 + Python 3.11 + Node.js 25
- **Timeout:** 10 minutos (total)

## 3. Restricoes

- Lint Gate: ruff check . (zero erros)
- Unit Test Gate: pytest tests/core/ tests/nexus/ (100% pass)
- Spec Coverage Gate: >= 80% das skills ativas tem spec documentada
- Integration Test Gate: pytest tests/integration/ (100% pass)
- Health Check Gate: health.json.status == "OK" e timestamp < 24h

## 4. Casos de Borda

- Teste intermitente (flaky): re-executar ate 3 vezes. Se falhar 3x, reportar como FAIL com tag [FLAKY]
- Timeout do pipeline: reportar ultimo gate concluido, sugerir otimizacao
- MCPs offline: Health Check gate deve distinguir "MCP offline" de "erro de codigo"
- Sem testes para novo componente: Spec Coverage gate reporta WARNING, nao FAIL (para nao bloquear MVP)

## 5. Criterios de Aceitacao

- [ ] Pipeline executa em < 10 minutos
- [ ] Lint gate detecta erros de estilo e reporta file:line
- [ ] Unit test gate detecta regressoes
- [ ] Spec coverage gate reporta % de skills com spec
- [ ] Integration gate valida fluxos cross-component
- [ ] Health gate verifica agentes, MCPs e DB
- [ ] Pipeline gera relatorio consolidado ao final

## 6. Implementacao

Arquivo: `.github/workflows/ci.yml`

```yaml
name: CI — OpenCode Ecosystem
on: [push, pull_request]
jobs:
  lint:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff
      - run: ruff check .
  unit-tests:
    needs: lint
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/core/ tests/nexus/ -v
  spec-coverage:
    needs: unit-tests
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/check_spec_coverage.py
  integration:
    needs: spec-coverage
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/integration/ -v
  health-check:
    needs: integration
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/health_check.py
```
