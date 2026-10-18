---
spec_id: SPEC-935-R915
title: Atualização local do conector NotebookLM para 0.15.6
version: 1.0.0
status: implemented
---

# SPEC-935-R915 — atualização do NotebookLM

## Escopo

Atualização explicitamente autorizada pelo operador após o aviso 0.11.6 →
0.15.6. Usar a distribuição publicada no PyPI no ambiente `.venv` do Core,
mantendo FastMCP 3.2.3 e MCP 1.28.1. A distribuição publicada substitui o
runtime antigo; não reinstalar por cima o checkout histórico f212ed9a.
Preservar esse checkout e os recibos históricos como evidência da versão antiga.

O MarceloClaro permanece como entrada. Não alterar provedores de modelos,
senhas, cookies, notebooks, compartilhamento ou configuração de outros clientes.
Não atualizar dependências alheias. Salvar pacote e wrappers anteriores para
reversão, sem copiar o armazenamento de autenticação.

## Critérios de aceitação

1. O executável `.venv/bin/nlm` e o processo MCP novo reportam 0.15.6;
   `pip check` não introduz dependências quebradas.
2. Descoberta real dos schemas MCP e da árvore CLI pelo Core, sem executar
   callbacks durante o inventário. Nomes novos continuam bloqueados quando
   não possuem política explícita; disponibilidade não concede permissão.
3. Login existente validado e contagem de notebooks obtida por leitura, sem
   divulgar títulos, conteúdo, credenciais ou identificadores dos notebooks.
4. Regressões de transporte, política, entrada central, pipeline e podcast
   permanecem aprovadas. Falhas novas exigem reprodução RED antes da correção.
   Testes físicos da instalação são separados dos testes com fixtures antigas.
5. Atualizar a pinagem e a documentação; migrar a cópia da skill no Core
   somente quando os bytes existentes correspondem à distribuição anterior,
   preservando quaisquer alterações locais. Registrar versão, hashes e limites.

## Verificação

Reutilizar os testes R548, R549, R672–R676 e sondas de leitura reais pelo
`gemini_notebook_action`. Testes históricos de 49 ferramentas/155 callbacks
referem-se ao checkout retido, não à versão recém-instalada. Não modificar
suas fixtures apenas para aparentar compatibilidade com a nova versão.

Resultado limitado à atualização e às operações executadas. Não equivale a
teste de todas as operações Google, inferência de modelos ou validação externa.
