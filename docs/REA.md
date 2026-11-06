# REA no OpenCode Ecosystem Core

O REA está integrado ao orquestrador `marceloclaro` pela ferramenta
`ecosystem_rea`, pelo comando OpenCode `/rea` e pela CLI do Core.
O servidor `rea` expõe também o catálogo MCP completo. A skill
`reverse-engineer-anything` e suas referências acompanham a versão instalada.

## Uso

No OpenCode:

```text
/rea analisar a aplicação JavaScript em /caminho/absoluto/app e explicar suas dependências com evidências
```

No terminal WSL, a partir da raiz do Core:

```bash
.venv/bin/python -m marceloclaro.cli rea status
.venv/bin/python -m marceloclaro.cli rea catalog
.venv/bin/python -m marceloclaro.cli rea session
.venv/bin/python -m marceloclaro.cli rea analyze /caminho/absoluto/app --timeout 60
```

Na ferramenta `ecosystem_rea`:

```json
{"config": {"operation": "analyze", "path": "/caminho/absoluto/app", "timeout_seconds": 60}}
```

`status` confere a instalação; `catalog` faz initialize/tools/list;
`session` chama `binary_session`; `analyze` chama
`analyze_javascript_application` sem executar a aplicação. O prazo máximo da
ponte coordenada é 180 segundos. Erros e indisponibilidade retornam sucesso
falso; a CLI retorna código diferente de zero. A CLI conserva Evidence integral.
No MCP coordenado, a resposta completa é gravada em
`.opencode/rea/evidence/<sha256>.json`; o modelo recebe resumo com estatísticas,
limitações e caminho/hash do arquivo. O MetaBus recebe observação, sem promoção
de confiança. O catálogo no gateway mostra nomes, com schemas integrais no
arquivo indicado.

As ferramentas diretas `rea_*` ficam ocultas por padrão nos agentes para
respeitar o contexto dos modelos locais. O servidor continua registrado e
conectado; outras operações podem ser expostas seletivamente na configuração
de um agente, usando nomes atuais do catálogo. Esse filtro segue a
[gestão de ferramentas MCP do OpenCode](https://opencode.ai/docs/mcp-servers/#per-agent).

## Instalação identificada

- Origem preferencial: [morluto/rea](https://github.com/morluto/rea), upstream
  oficial do pacote `rea-agents`.
- Tag: `rea-agents-6.8.0`; commit `160d821ac9a0310afcb8d1fc427862dd6508add5`.
- Pacote: `rea-agents` 6.8.0; licença MIT preservada.
- Runtime preferencial: `~/.local/share/opencode-core/rea-6.8.0`, com o tarball
  npm e dependências de produção.
- Fallback preservado: `~/.local/share/opencode-core/rea`, fork
  [MarceloClaro/rea](https://github.com/MarceloClaro/rea) 6.4.0, commit
  `4daea941bfeeb426886f2d048aed7f3cb2dbf97b`.
- Neste host: Node.js 22.23.1, npm 10.9.8. O upstream declara
  `^22.23.4 || ^24.22.1 || >=26.12.1`; a versão 6.8.0 foi testada com
  22.23.1, mas o runtime ideal é um Node que satisfaça o campo `engines`.
- Seleção: `REA_SOURCE_DIR` tem precedência; sem ele, a ponte prefere
  `rea-6.8.0` e usa `rea` como fallback. `REA_NODE_BIN` escolhe outro Node.

Para reproduzir em outro host com Node suportado:

```bash
mkdir -p /tmp/rea-install ~/.local/share/opencode-core/rea-6.8.0
cd /tmp/rea-install
npm pack rea-agents@6.8.0
tar -xzf rea-agents-6.8.0.tgz
cp -a package/. ~/.local/share/opencode-core/rea-6.8.0/
cd ~/.local/share/opencode-core/rea-6.8.0
npm install --omit=dev --ignore-scripts --legacy-peer-deps --package-lock=false
cd /caminho/para/opencode-ecosystem-core
python3 -m integrations.opencode_cli
```

O `--legacy-peer-deps` evita um erro do Arborist/npm 10 ao resolver peers
deste pacote; com npm 11.16.0 (declarado em `packageManager`) a instalação
normal deve funcionar. O pacote npm já traz `dist/`; não é necessário compilar
TypeScript no host.

Reinicie ou reconecte o OpenCode após modificar seus servidores MCP.
Nenhum setup global de Codex, Claude ou Antigravity é necessário à ponte
coordenada deste projeto. O comando de inicialização registrado é
`.venv/bin/python -m integrations.rea_bridge mcp`.

## Escopo e evidências

O catálogo completo pode incluir ferramentas indisponíveis neste host.
`binary_session` distingue essas condições. Análise JavaScript estática não
exige Hopper, Ghidra ou IDA; análise nativa depende desses providers.
Ferramentas de runtime ou navegador têm efeitos diferentes e seguem a
autorização da tarefa concreta. Não são acionadas implicitamente pela ponte
estática. Para revisão comum de um repositório com fontes completas, use as
ferramentas usuais de código, conforme a própria skill upstream.

Uma resposta completa acima do limite MCP do REA pode falhar com
`resource_constraint`; escolha um escopo menor para análise estática. A ponte
conserva essa falha e não troca silenciosamente Evidence por referências retidas
numa sessão que será encerrada.

As provas executadas e os achados da revisão estão em
[revisão R808/R809](REVISAO_ECOSSISTEMA_R808.md). Testes com transportes
simulados e execução MCP real são registrados separadamente.
