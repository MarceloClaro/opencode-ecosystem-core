# R1051 — pesquisador científico ponta a ponta

Data: 2026-11-03/04. Frente: transformar o pesquisador científico do Core em um
fluxo **tema → protocolo → busca → evidência → auditoria → manuscrito para
validação humana**, usando a skill MIT `database-lookup` como referência de
contrato de recuperação, sem copiar ou executar código de terceiros.

## O que foi entregue

| Item | Caminho |
|---|---|
| Pipeline | `scientific_lab/research_project.py` |
| CLI | `research project` em `scientific_lab/native/cli.py` |
| Spec | `specs/SPEC-1051-pesquisador-cientifico-ponta-a-ponta.md` |
| Testes | `tests/test_r1051_research_project.py` |
| Schemas | `scientific_lab/schemas/research-project-manifest.schema.json`, `retrieval-contract.schema.json` |
| Documentação | `docs/SCIENTIFIC_RESEARCH_PIPELINE_R1051.md` |
| Regressão | `reports/r1051/final-regression.txt` |

## Comando

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "saúde mental em estudantes universitários" \
  --out projects/saude-mental-r1051 \
  --dry-run
```

Para executar a busca:

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "saúde mental em estudantes universitários" \
  --question "Quais evidências disponíveis descrevem a saúde mental em estudantes universitários?" \
  --out projects/saude-mental-r1051 \
  --sources openalex,crossref,europepmc,arxiv
```

Para um corpus fornecido, sem rede:

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "meu tema" --out projects/meu-corpus-r1051 \
  --dry-run --corpus corpus.json
```

## O que o pipeline faz

1. Valida tema, pergunta, fontes, orçamento e corpus antes de escrever.
2. Gera intake e contrato de recuperação com entidade, identificadores,
   endpoints, filtros, paginação, limites, proveniência e política para dados
   externos não confiáveis.
3. Cria protocolo de revisão em rascunho (`status=draft`).
4. Executa a busca nativa ou registra `blocked` sem inventar registros.
5. Deduplica por DOI/título via `review.ingest`.
6. Produz triagem lexical assistida, sem decisão de inclusão/exclusão.
7. Extrai recortes literais de resumos indexados e/ou corpus fornecido.
8. Aplica `mci.metacognitive_gate.aggregate` e, no corpus,
   `council.validate_claims`.
9. Gera análise descritiva sem teste estatístico, meta-análise ou causalidade.
10. Audita consistência, placeholders e overclaim.
11. Gera manuscrito IMRaD em Markdown e checklist humano.
12. Sela o pacote com manifesto SHA-256.

## Evidência de execução

| Verificação | Resultado |
|---|---|
| Testes R1051 | **13 passed** |
| Regressão R1033–R1051 | **360 passed, 1 skipped** |
| Guard Remotion | **11 casos, ok** |
| `doctor` | **healthy 22/22** |
| Dry-run real | `/tmp/opencode/r1051-dry`, status `planned`, manifesto íntegro |
| Busca externa real | **não executada neste ciclo** |
| PDFs baixados | **0** |
| Credenciais usadas | **0** |
| Publicação | **nenhuma** |

O dry-run real não instanciou buscador; o teste `test_dry_run_does_not_instantiate_searcher`
usa uma classe que falha se for construída.

## Estados do manifesto

- `planned`: dry-run ou corpus sem busca.
- `blocked`: busca falhou ou auditoria dura falhou.
- `partial`: pacote gerado sem claims/registros suficientes.
- `completed_pending_external_validation`: pacote interno completo, validação
  humana e externa pendentes.

`truth_claim`, `external_validation` e `human_review_required` são fixos:
`false`, `false`, `true`.

## Limites

- A busca real depende de rede e limites dos provedores; não foi executada
  neste ciclo.
- Claims de metadados são em nível de resumo indexado; não houve leitura do
  texto integral.
- A triagem é lexical e assistida; não substitui dois revisores humanos.
- O corpus é validado contra si mesmo, não contra a versão publicada.
- Não há teste estatístico, meta-análise, risco de viés ou inferência causal.
- O manuscrito é rascunho; não é artigo aceito, publicado ou Qualis A1.
- A suíte integral do repositório não foi concluída dentro do limite de 15
  minutos; a regressão focada R1033–R1051 passou integralmente.
