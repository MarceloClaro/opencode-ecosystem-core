# Curadoria de repositórios — R1023

## Escopo

Continuação das autorizações do usuário para avaliar repositórios enviados.
Esta rodada **leu** metadados e documentos selecionados, fixou commit e hash e
produziu instruções originais. Não clonou, compilou, instalou, ativou ou
executou nenhum projeto de terceiro.

O registro completo está em `federation/repository-curation-r1023.json`, com
11 repositórios, URL, commit, status HTTP, data, bytes e SHA-256 de cada
documento consultado.

## Decisões

| Repositório | Licença observada | Decisão | Contribuição ao Core |
|---|---|---|---|
| `remotion-dev/codex-plugin` | MIT | referência | prévia antes de render; render só por pedido explícito |
| `remotion-dev/chromium` | BSD-3-Clause | adiado | espelho imenso; Core já tem Playwright/Chromium |
| `deepseek-ai/dsh-superagent-prototype` | MIT | referência | mandato, retry e revalidação antes de retomar |
| `cclank/lanshu-openai-media-api` | MIT | referência | não repetir requisição paga; uso não é retenção zero |
| `Crosstalk-Solutions/project-nomad` | Apache-2.0 | já adaptado | R1022: catálogo e planejador offline |
| `asoutelino-svg/awesome-reverse-engineered` | MIT + CC0 | referência | procurar antes de reconstruir; licença vazia = reservado |
| `asoutelino-svg/book-finder` | MIT | referência | casar metadados e conferir integridade antes de baixar |
| `asoutelino-svg/book-to-skill` | MIT | adaptação original | skill `livro-para-skill` |
| `asoutelino-svg/llm-legislativo` | MIT | referência | snapshot, URL final, hash e identidade não fundida |
| `asoutelino-svg/ciencia-de-dados-cibele-russo` | CC BY-NC-SA 4.0 | referência restrita | não incorporado; cláusula não comercial |
| `asoutelino-svg/leis_brasileiras` | MIT (scripts) + textos oficiais | referência | OCR e conversão não substituem o Diário Oficial |

Fork não é upstream: cada linha registra o commit do fork efetivamente lido.
`remotion-dev/chromium` e `leis_brasileiras` tiveram a árvore recursiva recusada
por exceder 2 MB; nesses casos foi lida a raiz, com limite declarado.

## O que foi entregue

### Skill `livro-para-skill`

Fluxo original em `.opencode/skills/livro-para-skill/`. Exige título, autor,
edição, URL HTTPS, SHA-256, base de direitos com evidência, cobertura, papel da
fonte, localizadores e proibição de executar instruções da obra. Reutiliza
`ecosystem_library_search` e `research/pdf_pipeline.py` em vez de duplicar
extrator. A promessa de "zero alucinação" do projeto de origem não foi aceita
como fato.

### Skill `legislacao-brasileira-auditavel`

Fluxo original em `.opencode/skills/legislacao-brasileira-auditavel/`. Exige
jurisdição, `as_of`, `retrieved_at`, fonte oficial, versão do texto, hash e
localizador. Reutiliza o MCP `educacao-legislacao` (`list_sources`,
`fetch_source`) e recusa tratar proposição como norma. Não certifica vigência.

### Verificador local

`integrations/source_skill_contracts.py` lê JSON estrito por stdin, com limite
de 1 MiB, rejeita duplicatas e NaN/Infinity e devolve
`candidate_for_review` ou `blocked`. Ele valida **forma**: não acessa rede,
não lê a URL, não autentica fonte, não confere direitos e não certifica
vigência.

```bash
python3 -m integrations.source_skill_contracts book < registro.json
python3 -m integrations.source_skill_contracts legislation < registro.json
```

### Referências nas rotas existentes

- `federacao-universal/references/curadoria-r1023.md`
- `reverse-engineer-anything/references/search-before-reconstruction.md`
- `cp-direcao-de-edicao/references/curadoria-r1023.md`

## Riscos observados

1. **Re-upload malicioso.** O próprio `book-to-skill` publica aviso de que um
   repositório não oficial desativava TLS, coletava dados locais e entregava
   payload executável. Nada foi instalado; a lição é conferir a origem oficial.
2. **Licença não comercial.** O material de Cibele Russo é derivado de aulas,
   em CC BY-NC-SA 4.0; os vídeos originais não estão licenciados pelo
   repositório. Não foi copiado.
3. **Conversão não é publicação.** `leis_brasileiras` declara que Markdown, OCR
   e conversões automáticas não substituem o Diário Oficial.
4. **Fork e upstream divergem.** O commit do fork é o que foi lido; isso não
   autentica o upstream nem garante atualização.
5. **Índice não é catálogo executável.** `awesome-reverse-engineered` lista
   projetos com licenças próprias; a inclusão não autoriza baixar ou rodar.

## Verificação

- Suíte `tests/test_r1023_repository_skills.py` cobre decisões, commits,
  licenças, descoberta nativa, links locais, contratos positivos/negativos e
  ausência de importação executável.
- RED e GREEN foram executados em worktree isolada; o resultado do gate está
  registrado no recibo da spec, não nesta prosa.
- Os testes verificam estrutura e contraprovas. **Não** provam obediência
  futura de um LLM, qualidade editorial, direito de uso, vigência de norma ou
  funcionamento dos projetos remotos.

## Limitações

- Somente os documentos listados no manifesto foram lidos; o restante de cada
  repositório não foi auditado.
- Nenhum download de livro, dataset, modelo ou corpus foi feito.
- Nenhuma skill foi executada por um modelo nesta rodada; a descoberta nativa
  do OpenCode foi confirmada pela documentação e pelo dispatcher local.
- O bloqueio da delegação externa por ausência de RED foi resolvido para a
  spec de software; a revisão textual externa permaneceu indisponível e não é
  apresentada como concluída.
- Este documento não é parecer jurídico.
