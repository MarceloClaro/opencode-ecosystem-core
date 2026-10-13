---
spec_id: SPEC-935-R879
title: Mapas completos da arquitetura e fluxos do Core com proveniência estática
component: scripts.build_architecture_maps
status: implemented
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    snapshot:
    - tests/test_r879_architecture_maps.py::test_snapshot_is_deterministic_and_ignores_worktree
    - tests/test_r879_architecture_maps.py::test_git_ref_rejection_is_explicit
    dependencias:
    - tests/test_r879_architecture_maps.py::test_absolute_relative_imports_symbols_and_isolated_modules
    - tests/test_r879_architecture_maps.py::test_mixed_import_keeps_external_and_missing_module_explicit
    seguranca:
    - tests/test_r879_architecture_maps.py::test_configuration_allowlist_never_exports_values
    - tests/test_r879_architecture_maps.py::test_configuration_wrong_shapes_do_not_promote_values_to_names
    - tests/test_r879_architecture_maps.py::test_symlink_target_never_read_or_parsed
    - tests/test_r879_architecture_page.py::test_dados_json_nao_encerram_script_inerte
    - tests/test_r879_architecture_page.py::test_svg_ativo_ou_recurso_externo_e_recusado
    mapas:
    - tests/test_r879_architecture_maps.py::test_dot_labels_escaped_renderable_and_outputs_reproducible
    - tests/test_r879_architecture_maps.py::test_cli_check_detects_tampering_without_rewriting
    - tests/test_r879_architecture_page.py::test_pagina_local_tem_navegacao_e_nao_carrega_cdns
    - tests/test_r879_architecture_page.py::test_rotulo_fluxo_e_escapado_sem_perder_texto
    fluxos:
    - tests/test_r879_architecture_contract.py::test_fluxos_correspondem_a_ancoras_reais_do_snapshot
    - tests/test_r879_architecture_contract.py::test_html_embute_os_mesmos_catalogos_sem_dados_antigos
    - tests/test_r879_architecture_contract.py::test_svg_completo_nao_omite_modulos_ou_pares_internos
    limites:
    - tests/test_r879_architecture_maps.py::test_classification_excludes_snapshots_tests_and_domain_from_production
    - tests/test_r879_architecture_maps.py::test_non_python_surfaces_label_the_parser_and_symbols
    - tests/test_r879_architecture_maps.py::test_domain_generators_and_external_plugin_packages_have_explicit_categories
---

# R879 — Arquitetura completa e fluxogramas atuais

## Objetivo e escopo

Documentar o snapshot Git do Core, incluindo as implementações até R869, por
meio de um inventário reproduzível, mapa geral, dependências internas por módulo
e fluxos operacionais detalhados. A página `docs/architecture_map.html` deve
funcionar localmente, sem CDN, telemetria ou importação de código do inventário.
Os mapas R433–R438 ficam explicitamente históricos e apontam para a edição atual.

O inventário distingue fonte de produção, teste, exemplo, template, snapshot
histórico, artefato de domínio e documentação. Inspeciona somente arquivos
versionados de um ref Git explícito; mudanças concorrentes e runtime privado
ficam fora do snapshot. Uma aresta AST significa importação declarada, não
execução comprovada; integrações por CLI/MCP e relações de controle são
documentadas separadamente com referências a arquivos e símbolos existentes.

## Critérios de Aceitação Executáveis

- `snapshot` — extração Git determinística, sem leitura de arquivos privados ou
  execução dos módulos; mudanças não commitadas não alteram o inventário.
- `dependencias` — parser AST resolve imports absolutos e relativos internos,
  inclui módulos sem arestas e registra erros e imports não resolvidos; não
  apresenta grafo estático como rastreamento dinâmico nem taxa de qualidade.
- `seguranca` — textos, labels e dados são escapados corretamente; referências
  de arquivo são verificáveis; configuração não expõe valores de credenciais.
- `mapas` — arquivos DOT/SVG e Mermaid têm sintaxe validada; visão detalhada e
  índice permitem localizar todos os módulos incluídos, com hashes e símbolos.
- `fluxos` — primário compartilhado, Blackboard/MetaBus, texto spec-first,
  workflow com checkpoints, gates RED/GREEN, trust, REA direto e por modelo,
  isolamento/cancelamento, diagnóstico, memória/grafo, raciocínio restrito,
  ciência/RAG, federação e publicação possuem fluxos referenciados.
- `limites` — histórico, configuração, inferência, análise aceita, corpus de
  autodescoberta, skips e validação externa aparecem como estados distintos.

## Validação e entrega

Testes de parser e snapshot com fixtures externas pequenas; renderização real
dos diagramas; inspeção visual da página e controles. Registrar ciclo R879 com
escopo local, sem preencher retroativamente histórico RED. Publicar o commit
anterior e o commit dos mapas na branch autorizada, preservando outros trabalhos.

A validação semântica das 78 âncoras e os 13 renders Mermaid são artefatos
complementares executados, separados dos testes unitários do contrato. A página
foi inspecionada em navegador local; isso não comprova execução dos módulos.
