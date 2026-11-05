---
name: code-video-visual-qa
description: >
  QA técnico de vídeo renderizado por código: metadados ffprobe, quadros
  pretos, silêncio, loudness integrada e extração de frames para inspeção
  humana. Use antes de declarar um MP4 pronto, ao revisar legendas/áudio ou
  quando outro pipeline (HyperFrames, Remotion, ffmpeg) precisar de um gate
  técnico. Não avalia qualidade estética, não abre o vídeo como programa e
  não substitui revisão humana.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R1069
spec: SPEC-935-R1069-centro-producao-global.md
---

# Skill: Code Video Visual QA (R1069)

Gate técnico para vídeos produzidos por código. A saída é um JSON com
metadados, intervalos pretos, silêncio, loudness e caminhos de frames; a
decisão estética continua humana.

## Comando

```bash
python3 -m integrations.video_qa probe CAMINHO.mp4 \
  --output-dir qa/frames --frames 3 --timeout 120
```

## O que verifica

| Sinal | Método | Limite de alerta |
|---|---|---|
| Metadados | `ffprobe` | duração, codec, resolução, fps, áudio |
| Quadros pretos | `ffmpeg blackdetect` | intervalo ≥ 0,2 s |
| Silêncio | `ffmpeg silencedetect` | intervalo ≥ 1,0 s |
| Loudness | `ffmpeg ebur128` | fora de −30 a −10 LUFS |
| Frames | `ffmpeg -ss` | 1–12 PNGs para inspeção |

## Protocolo

1. Rode `probe` no MP4 final, não no preview.
2. Abra os PNGs gerados em resolução integral; procure mãos, rostos, texto
   cortado, legendas fora da safe area e continuidade.
3. Trate `issues` como alerta, não como laudo. Um vídeo sem alertas ainda pode
   estar visualmente ruim.
4. Não declare `aprovado`, `Qualis`, `verificado` ou equivalente. O máximo é
   `QA técnico concluído; revisão humana pendente`.
5. Se `ffmpeg`/`ffprobe` faltarem, devolva `blocked`; não simule resultado.

## Limites

- Não avalia narrativa, estética, originalidade, direitos autorais ou adequação
  científica.
- Não executa o vídeo como programa; só lê o arquivo com ffmpeg/ffprobe.
- Não substitui o QA específico de HyperFrames/Remotion nem a revisão humana.
- Nenhuma validação externa.
