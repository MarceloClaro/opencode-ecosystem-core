---
name: federacao-universal
description: >-
  Federar plugins, MCPs e agentes de Claude, ChatGPT/Codex, Antigravity CLI e
  GitHub sob o primário MarceloClaro (SPEC-935-R1012). Use para inventariar o
  que existe nas máquinas, triar licença/execução, gerar candidatos MCP
  desativados e rotear artefatos para uma tarefa. Nunca instala código de
  terceiro silenciosamente, nunca habilita MCP sem confirmação e nunca trata
  registro como prova de execução.
---

# Federação universal de artefatos (SPEC-935-R1012)

## Quando usar

- O usuário pergunta "o que existe de plugin/MCP/agente instalado?".
- É preciso reaproveitar uma skill/agente de outro harness sem copiar às cegas.
- Uma tarefa pede um MCP que ainda não está no `opencode.json`.
- É preciso auditar licença e proveniência antes de adotar artefato externo.

## Comandos

```bash
python3 -m marceloclaro.cli federacao sync            # coleta e grava federation/
python3 -m marceloclaro.cli federacao status          # digest, contagens, caminhos
python3 -m marceloclaro.cli federacao list --status admitted --kind mcp
python3 -m marceloclaro.cli federacao show <id>
python3 -m marceloclaro.cli federacao candidates      # MCPs desativados
python3 -m marceloclaro.cli federacao apply           # dry-run
python3 -m marceloclaro.cli federacao apply --stage   # grava patch, não toca opencode.json
python3 -m marceloclaro.cli federacao install         # mostra a instalação isolada
python3 -m marceloclaro.cli federacao probe           # initialize + tools/list
python3 -m marceloclaro.cli federacao activate        # perfil padrão (6); exige probe + smoke recentes
python3 -m marceloclaro.cli federacao activate --ids mcp-everything  # opcional, após probe/smoke
python3 -m marceloclaro.cli federacao smoke           # chama 1 ferramenta por servidor
python3 -m marceloclaro.cli federacao doctor          # versão/hash, comando, frescor e smoke
python3 -m marceloclaro.cli federacao route "extrair texto de pdf" --top 5
python3 -m marceloclaro.cli federacao verify          # integridade do digest
```

## Regras invioláveis

1. **Descoberta ≠ instalação ≠ habilitação ≠ execução.** Relate cada etapa
   separadamente; nunca diga que um MCP "funciona" porque foi registrado.
2. **Licença ausente rebaixa para `degraded`.** Não complete SPDX por
   suposição; não materialize conteúdo sem licença declarada.
3. **Hooks e scripts de terceiro ficam `blocked`.** O Core não os executa.
4. **Candidato MCP nasce `enabled: false` e só existe como patch.** `apply`
   grava `federation/mcp_patch.json`; nunca altera `opencode.json`. A ativação
   é manual, depois de instalar o pacote e confirmar que o comando responde.
   Credenciais nunca são copiadas (`env_keys` apenas).
5. **Registro no config é tentativa de inicialização.** Entrada MCP sem pacote
   instalado aparece como erro no host, mesmo desativada (lição R1013). Não
   prometa conexão a partir de manifesto.
6. **Roteamento** usa a quinta cabeça de atenção (semântica, capacidade,
   maturidade, licença) e devolve a decomposição do score.
7. **Ativação exige duas provas recentes.** `probe` + `smoke` sem `isError`,
   com hashes do binário e do manifesto, versão instalada e comando/ambiente
   correspondentes, emitidos há até 24 h. Recibos legados são inválidos.
   `doctor` degrada em falha; `build_config()` omite entradas inválidas.
   Não edite `opencode.json` à mão. Expiração exige revalidar e regenerar.
8. **Instalação é isolada e sem postinstall.** `npm --ignore-scripts`, versões
   fixadas, um venv por servidor Python; navegador só com `playwright install`
   explícito e perfil `--isolated`.
9. **Perfil seletivo é reversível.** `mcp-everything` (demo) e
   `executeautomation-playwright` (alternativo lento) continuam instalados,
   mas são removidos da ativação padrão. Após `probe --ids X` e `smoke --ids X`,
   use `activate --ids X` e regenere o config para reativar.

No checkout Ubuntu 26.04 observado, o Playwright alternativo 1.57.0 não
suporta essa plataforma durante `install chromium`. A revisão **1200** foi
instalada usando a variável upstream `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64`
e o CLI local `node .opencode/mcp/federated/node/node_modules/playwright/cli.js install chromium`.
Isso é fallback **não oficialmente suportado**; só o smoke real posterior
(`playwright_navigate` em `about:blank`, sem `isError`) autoriza reativação.
O navegador principal usa outra revisão: `playwright-mcp install-browser chrome-for-testing`.

## Curadoria de repositórios

Para o registro de commits, licenças e decisões da rodada R1023, leia
[Curadoria R1023 — federação de repositórios](references/curadoria-r1023.md).
O manifesto correspondente é `federation/repository-curation-r1023.json`.
Ele documenta leitura, não instalação; nenhum item foi clonado ou executado.

## Limites

- A etapa `sync` não acessa a rede; `probe`/`smoke` podem acessar serviços
  públicos conforme a ferramenta testada. O manifesto GitHub é declaração
  versionada, não verificação ao vivo.
- Hash e idade do recibo não autenticam proveniência remota nem transitivas;
  não asseguram saúde contínua após a geração do config.
- Conectores hospedados do ChatGPT são referência de capacidade
  (`install_mode: external`), não instaláveis localmente.
- Contagem não é certificação; proveniência não é parecer jurídico.
