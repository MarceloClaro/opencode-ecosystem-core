---
spec_id: SPEC-935-R673
title: Catálogo e política de capacidades Gemini Notebook
status: green
validation_scope: local_contract
component: integrations/gemini_notebook_catalog.py
test_file: tests/test_r673_gemini_notebook_catalog.py
---

# SPEC-935-R673 — Catálogo e política de capacidades Gemini Notebook

## Estado

GREEN no escopo do contrato local. Testes RED precederam a implementação; a validação funcional do transporte pertence à R672.

## Problema

O checkout Gemini Notebook 0.11.6, commit `f212ed9a321351aadf7ff7271469d6d4663df7d3`, registra 49 ferramentas MCP e 155 callbacks CLI. A documentação resumida ainda menciona 43 ferramentas. Classificar apenas o nome da ferramenta confunde leitura com mutações condicionais: `research_status(auto_import=true)`, `studio_status(action=rename)`, `label(action=list)` e pipelines são exemplos.

## Contrato

1. O Core conhece os 49 nomes MCP do checkout e rejeita nomes e ações desconhecidos.
2. A classificação pura retorna `read`, `inference`, `write`, `destructive`, `publish`, `download` ou `auth_private`.
3. Toda ramificação de ferramentas consolidadas é classificada; pipelines sem passos conhecidos recebem a classificação conservadora `destructive`.
4. O inventário CLI importa Typer somente quando solicitado e percorre a árvore sem invocar callbacks. Inclui callbacks de grupo e raiz.
5. O validador CLI aceita somente caminhos e parâmetros encontrados no inventário; não executa shell ou callbacks. Rejeita flags desconhecidas, debug e argumentos de credenciais.
6. Leituras de ajuda não viram execução do comando. As entradas interativas e privadas continuam representadas no catálogo com sua limitação explícita.
7. A camada de execução aplica a confirmação aos efeitos; este módulo não inventa aprovação humana e não modifica dados ou autenticação.

## Aceitação

`tests/test_r673_gemini_notebook_catalog.py` deve cobrir o inventário real em processo isolado, os 49 nomes, ramificações com efeitos ocultos, comandos CLI noun-first e verb-first, tipos/flags e contraprovas de injeção e de sucesso parcial.

## Limites de evidência

Inventário e classificação são contratos locais. Não comprovam autenticação, inferência, cota, disponibilidade de recurso Enterprise ou execução científica externa. O transporte deve registrar o resultado real separadamente.

## Evidências

RED inicial: `docs/evidence/R673_RED.xml`; contraprovas de subtipos: `docs/evidence/R673_RED_SUBTYPES.xml`; contraprovas de inicialização: `docs/evidence/R673_RED_BOOT_BEHAVIOR.xml`; GREEN: `docs/evidence/R673_GREEN.xml`. O inventário real em subprocesso contém os 155 callbacks e recebe contraprova que impede qualquer conexão de rede ou leitura de perfil. O prefixo fixo `nlm` é aceito, processos MCP/servidores e outros executáveis são rejeitados no canal CLI, e ajuda de comandos interativos permanece leitura. O catálogo expõe os doze destinos oficiais de skills, incluindo Hermes e OpenCode; descoberta não implica instalação nesses destinos.
