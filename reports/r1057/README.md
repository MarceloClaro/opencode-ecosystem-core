# R1057 — SVG primário, fontes Mermaid e pulso processual

- **Status:** verificado localmente; revisão humana e publicação pendentes
- **Data:** 2026-11-04
- **Spec:** `specs/SPEC-935-R1057-svg-pulse.md`
- **Galeria:** `docs/architecture/ANIMATED.md`
- **Manifesto:** `docs/architecture/animated/manifest.json`
- **Antecessor:** R1056 (`reports/r1056/README.md`)

## 1. Correções

1. **Âncoras do catálogo.** `flows.json` passou ao modo `current`; 115 fontes
   tiveram hash e linha recalculados a partir de arquivos rastreados. O
   comando `python3 scripts/sync_readme_flowcharts.py --refresh-current`
   atualiza a base e a apresentação.
2. **Integral Mermaid.** `dependencies.mmd` e
   `mermaid-correspondence.json` foram reexportados do inventário vigente;
   `dependencies-mermaid.svg` foi rerenderizado. Contagens: 711 módulos,
   1014 pares, 1153 declarações e 6843 símbolos.
3. **R881.** Os dois testes que falhavam passam sem reescrever snapshots
   históricos: `test_catalogo_atual_integralmente_publicado_no_readme` e
   `test_published_mermaid_manifest_and_rendered_svg_preserve_the_graph`.

## 2. SVG primário

- `scripts/svgify_markdown.py` troca cada bloco Mermaid de `README.md` e
  `docs/` por um `<img>` SVG, mantendo a fonte em
  `<details><summary>Fonte Mermaid (auditoria)</summary>`.
- O bloco de 22 fluxos gerado por `sync_readme_flowcharts.py` também mostra
  SVG, com links para GIF, PNG e `.mmd`.
- A fonte Mermaid não é removida: continua auditável, e os testes históricos
  que contam blocos Mermaid permanecem válidos.
- `--check` é idempotente e não escreve.

## 3. Pulso na ordem do processo

- `process_order()` calcula uma ordem topológica dos nós (Kahn), com empate
  por posição e quebra determinística de ciclos.
- Todas as arestas recebem um pulso; o GIF mostra uma onda avançando pela
  ordem do desenho, em vez de quatro arestas arbitrárias.
- Diagramas sem arestas destacam os nós em sequência, com caixa translúcida.
- A câmera permanece estável para preservar a leitura integral; o movimento
  vem do pulso. Isso também reduz muito o tamanho dos GIFs.
- O rodapé declara `PULSO NA ORDEM DO PROCESSO i/N` ou `NÓS EM SEQUÊNCIA i/N`.

## 4. Verificação

- R881: **31 passed**.
- Suítes focais: **189 passed** (R881, R1055, R1056, R1057, R127, R231, R236, R237, R449, R455, R879, R911, R916 e R919).
- `svgify_markdown.py --check`: **pass, 0 alterações e 0 fontes não correspondidas**.
- `sync_readme_flowcharts.py --check`: **pass**.
- `animate_architecture.py --check`: **pass — 46 diagramas, 22 fluxos e 13.771.507 bytes**.
- GIFs: **46** identidades, **13,8 MB (13.771.507 bytes)**, 1080×675, 80 quadros,
  8 s, um ciclo.
- `doctor`: **22/22, healthy**.

## 5. Artefatos

| Caminho | Papel |
|---|---|
| `scripts/svgify_markdown.py` | SVG primário + fonte Mermaid recolhida |
| `scripts/sync_readme_flowcharts.py` | bloco de fluxos em SVG e âncoras atuais |
| `docs/architecture/flows.json` | fontes e hashes do checkout |
| `docs/architecture/dependencies-mermaid.svg` | grafo integral rerenderizado |
| `docs/architecture/animated/manifest.json` | cobertura, pulso e hashes |
| `tests/test_r1057_svg_pulse.py` | ordem topológica e SVG idempotente |

## 6. Limites

- O pulso é uma ordem declarada de leitura; não prova que o processo executa
  nessa sequência, nem mede tempo real.
- A apresentação SVG não substitui a fonte Mermaid, o inventário ou os testes
  de proveniência.
- Não há validação externa; a estética e a legibilidade exigem revisão humana.
- As falhas R449 de README foram corrigidas nesta rodada (nome da seção de
  início rápido e frase sobre `curl`/`bash`); as suítes focais não têm falha
  conhecida. A suíte integral do repositório não foi executada por completo.
