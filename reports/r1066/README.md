# R1066 — REA upstream 6.8.0

**Status:** 6.8.0 promovido a runtime preferencial; fork 6.4.0 preservado como
fallback. Nada foi publicado; não há validação externa.

## Entregue

- `integrations/rea_bridge.py` prefere `~/.local/share/opencode-core/rea-6.8.0`
  e mantém `~/.local/share/opencode-core/rea` como fallback.
- `REA_SOURCE_DIR` continua com precedência.
- Proveniência lida do git remoto ou de `package.json.repository.url`.
- `REPOSITORY` atualizado para `https://github.com/morluto/rea`.
- Testes novos para preferência de diretório e normalização de repositório.
- `docs/REA.md` e `docs/REA_GHIDRA.md` atualizados.
- Fixture Electron mínimo em `reports/r1066/fixture/`.
- Comparação em `reports/r1066/comparison.json` e
  `reports/r1066/tool-diff.json`.

## Instalação

| Item | Upstream 6.8.0 | Fork 6.4.0 |
|---|---|---|
| Origem | `morluto/rea` | `MarceloClaro/rea` |
| Tag/commit | `rea-agents-6.8.0` / `160d821ac9a0310afcb8d1fc427862dd6508add5` | `4daea941bfeeb426886f2d048aed7f3cb2dbf97b` |
| Licença | MIT | MIT |
| Caminho | `~/.local/share/opencode-core/rea-6.8.0` | `~/.local/share/opencode-core/rea` |
| Tamanho | 168 MB | 719 MB |

Instalação do upstream: tarball npm `rea-agents@6.8.0` (já contém `dist/`) e
dependências de produção. O npm 10.9.8 falhou no Arborist com
`Cannot read properties of null (reading 'edgesOut')`; a instalação passou com
`--legacy-peer-deps`.

## Compatibilidade

- `status`: 6.8.0, repositório upstream, runtime no caminho preferencial.
- `catalog`: **229 ferramentas** no upstream contra **170** no fork.
- Diferença: **59 novas, 0 removidas** (`reports/r1066/tool-diff.json`).
- `analyze`: mesmo tool `analyze_javascript_application`, mesmo `input_path`,
  mesmo `subject.digest.sha256` no fixture.
- O upstream acrescenta `route_inventory`; as limitações passam de 7 para 8.
  O fork expõe `statistics.modules`, ausente no upstream.
- `analyze_binary` e as operações de camada não foram executadas nesta rodada;
  os testes herméticos R808/R841 continuam passando.

## Evidência de execução

Fixture `reports/r1066/fixture` (Electron mínimo, 5 arquivos):

```bash
python3 -m marceloclaro.cli rea status
python3 -m marceloclaro.cli rea catalog
python3 -m marceloclaro.cli rea analyze reports/r1066/fixture --timeout 120
```

Resultado da análise em 6.8.0:

- `status=completed`, `success=true`, `tool=analyze_javascript_application`;
- `tool_count=229`;
- `subject.digest.sha256=192b7be6ca7edcb194994af818a45962abaa526d77e79a62d2725dfd3229139f`;
- `limitations=8`;
- `normalized_result` contém `route_inventory`.

Comparação com o fork no mesmo conteúdo (executada em `/tmp`):

| Campo | 6.8.0 | 6.4.0 |
|---|---|---|
| `status` | completed | completed |
| `tool_count` | 229 | 170 |
| `subject.sha256` | `192b7be...` | `192b7be...` |
| `limitations` | 8 | 7 |
| `route_inventory` | presente | ausente |
| `statistics.modules` | ausente | presente |

## Testes

```text
tests/test_r808_rea_bridge.py
tests/test_r808_rea_surface.py
tests/test_r841_rea_layers.py
93 passed
```

## Riscos e limites

- Node 22.23.1 está abaixo do `engines` `^22.23.4`; a execução funcionou, mas
  não é uma compatibilidade oficial. Use `REA_NODE_BIN` para apontar um Node
  que satisfaça o campo.
- O catálogo maior não prova que as ferramentas nativas externas estão
  instaladas.
- Análise estática não prova execução nem comportamento do alvo.
- O fork 6.4.0 permanece como fallback manual; não é atualizado sozinho.
- Nenhuma revisão de segurança independente, validação externa ou publicação.

## Próximo passo

Se o host receber Node 22.23.4+ ou 24.22.1+, repetir `status`, `catalog` e
`analyze` para remover o aviso de engine. Para uma operação binária, verificar
antes a prontidão de Ghidra/IDA/Hopper e registrar a proveniência nativa.
