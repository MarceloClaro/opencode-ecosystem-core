---
spec_id: SPEC-935-R1007
title: Buscador de datasets multi-provedor com ranking científico auditável
component: research.dataset_search
status: implemented
test_file: tests/test_r1007_dataset_search.py
---

# SPEC-935-R1007 — Buscador de datasets multi-provedor

**Status:** Implementado (RED → GREEN)
**Data:** 2026-11-01
**Agente:** marceloclaro

## 1. Problema

Projetos do Core precisam localizar datasets reutilizáveis sem depender de
buscas manuais e sem inflar a confiança em metadados incompletos. Um resultado
de busca não é evidência: precisa de provedor, endpoint, instante de coleta,
hash do registro bruto, licença classificada e acesso declarado.

## 2. Objetivo

Oferecer `research.dataset_search`: busca em seis provedores públicos
(Zenodo, DataCite, Figshare, OpenAlex, Hugging Face, GBIF), normaliza os
registros, deduplica, pontua relevância e prontidão FAIR de forma determinística
e emite manifesto com SHA-256.

## 3. Não-objetivos

- Baixar arquivos de dados (a busca só resolve metadados e URLs).
- Autenticar em provedores pagos ou com chave obrigatória.
- Declarar que um dataset é adequado ao projeto: isso exige revisão humana.
- Substituir revisão sistemática ou avaliação de qualidade dos dados.

## 4. Requisitos

- R1. Stdlib apenas; nenhuma dependência nova.
- R2. Rede só por `runner` injetável; sem runner, o provedor retorna
  `status="unavailable"` (fail-closed) e a busca não inventa resultados.
- R3. Toda URL é checada contra a política de fontes; host bloqueado é
  descartado com `reason="unauthorized_source"` e nunca vira resultado.
- R4. Licença é classificada em `open | restricted | unknown`; ausência de
  licença nunca é tratada como aberta.
- R5. Campos ausentes são `None`, nunca zero fabricado.
- R6. Deduplicação por DOI (case-insensitive) ou título normalizado + ano,
  preservando a proveniência de todas as cópias.
- R7. Ranking determinístico: `0.6*relevância + 0.3*FAIR + 0.1*recência`,
  com pesos configuráveis e componentes expostos por resultado.
- R8. Ordenação estável: score final desc, depois DOI, depois título.
- R9. Manifesto canônico (JSON ordenado) com SHA-256 do relatório.
- R10. `retrieved_at` injetável para reprodutibilidade.

## 5. Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| CA1 | Seis provedores montam requisição correta | `test_build_request_*` |
| CA2 | Cada parser normaliza o payload documentado | `test_parse_*` |
| CA3 | Sem runner, status `unavailable` e zero resultados | `test_sem_runner_fail_closed` |
| CA4 | Fonte bloqueada é descartada com motivo | `test_fonte_bloqueada_descartada` |
| CA5 | Licença ausente não é aberta | `test_licenca_ausente_nao_e_aberta` |
| CA6 | Dedup por DOI preserva proveniência | `test_dedup_por_doi_preserva_proveniencia` |
| CA7 | Ranking é determinístico e explicável | `test_ranking_deterministico_e_explicavel` |
| CA8 | Manifesto detecta alteração | `test_manifesto_detecta_adulteracao` |
| CA9 | Campos ausentes permanecem `None` | `test_campos_ausentes_sao_none` |
| CA10 | Busca completa com runner fake é reprodutível | `test_busca_completa_reprodutivel` |

## 6. Limites

Os endpoints foram verificados em 2026-11-01 com uma consulta real por provedor.
Mudanças de esquema podem quebrar parsers; por isso cada registro carrega
`raw_sha256` e o parser é tolerante a campos ausentes, mas nunca inventa valores.
