# SPEC-935-R469 — Open Science Core-Native v4.2

```yaml
spec_id: SPEC-935-R469
title: Pesquisador Universal v4.2 — Open Science Core-Native
status: implemented
version: 1.0.0
depends_on:
  - SPEC-017
  - SPEC-935-R468
primary_orchestrator: marceloclaro
```

## Objetivo

Eliminar do runtime ativo do OpenCode Ecosystem Core qualquer dependência de
executor destinado a contornar paywalls e tornar a aquisição de literatura
científica aberta uma capacidade nativa, auditável e fail-closed.

## Critérios de aceitação

1. `research/downloader.py` não importa `subprocess`, não consulta binário
   externo para download e não contém dependência do retriever legado.
2. `marceloclaro/doctor.py::EXTERNAL_CLIS` não registra esse retriever.
3. URL direta só é aceita quando a origem é uma fonte OA conhecida ou o registro
   declara `open_access`, `repository`, `preprint` ou `public_domain`.
4. DOI é resolvido na ordem: OpenAlex → Unpaywall (se e-mail configurado) →
   Europe PMC.
5. Crossref é tratado como fonte de DOI/metadados e não como autorização
   universal de PDF.
6. HTTP 200 não basta: o conteúdo precisa começar em `%PDF-`.
7. PDF acima do limite configurado é rejeitado e o arquivo parcial é removido.
8. Download aceito registra SHA-256, bytes, método/resolvedor e fundamento de
   acesso.
9. Repositórios/datasets nunca são processados como artigos.
10. Ausência de rota aberta resulta em falha explícita; não existe fallback de
    evasão de acesso.
11. A skill OpenCode identifica a integração como v4.2 Core-Native Open Science.
12. A supercamada científica completa v4.1 permanece opcional para revisão
    sistemática, GRADE, causalidade, Agent Mesh, Mission Control e federação;
    sua procedência continua verificada antes de dispatch.

## TDD

Arquivo principal: `tests/test_research_open_science_v42.py`.

Gates mínimos:

- PDF OA válido → `ok=true` + SHA-256 correto;
- HTML/paywall → rejeitado;
- `source=crossref` + `pdf_url` sem marca OA → não baixado diretamente;
- rota OpenAlex precede Unpaywall;
- registro institucional explicitamente marcado como `repository` pode usar
  URL direta;
- downloader não depende de subprocess/CLI externa;
- doctor não registra o retriever removido;
- SPEC-017 documenta Crossref como metadados.

## Limites

- Resolver uma URL OA não valida mérito científico do artigo.
- SHA-256 e magic bytes demonstram integridade de bytes/forma, não correção do
  conteúdo.
- Licença ausente nos metadados deve permanecer `null`; não inferir licença.
- Falha de rede não equivale a inexistência de acesso aberto.
