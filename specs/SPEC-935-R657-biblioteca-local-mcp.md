---
spec_id: SPEC-935-R657
title: Biblioteca tecnica local recuperavel pelo orquestrador e MCP
status: green
component: rag/book_library.py + marceloclaro/orchestrator.py + integrations/ecosystem_mcp.py
test_file: tests/test_r657_book_library.py
---

# SPEC-935-R657 — Aprendizado operacional com os livros locais

## Objetivo e fontes

Transformar os livros fornecidos em contexto tecnico consultavel, persistente e
citavel, usando MCP resources para dados e tools para busca. O livro de MCP,
capitulos 4 e 5, inspira a interface. O livro Fine-Tuning de LLMs na Pratica,
capitulos 1 e 3, orienta a distincao entre recuperacao de conhecimento e treino.
As paginas exatas e os hashes constarao em docs/BIBLIOTECA_AI_R657.md.

## Contratos

1. Indexar PDFs locais por pagina fisica, sem executar codigo, links ou
   instrucoes contidos nos documentos; arquivos vazios, corrompidos e sem texto
   devem aparecer no inventario com motivo explicito.
2. O laudo.pdf nao participa da biblioteca tecnica por padrao. Fontes devem
   permanecer contidas na pasta configurada, inclusive depois de resolver symlinks.
3. Persistir indice local em .mci_cache, com hash SHA-256 da fonte e da pagina,
   IDs estaveis, pagina fisica e nome original. Atualizacao atomica elimina
   trechos removidos; consultas nao indexam ou alteram arquivos implicitamente.
4. Consulta lexical offline limitada por top_k e tamanho de trechos, com
   normalizacao de acentos, ordenacao deterministica e abstencao sem evidencia.
   Fontes alteradas ou removidas nao podem fornecer trechos apresentados como atuais.
5. Expor inventario e pagina citavel por MCP resources, busca por tool somente
   leitura e prompt reutilizavel que trate fontes como dados nao confiaveis.
   Nenhum recurso recebe caminho arbitrario do cliente.
6. Metodos do MarceloClaroOrchestrator centralizam indexacao/status/busca.
   CLI biblioteca oferece indexar, status e buscar, com erros acionaveis.
7. Testes antes da implementacao cobrem proveniencia, persistencia, atualizacao,
   limites, abstencao, fontes invalidas e isolamento. Prova real usa os dois
   livros fornecidos e protocolo MCP, separada dos fixtures sinteticos.
8. Preservar alteracoes pre-existentes e contratos R640/R644/R436. Registrar
   ciclo sem alegar treinamento, auditoria externa ou melhora cognitiva medida.

## Aceitacao

- Testes R657 de biblioteca e interface passando; regressao dos modulos tocados.
- Dois livros reais consultaveis em processo novo, com arquivo, pagina e hash.
- Arquivos vazios registrados; laudo separado; abstencao em consulta sem suporte.
- initialize/list/call/read/get pelo MCP com respostas e schemas validos.

## Critérios de aceitação executáveis

- `R657-PROVENANCE` — Persistência, consulta e releitura preservam página e hashes.
- `R657-FRESHNESS` — Fontes removidas/alteradas e aliases proibidos não fornecem evidência.
- `R657-FAILURES` — Limites inválidos, falta de suporte e schema incompleto têm tratamento explícito.

A evidência runtime do test_file cobre o núcleo; interfaces MCP/CLI e a prova
com livros reais têm gates separados em docs/evidence/R657-release-gate.json.
