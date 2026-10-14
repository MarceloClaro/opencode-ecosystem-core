# Arquitetura integral em Mermaid — R881

A [fonte integral](dependencies.mmd) representa os mesmos **677 módulos Python**
e **935 pares internos** do [SVG Graphviz](dependencies.svg). São **45 pacotes**,
**18 camadas**, **1.051 declarações AST de importação** e **6.432 símbolos**.
O [SVG renderizado pelo Mermaid](dependencies-mermaid.svg) oferece outra
organização visual do mesmo grafo; as coordenadas e o estilo são diferentes.

A referência é o snapshot Git `6380cfa`, conservado no
[inventário](architecture-inventory.json). Esta exportação não atualiza esse
retrato para o HEAD atual. O inventário contém 9.672 arquivos rastreados e
outras superfícies; o grafo de dependências tem escopo Python de produção.
A inclusão de novas funcionalidades requer nova extração e nova conferência,
sem reutilizar as contagens desta fotografia como se fossem atuais.

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
conserva a origem Git, os IDs, os hashes dos módulos, todas as declarações por
par e o hash da fonte Mermaid. Os testes comparam os conjuntos do JSON,
do Mermaid e do SVG Graphviz, incluindo os módulos isolados.

## Escopo e limites

O inventário distingue código de produção, testes, exemplos, documentação,
história, domínio, fontes de terceiros e superfícies lexicais. Este grafo
não transforma essas últimas categorias em dependências Python. Imports
externos e dinâmicos constam no inventário em campos separados; a resolução
estática não cobre todas as relações possíveis em execução. Pacotes presentes
não comprovam instalação de dependências, autenticação, saldo, inferência,
isolamento de rede, aceitação pelo gate ou validação externa.

O desenho completo excede o limite padrão de **500 arestas** do renderer
Mermaid consultado localmente; também excede o limite padrão de 50.000
caracteres ao preservar os metadados. A configuração segura do GitHub não é
controlada pelo documento. Portanto, disponibilizamos a fonte completa e o
SVG renderizado localmente, sem prometer renderização integral no GitHub ou
no Mermaid Live. Nenhum nó ou par foi removido para contornar esses limites.
Os 13 fluxogramas menores estão integralmente no [README](../../README.md#fluxogramas-operacionais-completos).

## Reprodução e edição

Execute a partir da raiz do repositório:

```bash
python3 scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json

python3 scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json --check

python3 scripts/sync_readme_flowcharts.py
python3 scripts/sync_readme_flowcharts.py --check
```

Não edite os blocos gerados manualmente. Edite as fontes em `flows/*.mmd`
e o catálogo `flows.json` para alterar os fluxos. Para o grafo estrutural,
atualize o inventário por nova extração Git/AST e regenere os artefatos.
Os checks comparam os bytes esperados e recusam divergências sem reescrever.
O sincronizador preserva os bytes do README fora dos marcadores.

A renderização requer Node.js e Chromium compatível. A primeira execução do
comando abaixo pode baixar o renderer; a análise dos arquivos não usa LLM.
Para uma reprodução sem rede, use as mesmas dependências previamente instaladas.

```bash
npx --yes --package @mermaid-js/mermaid-cli@12.0.0 mmdc \
  -c docs/architecture/mermaid-render-config.json \
  -i docs/architecture/dependencies.mmd \
  -o docs/architecture/dependencies-mermaid.svg \
  --size 1800 --no-font-embed
```

A [configuração do host](mermaid-render-config.json) amplia os limites para
5.000 arestas e 10 milhões de caracteres, com `securityLevel: strict` e
rótulos SVG sem HTML. Esses parâmetros pertencem ao host confiável;
diretivas na fonte do diagrama não substituem limites seguros. A máquina
usada nesta revisão forneceu seu Chromium pelo argumento `-p` do CLI,
sem registrar seu caminho particular no artefato público.
O SVG é extenso: abra-o em uma aba própria e amplie a área de interesse.
Para navegação com busca e zoom por módulo, use o [mapa offline](../architecture_map.html),
que conserva a versão Graphviz equivalente e os 13 fluxogramas.
A fonte e o manifesto são determinísticos para o mesmo inventário;
o layout SVG depende das versões efetivas do renderer, engine e fontes.

## Camadas do retrato

| Camada | Módulos | Símbolos AST |
|---|---:|---:|
| `agentes` | 9 | 60 |
| `diagnostico` | 31 | 477 |
| `engenharia_reversa` | 10 | 69 |
| `evolucao` | 10 | 77 |
| `ferramentas` | 59 | 370 |
| `governanca` | 26 | 301 |
| `infraestrutura` | 6 | 5 |
| `integracoes` | 121 | 1360 |
| `interfaces` | 10 | 126 |
| `memoria_e_evidencias` | 43 | 226 |
| `modulos_adicionais` | 122 | 1092 |
| `orquestracao` | 37 | 459 |
| `pesquisa_e_rag` | 114 | 1141 |
| `plugins` | 5 | 15 |
| `protocolos` | 9 | 8 |
| `publicacao` | 3 | 32 |
| `raciocinio` | 16 | 146 |
| `skills` | 46 | 468 |

## Pacotes do retrato

A classificação segue o inventário, sem inferir capacidades pelo nome.

| Pacote | Camadas | Módulos | Símbolos AST |
|---|---|---:|---:|
| `.opencode` | interfaces | 2 | 44 |
| `academic` | pesquisa_e_rag | 31 | 214 |
| `agent_runners` | agentes | 3 | 44 |
| `agentic_science_v2` | pesquisa_e_rag | 11 | 296 |
| `agents` | agentes | 6 | 16 |
| `economy` | governanca | 2 | 30 |
| `evaluation` | modulos_adicionais | 2 | 7 |
| `evolution` | evolucao | 10 | 77 |
| `gametheory` | governanca | 4 | 94 |
| `governanca` | governanca | 6 | 5 |
| `hermes_bridge` | modulos_adicionais | 7 | 18 |
| `hooks` | modulos_adicionais | 4 | 16 |
| `infra_dados` | infraestrutura | 6 | 5 |
| `integrations` | integracoes | 121 | 1360 |
| `landscape` | modulos_adicionais | 2 | 10 |
| `legal` | modulos_adicionais | 13 | 158 |
| `marceloclaro` | orquestracao | 28 | 369 |
| `mci` | memoria_e_evidencias | 43 | 226 |
| `mirofish` | modulos_adicionais | 11 | 104 |
| `model_lab` | modulos_adicionais | 4 | 12 |
| `nano_orchestration` | orquestracao | 9 | 90 |
| `packages` | modulos_adicionais | 10 | 0 |
| `pdf2latex` | modulos_adicionais | 21 | 142 |
| `plugins` | plugins | 5 | 15 |
| `protocolos` | protocolos | 9 | 8 |
| `publishing` | publicacao | 3 | 32 |
| `rag` | pesquisa_e_rag | 7 | 134 |
| `reasoning` | raciocinio | 16 | 146 |
| `research` | pesquisa_e_rag | 46 | 374 |
| `research_factory` | pesquisa_e_rag | 10 | 83 |
| `reversa_feynman` | engenharia_reversa | 6 | 38 |
| `reversa_universal` | engenharia_reversa | 4 | 31 |
| `sandbox` | modulos_adicionais | 2 | 13 |
| `scanners` | diagnostico | 31 | 477 |
| `scientific_lab` | pesquisa_e_rag | 9 | 40 |
| `scripts` | ferramentas | 59 | 370 |
| `sdd` | governanca | 5 | 102 |
| `skills` | skills | 46 | 468 |
| `synthetic_university` | modulos_adicionais | 29 | 435 |
| `tools` | modulos_adicionais | 1 | 1 |
| `transformer` | modulos_adicionais | 8 | 107 |
| `translation` | modulos_adicionais | 5 | 57 |
| `trust` | governanca | 9 | 70 |
| `webapp` | interfaces | 8 | 82 |
| `workbench` | modulos_adicionais | 3 | 12 |

## Verificações locais

A [evidência R881](verification-local-r881.json) registra os testes e a renderização
desta exportação. Os recibos R879/R880 permanecem históricos. Nenhum desses
resultados constitui validação externa ou execução integral do ecossistema.
