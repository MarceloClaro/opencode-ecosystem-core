# Catálogo completo — 177 skills em 11 categorias

O catálogo local está em `external/kdense-scientific-agent-skills/CATALOG.json`,
com commit pinado e fonte por skill. Ele é **sob demanda**: `external/` não é
auto-carregado pelo OpenCode.

| Categoria | Skills |
|---|---:|
| Bioinformática e genômica | 36 |
| Química, fármacos e materiais | 21 |
| Estatística, dados e ML | 21 |
| Literatura, citação e editorial | 18 |
| Escrita, figuras e comunicação | 15 |
| Operações de laboratório e bases | 15 |
| Imagem, sinal e neuro | 14 |
| Física, matemática e simulação | 10 |
| Hipótese, raciocínio e delineamento | 10 |
| Infraestrutura de IA científica | 10 |
| Clínica e saúde | 7 |

**168** instruções permissivas foram espelhadas; **9** ficaram em
`license_hold` (GPL, não comercial, proprietária ou desconhecida) e só têm
metadados/fonte. Nenhum script, asset ou dependência foi copiado ou executado.

## Comandos

```bash
python3 -m integrations.kdense_catalog stats
python3 -m integrations.kdense_catalog categories
python3 -m integrations.kdense_catalog search "literature review"
python3 -m integrations.kdense_catalog show literature-review
```

## Gate

Antes de executar qualquer passo de uma skill: leia o `SKILL.md`, confira
licença, dependências, rede, credenciais e risco; peça autorização. O catálogo
não é aprovação científica, clínica ou de segurança.
