# mindspore-config — Skills de Parsing e Validação de Configurações MindSpore

## Visão geral

Skills para parsing, validação e análise de configurações MindSpore (JSON) encontradas no repositório `MarceloClaro/mindspore`.

## Arquivos suportados

Os seguintes padrões de arquivo são suportados:

| Padrão | Descrição |
|---|---|
| `config/acl_dump_cfg.json` | Configuração de dump ACL |
| `config/hccl_*.json` | Configurações HCCL (single/multi machine, multi rank) |
| `config/super_bar_config.json` | Configuração de barreira superior |
| `tests/ut/data/dataset/*/datasetSchema.json` | Schemas de dataset (MNIST, CIFAR, ImageNet, etc.) |
| `config/*.json` | Qualquer outro config JSON do MindSpore |

## Skills disponíveis

### 1. `mindspore-validate`

Valida um arquivo de configuração MindSpore, verificando:
- Estrutura JSON esperada
- Campos obrigatórios
- Tipos de dados corretos
- Valores esperados para campos conhecidos

**Uso:**
```bash
mindspore-validate <caminho-do-arquivo>
```

**Exemplo:**
```bash
mindspore-validate config/acl_dump_cfg.json
mindspore-validate config/hccl_single_machine_multi_rank.json
mindspore-validate tests/ut/data/dataset/testMnistData/datasetSchema.json
```

### 2. `mindspore-summary`

Gera um resumo estruturado de um ou mais arquivos de configuração, incluindo:
- Quantidade de campos
- Tipos de dados encontrados
- Padrões de configuração comuns
- Possíveis problemas ou warnings

**Uso:**
```bash
mindspore-summary <caminho-do-arquivo> [...]
```

**Exemplo:**
```bash
mindspore-summary config/acl_dump.cfg.json
mindspore-summary config/hccl_*.json tests/ut/data/dataset/testMnistData/datasetSchema.json
```

### 3. `mindspore-schema`

Gera um schema JSON based on um arquivo de configuração MindSpore, útil para:
- Documentação automática
- Validação em outros sistemas
- Geração de skills TypeScript/Python

**Uso:**
```bash
mindspore-schema <caminho-do-arquivo>
```

## Padrões de Configuração Encontrados

Durante a análise REA, foram identificados 124 arquivos JSON com os seguintes padrões comuns:

### Config ACL Dump (`acl_dump_cfg.json`)
```json
{
  "dump": {
    "dump_list": [],
    "dump_path": "/tmp/acl_data_dump",
    "dump_mode": "all",
    "dump_op_switch": "on"
  }
}
```

### Config HCCL (`hccl_*.json`)
```json
{
  "board_id": "0x0000",
  "chip_info": "910",
  "deploy_mode": "lab",
  "group_count": "1",
  "group_list": [{
    "device_num": "8",
    "group_name": "",
    "instance_count": "8",
    "instance_list": [{
      "devices": [{"device_id": "0", "device_ip": "[device_ip_0]"}],
      "rank_id": "0",
      "server_id": "[server_id]"
    }]
  }]
}
```

### Schema de Dataset (`datasetSchema.json`)
```json
{
  "datasetType": "MNIST",
  "numRows": 10,
  "columns": {
    "image": {"type": "uint8", "rank": 1, "t_impl": "cvmat"},
    "label": {"type": "uint32", "rank": 1, "t_impl": "flex"}
  }
}
```

## Integração OpenCode

### Comando `mindspore-config`

Registra um comando OpenCode para operação unificada:

```bash
# Listar skills disponíveis
mindspore-config skills

# Validar arquivo
mindspore-validate config/acl_dump_cfg.json

# Gerar resumo
mindspore-summary config/hccl_*.json

# Gerar schema
mindspore-schema tests/ut/data/dataset/testMnistData/datasetSchema.json
```

### Integração SDD/TDD

Os arquivos de config podem ser validados no ciclo SDD/TDD:

1. **Spec**: Definir schema esperado para config MindSpore
2. **Test**: Validar arquivos reais contra o schema
3. **Refactor**: Ajustar configs quando testes falharem

## Limitações

- Foco em arquivos JSON de configuração
- Não inclui análise de código Python do MindSpore core
- Padrões baseados no repositório cloneado (versão específica)
- Novos padrões de config podem exigir atualização de skills