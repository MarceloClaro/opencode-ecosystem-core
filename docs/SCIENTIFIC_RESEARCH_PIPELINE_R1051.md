# Pesquisador científico ponta a ponta — R1051

O pipeline R1051 transforma um **tema** em um pacote file-first de pesquisa:
contrato de recuperação, protocolo em rascunho, busca, deduplicação, triagem
assistida, evidências literais, análise descritiva, auditoria, manuscrito IMRaD
e checklist de validação humana.

> **Evolução:** o R1052 acrescenta texto integral, triagem humana, integridade
> via Crossref e `research refresh`. Ver
> [`SCIENTIFIC_RESEARCH_PIPELINE_R1052.md`](SCIENTIFIC_RESEARCH_PIPELINE_R1052.md).

Ele não publica, não baixa PDFs, não usa credenciais e não declara o artigo como
aceito, publicado, Qualis A1 ou validado externamente.

## Comandos

### Planejar sem rede

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "saúde mental em estudantes universitários" \
  --out projects/saude-mental-r1051 \
  --dry-run
```

O dry-run gera intake, contrato, protocolo, plano de busca, triagem vazia,
gate bloqueado, manuscrito metodológico e checklist. Nenhum buscador é
instanciado.

### Executar a busca

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "saúde mental em estudantes universitários" \
  --question "Quais evidências disponíveis descrevem a saúde mental em estudantes universitários?" \
  --out projects/saude-mental-r1051 \
  --sources openalex,crossref,europepmc,arxiv \
  --limit 30 \
  --per-platform 5 \
  --timeout 90
```

A busca usa o `MultiSearcher` nativo do Core. O `--timeout` é um limite de
parede para a etapa de busca; se estourar, o estado vira `blocked` e o erro é
registrado. Se uma plataforma falhar, o erro
é registrado e as demais continuam; se a busca inteira falhar, o estado vira
`blocked` e nenhum registro é inventado.

### Usar um corpus fornecido

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "meu tema" \
  --out projects/meu-corpus-r1051 \
  --dry-run \
  --corpus corpus.json
```

Formato do corpus:

```json
{
  "sources": [
    {"id": "S1", "text": "texto literal", "provenance": "arquivo ou URL"}
  ],
  "claims": [
    {
      "id": "CLAIM-C1",
      "text": "afirmação",
      "confidence": 0.7,
      "evidence": [{"source_id": "S1", "quote": "trecho literal"}],
      "inference_level": "observation",
      "falsifier": "critério de refutação",
      "mechanism": "mecanismo declarado com pelo menos vinte caracteres",
      "contradictions": [],
      "status": "supported"
    }
  ]
}
```

O conselho valida cada recorte contra o texto fornecido. Um trecho que não é
substring da fonte é recusado antes de qualquer manuscrito.

## Estrutura do pacote

```text
00_contract/
  intake.json
  retrieval-contract.json
  systematic-review-protocol.json
01_sources/
  search-plan.json | search-error.json | metadata/search-*.json
  source-records.json
  systematic_review/studies/*.json
02_screening/
  triage.json
03_evidence/
  claims.json
  claim-gate.json
  evidence-cards.json
  gaps.json
  council-claims.json          # quando há corpus
  corpus-sources.json          # quando há corpus
04_analysis/
  descriptive.json
05_audit/
  audit-report.json
06_manuscript/
  manuscript.md
  references.json
07_validation/
  VALIDATION.md
07_artifacts/
  systematic_review/prisma-flow.json
  evidence_graph/research-evidence-graph.json
08_manifest/
  project-manifest.json
README.md
```

## Contrato de recuperação

O contrato registra:

- entidade-alvo, pergunta e status (`explicit` ou `provisional_from_theme`);
- identificadores aceitos e bases com endpoint, acesso, papel e limite;
- separação entre filtros de servidor e filtros locais;
- paginação limitada por plataforma, sem alegar exaustão;
- orçamento de queries, registros, downloads e timeout;
- data de acesso, caminho de log e algoritmo de hash;
- política para respostas externas não confiáveis;
- restrições ausentes e necessidade de esclarecimento;
- status sempre `draft` sem aprovação humana.

A referência conceitual é a skill MIT
[`database-lookup`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/database-lookup/SKILL.md),
versão 1.8. Nenhum código, script ou endpoint da skill é executado pelo Core.

## Estados

| Estado | Significado |
|---|---|
| `planned` | dry-run ou corpus sem busca; nenhum resultado externo foi lido |
| `in_progress` | reservado para execução interrompida |
| `blocked` | busca falhou ou auditoria dura falhou |
| `partial` | pacote gerado, mas sem claims/registros suficientes |
| `completed_pending_external_validation` | pacote interno completo; validação humana e externa pendentes |

Em todos os estados: `truth_claim=false`, `external_validation=false` e
`human_review_required=true`.

## Evidência em dois níveis

1. **Metadados e resumo indexado.** Para cada estudo único com resumo
   suficiente, o pipeline extrai uma frase literal, registra o SHA-256 do resumo
   e cria um claim do tipo “o resumo indexado contém este trecho”. O status
   máximo é `candidate`.
2. **Corpus fornecido.** O conselho valida citações contra o texto do operador.
   O resultado pode ser `partial` ou `candidate`, nunca `truth`.

Nenhum dos níveis substitui a leitura do texto integral ou a conferência da
versão publicada.

## Auditoria

`05_audit/audit-report.json` verifica:

- presença de intake, protocolo e contrato completo;
- pergunta explícita ou provisória marcada;
- busca executada, planejada ou bloqueada;
- reconciliação de contagens e duplicatas;
- triagem pendente de humano;
- claims com evidência;
- gate sem promoção de confiança a verdade;
- referências presentes;
- seções do manuscrito;
- checklist de validação;
- marcadores de preenchimento;
- linguagem absoluta não negada (overclaim).

O status `pass_with_pending_human` significa apenas que a consistência interna
passou; não é aprovação científica.

## Validação humana

`07_validation/VALIDATION.md` lista, com estado `pending_human`:

- confirmação da pergunta e do escopo;
- aprovação do protocolo;
- cobertura e datas das bases;
- triagem por dois revisores independentes;
- obtenção legal dos textos integrais;
- conferência de cada citação;
- retratações e correções;
- risco de viés;
- análise e limites inferenciais;
- ética, consentimento e conflitos;
- adequação ao periódico;
- ausência de overclaim;
- autorização de submissão ou publicação.

## Limites

- A busca depende de rede, disponibilidade e limites dos provedores.
- A ausência de resultados não prova ausência de literatura.
- A triagem é lexical e assistida; não decide inclusão ou exclusão.
- Claims de metadados são em nível de resumo indexado.
- O corpus é validado contra si mesmo, não contra a versão publicada.
- Não há teste estatístico, meta-análise, modelagem causal ou risco de viés.
- Não há download de PDF, uso de credencial, upload ou publicação.
- O manuscrito é rascunho para validação humana.

## Testes

```bash
python -m pytest -q tests/test_r1051_research_project.py
```

Os testes cobrem dry-run sem rede, busca com deduplicação, falha de busca sem
fabricação, pergunta provisória, corpus literal, scanners de overclaim e
placeholder, integridade do manifesto, schemas e roteamento da CLI.
