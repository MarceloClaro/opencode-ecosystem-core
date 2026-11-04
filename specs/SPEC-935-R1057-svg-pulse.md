# SPEC-935-R1057 — SVG primário, fontes Mermaid e pulso processual

## Estado

Implementado e verificado localmente; substitui a apresentação inline de Mermaid por SVG nas páginas
renderizadas, mantendo a fonte Mermaid recolhida para auditoria. Corrige as
duas falhas R881 sem reescrever snapshots históricos e refaz os GIFs dos
fluxogramas com um pulso que percorre todas as arestas na ordem do processo.

## Requisitos

1. **SVG primário.** Cada diagrama Mermaid de `README.md` e `docs/` deve
   mostrar um `<img>` SVG estático. O código Mermaid permanece em
   `<details><summary>Fonte Mermaid (auditoria)</summary>` e em link `.mmd`.
   O SVG não depende do renderizador Mermaid do GitHub.
2. **Compatibilidade.** Os testes históricos que contam blocos Mermaid
   continuam válidos porque a fonte não é removida; a apresentação visível é
   SVG. Nenhum teste é apagado para obter verde.
3. **Âncoras atuais.** `flows.json` deve ser atualizado a partir dos arquivos
   rastreados atuais, com hash e linha recalculados. O modo `current` declara
   que a base é o checkout, não um permalink histórico.
4. **Integral consistente.** `dependencies.mmd` e
   `mermaid-correspondence.json` são reexportados do inventário vigente;
   `dependencies-mermaid.svg` é rerenderizado e conserva os mesmos nós/pares.
   Contagens documentais passam a refletir o inventário (711 módulos, 1014
   pares, 1153 declarações, 6843 símbolos).
5. **Pulso na ordem do processo.** Para cada grafo com arestas, calcular uma
   ordem topológica de nós (Kahn; empate por posição; ciclo resolvido de forma
   determinística) e ordenar as arestas por essa ordem. Todas as arestas
   recebem um pulso; o GIF mostra a onda avançando, não quatro arestas
   arbitrárias.
6. **Sem arestas.** Diagramas de camadas recebem destaque sequencial dos nós
   na ordem de leitura, com a mesma declaração de que não é execução.
7. **Acessibilidade e tamanho.** SVG/PNG permanecem disponíveis; GIF é opcional,
   de um ciclo, sem loop infinito, ≤3 MB por arquivo. O orçamento agregado pode
   chegar a 65 MB nesta revisão por causa dos pulsos em todas as arestas; o
   limite e a medição ficam no relatório.
8. **Limites.** Nada é publicado. O pulso é ilustração de ordem declarada, não
   telemetria, execução observada ou garantia de que o caminho ocorre.

## Aceites

- R881: os dois testes que falhavam passam; a suíte integral de Mermaid
  permanece verde.
- `sync_readme_flowcharts.py --check` passa após `--refresh-current`.
- Nenhum bloco Mermaid visível fora de `<details>` de auditoria.
- `svgify_markdown.py --check` é idempotente e cobre todos os blocos com
  fonte no manifesto.
- Testes de ordem: toda aresta aparece uma vez; se `e1` termina onde `e2`
  começa, `e1` vem antes; ciclos não entram em loop.
- `animate_architecture.py --check` passa; cada GIF tem todos os pulsos
  agendados e o total respeita o orçamento declarado.
- Revisão visual de amostras; sem validação externa.
