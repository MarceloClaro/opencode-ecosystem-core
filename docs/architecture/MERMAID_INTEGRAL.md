# Arquitetura integral em Mermaid — R916

> [Atlas animado R1056](ANIMATED.md): 22 fluxos e vistas publicadas, com fonte
> editável e alternativa sem movimento. Para este grafo integral, o GIF é
> **somente uma síntese por camadas**; os módulos e as arestas continuam nos
> artefatos originais abaixo. Não é uma nova auditoria do código.

**711 módulos Python**, **1014 pares internos**, **1153 declarações de importação**, **6843 símbolos**, **45 pacotes**, **18 camadas** e **22 fluxogramas**.

Base Git `b7f5683f84609a5e957a56af4ca090c905f5ab80`; identidade das fontes locais `1a170ef08b78071c65b55ee5cc0bb4821d77622b8326d018835dbf4a27d6ec7a`.

A [fonte Mermaid — raw 2,4 MB](https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/docs/architecture/dependencies.mmd), o [SVG Graphviz](dependencies.svg) e o
[SVG Mermaid](dependencies-mermaid.svg) representam os mesmos conjuntos de
módulos e pares. Os layouts são diferentes.

> **GitHub:** o arquivo integral tem 2,4 MB e excede o limite do renderizador
> Mermaid. Não espere vê-lo renderizado na interface; use o SVG, a página
> offline ou baixe o raw e renderize localmente com `mermaid-render-config.json`. O [inventário](architecture-inventory.json)
explicita produção rastreada local e metadados da base Git; o
[guia R916](../ARQUITETURA_COMPLETA_CORE_R916.md) detalha exclusões e identidade.

## Como ler cada detalhe

| Elemento | Contrato de interpretação |
|---|---|
| Nó `n_…` | Um módulo do inventário, incluindo módulos sem relações internas. Mantém exatamente o ID utilizado no SVG Graphviz. |
| Rótulo | Caminho do arquivo, número de classes e de funções; funções assíncronas também entram no total de funções. Métodos conservam seus nomes qualificados nos metadados. |
| Seta `A --> B` | O arquivo A declara importação interna resolvida para B. Não é uma chamada observada, sequência temporal ou prova de execução. |
| Par único | Várias declarações do mesmo importador para a mesma dependência produzem uma seta; todas as declarações e linhas permanecem no JSON de comentário. |
| Grupo `pkg_…` | Pacote de origem. O título explicita as camadas encontradas naquele pacote; não implica isolamento entre processos. |
| Cor `layer…` | Conveniência visual para camadas, com paleta reutilizada; o nome escrito no grupo e na legenda é a identificação inequívoca. |
| `module-metadata` | Comentário JSON com dados do módulo: caminho, nome, camada, parser, hash, todos os símbolos e seus intervalos de linha. |
| `edge-metadata` | Comentário JSON com as declarações AST de cada par, seus arquivos e linhas. |
| Nós `leg_…` | Exemplos e explicações da legenda, excluídos das contagens da arquitetura. A seta de exemplo também é excluída. |
| Hash de fonte | Identifica os bytes do arquivo no retrato; não atesta correção do programa. |

Os símbolos estão integralmente preservados em comentários estruturados,
sem criar milhares de nós extras que alterariam a granularidade do SVG
original. O [manifesto de correspondência](mermaid-correspondence.json)
conserva a origem declarada, os IDs, os hashes dos módulos, todas as declarações por
par e o hash da fonte Mermaid. Os testes comparam os conjuntos do JSON,
do Mermaid e do SVG Graphviz, incluindo os módulos isolados.




## Escopo e limites

O grafo é Python de produção classificada. Testes, documentação, terceiros,
história e superfícies lexicais continuam em categorias próprias. O AST não
prova que imports sejam executáveis nem cobre toda reflexão/MCP em runtime.
Os 22 [fluxos completos no README](../../README.md#fluxogramas-operacionais-completos)
explicam caminhos e gates, sem promover desenho a evidência de execução.

O grafo integral ultrapassa os limites padrão de 500 arestas e 50.000
caracteres do renderer. A configuração do GitHub não é controlada pelo
documento; não se promete renderização integral ali. Nenhum nó ou par foi
removido para caber. Use o SVG e a [página offline](../architecture_map.html).

## Reprodução e edição

```bash
.venv/bin/python scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json

npx --yes --package @mermaid-js/mermaid-cli@12.2.0 mmdc \
  -c docs/architecture/mermaid-render-config.json \
  -i docs/architecture/dependencies.mmd \
  -o docs/architecture/dependencies-mermaid.svg \
  --size 1800 --no-font-embed

.venv/bin/python scripts/sync_readme_flowcharts.py --refresh-sources
.venv/bin/python scripts/render_architecture_page.py
.venv/bin/python scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json --check
.venv/bin/python scripts/sync_readme_flowcharts.py --check
```

Para todos os fluxos, repita o comando `mmdc` para cada entrada de `flows.json`,
com `-i` para sua fonte `.mmd` e `-o` para o `.svg` de mesmo nome. A primeira
execução de `npx` pode baixar dependências. Para reprodução sem rede, invoque
o renderer já instalado. Um Chromium próprio pode ser indicado por `-p`
com configuração local fora dos artefatos públicos. A revisão usou browser
headless em sequência, reutilizando o processo entre diagramas.

A configuração do host amplia o limite para 5.000 arestas e 10 milhões de
caracteres, com `securityLevel: strict` e `htmlLabels: false`. Não afrouxar
esses controles por diretivas do diagrama. Fonte e manifesto são determinísticos
para o mesmo inventário; layout depende do renderer, engine, fontes e browser.

Edite fontes `flows/*.mmd` e o catálogo para alterar fluxos; atualize o inventário
para alterar o grafo. O sincronizador confere hash, linha e símbolo das fontes
ancoradas, e preserva os bytes do README fora dos marcadores. O modo de extração
e a ref-base devem ser os mesmos do [guia de reprodução](../ARQUITETURA_COMPLETA_CORE_R916.md#reprodução).

## Camadas da coleta

| Camada | Módulos | Símbolos AST |
|---|---:|---:|
| `agentes` | 10 | 80 |
| `diagnostico` | 31 | 477 |
| `engenharia_reversa` | 10 | 69 |
| `evolucao` | 10 | 84 |
| `ferramentas` | 66 | 439 |
| `governanca` | 26 | 304 |
| `infraestrutura` | 6 | 5 |
| `integracoes` | 130 | 1516 |
| `interfaces` | 10 | 126 |
| `memoria_e_evidencias` | 44 | 234 |
| `modulos_adicionais` | 122 | 1092 |
| `orquestracao` | 39 | 476 |
| `pesquisa_e_rag` | 124 | 1201 |
| `plugins` | 5 | 15 |
| `protocolos` | 9 | 8 |
| `publicacao` | 3 | 32 |
| `raciocinio` | 16 | 152 |
| `skills` | 46 | 469 |

> A tabela detalhada preserva o recorte R916. O total acima foi atualizado
> pelo inventário vigente (711 módulos, 1014 pares, 1153 declarações e 6843
> símbolos); a soma das linhas pode não coincidir com o total atual.

## Pacotes da coleta

| Pacote | Camadas | Módulos | Símbolos AST |
|---|---|---:|---:|
| `.opencode` | interfaces | 2 | 44 |
| `academic` | pesquisa_e_rag | 40 | 257 |
| `agent_runners` | agentes | 3 | 44 |
| `agentic_science_v2` | pesquisa_e_rag | 11 | 296 |
| `agents` | agentes | 7 | 36 |
| `economy` | governanca | 2 | 30 |
| `evaluation` | modulos_adicionais | 2 | 7 |
| `evolution` | evolucao | 10 | 84 |
| `gametheory` | governanca | 4 | 94 |
| `governanca` | governanca | 6 | 5 |
| `hermes_bridge` | modulos_adicionais | 7 | 18 |
| `hooks` | modulos_adicionais | 4 | 16 |
| `infra_dados` | infraestrutura | 6 | 5 |
| `integrations` | integracoes | 130 | 1516 |
| `landscape` | modulos_adicionais | 2 | 10 |
| `legal` | modulos_adicionais | 13 | 158 |
| `marceloclaro` | orquestracao | 30 | 386 |
| `mci` | memoria_e_evidencias | 44 | 234 |
| `mirofish` | modulos_adicionais | 11 | 104 |
| `model_lab` | modulos_adicionais | 4 | 12 |
| `nano_orchestration` | orquestracao | 9 | 90 |
| `packages` | modulos_adicionais | 10 | 0 |
| `pdf2latex` | modulos_adicionais | 21 | 142 |
| `plugins` | plugins | 5 | 15 |
| `protocolos` | protocolos | 9 | 8 |
| `publishing` | publicacao | 3 | 32 |
| `rag` | pesquisa_e_rag | 7 | 134 |
| `reasoning` | raciocinio | 16 | 152 |
| `research` | pesquisa_e_rag | 47 | 391 |
| `research_factory` | pesquisa_e_rag | 10 | 83 |
| `reversa_feynman` | engenharia_reversa | 6 | 38 |
| `reversa_universal` | engenharia_reversa | 4 | 31 |
| `sandbox` | modulos_adicionais | 2 | 13 |
| `scanners` | diagnostico | 31 | 477 |
| `scientific_lab` | pesquisa_e_rag | 9 | 40 |
| `scripts` | ferramentas | 66 | 439 |
| `sdd` | governanca | 5 | 105 |
| `skills` | skills | 46 | 469 |
| `synthetic_university` | modulos_adicionais | 29 | 435 |
| `tools` | modulos_adicionais | 1 | 1 |
| `transformer` | modulos_adicionais | 8 | 107 |
| `translation` | modulos_adicionais | 5 | 57 |
| `trust` | governanca | 9 | 70 |
| `webapp` | interfaces | 8 | 82 |
| `workbench` | modulos_adicionais | 3 | 12 |

## Verificação e história

A [verificação R916](../verification-documentation-r916.json) registra testes,
renders, links e inspeção visual. Os recibos R879/R881 permanecem históricos;
não certificam os bytes atuais, a produção científica ou ausência de bugs.
