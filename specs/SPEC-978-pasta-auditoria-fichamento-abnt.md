# SPEC-978 — Pasta de Auditoria por Artigo com Fichamento ABNT Obrigatório

```yaml
spec_id: SPEC-978
title: Download OA + fichamento ABNT com recortes citados como padrão obrigatório de auditoria
status: green
component: research/auditoria_fichamento.py + research/downloader.py + research/fichamento.py + research/legal_oa_pipeline.py
test_file: tests/test_r978_pasta_auditoria_fichamento.py
validation_scope: local_runtime
```

## Contexto e gap

SPEC-977 entregou gate legal por DOI sem Sci-Hub, mas não padroniza a custódia por artigo nem o vínculo entre cada citação do manuscrito e o trecho que a sustenta. O usuário exige padrão obrigatório: cada artigo em pasta própria para auditoria, com fichamento ABNT atualizado contendo recortes citados com página, autor, ano e justificativa de relevância.

Base existente reutilizada sem duplicação:
- `research/downloader.py` — OA-only, valida `%PDF-`, SHA-256, nunca contorna paywall;
- `research/fichamento.py::CitationFormatter.abnt` — NBR 6023:2018, citações NBR 10520:2023;
- `research/legal_oa_pipeline.py` — gate `allowed` somente com licença + URL.

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-978.1 | Pasta por artigo | `auditoria_fichamentos/<slug-doi>/` contém `metadados.json`, `fichamento.md` e, quando permitido, `artigo.pdf`; slug determinístico do DOI normalizado |
| R-978.2 | Download somente OA permitido | PDF baixado somente se `is_download_allowed==True` e fonte OA verificada; fechado gera pasta sem PDF com `sem_pdf.json` + rota institucional; pirata bloqueado |
| R-978.3 | Fichamento ABNT obrigatório | `fichamento.md` contém referência ABNT NBR 6023:2018, seção de recortes e seção de síntese crítica; ausência reprova auditoria |
| R-978.4 | Recorte citado rastreável | Cada recorte = `trecho_literal_curto` até 400 caracteres, `pagina`, `autor`, `ano`, `justificativa_relevancia` com mínimo 20 caracteres, `id_trecho_manuscrito` onde é citado; citação no manuscrito sem recorte correspondente reprova |
| R-978.5 | Auditoria fail-closed | `auditar_pasta()` retorna `aprovado` somente se pasta, metadados, fichamento e cobertura total de citações existirem; caso contrário `reprovado` com motivo |
| R-978.6 | Proveniência e hashes | `metadados.json` com `doi`, `fonte`, `licenca`, `pdf_sha256`, `data_consulta`, `hash_resposta`; PDF com magic `%PDF-` validado |
| R-978.7 | Direito de citação | Recortes curtos com fonte completa; nenhuma reprodução integral; teste rejeita trecho >400 caracteres ou sem página/autor/ano |

## Invariantes

- INV-978.1: Nenhum PDF fechado baixado; fechado nunca vira `allowed=True`.
- INV-978.2: Nenhum domínio `sci-hub`/`scihub` contatado em qualquer etapa.
- INV-978.3: Toda citação `(AUTOR, ano, p. X)` no manuscrito exige recorte com mesma autoria/ano/página.
- INV-978.4: Fichamento sem justificativa de relevância é incompleto.
- INV-978.5: Módulo novo stdlib-only; reuso por composição, sem novas deps.

## Fora de escopo (v1)

- Conversão PDF→Markdown integral, resumo por LLM, resenha automática longa.
- Integração ILL/proxy institucional automatizada.
- Juízo de qualidade científica ou Qualis.

## Referências

- NBR 6023:2018 (referências), NBR 10520:2023 (citações); art. 46 Lei 9.610/98 (direito de citação).
- SPEC-977 (gate), SPEC-935-R663 (proveniência), `research/downloader.py`, `research/fichamento.py`.

## Validação

Testes herméticos com doubles e PDFs falsos `%PDF-` mínimos, sem rede real e sem promover fixtures a evidência externa. Prova real futura com 1 DOI OA em SPEC separada.
