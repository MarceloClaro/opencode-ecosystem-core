---
spec_id: SPEC-935-R675
title: Podcast NotebookLM com execução e artefato comprovados
status: green
validation_scope: local_runtime
component: agent_runners/nlm_executor.py + marceloclaro/orchestrator.py::podcast
test_file: tests/test_r675_notebook_podcast_truthfulness.py
---

# R675 — Correção do contrato legado de podcast

O executor encontra `nlm` na `.venv/bin` do Core mesmo fora do PATH, sem
instalação automática. Caminho explícito vazio continua desabilitando o executor.
Resultados JSON de erro não se tornam sucesso por terem código de saída zero.
Criação de áudio confirma apenas aceitação; conclusão do podcast exige download
de arquivo novo, regular, não vazio, com tamanho e SHA-256 registrados.

Retentativas de download são limitadas e se aplicam somente à propagação do
artefato ainda indisponível. Autenticação, permissão, parâmetros inválidos,
erros de negócio e falhas não classificadas não são repetidos. Entradas inválidas
e arquivos preexistentes são recusados antes da chamada externa.

O orquestrador usa o caminho indicado pelo recibo atual, sem selecionar áudio
antigo da pasta. Registra observação operacional delimitada no MetaBus, sem
nota científica, reflexão pontuada ou promoção de confiança. Falhas preservam
etapa e IDs realmente obtidos. A API pública e o fluxo do operador permanecem.

Validação: `docs/evidence/R675_RED.xml` registra 28 falhas e 1 caso já correto.
`docs/evidence/R675_COUNTEREXAMPLES_RED.xml` registra as três contraprovas
adicionais de resultado falso e identificação do artefato. O GREEN em
`docs/evidence/R675_GREEN.xml` contém 32 casos R675 e 34 regressões R549/R550:
66 testes aprovados. Os fixtures antigos de download materializam o arquivo e
identificam explicitamente a propagação transitória, preservando suas asserções.
Ruff específico aprovado. Os testes não geram conteúdo externo nem consomem
quota NotebookLM; GREEN local não é validação científica externa.
