# Prontidão local do Core — R868

Este documento descreve os caminhos de uso e a evidência local disponível em
13 de outubro de 2026. A prontidão depende da operação solicitada, do serviço
ativo e do contrato aplicável. A suíte consolidada concluiu com 7.204 aprovações, 65 skips e nenhuma falha
ou erro. O quadro de entrega registra o escopo testado e os limites restantes.

## O que está demonstrado

| Verificação | Evidência disponível | Alcance |
| --- | --- | --- |
| Diagnóstico estrutural | [Resumo sanitizado](evidencias-r868/diagnostico-e-catalogo.json): `healthy`, 22 checks aprovados, `installation_only` | Especificações, configuração e componentes encontrados naquele diagnóstico; não comprova inferência ou execução de todos os agentes |
| Sonda Ollama local | [Snapshot do catálogo](evidencias-r868/diagnostico-e-catalogo.json): catálogo com 9 modelos, `http_model_catalog_only`, `inference_verified=false` | Resposta HTTP e catálogo naquela sonda anterior; não comprova carregamento ou resposta de cada modelo |
| Inferência de modelo em endpoint local | [Resumo da sonda](evidencias-r868/sonda-inferencia-local.json): resposta de `llama3.2:latest` registrada | O processo de modelo não teve sua rede isolada ou seu tráfego externo observado; endpoint loopback não comprova ausência de saída externa |
| Análise estática direta pela CLI | [Prova controlada](evidencias-r868/analise-direta-controlada.json): inspeção e explicação com código zero, HTML de 115 bytes, 2 achados, alvo intocado e worker com somente loopback | Caminho direto sem LLM, nesse alvo controlado; não comprova todos os formatos ou provedores |
| Status do MCP REA no cliente instalado | [Resumo das chamadas](evidencias-r868/mcp-e-tentativas.json): `core_rea_status` concluiu, instalação disponível e guard aprovado | Confirma status e isolamento do worker; nenhum alvo foi analisado por essa chamada |
| Tentativas de análise conduzidas por LLM | [Resumo das falhas](evidencias-r868/mcp-e-tentativas.json): argumentos inválidos na tentativa inicial; outra saída sem recibo foi bloqueada; tentativa Qwen excedeu 300 segundos | Falhas observadas, sem entrega analítica aceita; não demonstram assistente LLM autônomo funcional em todos os alvos |
| Contratos do diagnóstico | [Resumo de testes](evidencias-r868/testes-e-ci.json): 60 testes aprovados no conjunto R863 executado | Contratos R863 e regressões específicas do doctor |
| Relatório de CI | [Resumo de testes e JUnit](evidencias-r868/testes-e-ci.json): 51 testes aprovados no conjunto R866 executado | Parser, workflow declarado e regressões específicas; não é execução remota do GitHub Actions |

Os recibos públicos acima são resumos pequenos sanitizados, preparados para
versionamento em [evidencias-r868](evidencias-r868/README.md). Conservam hashes das
fontes utilizadas, sem copiar logs, prompts, caminhos privados ou credenciais.
Sanitização e hash não conferem autenticação externa. Os recibos canônicos históricos permanecem preservados. Tentativas interrompidas
e incidentes de execução não são contabilizados como aprovação.

A tentativa inicial com OpenCode teve erro no argumento `kind` e tentou explicar
um recibo inexistente. Seu encerramento com código zero e a conclusão textual
produzida pelo modelo não estabeleceram sucesso analítico. O gate atual impede
publicar esse texto como análise aceita. A evidência analítica do quadro é a
execução direta controlada, separada da conversa e da chamada de status.

## Entrada principal e modelo

O primário é `marceloclaro`. A configuração gerada atualmente seleciona
`ollama-local/llama3.2` como modelo padrão do Core, com provedor Ollama local.
O modelo do perfil privado dedicado do assistente REA é escolhido no setup e
pode mudar durante sondagens. Escolha um modelo instalado e servido no endpoint
loopback; este documento não fixa esse perfil temporário. Confira as fontes em
[opencode.json](../opencode.json),
[gerador da configuração](../integrations/opencode_cli.py) e
[lançador do assistente](../integrations/rea_assistant.py).

Na raiz do repositório, os comandos a seguir consultam estados distintos:

```bash
.venv/bin/python -m marceloclaro.cli doctor
.venv/bin/python -m marceloclaro.cli doctor --live
.venv/bin/python -m marceloclaro.cli network status
.venv/bin/python -m marceloclaro.cli rea agent --check
```

`doctor` é estrutural por padrão. `doctor --live` executa sondagens explícitas
de HTTP, CLIs e exemplos internos; um aviso sobre componente opcional precisa
ser lido no seu próprio contexto. A sonda Ollama executa GET local com limite
de tempo e tamanho, recusa proxy herdado e redirects e informa indisponibilidade
tipada. Nenhum GET do catálogo equivale a inferência.

`network status` distingue executores instalados, elegibilidade automática e
última execução observada. Uma CLI instalada não confirma login, saldo ou uma
nova inferência bem-sucedida. O comando `rea agent --check` confere a configuração
resolvida no OpenCode e mantém `model_inference_verified=false`.

## Operação REA com evidência

Para inspecionar um artefato e ler sua explicação, utilize o caminho direto:

```bash
.venv/bin/python -m marceloclaro.cli rea inspect CAMINHO --kind auto --format text
.venv/bin/python -m marceloclaro.cli rea explain RECIBO --format text
```

`CAMINHO` e `RECIBO` são campos a substituir por dados locais. A operação
`inspect` usa o worker analítico com namespace privado de rede e PID; a aplicação
alvo não é executada. O recibo registra alvo, hash, achados do provedor e limites.
O isolamento de rede não é uma sandbox universal do sistema de arquivos.

No fluxo `rea agent --prompt`, a resposta pública de análise exige uma chamada
de ferramenta concluída e um recibo local válido. O lançador relê o recibo,
confere sua integridade e o escopo da inspeção e publica a explicação derivada
desse dado. Texto livre produzido pelo modelo não se transforma em achado ou
evidência. Uma chamada somente à ferramenta de status pode confirmar prontidão,
com `executed_readiness_tool_only` e `verified_target_analysis=false`; isso não
é análise de um alvo. Falta de recibo válido bloqueia a alegação de análise.

O modo interativo `rea agent` é exploratório. Seu encerramento informa
`client_exit_only`: código de saída zero do cliente não comprova inferência,
correção da conversa ou análise executada. Examine os recibos das ferramentas.
Os indicadores `model_inference_verified=false` do lançador não são promovidos
pela presença de texto em uma resposta.

O cliente e o servidor de modelo precisam permanecer locais. Um cliente que
envia posteriormente alvos ou resultados à nuvem fica fora do escopo deste
perfil. Veja o [guia do assistente REA](ASSISTENTE_REA_LOCAL.md) para setup,
formatos e limites. A ponte legada `rea layer` conserva seu próprio contrato e
não aplica automaticamente o namespace da operação `inspect`.

## Coordenação e componentes opcionais

Tarefas coordenadas passam pelo primário, Blackboard e MetaBus. A execução real
registrada no [resumo final](evidencias-r868/verificacao-final.json) usou o
primário compartilhado, criou a especificação antes da tarefa e obteve `15`
para `8 + 7` pelo Codex em 9,303 segundos. O executor operou somente com leitura
e nenhum alvo REA foi fornecido; esse resultado demonstra esse caminho de
coordenação, sem medir a capacidade geral de todos os executores. A rede executa
análise e texto com leitura, orçamento finito e conclusão sujeita ao gate SDD.
Informe uma especificação válida em `--spec` ou `spec_id`, conforme a superfície
utilizada. Entregas de software exigem os testes e o histórico RED requeridos
pelo contrato; não desative o gate para fazer uma tarefa passar. Workflows
conservam checkpoints e dependências e exigem autorização explícita para repetir
etapas falhas. Consulte o [guia de workflows](WORKFLOWS_R644.md).

Presença no inventário, prontidão e execução são estados diferentes. IDA e JEB
são opcionais e continuam dependentes de instalação, configuração e licença.
Hopper também é comercial e sua evidência específica não comprova todas as
operações nativas. Ghidra, ferramentas de extração e outras camadas precisam ser
avaliados na operação e no formato solicitados. Licenças de artefatos federados,
autenticação de serviços e saldo dos executores não são resolvidos pela mera
presença de arquivos ou binários.

## CI e entrega consolidada

O [workflow de CI](../.github/workflows/ci.yml) declara Node 22, `npm ci` com o
lockfile de `.opencode` e uma execução de pytest por versão Python. Pytest grava
JUnit; o [relatório de qualidade](../scripts/quality_report.py) lê esse arquivo
sem repetir a suíte e preserva falhas, erros e skips. Modo quick e bateria
somente com skips recebem `NOT_RUN`, sem medição de aprovação inventada.

A leitura local do JUnit histórico reutilizado registrou 7.074 aprovações e
65 skips em 7.139 testcases físicos. O agregado pytest informou 7.173 itens;
34 ficaram explicitamente separados como `unrepresented_tests`, sem aumentar
as aprovações medidas. O status foi `PASS_WITH_SKIPS`. Essa leitura não executou
novamente a suíte e não representa o resultado da revisão atual. O score do
relatório é heurístico; o lint global legado ainda possui pendências e não se
confunde com o Ruff aprovado da superfície alterada.

A CI remota do GitHub Actions **não foi executada nesta verificação**. O
[recibo público final](evidencias-r868/verificacao-final.json) separa esse estado
da execução local concluída.

| Entrega desta revisão | Estado |
| --- | --- |
| Suíte completa | **PASS_WITH_SKIPS** — 7.204 aprovações, 65 skips, zero falhas/erros; 7.269 nodes coletados em 438 arquivos, duas partes com código zero |
| Subtestes agregados | 34 itens sem testcase próprio, separados das aprovações físicas; agregado de 7.303 |
| Fontes durante a suíte | 3.904 arquivos com hashes iguais antes/depois; nenhum arquivo alterado durante a execução |
| Vínculo do candidato | Blobs preparados presentes no manifesto da suíte conferidos; alterações concorrentes posteriores não incorporadas |
| SDD/TDD | Contraprovas RED e GREEN executadas; fechamento pelo primário registrado em cópia isolada do candidato, com histórico autenticado próprio e sem preenchimento retroativo |
| Evolução preparada | R863–R869 acrescentadas: 703 → 710 entradas, prefixo anterior preservado; o ledger de trabalho pode receber outras atualizações em paralelo |
| Exportação Git | 81 testes específicos aprovados, instalação Node com lockfile e TypeScript aprovados; Python usou o ambiente local existente |
| Livro local | PDF de 388 páginas sincronizado com a cópia de entrega; SHA-256 `c790e30604dbde5993283169fae5c8f50be4d23880c048fdfd169d573087fa7e`; entrega anterior preservada |
| Registro Git | Candidato na branch `codex/core-prontidao-rea`; o hash do commit que contém este relatório é consultável pelo histórico e informado no fechamento |
| CI remota | **NÃO EXECUTADA** |

A execução total durou 682,56 segundos. O relatório reutilizou o JUnit,
sem repetir a suíte. Seu status é `PASS_WITH_SKIPS`; a pontuação continua
heurística e não mede qualidade externa. O lint global registrou 14.195
ocorrências no workspace, incluindo superfícies legadas e trabalho concorrente;
os checks da superfície alterada foram executados separadamente. Não se declara
lint global limpo.

Os skips continuam como casos não executados. Análise REA autônoma pelo LLM
local, todos os formatos/engines, licenças comerciais e autenticação dos demais
executores não foram demonstrados por essa suíte. Os caminhos diretos de REA e
o caminho de coordenação Codex têm evidência local delimitada de operação.
Resultados locais não certificam ausência de falhas, equivalência funcional com
aplicações analisadas ou validação externa do ecossistema.
