---
spec_id: SPEC-935-R672
title: Transporte delimitado para o servidor e a CLI oficiais Gemini Notebook
status: green
validation_scope: local_runtime
component: integrations/gemini_notebook_transport.py + integrations/gemini_notebook_session.py
test_file: tests/test_r672_gemini_notebook_transport.py
---

# R672 — Processo oficial e protocolo MCP

O Core deve resolver `nlm` e `notebooklm-mcp` na sua `.venv/bin`, mesmo fora do
PATH, sem importar ou reproduzir o motor NotebookLM. `NLM_BIN` pode selecionar
explicitamente um executável CLI instalado. A autorização das operações e os
destinos dos artefatos pertencem ao serviço central, não a este transporte.

## Contratos de aceitação

1. Descobrir ferramentas mediante `initialize`, `notifications/initialized` e
   `tools/list` no servidor oficial, preservando nomes, descrições, schemas e
   anotações. Respostas paginadas têm limite total e cursores repetidos falham.
2. Validar nome, argumentos JSON finitos e schema completo antes de
   `tools/call`. Campos desconhecidos, inclusive objetos aninhados, são
   recusados mesmo quando o schema upstream omite `additionalProperties`.
3. Cada processo tem tempo máximo, entrada delimitada, saída limitada a 1 MiB,
   stderr limitado e encerramento do grupo de processos ao falhar. Não usa
   shell, entrada interativa, debug ou dumps de autenticação.
4. Exit code zero e `isError=false` não bastam para declarar conclusão:
   `status:error`, `status:failed`, `success:false` ou `ok:false` presentes no
   conteúdo estruturado ou JSON textual classificam a operação como falha.
   Contagens batch/pipeline com `failed>0` ou `succeeded<total_steps` preservam
   conclusão parcial ou falha; estados `pending`, `running`, `generating` e
   `partial` nunca viram conclusão total. Estados assíncronos permanecem
   explícitos no MCP e na CLI, mesmo com exit code zero.
5. Relatórios removem tokens, cabeçalhos Authorization/Cookie e valores de
   campos de credenciais; o transporte não lê arquivos de autenticação.
6. Ausência de executável retorna bloqueio explícito e
   `process_executed=false`; falha posterior preserva a informação de que um
   processo foi iniciado. Descoberta local não equivale a inferência remota.

## Validação

Testes com servidor de protocolo local, identificado como fixture hermética,
incluem handshake, schema, limites, timeout e classificação de erro de negócio.
O teste local não representa autenticação ou execução NotebookLM remota.
RED: `docs/evidence/R672_RED.xml`; GREEN: `docs/evidence/R672_GREEN.xml`.

## Reprodução do ambiente

O fork foi fixado no commit
`f212ed9a321351aadf7ff7271469d6d4663df7d3`, que declara a versão `0.11.6`.
A distribuição instalada inicialmente escolheu FastMCP `4.0.5`, cujo extra de
servidor exige MCP `>=2,<3`; o Core conserva MCP `1.28.1`. A incompatibilidade
foi reproduzida por erro de importação, e corrigida com FastMCP `3.2.3`, que
declara MCP `>=1.24,<2`. `pip check` concluiu sem requisitos quebrados.

```bash
.venv/bin/python -m pip install -r requirements.txt -r requirements-notebook.txt
# No checkout do fork, confirmar o commit acima antes da instalação abaixo.
.venv/bin/python -m pip install --no-deps /home/marceloclaro/projetos/gemini-notebook-mcp-cli-core
```

A segunda instalação preserva as extensões do fork, pois a igualdade de versão
`0.11.6` não identifica por si só o conteúdo de um commit do repositório.
`requirements-notebook.txt` delimita as versões compatíveis, sem alterar os
requisitos compartilhados do Core. Recibo da instalação delimitada:
`docs/evidence/R672_DEPENDENCY_INSTALL.json`.

## Prova funcional delimitada

`docs/evidence/R672_REAL_DISCOVERY.json` registra handshake do servidor oficial
e 49 ferramentas visíveis. `docs/evidence/R672_REAL_SERVER_INFO.json` registra
uma chamada real de `server_info`, versão do pacote `0.11.6` e saúde de
autenticação `configured`. Isso demonstra execução do processo e inspeção de
infraestrutura, sem declarar inferência, geração de artefatos ou suporte
confirmado a capacidades do provedor: o próprio servidor informa
`provider_capabilities.status=not_probed`. A atualização PyPI anunciada pelo
servidor não foi aplicada, pois a integração usa o commit solicitado.

## Sessões persistentes e jobs assíncronos

`GeminiNotebookTransport(..., persistent=True)` usa um broker Unix local que
preserva o servidor MCP oficial entre processos CLI separados. Isso mantém os
jobs `notebook_query_start` disponíveis para `notebook_query_status`, pois o
upstream guarda esses jobs somente na memória do processo. O modo padrão
`persistent=False` continua disponível para operações isoladas.

O diretório `.opencode/notebooklm/broker` tem permissão `0700`; sockets,
configurações, locks e PID têm `0600` e precisam pertencer ao mesmo usuário.
Symlinks e arquivos especiais são recusados; sockets obsoletos só são
removidos após checagem de tipo, proprietário e ausência de processo vivo.
O protocolo usa um alias `/proc/self/fd` para respeitar o limite AF_UNIX sem
retirar o socket do workspace. O cliente mantém limites de entrada/saída e
o broker verifica o usuário com `SO_PEERCRED`.

A identidade inclui hash do executável, versões instaladas, hash do ambiente
relevante, grupos, overrides internos de downloads e somente `mtime_ns`/tamanho
do `config.toml` oficial. Não lê `auth.json`, cookies ou conteúdo do config para
calcular a identidade, nem persiste o ambiente herdado. Troca de perfil/config
gera identidade nova. `close_persistent()` encerra e aguarda todas as sessões
privadas deste workspace, permitindo invalidar também a sessão anterior após
uma mudança feita pela CLI.

O Core registra uma associação mínima do identificador `query_id` com a
identidade do broker e o `session_id` que iniciou o job. Esses arquivos ficam
em `broker/jobs`, com diretório `0700` e arquivo `0600`, e não contêm perguntas,
respostas, fontes ou credenciais. Escritas têm lock e substituição atômica;
identificadores que colidem entre sessões não substituem associações anteriores.
`notebook_query_status` usa essa associação para consultar o processo original,
inclusive quando CLI, MCP ou UI possuem ambientes e idiomas diferentes.
Alterações no PATH não criam nova identidade para um executável já resolvido.
Se a sessão original expirou, fechou ou reiniciou, o Core retorna `lost` com
motivo explícito e não inicia um servidor diferente para procurar o job.

O broker encerra após **uma hora de inatividade**; operações ativas suspendem
esse relógio. Reinício, encerramento explícito ou timeout de um RPC podem
descartar jobs voláteis. Os recibos incluem `session_id`, retenção e, no reset,
`session_reset` e `volatile_jobs_lost`; uma requisição que apenas expirou na fila
retorna `session_busy` sem encerrar a operação ativa. O broker não adiciona
persistência a jobs que o servidor oficial mantém só em memória.

Testes adicionais: `tests/test_r672_gemini_notebook_session.py`; contraprovas:
`docs/evidence/R672_SESSION_CONTRAPROOFS_RED.xml`. Provas reais, em dois
processos Python separados e com a mesma sessão oficial:
`R672_REAL_PERSISTENT_DISCOVERY.json`, `R672_REAL_PERSISTENT_SERVER_INFO.json`
e `R672_REAL_PERSISTENT_CLOSE.json`, dentro de `docs/evidence`.
As contraprovas de roteamento entre processos com ambientes distintos e de
perda explícita após expiração estão em `docs/evidence/R672_JOB_ROUTING_RED.xml`.
