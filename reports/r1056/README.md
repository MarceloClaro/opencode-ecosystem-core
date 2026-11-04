# R1056 — Atlas animado, documentação e vídeo R1055

- **Status:** verificação local concluída; revisão humana e publicação externa pendentes
- **Data:** 2026-11-04
- **Spec:** `specs/SPEC-935-R1056-arquitetura-animada.md`
- **Galeria:** `docs/architecture/ANIMATED.md`
- **Manifesto:** `docs/architecture/animated/manifest.json`
- **Escopo:** documentação e mídia; não é reauditoria do runtime R916

## 1. O que foi entregue

1. **Vídeo R1055 documentado no README e nos índices.** O piloto de qubit tem
   duas versões locais, 16:9 e vertical nativa, com roteiro, referências, câmera
   e QC. O commit anterior `c800112d` contém código, spec, testes e relatório;
   os MP4 continuam ignorados pelo Git.
2. **Atlas animado R1056.** Os 46 blocos Mermaid publicados na raiz e em `docs/`
   foram inventariados, deduplicados por SHA-256 e convertidos em GIF, PNG, SVG
   e Mermaid editável. Os 22 fluxos de `docs/architecture/flows.json` estão
   cobertos; fontes repetidas compartilham a mesma mídia. Total: **49 identidades
   visuais**, **46 blocos** e **22 fluxos**.
3. **Câmera de leitura.** O GIF começa e termina na visão completa, percorre
   até quatro relações existentes e enquadra o nó de destino com zoom adaptativo.
   O destaque é uma guia de leitura, não uma execução observada, telemetria ou
   ordem temporal comprovada.
4. **Acessibilidade.** A prévia padrão é PNG estática; o GIF fica atrás de um
   link e executa um único ciclo de 8 s. SVG ampliável e `.mmd` acompanham cada
   vista. O grafo integral de 2,4 MB não foi truncado: recebeu uma **síntese por
   camadas** declarada como tal, e os artefatos originais continuam disponíveis.

## 2. Como reproduzir

Requisitos já presentes no ambiente: Python 3 com Pillow, Node, Mermaid 12.3.x
e Puppeteer/Chromium local. O exportador **não instala** pacotes e bloqueia
requisições HTTP do navegador.

```bash
# inventário e cobertura (sem render)
python3 scripts/animate_architecture.py --inventory

# geração completa (Mermaid -> SVG -> raster -> GIF -> manifesto -> galeria)
python3 scripts/animate_architecture.py

# verificação sem escrever nem abrir navegador
python3 scripts/animate_architecture.py --check

# testes focais
python3 -m pytest tests/test_r1056_animated_architecture.py -q
```

Se o Mermaid/Puppeteer estiver em outro prefixo, defina
`MERMAID_NODE_MODULES`; se o Chromium estiver fora do padrão, defina
`CHROME_EXECUTABLE`. O renderer usa `securityLevel: strict`, `htmlLabels: false`,
interceptação de rede e recusa de `%%{...}`, `click`, HTML ativo e URLs.

## 3. Verificação observada

- Testes focais: **21 passed (13 R1056 + 8 R1055)**.
- Cobertura: **49** identidades, **46** blocos e **22**
  fluxos; o teste `test_real_inventory_covers_catalog_and_published_blocks`
  compara o catálogo e os documentos reais.
- Cada GIF: 1080×675, 80 quadros, 100 ms por quadro, 8 s, sem loop infinito,
  ≤3 MB por arquivo e orçamento agregado ≤60 MB.
- Total de GIFs: **58,0 MB (58 030 108 bytes)**.
- Renderizador: Mermaid **12.3.0**, Chrome **151.0.7922.47**, Pillow
  **12.3.0**. Hashes de fonte, renderer e cada artefato estão no manifesto.
- `--check` valida cobertura, SHA-256, dimensões, duração, loop, galeria e
  orçamento; ele **não** reabre o navegador nem reescreve arquivos.
- Fonte Mermaid e SVG estático são preservados; o PNG é o primeiro quadro
  (visão completa). O GIF é um derivado, não substitui a fonte.

## 4. Contraprovas e limites

- **Falhas históricas R881:** dois testes falham antes e depois desta rodada:
  1. `test_catalogo_atual_integralmente_publicado_no_readme` recusa a âncora
     `marceloclaro/orchestrator.py` porque o hash do catálogo R916 é anterior ao
     checkout atual;
  2. `test_published_mermaid_manifest_and_rendered_svg_preserve_the_graph` recusa
     a exportação integral existente porque ela diverge da exportação canônica.
  Não reescrevi esses snapshots históricos para “ficar verde”. O atlas R1056
  não depende desses hashes e não afirma que o inventário R916 descreve o
  runtime atual.
- **Delegação:** o workflow `r1056-architecture-gif-review` foi bloqueado por
  `spec_id_required` antes de executar. As tentativas de revisão independente
  com `mermaid-review` e `code-reviewer` falharam por ausência de assinatura
  OpenCode Go. Nenhuma delas produziu parecer; não há validação externa.
- **Câmera:** é 2D (crop/zoom determinístico sobre raster), não 3D, motion blur
  ou profundidade de campo. O enquadramento procura o nó de destino; arestas
  longas podem sair do quadro, e o SVG completo é a fonte para leitura integral.
- **Estética e ciência:** QC técnico de mídia não aprova legibilidade em todos
  os monitores, estética, precisão física do vídeo R1055 ou qualidade da voz.
- **Git:** os MP4 de R1055 e os `.render.png` intermediários não são versionados.
  A publicação continua sendo decisão humana.

## 5. Artefatos principais

| Caminho | Papel |
|---|---|
| `docs/architecture/ANIMATED.md` | galeria, prévias estáticas, links e origens |
| `docs/architecture/animated/manifest.json` | cobertura, metadados e SHA-256 |
| `docs/architecture/animated/*.mmd` | cópia fiel da fonte Mermaid |
| `docs/architecture/animated/*.svg` | vetor ampliável com o desenho completo |
| `docs/architecture/animated/*.png` | primeiro quadro, sem movimento |
| `docs/architecture/animated/*.gif` | animação de um ciclo, 8 s |
| `scripts/animate_architecture.py` | descoberta, câmera, empacotamento e verificação |
| `scripts/render_mermaid_animation.cjs` | render local estrito e geometria |
| `tests/test_r1056_animated_architecture.py` | contratos de cobertura e mídia |
| `reports/r1056/limitations.json` | falhas e delegações não concluídas |

## 6. Decisões

- **GIF, não vídeo:** o pedido era animação documental; 8 s e um ciclo evitam
  peso e movimento perpétuo.
- **Câmera no destino:** enquadrar o nó de destino deixa o rótulo legível e
  mostra a seta entrando; enquadrar o meio de arestas longas produzia quadros
  vazios.
- **Síntese por camadas:** `block-beta` em três colunas foi adotado porque
  subgrafos aninhados permaneciam verticais no Mermaid 12.3.
- **Fonte preservada:** nenhum `.mmd` histórico foi reescrito; o atlas é uma
  camada de apresentação.
