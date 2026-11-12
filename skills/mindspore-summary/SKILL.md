# mindspore-summary — Skill de Resumo Automatizado

## Visão geral

Skill para gerar resumos estruturados de configurações MindSpore (JSON). Extrai padrões, validações e estatísticas a partir de um ou mais arquivos de configuração.

## Objetivo

Fornecer uma visão geral consolidada de:
- Distribuição de padrões de configuração
- Campos mais comuns e seus valores
- Quantidade de arquivos válidos vs inválidos
- Principais erros encontrados

## Entrada

Aceita múltiplos caminhos de arquivos JSON:
- `config/acl_dump_cfg.json` - Config ACL dump
- `config/hccl_*.json` - Configurações HCCL
- `tests/ut/data/dataset/*/datasetSchema.json` - Schemas de dataset
- `config/*.json` - Qualquer config JSON do MindSpore

## Saída

Gera um relatório formatado com:

```
═════════════════ mindspore-config — Resumo ═════════════════
Arquivos total: N
  Válidos: M
  Inválidos: K

Distribuição de padrões:
  - padrăo A: X
  - padrăo B: Y

Campos mais comuns:
  - campo A: aparece em Z arquivo(s)
    valores amostra: val1, val2, val3

Erros encontrados:
  ❌ erro1
  ❌ erro2
  ... e mais N erros
```

## Comandos Disponíveis

```bash
# Resumo de arquivos específicos
mindspore-summary <caminho1> <caminho2> ...

# Resumo com todos os configs da pasta
mindspore-summary config/*.json

# Listar padrões conhecidos
mindspore-summary --list-patterns
```

## Integração OpenCode

Registrada como ferramenta MCP no ecossistema OpenCode, pode ser usada no ciclo SDD/TDD:
- **Spec**: Definir expectativa de qualidade de configs
- **Test**: Executar mindspore-summary e validar resultado
- **Refactor**: Ajustar configs quando summaries indicarem problemas