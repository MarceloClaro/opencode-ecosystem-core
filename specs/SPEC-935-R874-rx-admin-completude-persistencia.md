---
spec_id: SPEC-935-R874
title: RX reprodução — completude das rotas admin/validacao e persistência (SQLite)
component: outputs/core-r853-rx
status: implemented
round_id: R874
test_file: tests/test_r874_rx_admin.py
---

# SPEC-935-R874 — Completar a superfície admin/validação e persistir

## Contexto e decisão

O operador perguntou **"o que falta para ficar funcional?"**. A análise de lacunas
identificou que a reprodução (SPEC-935-R853) cobre 22 das 23 rotas do contrato,
mas **omite 11 rotas administrativas** que as páginas `/review` e `/validacao`
realmente chamam — logo, essas páginas quebram ao serem usadas além do login.
Além disso, sessões e feedback eram **em memória** (perdidos ao reiniciar).

Decisão (autorizada pelo operador: *"sim prossiga mesmo sem gpu"*): completar a
superfície admin/validação com um **store SQLite persistente** e dados de
**demonstração explicitamente sintéticos** (substituíveis por export real),
sem GPU e sem modelos clínicos. Nada é declarado equivalência clínica.

## Rotas acrescentadas (contrato do front)

Faltantes e exercidas por `review.html`:
- `GET/DELETE /admin/api/images/{image_id}`
- `GET /admin/api/images/{image_id}/thumbnail` (PNG)
- `GET /admin/api/images/{image_id}/image` (PNG ampliado)
- `PUT /admin/api/images/{image_id}/age` (body `{"label": child|adult}`)
- `POST/DELETE /admin/api/images/{image_id}/edit-lock`
- `POST /admin/api/images/{image_id}/segment` (`?replace_teeth=`) → job
- `GET /admin/api/jobs/{job_id}`
- `GET/POST /admin/api/batch`, `DELETE /admin/api/batch/{batch_id}`
- `GET /admin/api/export?group=&task=` (ZIP)

Faltantes e exercidas por `validacao.html`:
- `GET /validacao/api/modelos/{slug}` (relatório; `?page=&page_size=`)
- `POST /validacao/api/modelos/{slug}/imagens/{image_id}/revisao`
- `GET /validacao/{slug}` (HTML que serve `validacao.html`)

Já existentes, alinhados ao formato do front:
- `POST /admin/api/login` → `{authenticated, csrf, role, is_admin, username}`
- `GET /admin/api/session` → idem
- `GET /admin/api/reviews` → `{page, pages, total, items, active_jobs, edit_locks}`
- `GET /admin/api/statistics` → `{images, reviewed_images, classes_increased,
  classes[], average_review_seconds, measured_reviews}`
- `GET /validacao/api/modelos` → `{models: [...]}`

## Contratos de aceite

1. Todas as rotas acima respondem com os **formatos que o front consome** (teste
   de contrato por campo), com **401** sem sessão (fail-closed).
2. `POST /admin/api/login` emite cookie `admin_session` e devolve `csrf`, `role`,
   `is_admin`, `username`.
3. `GET /admin/api/reviews` pagina (`page`, `pages`, `total`, `items`), filtra por
   `status` e devolve `active_jobs`/`edit_locks`; cada item traz
   `image_id, reviewed, reviewer, revision, created_at, source_database, width,
   height, annotation_count, segmented_count, complete_groups, group_counts,
   age_classification`.
4. Thumbnail/image devolvem **PNG válido** (`image/png`, assinatura PNG).
5. `POST /admin/api/images/{id}/segment` devolve job com `job_id` e `status`;
   `GET /admin/api/jobs/{id}` devolve o mesmo job (polling do front fecha).
6. Batch: `POST` cria/executa e devolve `{batch_id,status,current,total,succeeded,
   skipped,failed}`; `GET` devolve `idle` quando não há lote; `DELETE` cancela.
7. `GET /admin/api/export` devolve **ZIP válido** com manifesto + anotações.
8. `GET /validacao/api/modelos/{slug}` devolve relatório com `name, slug, eyebrow,
   description, kind, progress{processed,total,status}, summary{metrics,task},
   per_class[], plots[], examples[], pagination`; 404 para slug inexistente.
9. **Persistência**: sessão sobrevive a reabertura da conexão (mesmo arquivo);
   feedback salvo é lido por `GET /feedback/{id}` após reinit do store.
10. **Isolamento de teste**: o banco é escolhido por `RX_ADMIN_DB` (default
    `~/.cache/rx-admin/admin.db`); testes usam arquivo temporário.
11. Dados são **demonstração sintética** e rotulados como tal; nenhum dado real de
    paciente; `externally_validated=false`, `confidence_promoted=false`.

## Limites

Os dados de review/validação são **sintéticos de demonstração** (sem valor clínico),
criados para exercitar a interface. Não representam o banco real do alvo. Os modelos
de IA continuam ausentes (ver SPEC-935-R853). Sem GPU, a Opção 2 não executa.
