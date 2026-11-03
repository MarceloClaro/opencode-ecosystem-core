---
spec_id: SPEC-935-R1022
title: Catálogo e planejador de conteúdo offline
component: integrations.offline_content
status: implemented
test_file: tests/test_r1022_offline_content.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1022-1:
      - "tests/test_r1022_offline_content.py::test_load_valid_catalog"
      - "tests/test_r1022_offline_content.py::test_duplicate_category_id_fails"
      - "tests/test_r1022_offline_content.py::test_duplicate_tier_id_fails"
      - "tests/test_r1022_offline_content.py::test_conflicting_duplicate_resource_fails"
      - "tests/test_r1022_offline_content.py::test_identical_duplicate_resource_is_deduped"
      - "tests/test_r1022_offline_content.py::test_invalid_resource_fields_fail"
    R1022-2:
      - "tests/test_r1022_offline_content.py::test_plan_resolves_includes_and_totals"
      - "tests/test_r1022_offline_content.py::test_plan_cycle_is_rejected"
      - "tests/test_r1022_offline_content.py::test_plan_missing_tier_is_rejected"
    R1022-3:
      - "tests/test_r1022_offline_content.py::test_plan_marks_estimated_size_and_missing_license"
      - "tests/test_r1022_offline_content.py::test_plan_is_deterministic_and_does_not_mutate_catalog"
    R1022-4:
      - "tests/test_r1022_offline_content.py::test_render_plan_contains_totals_and_read_only_notice"
      - "tests/test_r1022_offline_content.py::test_cli_plan_json"
      - "tests/test_r1022_offline_content.py::test_cli_error_is_structured"
    R1022-5:
      - "tests/test_r1022_offline_content.py::test_load_rejects_symlink"
      - "tests/test_r1022_offline_content.py::test_load_rejects_oversized_catalog"
---

# SPEC-935-R1022 — Catálogo e planejador de conteúdo offline

**Estado:** implementado e testado localmente; nenhum download foi executado.
**Inspiração:** o modelo de coleções por categoria/tier do Project NOMAD
(Apache-2.0), sem copiar seus dados ou código.

## Objetivo

Dar ao Core uma forma auditável de descrever e planejar pacotes de conteúdo
offline — Wikipedia/ZIM, livros, cursos, mapas, datasets — com categoria, tier,
versão, URL HTTPS, tamanho, licença e hash opcional. O planejador calcula o
espaço necessário e resolve tiers inclusos, sem baixar, instalar ou executar.

## Escopo

- `integrations/offline_content.py`: carregamento, validação, planejamento,
  renderização e CLI.
- `tests/test_r1022_offline_content.py`: contrato determinístico, sem rede.
- Formato JSON próprio:

```json
{
  "schema_version": "1.0",
  "categories": [
    {
      "id": "saude",
      "title": "Saúde",
      "description": "Referências",
      "tiers": [
        {
          "id": "saude-essencial",
          "title": "Essencial",
          "includes_tiers": [],
          "resources": [
            {
              "id": "primeiros-socorros",
              "title": "Primeiros socorros",
              "version": "2026-01",
              "url": "https://example.org/arquivo.zim",
              "size_mb": 10,
              "kind": "zim",
              "license": "CC-BY-4.0",
              "sha256": "…"
            }
          ]
        }
      ]
    }
  ]
}
```

## Contrato

1. `load_catalog` aceita somente arquivo regular local, não symlink, até 8 MiB.
2. Categoria/tier usam slugs; recurso usa ID com letras, números, ponto,
   sublinhado e hífen.
3. URL precisa ser `https`, com host e sem credenciais embutidas.
4. Recurso exige `bytes` inteiro positivo ou `size_mb` numérico positivo.
   `size_mb` é convertido para bytes e marcado como estimado.
5. `sha256`, quando presente, precisa ter 64 hexadecimais.
6. `kind` pertence ao conjunto declarado; padrão `other`.
7. IDs de recurso repetidos são deduplicados somente se URL, bytes e hash forem
   idênticos; divergência gera `resource_conflict`.
8. `plan` resolve `includes_tiers` dentro da mesma categoria, detecta ciclo,
   deduplica recursos e calcula totais exatos/estimados e licenças.
9. `render_plan` e a CLI deixam explícito que nada foi baixado, instalado ou
   executado.
10. Nenhuma função acessa a rede, baixa URL, instala pacote ou executa conteúdo.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1022-1` — Validação: catálogo válido, duplicatas, conflito de recurso,
  URL HTTP, tamanho inválido, SHA-256 inválido e `kind` inválido.
- `R1022-2` — Planejamento: includes resolvidos, ciclo recusado e tier ausente
  recusado.
- `R1022-3` — Totais: tamanho exato/estimado, licença ausente e determinismo sem
  mutar o catálogo.
- `R1022-4` — Apresentação: renderização legível e CLI JSON com erro estruturado.
- `R1022-5` — Segurança local: symlink e arquivo acima do limite recusados.

## Evidência observada

- Suíte `tests/test_r1022_offline_content.py`: **20 passed**.
- RED controlado em worktree isolada: o único teste reprovado foi o contrato de
  formatação (`human_bytes` deliberadamente incorreto), com falha de asserção;
  GREEN com **20/20**; `SpecVerifier` **5/5** no gate
  `software_delivery_gate`, com par RED/GREEN válido.
- Nenhuma URL foi acessada; o teste usa apenas fixtures locais.

## Limites

O catálogo não verifica se a URL existe, se o conteúdo é adequado, se a licença
declarada é suficiente ou se o hash corresponde ao arquivo remoto. Tamanhos em
`size_mb` são aproximados. O planejador não substitui revisão de licença,
direitos autorais, segurança de download ou decisão humana. A integração com
MCP/CLI principal e a execução de downloads ficam fora desta entrega.
