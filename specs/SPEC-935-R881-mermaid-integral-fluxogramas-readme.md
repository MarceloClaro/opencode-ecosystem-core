---
spec_id: SPEC-935-R881
title: Mermaid integral equivalente ao SVG e catálogo completo de fluxos no README
component: scripts.build_mermaid_architecture
status: implemented
test_file: tests/test_r881_mermaid_integral.py
---

# R881 — Arquitetura integral e fluxogramas em Mermaid

## Escopo autorizado

Gerar o mesmo grafo estrutural do SVG `dependencies.svg` em Mermaid: todos os
677 módulos Python e os 935 pares internos do snapshot `6380cfa`, incluindo
módulos isolados, sem reduzir o grafo a um resumo. As 1.051 declarações AST
devem permanecer rastreáveis nos metadados, sem criar arestas de execução.

Incluir no README os 13 fluxogramas de `flows.json`, na ordem do catálogo,
com código Mermaid completo, legenda, fontes e limites. A página local e o
README devem consumir as mesmas fontes; a reprodução não usa LLM ou rede.

## Critérios de aceitação

- Identificadores estáveis e conjuntos de módulos/pares iguais ao JSON e SVG.
- Agrupamento por pacote/camada e legenda explícita: importador → dependência,
  módulos isolados, contagens, símbolos, fontes, categorias excluídas e limites.
- Legenda visual possui IDs próprios, não aumenta contagens da arquitetura.
- Fonte integral `.mmd`, SVG renderizado, manifesto de correspondência e guia
  de edição. Limites de tamanho/arestas do renderer são declarados; nenhuma
  omissão silenciosa é permitida para satisfazer um limite de visualização.
- Todos os fluxos são incluídos integralmente no README, com marcadores que
  permitem regeneração idempotente e check que acusa edição divergente.
- Testes verificam igualdade de conjuntos, escape de labels, preservação de
  conteúdo fora do bloco, origem exata das fontes e detecção de omissões.
- Renderização real Mermaid e revisão independente da correspondência entre
  formatos; os resultados são locais, sem alegar prova de execução do Core.

## Entrega

Registrar ciclo R881 e publicar o commit na branch autorizada. Preservar os
trabalhos concorrentes e os recibos históricos das edições anteriores.

## Evidência local da entrega

- Os testes novos cobrem perdas de nós/arestas/metadados, rotas de escrita,
  travessia de diretórios, symlinks externos, preservação de bytes e fontes
  integrais dos 13 fluxos. Os testes antigos da documentação também são executados.
- Comentários JSON escapam diretivas Mermaid; destinos Mermaid/manifesto
  iguais, inclusive por symlink, são recusados antes de escrever.
- A renderização integral conserva os 677 IDs e os 935 pares do SVG original.
  As contagens excluem nós e aresta da legenda.
- O recibo `docs/architecture/verification-local-r881.json` registra hashes,
  resultados locais, revisão e limites. Não há validação externa nesta entrega.
