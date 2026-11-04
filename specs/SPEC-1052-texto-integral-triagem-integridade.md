---
spec_id: SPEC-1052
title: Texto integral, triagem humana, integridade de literatura e atualização do projeto
version: 1.0.0
status: green
test_file: tests/test_r1052_fulltext.py, tests/test_r1052_integrity.py, tests/test_r1052_screening.py, tests/test_r1052_refresh.py
---

# SPEC-1052 — do resumo ao texto integral, com decisão humana

## Problema

O R1051 entregou a espinha dorsal auditável: contrato de recuperação, busca,
deduplicação, triagem lexical assistida, evidência literal em nível de resumo,
gate metacognitivo, auditoria e manuscrito. Ele não lia texto integral, não
consumia decisões humanas de triagem, não verificava retratações/correções e
não permitia atualizar um projeto sem recriá-lo.

Isso limita o pesquisador a um **mapa de resumos**. Para uma revisão de
literatura defensável, é preciso ligar arquivos de texto integral, aprovação
humana explícita, decisões de triagem registradas e integridade editorial.

## Escopo

1. Indexar PDFs, Markdown e TXT locais, com SHA-256, páginas/parágrafos e
   contagens, sem reter o texto integral nos JSONs.
2. Casamento entre arquivos e estudos por DOI, título, nome de arquivo e
   similaridade, com marcação de ambiguidade.
3. Extração determinística de recortes citáveis com página/parágrafo,
   `quote_sha256` e `source_sha256`.
4. Aprovação humana explícita em arquivo próprio, exigindo revisor, data,
   `human_confirmation=true` e IDs conhecidos.
5. Anotação `verified` apenas com `source_file` e `human=True`; os demais
   recortes ficam `candidate` ou `rejected`.
6. Leitura das decisões de `review.screen`, com resumo de pendências,
   conflitos, revisores e PRISMA.
7. Verificação de retratações/correções/atualizações via Crossref, com
   verificador injetável e status observacional.
8. Atualização de projeto existente (`refresh`) sem repetir busca ou recriar
   estudos, preservando decisões e claims.
9. Download opcional apenas por rotas abertas verificadas, com `rights_basis`,
   hash e recusa explícita de paywall.
10. Auditoria e manifesto atualizados para os novos artefatos.

## Não objetivos

- Não contornar paywall, Sci-Hub ou fonte não autorizada.
- Não declarar aprovação humana sem arquivo de aprovação.
- Não transformar `no_update_found` em atestado de integridade.
- Não fazer meta-análise, risco de viés ou GRADE nesta revisão.
- Não declarar validação externa, aceite editorial ou publicação.
- Não usar LLM para reescrever ou inventar recortes.

## Contratos

### Texto integral

`fulltext-index.json` contém apenas metadados: `fulltext_id`, caminho relativo,
SHA-256, bytes, formato, número de páginas/parágrafos, caracteres e limitações.
O texto completo permanece no arquivo original.

`fulltext-candidates.json` contém recortes candidatos com:

- `claim_id`, `study_id`, `article_id`;
- `page`, `locator` (`p.N` ou `par.N`);
- `quote`, `quote_sha256`, `source_file`, `source_sha256`;
- `match_method`, `match_confidence`;
- `verification_status=candidate`.

### Aprovação

`fulltext-approval.template.json` é um template. A aprovação real exige:

```json
{
  "human_confirmation": true,
  "reviewer": "nome",
  "reviewed_at": "data ISO",
  "decision": "approved",
  "approved_claim_ids": ["CLAIM-..."],
  "rejected_claim_ids": []
}
```

IDs desconhecidos, sobreposição entre aprovados/rejeitados ou ausência de
confirmação humana são recusados.

### Triagem

`screening-summary.json` lê `09_provenance/systematic_review/screening/*.json`
e separa:

- pendentes;
- triagem de título/resumo;
- decisão de texto integral;
- incluídos, excluídos e incertos;
- conflitos entre revisores;
- estudos com apenas um revisor.

`human_verified` só é verdadeiro com decisões de texto integral para todos os
estudos, dois revisores e nenhum conflito. Pendência nunca vira inclusão.

### Integridade

`integrity-checks.json` registra por estudo:

- DOI;
- status `retracted`, `retracted_notice`, `correction`, `update`,
  `no_update_found`, `unchecked` ou `error`;
- atualizações e hash da resposta;
- limitações.

`no_update_found` não é certificado de integridade. Estudo retratado é excluído
dos claims e registrado como lacuna.

### Atualização

`refresh` não repete busca e não recria estudos. Ele:

- relê decisões humanas;
- aplica texto integral aprovado;
- reaplica integridade;
- preserva claims/cartões existentes;
- remove claims de estudos retratados;
- substitui annotations de texto integral de forma idempotente;
- regenera manuscrito, auditoria e manifesto.

## Critérios de aceitação

1. Indexação de PDF/MD/TXT com hash e páginas/parágrafos, sem texto integral no JSON.
2. Casamento por DOI/título/arquivo, com ambiguidade explícita.
3. Recortes com localizador, hash do arquivo e hash do trecho.
4. Aprovação recusada sem `human_confirmation`, revisor, data ou IDs conhecidos.
5. `verified` só existe com `source_file` e `human=True`; o resto é candidato/rejeitado.
6. Resumo de triagem lê `review.screen`, detecta conflitos e pendências.
7. `human_verified` exige dois revisores, decisão de texto integral e ausência de conflito.
8. Integridade classifica retração, correção, atualização, ausência e erro.
9. Estudo retratado não gera claim e vira lacuna.
10. `refresh` preserva decisões/claims e é idempotente para annotations de texto integral.
11. Download OA só aceita `rights_basis` permitido e SHA-256; paywall não é contornado.
12. Auditoria cobre downloads, candidatos, aprovação, triagem e integridade.
13. Manifesto inclui os novos artefatos e hashes.
14. CLI expõe `--fulltext-dir`, `--fulltext-approval`, `--allow-open-access`,
    `--check-integrity` e o subcomando `refresh`.
15. Testes herméticos não usam rede real.

## RED/GREEN

RED: 16 testes novos falharam antes dos módulos e da integração.

GREEN: `tests/test_r1052_fulltext.py`, `tests/test_r1052_integrity.py`,
`tests/test_r1052_screening.py` e `tests/test_r1052_refresh.py` passam; a
regressão R1051+R1052 fica em **29 passed**.

## Evidência de execução

- Testes R1051+R1052: **29 passed**.
- Regressão focada R1033–R1052: **376 passed, 1 skipped**.
- `doctor`: **healthy 22/22**.
- Nenhum PDF, credencial ou publicação usados nos testes.
- O benchmark real de 2–3 fontes é registrado em `reports/r1052/`.

## Limitações

- A aprovação humana confirma o recorte contra o arquivo fornecido, não contra a
  versão publicada.
- O casamento textual pode errar em PDFs sem camada de texto.
- Crossref pode não registrar toda retração/correção.
- `refresh` não repete a busca; atualização de literatura exige nova rodada.
- Meta-análise, risco de viés, GRADE e submissão continuam fora desta revisão.
