---
spec_id: SPEC-935-R1257
title: Política explícita fail-closed na fronteira do túnel completo
component: integrations.ecosystem_mcp_tunnel
status: proposed
test_file: tests/test_r1257_tunnel_tool_policy.py
---

# SPEC-935-R1257 — Política do túnel completo

## Problema e autorização

O bridge R1222 encaminhava mensagens e stdout sem controle. Acesso ampliado
não concede autorização genérica para efeitos. Este ciclo altera somente código,
testes e documentação locais; não inicia/reinicia túnel, abre rede, instala
dependências, faz commit/push ou chama Burp. `integrations/chatgpt_status_mcp.py`
deve permanecer byte a byte intacto.

## Contrato e critérios de aceitação

- AC1: catálogo explícito dos 27 nomes atuais, separado de inventários de MCPs.
  Nomes desconhecidos, inclusive futuros, são negados. Não inferir autorização
  de anotações MCP, prefixos, confirm, consent ou instruções em argumentos.
- AC2: tools/list filtra a resposta real do filho por política; operações de
  leitura têm schemas estreitos. Ferramentas com efeitos só aparecem quando
  existe uma autorização local ainda válida. O schema anunciado inclui a
  seleção de autorização em params._meta, descrita abaixo, sem injetar args.
- AC3: tools/call valida nome, envelope, argumentos e operação antes do envio.
  Escrita, execução e rede exigem grant local por ferramenta/operação exatas,
  SPEC existente e hash do documento, SHA-256 do JSON canônico integral dos
  argumentos, workspace, efeitos e alvos explícitos. Sem curingas. Alteração de
  qualquer campo invalida a autorização. Ausência/erro da fonte nega efeitos.
- AC4: grants são privados, locais e externos ao workspace; não podem ser
  criados pelo cliente MCP. Expiram em até uma hora e são consumidos em disco,
  sob lock e fsync, antes do encaminhamento. Replay inclusive após reinício é
  negado. Falha no envio não reabilita o grant. Nenhum grant real é criado aqui.
- AC5: Burp não é exposto nem chamado; somente a fachada local de planejamento
  `ecosystem_claude_bughunter_plan` pode ser lida. Proxies genéricos de notebook,
  plugins e execução delegada permanecem bloqueados, mesmo com grant, pois esta
  fronteira não consegue confinar suas operações transitivas. O gate não é um
  sandbox de sistema operacional; os validadores Core continuam obrigatórios.
- AC6: JSON malformado, batch, chaves duplicadas, NaN, notificações de chamada,
  envelopes extras e métodos não permitidos nunca chegam ao filho. Respostas do
  filho são correlacionadas a IDs internos; IDs pendentes duplicados, respostas
  órfãs e paginação inesperada falham fechados. Initialize anuncia somente tools;
  recursos/prompts não constituem um caminho alternativo de execução.
- AC7: testes locais com filho simulado registram RED real antes da produção e
  GREEN após. R1222 verifica o contrato nominal, sem contagem histórica 26 e sem
  tools/call real. Nenhuma evidência local comprova conexão remota ou frota.

## Política categorizada

Leitura: integration_status, artifact_handoff, skill_plan,
claude_bughunter_plan, library_search, quantum_catalog, knowledge_query,
status, route, workflow_status (todos com prefixo `ecosystem_`).

Efeitos locais: agent_profile, local_ci, knowledge_plan, scientific_verify,
rea, production, code_context, dataset_custom, text_spec. Todas as operações
dessas fachadas exigem grant, inclusive status/list se gravam observações.
REA permite apenas status/catalog/layers; análise de alvos não é autorizável
neste ciclo. Produção permite status/list/plan; run/resume ficam bloqueados.

Rede/execução delimitadas: scientific_run, scientific_runtime, dataset_download,
browser. Exigem grant com efeitos e alvos próprios da ferramenta.

Negação permanente nesta versão: scientific_plugins, gemini_notebook, run,
workflow (proxies ou delegação transitiva). Novas operações exigem nova revisão
da política e testes; um grant não altera essa classificação.

## Autorizações do operador

Fonte fixa: ~/.config/opencode-core/tunnel-authorizations.json, diretório 0700,
arquivo regular 0600 do mesmo UID, sem symlink/hardlink, fora do workspace.
Formato version=1, grants=[...]. Cada grant contém grant_id, tool, spec_id,
spec_sha256, arguments_sha256, scope, expires_at (Unix), used=false.
scope contém workspace absoluto canônico, operation exata, effects e targets
como listas não vazias sem curingas. O cliente seleciona o grant em
params._meta.authorization={grant_id,spec_id,scope}; essa seleção não cria
autoridade. A ferramenta recebe apenas seus argumentos originais.
targets devem corresponder aos caminhos/URLs explícitos extraídos por regras
da ferramenta, ou ao workspace para operações sem outro alvo. Argumentos
arbitrários não representam confinamento de efeitos transitivos.

## Inventários e limites

Há 27 ferramentas no contrato Core deste checkout. O inventário Core de 28
MCPs e o manifesto privado de 33 são conjuntos distintos. Sem caminho e lista
redigida do manifesto privado, a reconciliação nominal permanece bloqueada;
nenhum mapeamento é inventado. Validação remota e ativação ficam fora do ciclo.
