# SPEC-985 — Pesquisa de inovação inspirada no Innovation Map

## Objetivo
Criar uma pesquisa de inovação inspirada no `https://innovationmap.at/?pg=home` (Innovation Map, WKÖ + Envisioning), adaptada ao domínio brasileiro/organizacional, com estrutura de categorias, maturidade (TRL/SRL) e fichas de tecnologia, mais um artefato navegável.

## Escopo
- Extrair estrutura metodológica e categorias do Innovation Map.
- Curar 28 tecnologias representativas em 5 clusters.
- Produzir JSON estruturado, relatório Markdown e interface HTML (radar + filtros).
- Declarar limitações (amostra representativa, não base completa 100+).

## Critérios de aceitação
- JSON válido com 28 entradas, campos id, titulo, cluster, trl, descricao_curta, casos_de_uso, sdgs.
- HTML funcional (abre localmente) com radar e filtros.
- Relatório PT-BR com referência à fonte e anti-overclaim explícito.
- Teste de validação JSON e carga de arquivo.

## Anti-overclaim
Não afirma cobertura completa do radar original nem validação externa independente da completude.
