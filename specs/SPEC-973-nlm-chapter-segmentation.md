# SPEC-973 — Segmentação por Capítulo → Episódios Separados (NLM Podcast Executor v2)

- frente: pesquisador-universal | raiz: R550 | derived de: SPEC-972 (nlm_executor), SPEC-935-R468 (core-integration)
- estado: proposta-aberta (R551) | ciclo-alvo: R551 → R552

## Contexto (verdade física, não opinião)
O executor da trilogia (SPEC-972 → agen_runners/nlm_executor.py) executa o manuscrito
como **episódio único** (segmenta o texto por `\x00`, 1 job → 1 áudio). O manuscrito
de produção real é o romance **Molambudos** (26k palavras, 32 headers de capítulo físicos).
O usuário pediu: **"cada capítulo separado"** = 1 episódio-áudio por capítulo.

## Requisito
1. O executor DEVE expor rota `--por-capitulo` que:
   a. detecta marcadores de capítulo no manuscrito físico (regex canônica de front):
      `^\s*(CAP[IÍ]TULO\s+[0-9XVI]+|##?+\s+[0-9]+\.?|PR[OÓ]LOGO|EP[ÍI]LOGO)\s*$`
   b. segmenta o manuscrito em N episódios (1 por capítulo), cada um com seu trecho.
   c. para CADA capítulo dispara **1 job** `nlm download audio -o <trecho_cap>` — sintaxe
      real v0.11.6 comprovada pela trilogia (SEM `--profile`, retries/polling).
2. Gate de aceitação (teste r550):
   - r550_prova_segmentacao: dado o manuscrito real Molambudos, `segmentar()` retorna
     **N ≥ 2** trechos, e cada trecho começa com o marcador de capítulo correspondente.
   - r550_prova_cli_por_capitulo: monta N comandos `nlm download audio -o …` — 1 por trecho.
   - r550_prova_episodio_audio: 1 job NLM real por capítulo → áudio físico por episódio.
3. Anti-overclaim: NUNCA declare "capítulo separado" sem o teste r550 executando
   a segmentação NO manuscrito real (320/105k?) — números = do físico, não do teórico.

## Delta físico esperado
- specs/SPEC-973-nlm-chapter-segmentation.md
- agent_runners/nlm_executor.py (adição rota --por-capitulo + segmentar())
- tests/test_r550_chapter_segmentation.py
