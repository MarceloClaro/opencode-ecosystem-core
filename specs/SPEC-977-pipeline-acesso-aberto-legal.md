# SPEC-977 — Pipeline de Acesso Aberto Legal por DOI (Crossref + OpenAlex + Unpaywall)

```yaml
spec_id: SPEC-977
title: Pipeline de acesso aberto legal por DOI sem Sci-Hub
status: green
component: research/legal_oa_pipeline.py + integrations/legal_oa_stub.py
test_file: tests/test_r977_acesso_aberto_legal.py
validation_scope: local_runtime
```

## Contexto e gap

A orquestração recebeu pedido de automação de downloads por DOI via Sci-Hub (`scihub-mcp`, `scihub-cli`). Esse caminho foi **bloqueado** por risco jurídico: obtenção por via não autorizada pelos detentores de direitos, sem que aprovação interna supra a titularidade.

Levantamento PyPI auditável identificou vias legais e abertas:
- `openalex-local v0.7.9` — 284M+ obras, resumos e busca semântica local;
- `crossref-academic-mcp-server v0.1.0` (MIT) — Crossref + OpenAlex + Semantic Scholar, sem API keys;
- `unpaywall-mcp-server v1.0.1` — disponibilidade OA para 120M+ artigos por DOI.

Falta no Core um contrato único que resolva DOI → metadados → verificação OA → entrega somente com licença, com proveniência por observação e abstinência fail-closed quando fechado.

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-977.1 | Resolução canônica por DOI | `resolve_doi(doi)` normaliza DOI, consulta Crossref como fonte canônica de metadados (título, autores, periódico, ano) e retorna erro tipado para DOI inválido/inexistente, sem fabricar metadados |
| R-977.2 | Enriquecimento OpenAlex | `enrich_openalex(doi)` retorna `best_oa_location`, licença, lista de locais OA e flag `is_oa`; ausência de registro retorna `status=unknown`, nunca `is_oa=True` presumido |
| R-977.3 | Verificação Unpaywall | `check_unpaywall(doi)` retorna `oa_status`, URLs de PDF/landing, licença e todos os locais OA; sem e-mail/API key configurado, retorna `status=unavailable` fail-closed |
| R-977.4 | Gate de licença | `is_download_allowed()` permite download somente se `license` indica OA permitido (CC, OA de editora ou repositório) ou `best_oa_location.pdf_url` presente com licença compatível; caso contrário `allowed=False` com rota institucional indicada |
| R-977.5 | Rota institucional quando fechado | Obra fechada retorna `allowed=False`, `reason=closed_access` e indicações: assinatura institucional, empréstimo interbibliotecário, contato com autores; nunca tenta Sci-Hub ou espelho não autorizado |
| R-977.6 | Proveniência por observação | Toda resposta contém `doi`, `fonte`, `licenca`, `url_pdf_ou_landing`, `data_consulta`, `hash_resposta`; hashes SHA-256 de respostas preservados; alteração detectável |
| R-977.7 | Proibição Sci-Hub | Qualquer tentativa de usar domínio Sci-Hub, `scihub-mcp`, `scihub-cli` ou espelho pirata é bloqueada com `status=blocked`, `reason=unauthorized_source`; bloqueio coberto por teste |
| R-977.8 | Driver injetável fail-closed | Runner HTTP injetável (padrão R473); serviço ausente retorna `unavailable`, nunca sucesso silencioso; sem rede, abstém-se com mensagem clara |
| R-977.9 | Anti-overclaim | Respostas carregam `evidence_eligible` apenas quando PDF OA com licença foi observado; simulação ou metadados sem PDF não são promovidos a evidência; revisão humana permanece obrigatória |

## Invariantes

- INV-977.1: Nenhum download sem `allowed=True` fundado em licença observada.
- INV-977.2: `is_oa=True` exige URL OA + licença observadas; ausência de prova implica `unknown` ou `False`, nunca `True` presumido.
- INV-977.3: Domínios não autorizados nunca são contatados; lista de bloqueio inclui `sci-hub.*`.
- INV-977.4: Determinismo de normalização de DOI (caixa, prefixo `https://doi.org/`, espaços).
- INV-977.5: Nenhuma dependência nova em runtime do contrato base (stdlib only); clientes externos via composição.

## Fora de escopo (v1)

- Instalação de `openalex-local`, `crossref-academic-mcp-server`, `unpaywall-mcp-server` — somente contratos e stubs; instalação exige nova SPEC e consentimento explícito.
- Download de PDF fechado, autenticação em proxy institucional, integração ILL automatizada.
- Avaliação de qualidade científica, revisão por pares ou juízo Qualis.

## Referências

- PyPI: `openalex-local 0.7.9`, `crossref-academic-mcp-server 0.1.0 (MIT)`, `unpaywall-mcp-server 1.0.1`
- SPEC-935-R663 (proveniência), SPEC-935-R470 (acesso restrito opcional), SPEC-935-R473 (executor multiprovider), padrão R473 runner injetável + fail-closed
- `doctor` 2026-10-11: healthy 21/21, 180 specs, 254 agentes — instalação apenas, sem prova de inferência.

## Validação

Testes herméticos em `tests/test_r977_acesso_aberto_legal.py` usam fixtures artificiais e doubles injetáveis, sem rede real e sem promover fixtures a evidência externa. Prova real futura exige rede e chaves quando aplicável, em SPEC separada.
