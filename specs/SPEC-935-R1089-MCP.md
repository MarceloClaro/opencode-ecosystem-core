# SPEC-935-R1089-MCP — Servidor MCP stdio local Tiangong (HDR/RSIR/VRP)

## Demanda e autoridade

A `SPEC-935-R1089` exigia, na AC5, "testes unitários e transporte MCP real
local" e, na AC7, "MCP preparado e desativado por padrão". A entrega anterior
publicou skill, agent card e testes, mas **não implementou o servidor MCP**.
Em vez disso, a configuração global apontava para `npx -y tiangong-handler`,
pacote inexistente no npm (E404), gerando `Request timed out` no OpenCode.

O operador autorizou explicitamente a Opção C: implementar o servidor MCP
stdio local, apontar `command` para `.venv/bin/python -m integrations.tiangong_mcp`
com `cwd` no repositório e manter desativado enquanto a implementação não
existir. Esta spec rege essa entrega.

## Escopo

1. Servidor MCP stdio em `integrations/tiangong_mcp.py`, usando o SDK `mcp`
   já instalado (`mcp==1.28.1`), sem novas dependências.
2. Quatro ferramentas: `tiangong_catalog`, `hdr_handler`, `rsir_handler`,
   `vrp_handler`.
3. Operações locais determinísticas: validação, pré-processamento de imagem
   PNG, extração de vetor 784, comparação de vetores, validação de vetores
   768 e heurística clássica de CVRP.
4. Operações que dependem de backend não observado retornam
   `status="unavailable"`, sem rótulo, dígito, confiança ou resultado inventado.
5. Testes unitários e de transporte stdio real; negativos para entrada
   inválida, operação desconhecida e provedor indisponível.
6. Entrada em `opencode.json` do projeto com `command`, `cwd` e `timeout`,
   inicialmente desativada e habilitada apenas após o teste stdio passar.

## Fora de escopo

- Rede, autenticação, API key, submissão de jobs, hardware quântico.
- Leitura arbitrária de arquivos (`image_path` é recusado).
- Escrita de arquivos, shell, instalação de pacotes.
- Alegar execução quântica, vantagem quântica, treinamento ou reprodução do
  backend da Tiangong.
- Substituir a skill ou o agent card; o MCP é o transporte local do contrato.

## Contrato das ferramentas

### Envelope comum

```json
{
  "status": "success | error | unavailable",
  "app": "HDR | RSIR | VRP | null",
  "technique": "string | null",
  "result": {"...": "..."},
  "evidence": {
    "source_html_sha256": "string | null",
    "source_bundle_sha256": "string | null",
    "method": "static_analysis_REA",
    "provider": "REA_6.8.0_static_analysis"
  },
  "limitations": ["string"]
}
```

`status="unavailable"` significa: a operação é reconhecida, mas nenhum
provedor verificável foi implementado. Nunca é acompanhada de resultado
fabricado. `status="error"` inclui `result.code` estável para teste.

### `tiangong_catalog`

Sem argumentos. Retorna os três apps, ações suportadas, disponibilidade,
hashes das fontes observadas e limitações. Não acessa rede.

### `hdr_handler`

| Ação | Comportamento |
|---|---|
| `validate` | Valida o payload e o tipo de entrada. |
| `preprocess` | Decodifica PNG (stdlib) ou aceita matriz `pixels`; devolve vetor 784 normalizado e SHA-256 da entrada. |
| `recognize` | `unavailable`: backend QNN não observado. `digit` e `confidence` são `null`. |
| `compare` | Compara dois vetores 784 ou duas imagens; devolve L1, L2 e cosseno. |
| `export` | Devolve o envelope JSON em memória; não grava arquivo. |

Entradas aceitas: `image_base64` (PNG) ou `pixels` (matriz 2D de números
finitos). `image_path` é recusado com `result.code="path_not_allowed"`.

### `rsir_handler`

| Ação | Comportamento |
|---|---|
| `validate` | Valida o payload. |
| `features` | Valida vetor numérico de dimensão configurável (padrão 768) e devolve norma/média. |
| `analyze`, `classify` | `unavailable`: modelo ViT/QViT não observado; sem rótulo fabricado. |

### `vrp_handler`

| Ação | Comportamento |
|---|---|
| `validate` | Valida nós, demandas, veículos e capacidades. |
| `solve` | Heurística clássica determinística (vizinho mais próximo + 2-opt) com capacidade; `backend="classical-heuristic"`, `quantum=false`, `optimality="not_proven"`. |
| `upload` | `unavailable`: não há upload/leitura de arquivo. |

Limite: até 200 nós e até 64 veículos.

## Segurança e limites

- Sem `socket`, `requests`, `urllib`, `http.client`, `subprocess` ou shell.
- Base64 máximo: 2.000.000 bytes decodificados.
- Dimensão máxima de imagem: 1024×1024; vetores até 4096 dimensões.
- Números não finitos, dimensões erradas e ações desconhecidas falham fechado.
- Nenhuma credencial é lida, exigida ou registrada.

## Critérios de aceitação

- **AC-MCP1**: `tiangong_catalog` lista HDR/RSIR/VRP com hashes reais dos
  artefatos locais e limitações explícitas.
- **AC-MCP2**: `hdr_handler preprocess` decodifica PNG cinza, RGB e RGBA
  8 bits sem Pillow, devolvendo 784 valores em [0,1] e SHA-256 estável.
- **AC-MCP3**: `hdr_handler recognize` retorna `unavailable` com `digit=null`
  e `confidence=null`; nenhum resultado simulado.
- **AC-MCP4**: `hdr_handler compare` calcula L1/L2/cosseno determinísticos e
  recusa dimensões diferentes.
- **AC-MCP5**: `rsir_handler analyze/classify` retorna `unavailable`; não há
  `class_label` ou probabilidades inventadas.
- **AC-MCP6**: `vrp_handler solve` devolve rotas determinísticas, factíveis,
  com `backend="classical-heuristic"` e `quantum=false`; instância inviável
  é reportada como tal, não "sucesso".
- **AC-MCP7**: entradas inválidas, ação desconhecida, `image_path`, payload
  acima do limite e formato não PNG falham com `status="error"` e código.
- **AC-MCP8**: teste de transporte stdio real faz `initialize`,
  `notifications/initialized`, `tools/list` e `tools/call` contra
  `.venv/bin/python -m integrations.tiangong_mcp`, com `cwd` no repositório.
- **AC-MCP9**: a entrada existe no gerador e no `opencode.json` com `command`,
  `cwd` e `timeout`. O `--check` não é usado como gate enquanto a divergência
  federada pré-existente não for resolvida: a regeneração completa removeria
  seis MCPs ativos e reverteria comandos locais.
- **AC-MCP10**: `opencode mcp list` (binário 2.2.7) mostra `tiangong-hdr`
  conectado após a habilitação; desativar é um único campo `enabled: false`.

## Plano TDD

1. Escrever `tests/test_r1089_tiangong_mcp.py` e observar RED (módulo ausente).
2. Implementar `integrations/tiangong_mcp.py` até GREEN.
3. Corrigir a importação tardia de `colab_mcp_config` no gerador (bug
   pré-existente que impedia `--check` e a regeneração).
4. Adicionar a entrada ao gerador e ao `opencode.json`; validar `--check`.
5. Executar o teste stdio real, habilitar e conferir `opencode mcp list`.
6. Registrar ciclo evolutivo e reflexão com limites.

## Evidência de origem

- HDR HTML: `8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342`
- HDR bundle: `7f6e3f71fa4fcc42cd6dafef79f881f0a32afe44db43f001eac9893e7d1f9eea`
- RSIR bundle: `76308919310a4b6235a21fe83a4e96d0b83949f486602ea774998a508ff8c418`
- VRP bundle: `38acd57efc1fd70229a9fad67bfd0a4c3d2886bc4146d562675de9383397cfe6`
- HTML de RSIR/VRP é o mesmo shell SPA (mesmo SHA-256), o que é registrado
  como limitação, não como identidade de aplicação.

## Riscos residuais

- O PNG decoder cobre 8 bits, sem entrelaçamento e tipos 0/2/4/6. Formatos
  exóticos retornam `unavailable`/`error` explícito.
- A heurística CVRP não prova otimalidade e não é comparação com QAOA.
- O servidor não substitui a análise estática REA nem valida o backend remoto.

## Recibos de execução (2026-11-12)

### RED
- `pytest tests/test_r1089_tiangong_mcp.py -q` → `ImportError: cannot import
  name 'tiangong_mcp' from 'integrations'`, antes da implementação.

### GREEN
- `pytest tests/test_r1089_tiangong_mcp.py -q` → **35 passed** em 2,08 s.
- Regressões (`test_r1088_mcp_recovery.py`, `test_r1015_mcp_hardening.py`,
  `test_r660_mcp_validation.py`) → **139 passed, 13 failed**. As 13 falhas são
  pré-existentes do Colibri (`ModuleNotFoundError: No module named 'colibri'`),
  sem relação com esta entrega.
- `python -m py_compile integrations/opencode_cli.py` → OK.

### Runtime real (binário 2.2.7)
- `opencode mcp list` → `✓ tiangong-hdr connected`.
- `tiangong_catalog` → `success`; apps HDR/RSIR/VRP.
- `hdr_handler recognize` → `unavailable`; `digit=null`, `confidence=null`.
- `rsir_handler features` (768×0,5) → `success`; `dimension=768`, `mean=0,5`.
- `vrp_handler solve` (4 nós, 2 veículos) → `success`, `feasible=true`,
  `backend=classical-heuristic`, `quantum=false`, `total_distance=5.414214`.

### Configuração
- `opencode.json`: entrada `mcp.tiangong-hdr` com `command`, `cwd`,
  `enabled=true` e `timeout=30000`; total de 32 MCPs.
- Gerador `integrations/opencode_cli.py`: entrada adicionada e importação
  tardia de `colab_mcp_config`/`server_specs` movida para o topo de
  `build_config()`, corrigindo o `UnboundLocalError` que impedia `--check`.
- A regeneração completa **não** foi executada: `build_config()` removeria seis
  MCPs federados ativos (`chroma`, `context7`, `mcp-memory`, `mcp-time`,
  `playwright`, `qdrant`) e reverteria comandos locais (`gjq`, `mindspore-*`).
  A edição no JSON foi textual e mínima; o gerador fica preparado para quando a
  divergência federada for resolvida com autorização.

### Achados residuais (resolvidos em R1108)
- `.opencode/skills/tiangong-harness/{HDR,RSIR,VRP}/SKILL.md` publicado; o
  `skill.py` agora delega ao MCP local e não simula dígito, rótulo ou rota.
- `federation/activated.json` restaurado como JSON válido
  (`federation-activated-mcp/v2`); o gate R1015 volta a poder operar.
- As 13 falhas Colibri pré-existentes foram corrigidas: os testes usam
  `integrations.colibri.colibri_mcp_server`, a API JSON-RPC atual e validam
  entrada antes do provedor.
- `opencode.json` continua divergindo de `build_config()` por escolhas locais
  (`uvx` sem caminho absoluto, `npx` em vez de binário versionado) e por
  `playwright`, cujo smoke falhou. A regeneração completa não é automática.

### Lições
- Pacote npm não publicado não deve ser registrado como MCP: falha muda entre
  E404 e timeout conforme o registry responde ou entra em retry.
- `disabled=true` depois de `--` é argumento do processo filho, não campo de
  configuração; o campo correto é `enabled: false` (legado) ou `disabled: true`
  (`mcp.servers`).
- Regenerar configuração compartilhada sem diff prévio pode apagar MCPs ativos;
  a edição mínima preservou o estado do operador.
- Resultado `unavailable` é mais honesto que "success" simulado: o handler não
  inventa dígito, rótulo ou confiança sem backend observado.
