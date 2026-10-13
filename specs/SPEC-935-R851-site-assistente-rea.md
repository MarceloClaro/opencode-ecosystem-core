---
spec_id: SPEC-935-R851
title: Site local de configuração e exemplos do assistente REA
component: webapp.rea_assistant_site
status: implemented
test_file: tests/test_r851_rea_assistant_site.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    acesso_local:
      - tests/test_r851_rea_assistant_site.py::test_loopback_e_recursos_publicos
      - tests/test_r851_rea_assistant_site.py::test_host_externo_duplicado_ou_ausente_e_recusado
      - tests/test_r851_rea_assistant_site.py::test_origin_externo_e_recusado
    allowlist:
      - tests/test_r851_rea_assistant_site.py::test_caminhos_do_repositorio_nao_sao_expostos
      - tests/test_r851_rea_assistant_site.py::test_traversal_e_caminho_nao_canonico_sao_recusados
      - tests/test_r851_rea_assistant_site.py::test_metodos_que_podem_enviar_dados_sao_recusados
    navegador_local:
      - tests/test_r851_rea_assistant_site.py::test_politica_do_navegador_bloqueia_conexoes_e_enquadramento
      - tests/test_r851_rea_assistant_site.py::test_pagina_tem_recursos_locais_e_comandos_associados
    copia_acessivel:
      - tests/test_r851_rea_assistant_site.py::test_copia_comando_e_informa_sucesso_no_cliente
      - tests/test_r851_rea_assistant_site.py::test_falha_de_copia_informa_como_prosseguir
      - tests/test_r851_rea_assistant_site.py::test_copia_alternativa_sem_clipboard_api
---

# R851 — Instruções locais do assistente

## Critérios de Aceitação Executáveis

- `acesso_local` — servidor vinculado exclusivamente a 127.0.0.1, com porta
  configurável; somente Host e Origin locais vinculados à mesma porta são aceitos.
- `allowlist` — apenas GET nos cinco recursos públicos; nenhum caminho de
  repositório, traversal, upload ou método de análise é servido.
- `navegador_local` — página responsiva em pt-BR, recursos locais, CSP sem
  conexões, formulários ou enquadramento; os botões apontam para comandos legíveis.
- `copia_acessivel` — cópia altera feedback vivo no navegador, comunica falha e
  tem alternativa local quando Clipboard API estiver indisponível.

## Produto e limites

Site simples e responsivo em português, servido somente em 127.0.0.1:8767,
sem CDN, telemetria, recursos externos, uploads ou execução de análises por HTTP.
Explica setup, perfil de agente local, CLI inspect/explain, MCP stdio, exemplos
JavaScript/Electron, ELF/Ghidra, .NET e HTML, evidências e limites da reconstrução.
Inclui o fluxo fornecido pelo usuário, com provedores opcionais identificados.

Servidor permite somente arquivos explícitos do site, recusa Host/Origin externo
e traversal. Comandos podem ser copiados, sem executar nada no navegador.
Conteúdo distingue instalação, prontidão e inspeção realmente executada; não
promete desempenho universal nem proteção contra cliente que envie dados à nuvem.

Contrato CLI compartilhado R850: `rea setup`, `rea inspect CAMINHO --kind auto
--format text`, `rea explain RECIBO`, `rea site --port 8767`; servidor MCP
`python -m integrations.rea_assistant_mcp`. Testes reais de HTTP, porta loopback,
paths recusados e recursos presentes; inspeção visual por browser local.

API Python pública: `serve_instructions(*, port=8767)`; `make_server(port=0)`
retorna servidor vinculado a loopback e permite ciclo de vida controlado. Recursos:
`/`, `/index.html`, `/styles.css`, `/script.js`, `/favicon.svg`. Não há análise
por HTTP. A interface não executa o conteúdo de aplicativos nem envia dados.

## Verificação

Doctor estrutural antes das edições. Testes escritos antes da implementação;
bootstrap de API ausente registrado separadamente do RED funcional. O RED/GREEN
é executado pelo primário via `tdd-history`, com o mesmo contrato e os mesmos
testes, e os recibos públicos são conservados em `outputs/core-r851`.
Os testes fazem requisições HTTP reais e executam o script entregue em Node com
um adaptador mínimo de DOM/Clipboard API; esse adaptador não é uma prova visual
de navegador. A inspeção visual final será realizada separadamente.
