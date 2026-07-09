# Evolução — Round 10: Menu Adaptativo

## Metadados
- **Timestamp**: 2026-05-28T17:52
- **Documento**: artigo_150_questoes.tex
- **Tipo**: Refatoração de infraestrutura (não-pipeline)
- **Artefato**: `menu.py` (reescrito), `.menu_registry.json` (novo)

## O que mudou

### Antes (menu estático)
- 11 opções fixas hardcoded em `menu.py`
- Quebrava se arquivos mudassem de nome ou diretório
- Sem suporte a plugins ou extensão sem editar código
- Categorias fixas: OPERACIONAR, REPRODUZIR, REGISTRAR, AUDITAR

### Depois (menu adaptativo)
- **DiscoveryEngine**: varre diretório e descobre `.tex`, `tests/test_*.py`,
  `orchestration/*.py`, `orchestration/backups/*.tex`, `orchestration/evolutions/*.md`
- **MenuActionBuilder**: constrói ações a partir dos artefatos descobertos
- **MenuRenderer**: renderiza menu com 6 categorias + cores + plugins
- **RunnerEngine**: executa ação selecionada em subprocesso
- **Plugin system** via `.menu_registry.json`: comandos externos registram-se
  sem editar `menu.py` (id, name, description, category, command, cwd, timeout)

### Modos de execução
| Modo | Comando | Descrição |
|------|---------|-----------|
| Interativo | `python menu.py` | Menu colorido com navegação numérica |
| Direto | `python menu.py <n>` | Executa opção N sem menu |
| Listagem | `python menu.py --list` | Exibe artefatos descobertos |
| Diagnóstico | `python menu.py --quick` | TDD + métricas, sai |

### Resiliência
- `_enter()` trata `EOFError` para operação não-interativa (pipe/automation)
- Encoding UTF-8 explícito (compatível Windows PowerShell)
- Números de opções variam conforme descoberta — sem posições fixas

## Artefatos descobertos (neste projeto)
- **1** `.tex` (60 KB, 24p)
- **4** testes (compile, quality, structure, run_all)
- **1** pipeline (refinement_loop)
- **1** backup (artigo_20260528_085255.tex)
- **1** insight (insight_20260528.md)
- **5** comandos registrados (SPEC, FRAMEWORK, README, contagem, limpeza)

## Recomendações
1. Adicionar comandos ao `.menu_registry.json` para tarefas repetitivas
2. O menu funciona em QUALQUER projeto LaTeX — copiar `menu.py` + `.menu_registry.json`
3. `python menu.py --list` como primeiro passo ao entrar em projeto novo
4. Se precisar de categoria extra, editar `CATEGORIES` em `menu.py` (dict simples)

## Assinatura
Gerado manualmente — Round 10 do ecossistema OpenCode.
