# SPEC-935-R1066 — REA upstream 6.8.0 com fallback para o fork

**Status:** implementado e testado; nenhuma validação externa ou publicação.
**Objetivo:** substituir a preferência pelo fork `MarceloClaro/rea` 6.4.0 pelo
upstream oficial `morluto/rea` 6.8.0, preservando a instalação antiga como
fallback e mantendo o contrato da ponte `ReaBridge`.

## 1. Origem e licença

| Item | Upstream | Fork instalado |
|---|---|---|
| Repositório | `https://github.com/morluto/rea` | `https://github.com/MarceloClaro/rea` |
| Versão | 6.8.0 | 6.4.0 |
| Tag/commit | `rea-agents-6.8.0` / `160d821ac9a0310afcb8d1fc427862dd6508add5` | commit `4daea941bfeeb426886f2d048aed7f3cb2dbf97b` |
| Licença | MIT | MIT |
| Estado | upstream ativo, publicado em 2026-10-25 | fork 4.234 commits atrás |
| Runtime | `~/.local/share/opencode-core/rea-6.8.0` | `~/.local/share/opencode-core/rea` |

O pacote npm `rea-agents@6.8.0` inclui `dist/`; não foi necessário compilar
TypeScript no host. A instalação foi feita em diretório isolado e só depois
promovida para o caminho preferencial.

## 2. Runtime

- Node do host: `v22.23.1`.
- `engines` do upstream: `^22.23.4 || ^24.22.1 || >=26.12.1`.
- A versão 6.8.0 executou CLI, handshake MCP, catálogo e análise estática com
  Node 22.23.1, mas o campo `engines` não é satisfeito. O runtime ideal é um
  Node que atenda ao campo; `REA_NODE_BIN` permite selecioná-lo.
- Instalação das dependências de produção exigiu
  `npm install --omit=dev --ignore-scripts --legacy-peer-deps
  --package-lock=false` no npm 10.9.8. O erro sem `--legacy-peer-deps` foi
  `Cannot read properties of null (reading 'edgesOut')`, do Arborist.
- `REA_SOURCE_DIR` continua tendo precedência. Sem ele, a ponte prefere
  `rea-6.8.0` e usa `rea` como fallback.

## 3. Contrato da ponte

Operações preservadas: `status`, `catalog`, `session`, `layers`, `layer`,
`analyze`, `analyze_binary`.

- `analyze` continua usando `analyze_javascript_application` e
  `input_path`, com `detail=complete`, `format=auto` e
  `integrity_policy=fail`.
- O catálogo upstream tem **229 ferramentas**; o fork tem **170**. Foram
  **59 novas** e **0 removidas**.
- A resposta de análise mantém `evidence_id`, `subject`, `provider`,
  `normalized_result`, `limitations`, `locations` e `evidence_links`.
- O upstream acrescenta `route_inventory` e aumenta as limitações de 7 para 8
  no fixture analisado. O fork expõe `statistics.modules`, ausente no upstream.
- O `subject.digest.sha256` do fixture foi idêntico nos dois (mesmo conteúdo).
- O upstream inclui `_meta.provenance` com `untrusted_content` e
  `source=analysis_target`; o fork não incluía esse campo.

## 4. Proveniência

`ReaBridge.REPOSITORY` passa a apontar para o upstream. O campo
`provenance.repository` é lido do checkout git quando existe; sem git, lê
`package.json.repository.url`. Isso evita rotular o fork como upstream ou o
upstream como fork.

## 5. Aceitação

1. `status` encontra 6.8.0 no caminho preferencial e reporta
   `repository=https://github.com/morluto/rea`.
2. `catalog` faz handshake MCP e anuncia 229 ferramentas.
3. `analyze` conclui no fixture Electron mínimo sem executar a aplicação.
4. O fallback 6.4.0 permanece instalado e selecionável por `REA_SOURCE_DIR`.
5. Testes R808/R841 continuam passando.
6. Nenhuma ferramenta removida; contrato de `analyze` preservado.

**Resultado:** `93 passed` em `tests/test_r808_rea_bridge.py`,
`tests/test_r808_rea_surface.py` e `tests/test_r841_rea_layers.py`.
`rea status`, `rea catalog` e `rea analyze` foram executados com a instalação
preferencial 6.8.0.

## 6. Limites

- A análise é estática; não prova execução, comportamento dinâmico ou
  autenticidade do alvo.
- Ferramentas nativas externas (Ghidra, IDA, Hopper, Frida, etc.) dependem de
  instalação e configuração próprias; o catálogo não comprova disponibilidade.
- O Node 22.23.1 está abaixo do `engines` declarado; a promoção é operacional,
  não uma declaração de compatibilidade oficial.
- Nenhuma validação externa, revisão de segurança independente ou publicação.
- O fork 6.4.0 é fallback, não é atualizado automaticamente.
