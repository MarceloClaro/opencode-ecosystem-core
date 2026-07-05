# SPEC-090: Canonical Entrypoint Architecture

## 1. Visão Geral
**Objetivo:** Unificar todos os 21+ entrypoints fragmentados do ecossistema em um único ponto de entrada canônico (`ecosystem` CLI), eliminando ambiguidade de inicialização e estabelecendo um hub de comando centralizado, auditável e extensível.

**Motivação:** O diagnóstico revelou 21+ entrypoints `if __name__` espalhados por `nexus/`, `basis-research/`, `criador-artigo/`, `editais-br/`, além de scripts `.sh` e `.ps1`. Não há um entrypoint único registrado como comando do sistema. O `menu.py` é o mais próximo, mas não está registrado formalmente.

## 2. Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ecosystem CLI (canonical)                      │
│                                                                         │
│  ecosystem [--verbose] [--version] <comando> [args...]                  │
│                                                                         │
│  Comandos:                                                              │
│    menu          → Menu adaptativo interativo                           │
│    run <script>  → Executa script Python/Shell no ecossistema          │
│    serve <svc>   → Inicia servidor (dashboard, api, mcp)               │
│    sync          → Sincronização do ecossistema                        │
│    evolve        → Ciclo evolutivo                                     │
│    audit         → Auditoria completa                                   │
│    test          → Executa suítes de teste                              │
│    doctor        → Diagnóstico de saúde do ecossistema                 │
│    status        → Status resumido do ecossistema                      │
│    help          → Ajuda detalhada                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Estrutura de Diretórios

```
ecosystem/
├── __init__.py          # Versão, metadados, lazy registry
├── __main__.py          # python -m ecosystem → CLI
├── cli.py               # Parser argparse + dispatch
├── commands/            # Implementação de cada comando
│   ├── __init__.py
│   ├── cmd_menu.py      # Delega para menu.py
│   ├── cmd_run.py       # Executa scripts
│   ├── cmd_serve.py     # Inicia servidores
│   ├── cmd_sync.py      # Sincronização
│   ├── cmd_evolve.py    # Evolução
│   ├── cmd_audit.py     # Auditoria
│   ├── cmd_test.py      # Testes
│   ├── cmd_doctor.py    # Diagnóstico
│   └── cmd_status.py    # Status
├── adapters/            # Ponte para entrypoints existentes
│   ├── __init__.py
│   ├── nexus_adapter.py
│   ├── basis_adapter.py
│   ├── artigo_adapter.py
│   └── editais_adapter.py
└── contracts/           # Contratos formais (SPEC-091)
    └── __init__.py
```

### 2.2 Fluxo de Delegação

```
ecosystem run pipeline-academico
  → cli.py dispatch("run", "pipeline-academico")
  → adapter = resolve_adapter("pipeline-academico")
  → adapter.execute(args)
  → retorna resultado formatado
```

## 3. Requisitos TDD

| CT ID | Descrição | Critério |
|-------|-----------|----------|
| CT-9001 | CLI existe e é executável | `python -m ecosystem --help` retorna código 0 |
| CT-9002 | Versionamento correto | `python -m ecosystem --version` retorna string semântica |
| CT-9003 | Comando `menu` delega para menu.py | Saída contém "Menu Adaptativo" |
| CT-9004 | Comando `status` exibe métricas | Saída contém "ecosystem-state" |
| CT-9005 | Comando `doctor` diagnostica entrypoints | Saída lista entrypoints canônicos |
| CT-9006 | Adaptador Nexus redireciona corretamente | Chama função alvo sem erro |
| CT-9007 | Adaptador Basis redireciona corretamente | Chama função alvo sem erro |
| CT-9008 | Comando inválido retorna erro amigável | Exit code != 0 + mensagem de ajuda |
| CT-9009 | Todos os entrypoints antigos têm redirect | Mensagem "Use 'ecosystem ...'" |
| CT-9010 | Plugin registry descobre CLI dinamicamente | `ecosystem --list-plugins` lista plugins |

## 4. Métricas de Sucesso
- **Zero entrypoints diretos**: 100% dos entrypoints antigos redirecionam para `ecosystem`
- **Tempo de inicialização**: < 500ms para qualquer comando
- **Cobertura de comandos**: 100% dos casos de uso mapeados

## 5. ADRs

### ADR-architectu-090-1: CLI Unificada via `python -m ecosystem`
**Decisão:** Usar `python -m ecosystem` como entrypoint canônico em vez de `sys.executable ecosystem/cli.py` ou console_scripts. Motivo: funciona em qualquer ambiente Python sem instalação, é auto-documentado, e suporta descoberta dinâmica de plugins.

### ADR-architectu-090-2: Adaptadores em vez de Rewrites
**Decisão:** Não reescrever entrypoints existentes. Criar adaptadores finos que delegam para os módulos originais. Motivo: mínima superfície de mudança, compatibilidade retroativa, baixo risco de regressão.
