---
spec_id: SPEC-935-R674
title: Gemini Notebook sob orquestração central
status: green
validation_scope: central_runtime
component: integrations/gemini_notebook.py
test_file: tests/test_r674_gemini_notebook_orchestration.py
---

# SPEC-935-R674 — Gemini Notebook sob orquestração central

## Problema e decisão
O Core possuía uma ponte com diagnóstico histórico e um caminho de podcast,
mas não encaminhava o catálogo completo do repositório solicitado pelo usuário.
O MarceloClaroOrchestrator deve coordenar CLI, MCP e leitura da skill oficial.
Os serviços oficiais continuam responsáveis pelas APIs remotas; o Core valida
contratos, efeitos, arquivos e recibos operacionais.

## Contrato
- Entrada `gemini_notebook_action(operation, **config)`; operações status,
  catalog, skill, mcp e cli. Exposição por CLI, MCP central e OpenCode.
- Catálogo derivado do servidor instalado e da árvore Typer, com versão/hash;
  nenhum número histórico é usado para declarar disponibilidade.
- Configuração JSON delimitada, sem campos desconhecidos, segredos ou ambiente
  arbitrário. Timeout finito; CLI como vetor, sem shell ou modo interativo.
- Leitura pode executar sem confirmação. Efeitos de inferência, escrita,
  publicação, exclusão e download exigem `confirm: true`; `dry_run: true`
  prepara uma operação e não chama a ferramenta remota.
- Autenticação privada permanece no programa oficial; cookies não transitam
  por configuração, resultados ou MetaBus. MCP usa o perfil ativo upstream;
  o Core não troca silenciosamente esse perfil.
- Downloads ficam em outputs/gemini-notebook; resultado concluído exige
  arquivo real, não vazio, dentro da raiz e hash. Falha parcial não é sucesso.
- Skill e referências oficiais preservadas; leitura por ReversaSkillDispatcher.
- MetaBus recebe somente estado, identificação da operação e hashes;
  textos privados e argumentos não são persistidos, nem confiança promovida.
- Consultas assíncronas preservam o servidor oficial entre chamadas por broker
  local privado. Idle TTL de uma hora; reinício/perfil novo descarta jobs
  voláteis com sinalização explícita. CLI continua usando executável oficial.

## Verificação
RED antes de implementação; GREEN dos contratos de entrada, bloqueios antes
de efeitos, downloads ausentes, preflight e roteamento central. Provas reais
separadas dos testes isolados: inventário CLI/MCP, autenticação e leitura
remota. Geração, exclusão e publicação não são usadas como provas de leitura.

## Preflight de pipelines oficiais

`integrations/gemini_notebook_pipeline.py::pipeline_preflight` seleciona a
definição oficial efetiva: templates builtin têm precedência sobre arquivos
do armazenamento `pipelines/*.yaml`. A leitura não importa o cliente, acessa
credenciais, cria diretórios ou executa passos. AST extrai os templates
literais; YAML seguro tem limites de bytes, profundidade, quantidade de passos
e estrutura, sem symlinks, chaves duplicadas, campos desconhecidos ou segredos.

O preview contém todos os passos, seus alvos, parâmetros resolvidos, efeitos
e hashes da definição, do arquivo de origem e dos passos efetivos. Os passos
declarados pelo caller não são autoridade sobre a definição executada.
`$INPUT_URL` é resolvido como na interface oficial. `$NOTEBOOK_ID` em parâmetros
é mostrado resolvido, mas bloqueia execução: CLI/MCP upstream não injeta essa
variável; o alvo real dos passos é o argumento `notebook_id` central.

RED: `docs/evidence/R674_PIPELINE_RED.xml`; GREEN:
`docs/evidence/R674_PIPELINE_GREEN.xml`. Estes testes verificam somente o
preflight local; criação de conteúdo e exclusão remota não foram executadas.
