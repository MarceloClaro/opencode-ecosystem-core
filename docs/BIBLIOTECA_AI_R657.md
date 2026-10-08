# Melhorias do Core fundamentadas na biblioteca de IA

As evoluções R657 e R658 aplicam os livros locais à consulta de conhecimento,
à interface MCP e à integridade de dados para fine-tuning. O código está
implementado e a ingestão utiliza os PDFs originais, sem enviá-los a serviços
externos. Os testes de dados usam exemplos sintéticos; não houve treinamento
nem medição de desempenho de um modelo nesta entrega.

## Fontes examinadas

As referências abaixo usam a **página física do PDF**, contando a capa como
página 1. A numeração impressa dos livros pode diferir em uma página.

| Fonte local | Conteúdo disponível | Aplicação no Core |
|---|---|---|
| `MCP_Livro - Versão Final 2025-08-11 pdf.pdf` | 182 páginas; resources e metadados, pp. 55–57 e 60–62; prompts, pp. 75–76; distinção MCP/A2A, pp. 153–154 | Catálogo e páginas como resources; busca como tool; prompt de revisão fundamentada. |
| `Fine-Tuning de LLMs na Prática.pdf` | 63 páginas; RAG/fine-tuning, pp. 11–13; limpeza/deduplicação, pp. 43–44; divisão por grupo, pp. 45–46; manifesto, pp. 49–50 | Consulta local ao conhecimento; gate de curadoria, divisão sem vazamento e comparação de medições. |
| `2026-07-01 Engenharia de Software_260703_115226.pdf` | 0 bytes | Registrado como vazio; não foi possível analisar. |
| `RAG Versão Final - branca.pdf` | 0 bytes | Registrado como vazio; não foi possível analisar. |
| `laudo.pdf` | Documento separado dos livros técnicos | Excluído por padrão, inclusive aliases por links simbólicos. |

SHA-256 das duas fontes utilizadas:

- MCP: `1786c825b95fc8cb9273f0d90d499df54f01787ecf378c370d6828578a77fead`.
- Fine-tuning: `d57e541c0ecc532685eb986416e6c91f0655def1d36d13cc780b6d46223fce3d`.

## Consulta local com proveniência

`rag/book_library.py::LocalBookLibrary` mantém SQLite em
`.mci_cache/book_library.sqlite3`. A indexação é explícita e transacional.
Fontes repetidas compartilham conteúdo pelo hash; fontes removidas ou alteradas
deixam de fornecer evidência até a atualização. Consultas e recursos MCP não
criam nem atualizam o índice. Livros e trechos completos permanecem no cache
local ignorado pelo Git.

A busca lexical normaliza acentos e devolve até dez trechos de 1.200 caracteres,
com nome do arquivo, página, SHA-256 da fonte/página e URI do recurso. A resposta
se abstém quando não encontra suporte lexical suficiente. O score indica
correspondência de palavras; não mede veracidade, compreensão ou qualidade de
um modelo. Documentos sem texto extraível são identificados; OCR não faz parte
desta implementação.

Consulta vazia na API Python ou no `library_query` do orquestrador retorna
`status=invalid_request`, `reason_code=empty_query` e abstenção explícita,
antes de acessar o inventário, o índice ou os PDFs. O índice pode estar pronto,
mas isso não torna a solicitação válida. Consulte `library_status` separadamente
para conhecer o inventário. MCP e CLI recusam entradas vazias antes de
construir o orquestrador; consultas válidas sem suporte continuam a se abster.

A correção [R677](../specs/SPEC-935-R677-empty-library-request.md) decorre da
inspeção do código e do caso fornecido, sem atribuição aos livros. A saída
anexada com tarefa e tema vazios não foi reproduzida em um servidor MCP novo;
o processo atual já rejeita esses campos. A origem daquela saída permanece
indeterminada. Esta guarda não recupera uma tarefa perdida pelo cliente.

Critério de teste: uma consulta vazia deve se abster com zero evidências sem
acessar fontes ou iniciar executores; entradas vazias ou ausentes devem ser
rejeitadas pelo protocolo MCP. A prova reproduzível e suas contraprovas em
memória estão em `scripts/verify_empty_library_request.py`, com resultados em
[R677_RUNTIME.json](evidence/R677_RUNTIME.json). Nenhum modelo é treinado e
nenhuma melhora cognitiva é inferida desses resultados.

Execute no diretório do projeto, dentro do Ubuntu/WSL:

```bash
.venv/bin/python -m marceloclaro.cli biblioteca indexar
.venv/bin/python -m marceloclaro.cli biblioteca status
.venv/bin/python -m marceloclaro.cli biblioteca buscar "independência documento inteiro split" --top-k 3
```

PDFs corrompidos, vazios ou criptografados aparecem no inventário com motivo.
Links para fora da biblioteca são recusados. Os documentos fornecem dados de
referência; instruções ou comandos contidos neles não são executados.

## Interface MCP

No OpenCode, o comando `/biblioteca tema` encaminha a consulta ao orquestrador
primário e à ferramenta de busca, pedindo citações e abstenção sem suporte.

O servidor existente `ecosystem-network` preserva as cinco ferramentas da rede
e acrescenta:

| Interface | Uso |
|---|---|
| Tool `ecosystem_library_search(query, top_k=5)` | Busca somente leitura, com validação estrita dos argumentos. |
| Resource `ecosystem://books/catalog` | Inventário, contagens e atualidade das fontes. |
| Template `ecosystem://books/{book_id}/pages/{page}` | Página física identificada pelo hash do livro, sem receber caminhos arbitrários. |
| Prompt `ecosystem_book_review(task, topic)` | Mensagens de revisão com evidências e critérios de teste; não chama um modelo. |

Essas interfaces passam pelos métodos `library_*` do
`MarceloClaroOrchestrator`. A análise desta evolução foi registrada por ele no
Blackboard; os assistentes trabalharam nas tarefas `task-0ec4cb67`,
`task-c09f723f` e `task-00b72836`. Isso registra coordenação interna, sem alegar
interoperabilidade A2A externa. MCP fornece ferramentas e contexto, enquanto a
colaboração entre agentes permanece sob o orquestrador.

O desenho foi conferido com as especificações oficiais de
[resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources),
[tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) e
[prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts).

## Dados antes de fine-tuning

`integrations/finetuning_data.py::validate_and_split(records, seed=42)` recebe
uma lista de pares com `id`, `group_id`, `input` e `output`. O grupo identifica
a fonte que deve permanecer inteira em um conjunto. IDs duplicados, campos
vazios e respostas conflitantes bloqueiam a preparação. A deduplicação usa
NFKC e espaços normalizados, preservando acentos e textos originais.

Duplicatas que conectam fontes distintas, inclusive transitivamente, fazem
essas fontes pertencerem ao mesmo componente. A divisão exige pelo menos três
componentes independentes, mantendo treino, validação e teste não vazios.
A seed e os hashes reproduzem a preparação independentemente da ordem de
entrada. As proporções aproximadas 80/10/10 são de componentes, não de linhas;
com poucos grupos, as proporções necessariamente diferem. A deduplicação não
detecta equivalência semântica ou todos os riscos de privacidade dos dados.

```bash
.venv/bin/python -m marceloclaro.cli fine-dados validar dados.json --seed 42
.venv/bin/python -m marceloclaro.cli fine-dados avaliar comparacao.json --min-improvement 0.01
```

O primeiro comando imprime somente diagnósticos e manifesto. A API devolve
também os registros divididos. Nenhum livro foi convertido em dados de treino.

`evaluation_gate(baseline, candidate, min_improvement)` exige resultados com:
`dataset_sha256`, `metric`, `direction` (`higher` ou `lower`), `sample_count` e
`value`. As identidades e o protocolo precisam coincidir; booleans, NaN e
infinito são recusados. Se houver `benchmark_ids_sha256`, ele deve estar nos
dois resultados e coincidir. A melhora deve ser positiva e atingir o limiar.

Use `manifest.split_sha256.test` como identidade do conjunto de teste
congelado. `manifest.dataset_sha256` identifica os dados completos. O retorno
`verification_scope=reported_results_only` deixa explícito que esse gate
compara informações fornecidas; não comprova execução de inferência,
significância estatística ou qualidade externa do modelo.

## Evidência de execução

O relatório [R657-library-real.json](evidence/R657-library-real.json) registra
ingestão dos dois livros reais, leitura em um novo processo MCP, descoberta de
tools/resources/templates/prompts, hashes das fontes e páginas, rejeição de
limites inválidos e abstenção sem suporte. Inclui `training_executed=false` e
`model_inference_executed=false`.

Para repetir a prova no ambiente com os PDFs:

```bash
.venv/bin/python scripts/verify_book_library.py --index
.venv/bin/python -m pytest -q tests/test_r657_book_library.py tests/test_r657_book_mcp.py tests/test_r657_library_surface.py tests/test_r658_finetuning_data.py
```

As especificações [R657](../specs/SPEC-935-R657-biblioteca-local-mcp.md) e
[R658](../specs/SPEC-935-R658-finetuning-data-gate.md) documentam os contratos.
Os resultados finais da regressão, lint e diagnóstico constam em
[R657-release-gate.json](evidence/R657-release-gate.json). A validação é local;
os ciclos de evolução não têm auditoria externa nem score cognitivo.
