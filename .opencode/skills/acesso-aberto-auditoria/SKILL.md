---
name: acesso-aberto-auditoria
description: >-
  Resolver DOI por vias legais, baixar somente OA permitido e gerar pasta de
  auditoria com fichamento ABNT e recortes rastreáveis (SPEC-977/978/979).
  Use para DOI isolado ou lote, com cobertura total de citações. Nunca usa
  Sci-Hub. Revisão humana obrigatória; não promete nota, Qualis ou aceite.
disable-model-invocation: true
---

# Acesso Aberto com Auditoria Obrigatória (SPEC-977/978/979/980)

## Quando usar

- Baixar artigo por DOI em pasta de auditoria `auditoria_fichamentos/<slug-doi>/`.
- Fichar cada trecho citado no manuscrito com página, autor, ano e justificativa de relevância em ABNT NBR 6023:2018 / NBR 10520:2023.
- Auditar cobertura total antes de declarar pronto. Sem Sci-Hub em qualquer etapa.

## Pipeline (orquestrador — recomendado)

### Fontes expandidas (SPEC-980)

- `research/fontes_expandidas.py::buscar_todas` federa PubMed, arXiv, SciELO, LILACS, OasisBR/BDTD, Sucupira Observatório e Dados Abertos CAPES; Portal de Periódicos CAPES é fail-closed com rota institucional.

1. **Resolver:** `research/legal_oa_pipeline.py::resolve_doi` via Crossref.
2. **Enriquecer:** `enrich_openalex` com `best_oa_location` e licença.
3. **Verificar:** `check_unpaywall` quando configurado, senão `unavailable` fail-closed.
4. **Pastar:** `research/auditoria_fichamento.py::criar_pasta_auditoria` — OA permitido salva `artigo.pdf` com `%PDF-`; fechado salva `sem_pdf.json`.
5. **Fichar e auditar:** `adicionar_recorte` por citação + `auditar_pasta` até `aprovado True`.

## Uso via orquestrador (recomendado)

```bash
python3 - <<'PY'
from research.auditoria_fichamento import criar_pasta_auditoria, adicionar_recorte, auditar_pasta
meta = {"doi": "10.1371/journal.pone.0024352", "titulo": "Artigo Exemplo",
        "autores": ["Silva, João"], "ano": 2011, "fonte": "openalex",
        "licenca": "cc-by", "pdf_url": "https://exemplo.org/oa.pdf"}
pasta = criar_pasta_auditoria("auditoria_fichamentos", meta, pdf_bytes=b"%PDF-1.4 demo",
                              runner_allowed=lambda m: {"allowed": True})
adicionar_recorte(pasta, {"trecho_literal": "trecho literal curto",
  "pagina": "3", "autor": "SILVA", "ano": 2011,
  "justificativa_relevancia": "Sustenta o argumento central com evidência direta.",
  "id_trecho_manuscrito": "(SILVA, 2011, p. 3)"})
print(auditar_pasta(pasta, ["(SILVA, 2011, p. 3)"]))
PY
```

## Bloqueadores

- DOI inválido: `ValueError` antes de rede.
- Fonte `sci-hub`/`scihub`: `PermissionError: blocked: unauthorized_source`.
- Trecho >400 caracteres ou sem página/autor/ano/justificativa mínima 20: `ValueError`.
- Citação sem recorte: `auditar_pasta` reprovado.

## Anti-overclaim

Fichamento e auditoria são computacionais e exigem revisão humana. Não declaram qualidade científica, Qualis ou aceite.
