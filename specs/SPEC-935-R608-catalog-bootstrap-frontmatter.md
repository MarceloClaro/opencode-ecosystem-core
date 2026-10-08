# SPEC-935-R608: Bootstrap do catálogo tolerante a frontmatter com cabeçalho
#                + reparo das descrições dos cards (R608-R609)

## Objetivo
Corrigir o auto-registro de agentes do catálogo (`mci/agent_registry_bootstrap.py`)
para que cards que abrem com comentário HTML ou título (`#`) antes do frontmatter
YAML não sejam descartados pelo `parse_agent_catalog_md`, que exigia
`content.startswith("---")` rígido. E reparar os cards com frontmatter inválido
ou sem chave `description`, para que TODO card tenha nome, descrição e
capacidades não vazias — restabelecendo a paridade entre o catálogo (212 cards)
e o quadro do Blackboard em runtime.

## Motivação
Medição de auditoria (ciclo do manual, 2026-09-29): `agents/catalog/*.md` tem
212 cards; apenas 172 começam com `---`; 39 têm head e fence na posição 6–8
(ex.: `mira-*.md`, cards das famílias literary/cloud). Com a regra antiga
(`content.startswith("---")`), o quadro registrava **162 cards** (172 − 10 com
frontmatter YAML malformado). Auditado também: 6 cards sem chave `description`,
10 cards com frontmatter YAML quebrado (4 medico-* dupla-codificados, 4
reversa-* idem, `contextscout` com alias `*: allow`, `landscape-curator` com
`: ` em plain scalar) e `haystack-rag` sem par de fences `---`.
**Estado pós-R608: 212 cards, todos com frontmatter YAML válido e descrição
não vazia (201 espectados por `_locate_frontmatter` + 11 reparados).**

## Critérios de aceitação (gate SDD/TDD)
- [B1] `parse_agent_catalog_md` retorna metadados para card com comentário HTML e
      título antes do frontmatter (fence na posição > 0).
- [B2] Retorno idêntico ao comportamento anterior para cards cujo frontmatter
      começa na primeira linha (`---` na posição 0) — sem regressão de campos
      (`agent_id`, `name`, `description`, `capabilities`).
- [B3] Cards antes descartados (haystack-rag sem fence; medico/reversa com YAML
      quebrado; contextscout/landscape-curator com scalar inválido) agora
      produzem metadados válidos.
- [B4] `load_catalog_agents()` sobre o catálogo real carrega **212 cards**
      (100% do catálogo), cada um com `name`, `description` e `capabilities`
      não vazios — sem rede e sem tocar estado global.
- [B5] `register_catalog_agents` registra 212 no blackboard (idempotente);
      famílias com cabeçalho (mira, cloud, literary) e haystack-rag presentes.
- [B6] Tests RED herméticos (tmp_path) + verificação sobre o catálogo real.

## Arquitetura
```
mci/agent_registry_bootstrap.py → _locate_frontmatter() + parse_agent_catalog_md
tests/test_r608_catalog_bootstrap_frontmatter.py
```

## Escopo / anti-overclaim
- Não altera o esquema de metadados nem o contrato do `agent_id` (slug estável).
- Cards genuinamente sem frontmatter `---` ou com YAML inválido continuam
  pulados (documentados, ids fixos), nunca inventa-se metadado.
- A reparação dos 11 cards malformados (catálogo) é ciclo futuro declarado e
  NÃO é prometida nesta spec.
- Teste é hermético (tmp_path/caminho real do repo, sem rede).

## Registro
- Autores: auditoria técnica (ws-academic-pipeline) + revisão do orquestrador
- Data: 2026-09-29
- Ciclo: R608 (registro legado honesto, `audited=False` — sem auditor externo)