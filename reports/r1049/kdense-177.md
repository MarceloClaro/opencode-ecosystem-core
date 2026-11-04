# K-Dense — 177 skills organizadas em 11 categorias

Fonte pinada: `https://github.com/K-Dense-AI/scientific-agent-skills` commit `a25cf9ec00e2745d03f8704acf6f6919694ccd9a`.
Licença raiz: MIT; **168 instruções espelhadas** e **9 adaptações originais** para as restritas.

## Categorias

| Categoria | Skills |
|---|---:|
| `bioinformatica-genomica` | 36 |
| `clinica-saude` | 7 |
| `escrita-figuras-comunicacao` | 15 |
| `estatistica-dados-ml` | 21 |
| `fisica-matematica-simulacao` | 10 |
| `hipotese-raciocinio-delineamento` | 10 |
| `imagem-sinal-neuro` | 14 |
| `infraestrutura-ia-cientifica` | 10 |
| `literatura-citacao-editorial` | 18 |
| `operacoes-laboratorio-bases` | 15 |
| `quimica-farmacos-materiais` | 21 |

## Adaptações originais (license_hold)

| Skill | Licença original | Adaptação local |
|---|---|---|
| `bioservices` | GPLv3 license | `.opencode/skills/kdense-adaptacoes-originais/references/01-conectores-bio.md` |
| `etetoolkit` | GPL-3.0-or-later | `.opencode/skills/kdense-adaptacoes-originais/references/02-arvores-taxonomia.md` |
| `glycoengineering` | Unknown | `.opencode/skills/kdense-adaptacoes-originais/references/03-glicobiologia.md` |
| `phylogenetics` | Unknown | `.opencode/skills/kdense-adaptacoes-originais/references/09-filogenia.md` |
| `what-if-oracle` | CC BY-NC-SA 4.0 | `.opencode/skills/kdense-adaptacoes-originais/references/04-cenarios.md` |
| `deepspot-m` | PolyForm-Noncommercial-1.0.0 | `.opencode/skills/kdense-adaptacoes-originais/references/05-transcriptomica-espacial.md` |
| `cobrapy` | GPL-2.0 license | `.opencode/skills/kdense-adaptacoes-originais/references/06-modelos-metabolicos.md` |
| `primekg` | Unknown | `.opencode/skills/kdense-adaptacoes-originais/references/07-grafo-medicina.md` |
| `rowan` | Proprietary (API key required) | `.opencode/skills/kdense-adaptacoes-originais/references/08-quimica-nuvem.md` |

## Uso

```bash
python3 -m integrations.kdense_catalog stats
python3 -m integrations.kdense_catalog categories
python3 -m integrations.kdense_catalog search "literature review"
python3 -m integrations.kdense_catalog show literature-review
python3 -m integrations.kdense_catalog show cobrapy
```

O catálogo é sob demanda; `external/` não é auto-carregado. Scripts, assets e dependências não foram copiados nem executados. As 9 restritas têm texto original do Core, não cópia do original.
