# Adoção seletiva de skills Claude — R1049

Data: 2026-11-03. Implementação local baseada na triagem R1048. **Nenhum
repositório foi clonado; nenhum código de terceiro foi copiado ou executado.**
As fontes foram fixadas por commit em [`sources.json`](sources.json).

## O que foi implementado

| Frente | Skill local | Conteúdo |
|---|---|---|
| SDD/TDD | `superpowers-sdd-tdd` | RED→GREEN→REFACTOR, planos pequenos, debugging, verificação |
| Academia | `rigor-academico-chgagne` | fontes, bibliografia invertida, claims, provas |
| Ciência | `kdense-ciencia-seletiva` | **8 protocolos** em `references/` |
| Motion | `motion-design-seletivo` | **5 protocolos** de motion/data |
| QA de vídeo | `video-director-qa` | gates + `scripts/video_qa.py` |
| Receitas | `video-shotcraft-selecao` | **10 receitas originais** em JSON |
| Catálogo | `agentes-engenharia-selecao` | **10 papéis** em JSON |
| Pesquisa | `laboratorio-pesquisa-isolado` | `research_lab/` file-first com budget |

Total: **8 skills novas** em `.opencode/skills`, sem scripts de terceiros dentro
das skills.

## K-Dense: catálogo completo + 8 protocolos

`literatura`, `citação`, `hipótese`, `delineamento`, `estatística`, `poder`,
`peer review` e `análise exploratória`. A skill é uma guarda-chuva; cada
protocolo tem entradas, gates e saída. Nenhuma dependência científica foi
instalada.

Além disso, o catálogo completo tem **177 skills em 11 categorias**, com fonte e
commit pinados. **168** instruções permissivas foram espelhadas em
`external/kdense-scientific-agent-skills/`; **9** restritas (GPL, não comercial,
proprietária ou desconhecida) receberam **adaptações originais** em
`.opencode/skills/kdense-adaptacoes-originais/`, sem cópia do texto restrito. O
catálogo é sob demanda e não é auto-carregado. Ver
[`kdense-177.md`](kdense-177.md).

## Motion e QA

`motion-design-seletivo` cobre kinetic typography, data animation, explainer,
lower thirds e B-roll. `video-director-qa` usa o QC local:

```bash
python3 scripts/video_qa.py --video saida.mp4 --out qa.json \
  --expect-frames 600 --expect-fps 30/1 --contact-sheet contato.png
```

O QC mede streams, frames decodificados, fps, duração, loudness, true peak,
silêncio e frames pretos. Ele não ouve, não entende ironia e não aprova estética.

## Smoke real

O QC foi executado no MP4 final R1047:

- status: **pass**;
- 1920×1080, 30 fps, **600 frames**;
- AAC 48 kHz, estéreo;
- **−16,10 LUFS**, true peak **−2,16 dBTP**;
- silêncio mais longo: **0,549 s**;
- nenhum frame preto detectado.

Recibo: [`qa-smoke.json`](qa-smoke.json); contato: [`qa-contact.png`](qa-contact.png).

## Catálogos seletivos

- `video-shotcraft-selecao/references/receitas.json`: 10 padrões originais
  (revelação, recursos, antes/depois, dado, fluxo, depoimento, logo, comparação,
  CTA, gancho vertical). Não são os 124 cartões originais.
- `agentes-engenharia-selecao/references/agents.json`: 10 papéis (revisão,
  teste, debug, segurança, performance, refatoração, API, dados, DevOps, docs).
  Não são os 202 agentes originais.

## Laboratório de pesquisa

`research_lab/` é file-first:

- budget de passos, segundos, custo e chamadas externas;
- `--dry-run` cria plano/manifesto e **não executa**;
- `record_step` registra tempo/custo/artefato;
- `finalize_run` exige revisor humano e veredito;
- status máximo: `completed_pending_external_validation`;
- sem rede, sem LLM, sem experimento.

## Testes

- `tests/test_r1049_skills_adoption.py`: frontmatter, atribuição, licenças,
  8 protocolos K-Dense, 5 motion, 10 receitas, 10 agentes, pin de fontes.
- `tests/test_r1049_video_qa.py`: QC real com vídeo sintético e falha por frames.
- `tests/test_r1049_research_lab.py`: budget, manifesto, dry-run e revisão.

Resultado local: **28 testes R1049 passando**. Regressão completa: **331 passed,
1 skipped**; `doctor` 22/22; guard Remotion 11 casos.

## Limites

- As skills são adaptações textuais; não foram validadas por eval externo.
- Nenhum código de Superpowers, chgagne, K-Dense, motion-skills, video-director,
  video-shotcraft, wshobson, Co-Scientist ou ARIS foi copiado.
- O laboratório não produz descoberta; produz rastro auditável.
- Licenças: MIT/Apache-2.0 conforme `sources.json`; a Remotion License e
  direitos de mídia continuam separados.
- A adoção não altera a conclusão de que o Core não tem paridade com
  Premiere/DaVinci.
