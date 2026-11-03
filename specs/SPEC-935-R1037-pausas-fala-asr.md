---
spec_id: SPEC-935-R1037
title: Pausas de fala a partir de ASR para fronteiras de partes
component: integrations.video_dialogue_timing
status: implemented
test_file: tests/test_r1037_video_dialogue_timing.py
depends_on:
  - SPEC-935-R1034
  - SPEC-935-R1035
---

# SPEC-935-R1037

## Objetivo

Converter a transcrição local com timestamps de palavra em pontos de pausa
auditáveis para o planejador R1035. O ASR já é produzido por
`integrations.video_cpu_pipeline.py` em CPU, com modelo local explícito.

Esta etapa **não** traduz, não identifica locutores, não separa vozes e não
edita áudio. Ela apenas mede intervalos entre palavras/frases e propõe
fronteiras fora da fala. Uma pausa acústica não é uma fronteira semântica de
cena; o plano continua exigindo revisão.

## Regras

- Usar palavras quando existirem; se um segmento não tiver palavras, usar o
  intervalo do segmento como fallback explícito.
- Validar tempos finitos, não negativos, ordenados e dentro da duração do ASR.
- Unir intervalos sobrepostos antes de medir lacunas; não produzir lacuna
  negativa.
- Candidato = ponto médio de lacuna entre `min_gap_seconds` e
  `max_gap_seconds`, convertido para frame por fps racional, com arredondamento
  meio-para-cima e clamp em `[1, total_frames-1]`.
- Exportar `pause_frames` e `speech_intervals` em frames para o planejador.
  Intervalos de fala servem para sinalizar corte dentro de fala; não provam
  que todo o restante é silêncio.
- Se `audio` for fornecido, conferir SHA-256 e duração contra o ASR. Sem áudio,
  registrar que o vínculo não foi reverificado nesta chamada.
- Saída em arquivo novo; nunca sobrescrever. Nada de rede.

## Aceites

Testes antes do código: lacuna no ponto médio; lacuna curta ignorada;
sobreposição unida; fallback de segmento sem palavras; tempos inválidos
rejeitados; hash de áudio divergente rejeitado; ASR vazio válido sem pausas;
frames ordenados/únicos e dentro do total; fps fracionário; CLI sem
sobrescrita. Fixtures sintéticas não são o episódio real.

## Limites

ASR `small` pode perder fala, fundir palavras ou errar limites; música e
efeitos podem produzir lacunas falsas. O ponto médio de uma lacuna pode cair
em respiração ou mudança visual inadequada. A aprovação audiovisual humana
continua obrigatória. Não usar esses pontos para declarar sincronia labial,
tradução correta ou qualidade de dublagem.

## Estado implementado

`integrations/video_dialogue_timing.py` implementa a extração de lacunas,
união de sobreposições, fallback de segmentos, candidatos em frames e
verificação opcional de hash/duração do áudio. Os 14 testes R1037 passam.
Fixtures sintéticas; a transcrição real do episódio ainda estava em execução
quando esta linha foi registrada.

