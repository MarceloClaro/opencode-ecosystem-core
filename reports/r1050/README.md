# Metacognição, macro-rede e raciocínio científico — R1050

Data: 2026-11-03. Esta rodada melhora o **gate metacognitivo**, o **ledger de
claims do conselho** e cria uma **macro-rede read-only** da orquestração. Também
triou projetos de raciocínio científico/AGI no GitHub. Nenhum projeto foi
instalado ou executado; nenhum é declarado AGI.

## Macro-rede de orquestração

`mci/macro_network.py` projeta os arquivos locais como grafo:

- 1 orquestrador;
- agentes de `agents/catalog/`;
- 50 skills de `.opencode/skills/`;
- 177 skills K-Dense e 11 categorias;
- 4 gates: metacognitivo, conselho científico, QC de vídeo e laboratório isolado;
- arestas `delegates`, `exposes`, `contains`, `routes_to`, `governed_by`,
  `gated_by`.

O snapshot atual tem **576 nós e 768 arestas**. O grafo é **read-only**:
aresta não é execução, inferência ou confiança. CLI:

```bash
python3 -m mci.macro_network summary
python3 -m mci.macro_network snapshot --out reports/r1050/macro-network.json
python3 -m mci.macro_network path --source orchestrator:marceloclaro \
  --target kdense:literature-review --max-depth 5
```

O orquestrador expõe `macro_network_snapshot()` com
`confidence_promoted=false` e `network=false`.

## Gate metacognitivo

`mci/metacognitive_gate.py` classifica claims em:

- `blocked`: sem evidência literal, sem falseabilidade ou evidência não
  verificada;
- `partial`: alta confiança com uma fonte, contradição não resolvida, inferência
  sem mecanismo ou Brier > 0,25 com amostra suficiente;
- `candidate`: evidência literal e falseabilidade, sem validação externa;
- `externally_supported`: validação externa independente declarada com verificador
  e hash de artefato.

**Nenhum status é verdade absoluta.** `truth_claim=false` sempre; voto, nota,
payoff e autoavaliação não promovem claim. O método do orquestrador
`metacognitive_claim_gate` registra observação no MetaBus sem aumentar confiança.

## Conselho de 13 e ledger de claims

`scientific_lab.council.validate_claims()` acrescenta um ledger explícito:
claim, confiança, evidência literal, nível de inferência, falseabilidade,
mecanismo, contradições e status. `validate_report(..., claims=...)` inclui o
`claim_gate`. Regras:

- `supported` com uma única fonte → `partial`;
- confiança ≥ 0,8 exige duas fontes independentes;
- contradição não resolvida → `partial`;
- `inference`/`hypothesis` sem mecanismo → `partial`;
- recorte que não existe na fonte → erro;
- agregação nunca usa votação para verdade.

Isso complementa o Conselho de 13 existente: citação literal contra a fonte,
Feynman com observações/inferências separadas e revisão humana obrigatória.

## AGI e raciocínio científico — triagem

Fonte pinada: [`agi-scientific-reasoning.json`](agi-scientific-reasoning.json).

| Repositório | Licença | Papel | Uso recomendado |
|---|---|---|---|
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | MIT | relatório longo com citações | referência para síntese; não é verdade |
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | Apache-2.0 | RAG científico com citações | referência para recuperação e citação |
| [google-deepmind/alphageometry](https://github.com/google-deepmind/alphageometry) | Apache-2.0 | geometria formal | referência de domínio restrito; não é AGI |
| [SakanaAI/AI-Scientist-v3](https://github.com/SakanaAI/AI-Scientist-v3) | Apache-2.0 | orquestração de agentes científicos | laboratório isolado, orçamento e revisão |
| [Future-House/robin](https://github.com/Future-House/robin) | Apache-2.0 | descoberta multiagente | referência de workflow; não executar sem gate |
| [allenai/discoveryworld](https://github.com/allenai/discoveryworld) | Apache-2.0 | ambiente de avaliação | benchmark externo, não runtime |
| [principia-ai/PhysGym](https://github.com/principia-ai/PhysGym) | MIT | benchmark de raciocínio interativo | eval externo; não prova ciência |
| [idiap/SciR](https://github.com/idiap/SciR) | GPL-3.0 | dedução/indução/abdução causal | **license_hold**; só referência |
| [Paureel/LLM-SCI-GEN](https://github.com/Paureel/LLM-SCI-GEN) | MIT | bibliografia de hipóteses | descoberta, não implementação |

**Nenhum é AGI.** Benchmarks medem tarefas estreitas; demo não é inteligência
geral. AI-Scientist v1/v2 têm licença `NOASSERTION` e ficaram fora da
implementação. `SciR` é GPL-3.0 e exige decisão jurídica.

## Testes

- `tests/test_r1050_metacognitive_gate.py` (7)
- `tests/test_r1050_council_claims.py` (5)
- `tests/test_r1050_macro_network.py` (4)

Regressão: **347 passed, 1 skipped**; `doctor` 22/22; guard Remotion 11 casos.

## Limites

- A macro-rede é uma projeção de arquivos; não prova que um agente executou.
- O gate não substitui revisão humana, estatística, ética ou validação externa.
- `externally_supported` ainda não é verdade absoluta.
- Nenhum projeto AGI foi instalado, clonado ou executado.
- Contagens de nós/arestas mudam quando o catálogo ou as skills mudam.
