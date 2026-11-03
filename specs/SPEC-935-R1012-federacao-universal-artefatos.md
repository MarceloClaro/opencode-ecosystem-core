# SPEC-935-R1012 — Federação universal de plugins, MCPs e agentes sob MarceloClaro

**Ronda:** R1012
**Status:** implementado (verificação offline)
**Orquestrador:** `marceloclaro`

## 1. Problema

O Core já colhe artefatos de harness (`integrations/harness_federation`, R621) e
sabe exportar um plugin para o ChatGPT (`integrations/chatgpt_plugin.py`). Falta,
porém, uma operação única que:

1. extraia **plugins, MCPs e agentes** dos quatro ecossistemas reais
   (Claude, ChatGPT/Codex, Antigravity CLI e GitHub);
2. normalize tudo em um só registro com proveniência, licença e hash;
3. aplique triagem fail-closed (licença ausente nunca vira "instalado");
4. gere candidatos MCP **desativados** e só os integre ao `opencode.json` por
   ato explícito do operador;
5. exponha roteamento pelo primário `marceloclaro`.

## 2. Escopo

### 2.1 Fontes (somente leitura, sem rede, sem executar código de terceiros)

| Fonte | Caminho | O que rende |
|---|---|---|
| Claude (mercado oficial) | `~/.claude/plugins/plugin-catalog-cache.json` | 255 plugins e seus componentes (skills, agentes, comandos, hooks, MCPs) |
| Claude (instalados) | `~/.claude/plugins/installed_plugins.json` + `plugins/cache` | vínculo plugin → caminho instalado e definição MCP |
| Claude (marketplaces) | `~/.claude/plugins/marketplaces/*` | `LICENSE`, `plugin.json`, `mcp.json` reais |
| Antigravity CLI | `~/.gemini/antigravity-cli/builtin/skills`, `settings.json` | skills nativas e MCPs declarados |
| ChatGPT/Codex | `~/.codex` (quando existir) + manifesto `federation/chatgpt_sources.json` | plugins Codex e conectores hospedados |
| GitHub | manifesto `federation/github_sources.json` | servidores MCP e plugins curados, com SPDX declarado |

Nada é clonado, compilado ou executado. O manifesto GitHub é declaração
versionada; a ausência de SPDX rebaixa o item, nunca é completada por suposição.

### 2.2 Fora de escopo

- Autenticar em serviços de terceiros ou habilitar MCP com credencial.
- Copiar `scripts/`, `hooks/` ou binários de terceiros para o runtime.
- Declarar que um item "funciona": registro não é execução.

## 3. Modelo de dados

`FederatedItem` — `ecosystem`, `kind`, `name`, `parent`, `description`,
`version`, `license`, `license_scope`, `source_uri`, `source_path`,
`content_sha256`, `capabilities`, `tags`, `install_mode`, `status`,
`reasons`, `runtime_risk`, `metadata`.

Identificador estável: `<ecossistema>:<tipo>:<slug>[@<plugin-pai>]`.

Estados: `admitted`, `quarantined`, `degraded`, `blocked`.

Precedência da triagem (fail-closed):

1. hook/script de terceiro → `blocked` (`third_party_execution`);
2. licença ausente → `degraded` (`license_undeclared`);
3. licença não permissiva (GPL/AGPL/BUSL) → `quarantined` (`license_review_required`);
4. conector hospedado / não instalável → `quarantined` (`not_locally_installable`);
5. autenticação declarada → `quarantined` (`auth_required`);
6. caso contrário → `admitted`.

## 4. Critérios de aceitação

- **R1012-1** — `sync` produz `federation/registry.json`, `report.md`,
  `mcp_candidates.json` e `audit.jsonl`, com digest SHA-256 do conjunto.
- **R1012-2** — toda contagem vem do disco/manifesto; nenhuma constante de
  número de plugins no código.
- **R1012-3** — licença ausente nunca resulta em `admitted`.
- **R1012-4** — hooks e scripts de terceiros nunca são materializados.
- **R1012-5** — candidatos MCP nascem com `enabled: false`; `apply` sem
  `--stage` é dry-run e não escreve arquivo algum.
- **R1012-6** — `apply --stage` grava apenas `federation/mcp_patch.json`;
  **nunca** altera `opencode.json`, e o patch registra a pré-verificação do
  launcher sem alegar que o pacote existe.
- **R1012-7** — segredos em `env`/`headers` de MCP são substituídos por
  marcador; apenas nomes de chave permanecem.
- **R1012-8** — `marceloclaro federation-route` ranqueia artefatos com a quinta
  cabeça de atenção (semântica, capacidade, maturidade, licença), de forma
  determinística e explicável.
- **R1012-9** — `sync` é idempotente: duas execuções sem mudança de fonte
  produzem o mesmo digest.
- **R1012-10** — testes offline cobrem todas as regras acima.

## 5. Invariantes

- **INV-R1012.1** — descoberta ≠ instalação ≠ habilitação ≠ execução.
- **INV-R1012.2** — proveniência e hash acompanham cada item; conteúdo de
  terceiro é dado, não instrução para o orquestrador.
- **INV-R1012.3** — nenhuma operação de rede nesta camada.

## 6. Interface

```
python3 -m marceloclaro.cli federacao sync [--no-write]
python3 -m marceloclaro.cli federacao status
python3 -m marceloclaro.cli federacao list [--ecosystem X] [--kind Y] [--status Z]
python3 -m marceloclaro.cli federacao show <id>
python3 -m marceloclaro.cli federacao candidates
python3 -m marceloclaro.cli federacao apply [--ids a,b] [--stage]
python3 -m marceloclaro.cli federacao route "descrição" [--top N]
python3 -m marceloclaro.cli federacao verify
```

## 7. Evidência de verificação

- `pytest tests/test_federation_sync.py`
- `federation/registry.json` com digest e contagens
- `python3 -m marceloclaro.cli federacao status`

## 8. Correção R1013 — por que `apply` não escreve no config vivo

A primeira versão gravava os 8 candidatos em `opencode.json` com
`"enabled": false`, supondo que o host os ignoraria. A observação real do
host mostrou o contrário: as entradas apareceram como **erro** na lista MCP,
porque a presença no config é uma tentativa de inicialização e os pacotes
(`npx`/`uvx`) não estavam instalados. `mcp-everything` conectou por estar em
cache; os demais falharam.

Correção aplicada:

1. as 8 entradas foram removidas do `opencode.json` (19 MCPs, todos conectados);
2. `federation/applied.json` e a mesclagem em `build_config()` foram removidos;
3. `federacao apply` agora **produz patch** (`federation/mcp_patch.json`) e
   nunca toca o config vivo; a ativação é manual, após instalar o pacote e
   confirmar que o comando responde.

Lição: **registro é tentativa de execução no host**. O gate correto não é
"está no arquivo?", e sim "o pacote existe e o comando responde?" — e essa
segunda pergunta não pode ser respondida por um manifesto.

## 9. R1014 — instalação isolada, prova e ativação com recibo

Autorizada a instalação dos oito servidores, o fluxo passou a ser:

1. **instalar** em `.opencode/mcp/federated/` (fora do global), com versão
   fixada e `npm --ignore-scripts` — nenhum postinstall de terceiro executa;
2. **provar** `initialize` + `tools/list` (`federacao probe`);
3. **ativar** só o que provou (`federacao activate`), gravando
   `federation/activated.json`;
4. **regenerar** `opencode.json` a partir desse arquivo;
5. **fumar** uma ferramenta real por servidor (`federacao smoke`);
6. **auditar** binário e recibo (`federacao doctor`).

Achados reais que o processo precisou tratar:

| Servidor | Achado | Correção |
|---|---|---|
| `chroma` | `mcp==1.6.0` quebra com `pydantic ≥ 2.12` (`eval_type_backport`) | `pydantic<2.12` no venv isolado |
| `qdrant` | primeira inicialização baixa FastEmbed do HF; timeout de 60 s matava o handshake | `QDRANT_LOCAL_PATH` + timeout de 240 s na primeira prova |
| `playwright` | postinstall do npm tenta Chromium e falha em `ubuntu26.04-x64` | `--ignore-scripts` + `playwright install chromium` explícito |
| `chroma`/`qdrant` | venvs incompatíveis entre si | um venv por servidor Python |

Critérios:

- **R1014-1** — instalação nunca usa `sudo` nem diretório global; versões fixadas.
- **R1014-2** — sem `probe ok`, `activate` recusa e registra o motivo.
- **R1014-3** — `activated.json` é a única fonte de MCPs federados no
  `opencode.json`; `build_config()` o reproduz.
- **R1014-4** — `smoke` chama uma ferramenta por servidor e grava recibo com
  resultado, duração e erro.
- **R1014-5** — `doctor` reprova binário ausente ou recibo ausente.
- **R1014-6** — navegador roda headless e com perfil isolado; cookies não
  persistem entre sessões.

## 10. Correção R1015 — recibo de transporte não é prova de execução correta

A auditoria posterior encontrou recibos R1014 com `ok: true` e resposta
`isError: true` (Qdrant e Playwright). As afirmações históricas de "oito
smokes saudáveis" estão **retificadas**: algumas chamadas ocorreram, mas
retornaram erro de ferramenta. O contrato novo está em
`SPEC-935-R1015-mcp-activation-health-profile.md`: receipts v2 vinculados ao
comando, ambiente, bytes do launcher e manifesto da versão instalada,
frescor de 24 h e diagnóstico fail-closed. Servidores opcionais permanecem
instalados, mas não integram o perfil padrão. Os testes negativos de R1015
demonstram falhas no código anterior (RED); o estado operacional posterior
depende do novo probe/smoke e de uma nova inspeção do host, nunca desta nota.
