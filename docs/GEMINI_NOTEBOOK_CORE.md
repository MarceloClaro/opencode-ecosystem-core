# Gemini Notebook na orquestração do Core

O repositório [gemini-notebook-mcp-cli](https://github.com/MarceloClaro/gemini-notebook-mcp-cli)
é encaminhado pelo `MarceloClaroOrchestrator.gemini_notebook_action`. A CLI,
o MCP `ecosystem_gemini_notebook` e o comando OpenCode `/gemini-notebook`
usam a mesma validação e registram recibos no MetaBus.

## Instalação reproduzível

Instale `requirements.txt` e `requirements-notebook.txt` no ambiente do Core.
A integração opcional requer Python 3.11 ou superior; o broker persistente
implementado utiliza Linux/WSL.
A dependência opcional fixa NotebookLM MCP CLI 0.11.6, FastMCP 3.2.3 e MCP
1.28.1. FastMCP 4.0.5 instalado anteriormente exigia MCP 2 e impedia o servidor
de iniciar. Os executáveis são resolvidos também em `.venv/bin`, fora do PATH.
Para preservar extensões do fork, instale sem atualizar dependências o checkout
do commit `f212ed9a321351aadf7ff7271469d6d4663df7d3` indicado na spec R672.
Um número de versão do PyPI sozinho não identifica esse commit.

## Entradas

Salve uma configuração JSON e execute:

```bash
.venv/bin/python -m marceloclaro.cli notebook --config exemplos/notebook/catalog.json
```

`ciencia notebook --config ARQUIVO` e `gemini-notebook --config ARQUIVO` são
entradas equivalentes. Pelo MCP, envie a mesma configuração ao parâmetro
`config` de `ecosystem_gemini_notebook`. O OpenCode `/gemini-notebook` é uma
instrução ao agente primário, que chama essa ferramenta central.

| operation | Finalidade | Configuração adicional |
|---|---|---|
| status | Caminhos e versão instalados; não comprova login | nenhuma |
| catalog | Handshake, schemas MCP e árvore CLI atual | timeout_seconds opcional |
| skill | Preservar e ler skill/referências oficiais no contexto | nenhuma |
| mcp | Executar ferramenta descoberta no servidor oficial | tool, arguments |
| cli | Executar comando oficial sem shell | argv iniciado por nlm |

MCP/CLI aceitam `timeout_seconds` entre 1 e 300, `dry_run` e `confirm`
booleanos. O preflight valida o contrato e prepara a operação; seu resultado
`prepared` não significa que a ação remota ocorreu. Efeitos exigem confirmação
da operação concreta, inclusive suboperações de batch/pipeline.

## Superfície revisada

Os especialistas `Gemini notebook audit`, `Gemini notebook upstream` e
`Gemini notebook transport` estão em `agents/catalog`, com contratos A2A,
permissões explícitas e métodos existentes da entrada MarceloClaro. O Core
contém 238 agentes configurados após esse registro. Atribuir uma tarefa a um
perfil não comprova inferência desse agente.

O inventário do commit revisado contém 49 ferramentas MCP em 15 grupos e
155 callbacks CLI, incluindo callbacks de grupos e raiz. As ferramentas
habilitadas são descobertas em execução; os filtros `NOTEBOOKLM_DISABLED_GROUPS`,
`NOTEBOOKLM_DISABLED_TOOLS` e `NOTEBOOKLM_ENABLED_TOOLS` continuam aplicados.
O catálogo e seu hash ficam em `.opencode/gemini-notebook/catalog.json`.

| Área | Suporte encaminhado |
|---|---|
| Notebooks/fontes | Consulta, criação, renomeação, exclusão; URL/texto/arquivo/Drive e sincronização |
| Chats/pesquisa | Consultas síncronas e assíncronas, status, sessões, exportação, consulta entre notebooks, pesquisa/importação |
| Organização | Labels, tags, coleções e notas; `label(list)` também pode escrever |
| Automação | Batch e pipeline; passos desconhecidos recebem efeito destrutivo conservador |
| Studio | Nove tipos de criação, revisão/status/exclusão; onze tipos de download e exportação |
| Compartilhamento | Status, convites, acesso público e lote; confirmação explícita |
| Operação | Uso, diagnóstico, perfis, configuração e instalação de skills/MCP nos clientes suportados pela CLI |

Consultas consomem cota e persistem conversas. Batch Studio e pipelines não
enforçam todas as confirmações no upstream; a política central enforça antes
da chamada. `failed`, `partial`, tarefas pendentes e erros de negócio com
transporte bem-sucedido são preservados. Não existe promoção automática de
confiança científica por um retorno operacional.

## Autenticação, perfis e Enterprise

Login interativo e importação manual de cookies ficam no programa oficial,
fora da captura compartilhada. `nlm login --check` pode ser encaminhado para
verificação. O MCP usa o perfil ativo upstream; comandos CLI de perfil são
explícitos e não são chamados como probes. O Core não lê arquivos de cookies.

O ambiente configurado é herdado pelo processo oficial. Enterprise permanece
experimental, com os hosts Google autorizados pelo upstream e
`NOTEBOOKLM_PROJECT_ID`/`NOTEBOOKLM_LOCATION` configurados pelo operador.
Uma conexão padrão não comprova funcionamento de uma conta Enterprise.

O servidor upstream também suporta HTTP/SSE, RPC/CDP experimental e
configuração de múltiplos clientes. O Core usa stdio para sua conexão central;
comandos de servidor interativo são declarados no inventário e executados no
terminal do operador. Instalar uma configuração em outro cliente não comprova
que esse cliente iniciou ou inferiu com um modelo.

O Core mantém a sessão stdio em um processo local persistente para preservar
os jobs de consulta assíncrona entre chamadas, inclusive entre processos CLI.
O socket é privado ao usuário. A sessão encerra após uma hora de inatividade;
reiniciar o servidor ou trocar perfil/configuração pode descartar jobs voláteis,
o que deve aparecer no recibo. Isso não transforma jobs em tarefas duráveis.
O identificador do job é associado à sessão original em um arquivo privado,
sem texto da consulta. Consultas de status continuam nessa sessão mesmo entre
interfaces com ambientes diferentes. Sessão expirada/encerrada retorna `lost`,
com código de falha na CLI, e não cria um servidor novo para fingir continuidade.

## Proveniência e arquivos

Downloads coordenados ficam em `outputs/gemini-notebook`, com destino novo,
arquivo real não vazio, tamanho e SHA-256. O caminho de podcast exige esse
mesmo tipo de prova de arquivo. Sucesso sem áudio é falha.

Uma fonte ou síntese no NotebookLM pode alimentar a etapa de referências do
percurso pergunta → fontes/datasets → método → experimento → análise → revisão
→ artefato. Ela não comprova que um experimento foi executado nem constitui
revisão por pares. O conteúdo retornado permanece na resposta da operação;
o MetaBus recebe estado, identificação e hashes da requisição/resposta, preservando a origem sem
armazenar textos privados ou credenciais.

## Evidências e limites

Specs R672–R675 e XMLs RED/GREEN em `docs/evidence` cobrem transporte,
catálogo/política, entrada central e veracidade do podcast. O gate conjunto
separa testes isolados de conexões reais. Probes reais usam autenticação e
leitura de metadados; não geram Studio, enviam convites ou excluem notebooks.
Essas operações têm contratos disponíveis e exigem insumos/autorização para
uma execução específica. O gate não declara todas as operações remotas testadas.
