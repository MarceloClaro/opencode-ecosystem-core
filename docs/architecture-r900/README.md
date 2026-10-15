# Mapa estrutural completo do Core

Este conjunto descreve o snapshot Git `f930e196d5990a22651cd650fb30da44dd69bd2e`, que contém as alterações R894–R897 e tem como commit pai a revisão R900. O mapa é produzido a partir de blobs Git versionados; mudanças locais sem commit, artefatos ignorados e estado de execução não entram no inventário.

## Arquivos

- `overview.svg`: visão visual resumida por subsistema.
- `dependencies.svg` e `dependencies.dot`: dependências Python declaradas no snapshot.
- `architecture-complete.mmd`: inventário Mermaid integral, com módulos, pares importador/dependência, símbolos, pacotes e camadas.
- `architecture-inventory.json`: dados estruturados, hashes e classificações de arquivos.
- `mermaid-correspondence.json`: relação entre as declarações do inventário e as referências Mermaid exportadas.

O retrato contém 10.033 arquivos versionados, 691 módulos Python de produção, 1.083 arestas de importação declaradas, 965 pares únicos entre módulos, 6.670 símbolos, 45 pacotes e 18 camadas. Houve zero erros de parse Python no snapshot analisado. A classificação inclui 2.578 snapshots históricos, 2.399 templates e 782 arquivos de vendor; esses grupos não devem ser tratados como código operacional.

## Leitura correta

Uma aresta indica importação declarada no código estático. Ela não demonstra chamada, fluxo de dados em execução, correção, segurança, qualidade científica ou cobertura de testes. A extração lexical das superfícies não Python também possui limites explícitos no inventário. Zero erros de parse significa que a etapa AST analisou os módulos Python selecionados, não que o sistema inteiro esteja livre de bugs.

Os fluxos operacionais legíveis e suas limitações estão no [catálogo de treze fluxogramas do README](../../README.md#fluxogramas-operacionais-completos) e no [guia R894–R897](../ORQUESTRACAO_AGENTES_PLUGINS_CI_R894_R897.md). Esse catálogo representa contratos e relações; recibos separados sustentam apenas as operações realmente executadas.

## Reprodução

Na raiz do repositório, com as dependências de desenvolvimento disponíveis:

```bash
.venv/bin/python scripts/build_architecture_maps.py --ref HEAD --output docs/architecture-r900
.venv/bin/python scripts/build_mermaid_architecture.py \
  --inventory docs/architecture-r900/architecture-inventory.json \
  --output docs/architecture-r900/architecture-complete.mmd \
  --correspondence docs/architecture-r900/mermaid-correspondence.json
```

Para uma comparação sem reescrever os arquivos, acrescente `--check` a cada chamada. O resultado só é reproduzível para o mesmo commit e as mesmas versões das ferramentas de extração e renderização.
