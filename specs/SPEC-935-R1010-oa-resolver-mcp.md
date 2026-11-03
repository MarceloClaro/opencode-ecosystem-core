---
spec_id: SPEC-935-R1010
title: MCP oa-resolver — resolução, download auditado e RAG sob confinamento
component: .opencode/mcp/oa_resolver_server.py
status: implemented
test_file: tests/test_r1010_oa_resolver_mcp.py
---

# SPEC-935-R1010 — MCP `oa-resolver`

**Status:** Implementado (RED → GREEN + prova de protocolo)
**Data:** 2026-11-01
**Agente:** marceloclaro

## 1. Contexto

O Core já tinha resolução legal (`research/oa_resolver.py`) e pipeline de
auditoria (`research/pdf_pipeline.py`), mas sem superfície MCP. Federar um
servidor de terceiros exigiria confiar código externo com privilégio de host.
A opção escolhida foi expor o pipeline próprio, auditado e fail-closed.

## 2. Ferramentas

| Ferramenta | Efeito |
|---|---|
| `oa_resolve` | resolve DOI em candidatos legais; não baixa |
| `oa_download` | dry-run por padrão; com `confirm=true` baixa e cria o pacote |
| `oa_query_rag` | consulta BM25 na pasta, com página e citação ABNT |
| `oa_audit_status` | inventário, hash do PDF e manifesto RAG |
| `oa_list_folders` | lista pastas da base |

## 3. Requisitos

- R1. Nenhuma fonte bloqueada é consultada ou baixada (`source_policy`).
- R2. `oa_download` sem `confirm=true` não cria pasta nem baixa bytes.
- R3. Toda pasta é confinada a `OA_AUDIT_BASE` (padrão `<repo>/auditoria_fichamentos`);
  `..` e caminho absoluto externo são recusados.
- R4. Sem tradutor/argumentador, `fichamento.md` marca `Pendente` e o recibo
  informa `translations_ok=0` e `argumentations_ok=0`.
- R5. Erros retornam `isError=true` com motivo, nunca silêncio.
- R6. Nenhuma credencial é exigida; `mailto` do OpenAlex é opcional.
- R7. O servidor é registrado pelo gerador `integrations/opencode_cli.py` e em
  `opencode.json`.

## 4. Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| CA1 | Catálogo com cinco ferramentas | `test_catalogo_de_ferramentas` |
| CA2 | Fonte bloqueada recusada | `test_resolve_recusa_fonte_bloqueada` |
| CA3 | Dry-run não baixa | `test_download_exige_confirmacao` |
| CA4 | Download confirmado cria o pacote completo | `test_download_confirmado_cria_pacote` |
| CA5 | RAG retorna a página correta com ABNT | `test_query_rag_retorna_pagina` |
| CA6 | Confinamento recusa traversal | `test_confinamento_rejeita_traversal` |
| CA7 | Status e listagem coerentes | `test_status_e_listagem` |
| CA8 | Handshake MCP real e `tools/list` | prova de protocolo (stdio) |
| CA9 | `oa_resolve` real retorna candidato com licença | prova de protocolo (stdio) |

## 5. Prova de protocolo (2026-11-01)

`initialize` → `serverInfo: {name: oa-resolver, version: 1.28.1}`;
`tools/list` → 5 ferramentas; `oa_resolve("10.1371/journal.pone.0024352")` →
`status=ok`, 1 candidato, licença `cc-by`. No host, `oa_download` sem confirmação
retornou `confirmation_required` sem criar pasta.

## 6. Limites

- Tradução e argumentação exigem tradutor/argumentador externo; o MCP não
  executa LLM por padrão.
- O RAG é lexical; não há embeddings.
- O download depende de o provedor manter o PDF acessível; falha vira erro
  explícito, não resultado parcial silencioso.
