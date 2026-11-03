# Revisão R1016 — skills audiovisuais

**Data:** 1º de novembro de 2026.
**Escopo:** dez skills de projeto em `.claude/skills/`; correção do MCP `chroma`;
referências Remotion e Hypit.
**Natureza:** revisão local e revisão assistida por executor externo. Não é
parecer jurídico, auditoria independente, validação de runtime ou revisão humana.

## 1. O que foi instalado

- Sete skills `cp-*` do pacote `biblioteca ai/skills (1).zip`, com `SKILL.md`,
  `references/` e `agents/openai.yaml`.
- Três skills `meia-*` escritas a partir do Apêndice C de “Máquina de Edição IA”:
  `meia-briefing-de-edicao`, `meia-legendas-e-enquadramento` e
  `meia-revisao-economia`.
- Referências adicionais em `cp-direcao-de-edicao`: `remotion-cli-e-api.md` e
  `ecossistema-hypit.md`.

## 2. Correção do erro global do MCP

**Sintoma:** `ecosystem_integration_status` retornava `status: error` com
`mcp_command_invalid` para `chroma`.

**Causa:** a entrada `chroma` em `integrations/federation_sync/runtime.py`
passava `--dotenv-path ""`; o validador rejeita argumento vazio.

**Correção:** removido o argumento vazio; `probe` e `smoke` reexecutados para
`chroma` (13 ferramentas, protocolo 2024-11-05, smoke
`chroma_list_collections`); `federacao activate --ids chroma` atualizou
`federation/activated.json`; `opencode.json` regenerado.

**Resultado observado:** `ecosystem_integration_status` passou a
`config_checked`, com 25 MCPs e **zero issues**. `federacao doctor` reportou seis
servidores ativos com probe/smoke válidos. Isso confirma configuração e recibos
locais; não prova disponibilidade futura de cada processo.

## 3. Revisão externa assistida

O executor Claude foi tentado primeiro, mas recusou por limite/saldo da conta.
O Codex foi usado como alternativa. A leitura direta de arquivos foi bloqueada
pela política do ambiente; o conteúdo dos dez `SKILL.md`, da spec e do teste foi
transcrito na solicitação, e o parecer abaixo se limita a esse conteúdo.

### Achados e providências

1. **Teste de salvaguardas aceitava fragmentos lexicais** — providência:
   exigir cláusulas específicas (`preserve os arquivos originais`,
   `não sobrescreva`, `não envie`, `serviços externos`, `autorização
   específica`) e seção `Salvaguardas adicionais`. A limitação lexical
   permanece documentada.
2. **Falta de preservação/sobrescrita em alguns `cp-*`** — providência: seção
   universal acrescentada às dez skills.
3. **Falta de restrição explícita a serviços externos gratuitos** — providência:
   a mesma seção exige autorização específica para transferência, independente
   de cobrança.
4. **Detecção de dados pessoais limitada** — providência: regex para e-mail,
   CPF e padrões de segredo; a detecção continua limitada a marcadores
   conhecidos.
5. **Testes de contrato são lexicais** — providência: mantidos como verificação
   básica; a spec declara que presença de termos não prova semântica nem
   ausência de sobreposição.
6. **Frontmatter e links não eram validados** — providência: `yaml.safe_load`
   para `SKILL.md` e `agents/openai.yaml`; resolução de links relativos em todos
   os `.md`.
7. **Extratora não tratava pacote existente da mesma fonte** — providência:
   exigir nova versão/diretório e autorização antes de substituir resultados
   anteriores.
8. **Evidência da spec não distinguia importação e adaptação** — providência:
   seção “Adaptações em relação ao pacote fornecido” e contagens atualizadas.

### O que não foi comprovado

- Carregamento das skills em Claude Code ou OpenCode em runtime.
- Execução de edição, render ou exportação de vídeo.
- Qualidade estética, desempenho, custo, licença ou adequação jurídica.
- Funcionamento do Hypit ou do Remotion no ambiente local.
- Revisão humana independente.

## 4. Remotion

As referências citadas nas skills foram confrontadas com a documentação oficial
fornecida em 1º/11/2026. Foram registrados:
`npx create-video@latest --yes --blank my-video`, `npx remotion skills add`,
`npx remotion render HelloWorld`,
`npx remotion render --codec=vp8 HelloWorld out/video.webm` e
`npx remotion still --props='{"custom":"data"}' my-comp out.png`.

O endereço `https://www.remotion.dev/docs/cli/` retornou 404; os comandos foram
confirmados em páginas oficiais equivalentes. Nenhum comando foi executado.
A licença do Remotion tem condições específicas e pode exigir licença
empresarial; consulte a versão vigente.

## 5. Hypit

O repositório `hypit-ai/hypit` foi consultado, mas **não foi instalado,
autenticado nem executado**. A licença é uma versão modificada da Apache 2.0 com
condições para serviço multi-tenant, redistribuição comercial e preservação de
marca/copyright. Os artefatos produzidos pertencem ao usuário; modelos e
serviços de terceiros podem ter termos próprios. O comando indicado pelo projeto
é `npx skills add hypit-ai/hypit -g`, que instala uma skill global e exige
autorização explícita.

## 6. Verificação local

- `python3 -m pytest -q tests/test_r1016_cp_skills.py`: **23 passed**.
- `TDDHistory` RED/GREEN e `SpecVerifier`: **5/5 critérios**, gate
  `software_delivery_gate`, RED/GREEN válidos, em worktree isolada.
- **28 arquivos** de skill comparados byte a byte entre worktree e checkout.
- `python3 -m marceloclaro.cli doctor`: **healthy**, 22/22 verificações.
- `ecosystem_integration_status`: **config_checked**, zero issues.

## 7. Qdrant MCP: do lock local ao servidor HTTP

**Sintoma:** o MCP `qdrant` falhava com “Storage folder ... is already accessed by
another instance of Qdrant client” ao ser iniciado pelo OpenCode, embora
`probe` e `smoke` isolados passassem.

**Causa:** o modo local embarcado do Qdrant usa lock exclusivo no diretório
`.opencode/mcp/federated/data/qdrant`. Duas sessões/instâncias do OpenCode
competindo pelo mesmo diretório fazem a segunda falhar. O lock não era um
arquivo órfão simples; a correção durável é um servidor Qdrant único.

**Correção aplicada:**
- imagem `docker.io/qdrant/qdrant:latest` (ID `8a80c5500151`) executada em
  Podman rootless;
- container `qdrant-core`, porta `127.0.0.1:6333`, volume persistente em
  `.opencode/mcp/federated/data/qdrant-server`;
- unidade systemd de usuário
  `~/.config/containers/systemd/qdrant-core.container`, com `linger=yes`;
- telemetria desativada (`QDRANT__TELEMETRY_DISABLED=true`);
- MCP `qdrant` migrado de `QDRANT_LOCAL_PATH` para
  `QDRANT_URL=http://127.0.0.1:6333`;
- `probe`, `smoke` e `activate` reexecutados; `opencode.json` regenerado.

**Resultado observado:** `healthz check passed`, coleção
`core_federation_smoke` preservada, `opencode mcp list` com
`qdrant connected`, `federacao doctor` com seis servidores e zero issues.

## 8. Cadeia de modelos do primário

Decisão do operador: o agente `marceloclaro` usa
`ollama-cloud/deepseek-v4.1-flash` como cabeça e declara, nesta ordem,
`openai/gpt-6.1-sol`, `opencode-go/deepseek-v4.1-flash` e
`opencode-go/deepseek-v4-pro` como alternativas. O modelo global permanece
`ollama-local/llama3.2` e os demais agentes não foram alterados. A cadeia é
declarativa: não foi medida uma troca real de executor, latência ou custo.

## 9. Limites

A revisão externa foi assistida por modelo, com conteúdo transcrito e sem acesso
aos arquivos auxiliares completos. Ela não substitui auditoria independente,
teste de runtime, revisão jurídica ou avaliação humana. O gate local verifica
estrutura, links, YAML e cláusulas textuais; não prova que as instruções são
suficientes para toda edição real.
