# SPEC-935-R1015 — Gate de ativação e perfil MCP seletivo

**Orquestrador:** marceloclaro · **Estado:** implementado e testado localmente;
revisão externa indisponível nesta sessão.

## Objetivo e limites

Endurecer a ativação dos oito MCPs federados do R1014 sem alterar nem apagar o
trabalho pré-existente. Binário instalado e `ok: true` antigos **não** são
prova suficiente. Reduzir a exposição padrão: `mcp-everything` e
`executeautomation-playwright` continuam instalados e reativáveis mediante
`activate --ids ...`, mas não pertencem ao `activate` sem `--ids` nem ao perfil
ativo após esta migração. Não migrar a configuração inteira ao OpenCode V2.

## Contrato de segurança

1. Um recibo novo registra identificador de servidor, versão do pacote
   **instalado** (não só a versão declarada), hash SHA-256 do manifesto local e
   dos bytes do executável resolvido, comando integral e ambiente local
   declarado. O processo de coleta não executa código para apurar a versão.
   Symlink fora do diretório isolado é recusado. Não se afirma integridade de
   transitivas, origem remota, comportamento futuro ou resistência a um
   invasor que possa editar o repositório e os recibos.
2. `probe` e `smoke` gravam o mesmo vínculo; `smoke` só é considerado sucesso se
   a resposta JSON-RPC não tiver `error` e o resultado não tiver
   `isError: true`. Resposta de erro de ferramenta não é sucesso de saúde.
   No smoke, guardar instrumento e argumentos, além de `result_excerpt`.
3. `activate` exige recibos de probe **e** smoke novos, para o servidor
   requisitado, sem erro, com identidade idêntica à instalação atual e ao
   contrato, com timestamp UTC válido não futuro e idade máxima de 24 h.
   Recibos R1014 sem vínculo são inválidos: reexecutar probe/smoke, nunca
   converter `ok: true` retroativamente. Erro de um servidor não remove outros
   servidores já ativos. Operação sem `--ids` só tenta o perfil padrão, mas
   preserva opcionais explicitamente ativos. Na migração, removê-los com
   `deactivate --ids ...` antes da regeneração.
4. `doctor` reprova ausência, erro, expiração ou divergência de identidade de
   binário/pacote/comando/ambiente em quaisquer servidores ativados; reporta
   código de falha específico. O gerador não deve copiar entrada arbitrária
   de `activated.json` para o config: somente entradas cujos recibos passaram
   no mesmo gate, com `digest` íntegro cobrindo **entradas e proveniência**
   no schema v2, podem ir ao perfil ativo. A verificação
   não inicia processos nem prova saúde contínua; depois de 24 h o operador
   deve reexecutar probe/smoke e `activate`.
   Um `activated.json` v1 íntegro pode ser lido só para migração via `activate`;
   até então `doctor` degrada e o gerador não o importa ao config.
5. `deactivate --ids` e `activate --ids` preservam as outras entradas. O
   perfil reduzido é reversível sem reinstalação; os dois servidores de
   demonstração/alternativos permanecem no catálogo e seus arquivos locais.
   `opencode.json == build_config()` após regeneração. Perfil tem escopo
   somente dos MCPs federados; os MCPs históricos não são reconfigurados.
6. Não armazenar segredos em recibos. Os valores atuais de `env` são apenas
   caminhos locais. Qdrant deve receber seu ambiente local também no config,
   não apenas no processo de probe/smoke. Seu teste real escreve somente uma
   sentinela técnica sem dados pessoais na coleção local
   `core_federation_smoke`; o smoke do navegador usa `about:blank`. Respostas
   do MCP de memória são omitidas do recibo para não divulgar o grafo local.
   O servidor que gravar artefatos no diretório de trabalho do smoke deve
   usar um diretório temporário próprio, não poluir o checkout.

## Aceites testáveis (RED → GREEN → REFACTOR)

- **R1015-1:** recibo forjado `ok: true`, sem vínculo, com nome/comando/versão
  divergente, binário alterado, symlink escapado ou manifesto alterado é
  rejeitado na ativação e no diagnóstico.
- **R1015-2:** timestamp ausente, futuro, ilegível ou com idade >24 h é
  rejeitado (relógio injetável em testes, sem espera real).
- **R1015-3:** smoke ausente/`isError`/falha JSON-RPC reprova gate; o probe
  sozinho não basta. Recibos de smoke devem provar a ferramenta esperada.
- **R1015-4:** ativação parcial e falha preservam todos os não requisitados;
  `activate()` padrão exclui os dois opcionais; `--ids` reativa ambos.
- **R1015-5:** geração do config filtra registro inválido e reproduz o arquivo
  depois de aplicar o perfil seletivo; nenhum pacote é desinstalado.
- **R1015-6:** novos testes negativos executados e registrados em RED,
  depois GREEN; regressões e `doctor` do Core passam. Estado do host, quando
  consultado, é relatado como observação pontual, não garantia perpétua.

## Estratégia de migração

Criar recibos novos via `federacao probe` + `federacao smoke`, ativar somente
servidores que comprovarem o uso real. Se algum opcional ou servidor padrão
falhar, **não** marcá-lo como saudável; preservar instalado e publicar o
bloqueio. Depois atualizar `activated.json` sem os dois opcionais, regenerar o
config, validar regressão e conferir o estado observado do host.

## Evidência observada na rodada (01/11/2026)

- RED reproduzido antes da correção: 18 falhas/1 sucesso em
  `tests/test_r1015_mcp_hardening.py` (recibos forjados/antigos, falta de
  smoke, `isError: true`, perda de ativações), seguidos de falhas negativas
  adicionais para digest da proveniência, migração v1 e artefato no cwd.
- GREEN final: **88 testes** nos arquivos `test_r1015_mcp_hardening.py`,
  `test_federation_runtime.py`, `test_federation_sync.py`, R137, R618, R448
  e R455. `doctor` do Core: `healthy`/22 checks; diagnóstico da federação:
  `ok`/6 ativos/0 issues; `integrations.opencode_cli --check`: 329 agentes,
  25 MCPs no arquivo, 35 comandos; reconciliação documental sem divergência.
- Mudança pontual do config comparado ao backup: removidos somente
  `mcp-everything` e `executeautomation-playwright`; `qdrant` recebeu
  `environment.QDRANT_LOCAL_PATH` e `playwright` passou a usar
  `--browser chromium`. As demais entradas mantiveram o mesmo conteúdo.
  **R1020 posterior:** o Qdrant foi migrado para servidor HTTP único em
  `127.0.0.1:6333`; `QDRANT_LOCAL_PATH` não é mais usado, porque o lock local
  falhava com duas sessões do OpenCode.
- `opencode mcp list` observou **26 conexões** sem erro: 25 no arquivo de
  projeto e `opencode_console` adicional no host. Os dois opcionais não
  aparecem no perfil, mas ambos passaram em `probe` e `smoke` v2 e seguem
  instalados. `qdrant-find` pelo host achou somente a sentinela técnica na
  coleção local `core_federation_smoke`.
- O Playwright principal só passou após instalar Chrome for Testing revisão
  1252; o alternativo exigiu Chromium 1200. A instalação 1.57.0 não suporta
  Ubuntu 26.04; a revisão 1200 foi baixada com
  `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` **não oficial** e
  passou em smoke real (`about:blank`); não há garantia para outros ambientes.
- A revisão delegada ao agente `auditor` falhou antes de produzir parecer
  (`Insufficient account funds`); houve reflexão no MetaBus, não revisão
  independente. O gate local não autentica assinaturas de pacotes,
  dependências transitivas, navegador em cache, nem protege contra um invasor
  com escrita no repositório e nos recibos. Não há medição de economia de
  contexto ou desempenho de produção nesta rodada.
