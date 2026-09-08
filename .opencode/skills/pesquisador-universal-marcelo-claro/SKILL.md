---
name: pesquisador-universal-marcelo-claro
description: >
  Use para pesquisa científica rigorosa e auditável: busca/download open access,
  revisão sistemática e living review, Evidence Graph, meta-análise, GRADE,
  inferência causal, Agent Mesh, Mission Control, replicação federada e release
  reproduzível. MarceloClaro permanece o orquestrador primário do Core.
---

# Pesquisador Universal Marcelo Claro v4.2 — Core-Native Open Science

A integração v4.2 mantém o OpenCode Ecosystem Core como kernel/runtime e torna o
caminho básico de busca/download científico nativo do próprio Core alinhado à
política Open Science da supercamada.

## Entrada nativa

```bash
python -m marceloclaro.cli pesquisa "tema" --max-papers 10
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab synthesis --help
python -m marceloclaro.scientific_lab grade --help
python -m marceloclaro.scientific_lab causal --help
python -m marceloclaro.scientific_lab federation --help
python -m marceloclaro.scientific_lab production --help
```

## Política de literatura científica

O runtime ativo do Core prioriza:

1. URL já classificada como acesso aberto/repositório/preprint;
2. OpenAlex por DOI;
3. Unpaywall por DOI quando e-mail está configurado;
4. Europe PMC por DOI;
5. arXiv/SciELO/Semantic Scholar e demais fontes abertas já resolvidas pelos buscadores.

Crossref permanece fonte de DOI/metadados e não é interpretada como autorização
universal de PDF. HTTP 200, DOI ou URL de publisher isoladamente não comprovam
acesso aberto. Todo PDF aceito precisa começar em `%PDF-`, respeitar limite de
tamanho e recebe SHA-256.

## Supercamada completa

Para revisão sistemática/living, Evidence Graph, meta-análise, GRADE,
causalidade, Agent Mesh, Mission Control, federação e supply chain, a bridge
procura a instalação completa nesta ordem:

1. `PESQUISADOR_UNIVERSAL_HOME`;
2. `PU_PREFIX/skill`;
3. `~/.local/share/pesquisador-universal/skill`.

A instalação completa v4.1 continua verificada por versão e manifesto antes de
dispatch. A integração v4.2 reduz a dependência externa para busca/download,
mas não duplica todos os engines científicos dentro do kernel.

## Invariantes

- `marceloclaro` é o único orquestrador primário.
- ausência da supercamada completa é reportada explicitamente.
- o commit `a5478054...` permanece baseline auditada histórica; o HEAD evolui.
- nenhum score, consenso computacional, GRADE ou estimativa causal possui autoridade epistêmica automática.
- nenhum executor destinado a contornar paywalls integra o runtime ativo de pesquisa.
- downloads aceitos são content-addressed por SHA-256 e validados como PDF.

Veja `specs/SPEC-017-research.md`, `docs/SCIENTIFIC_LAB_V41.md` e
`specs/SPEC-935-R468-pesquisador-universal-v41-core-integration.md`.
