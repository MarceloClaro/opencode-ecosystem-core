---
spec_id: SPEC-935-R1036
title: Ingestão local, inspeção e extração frame-exata das partes
component: integrations.video_local_ingest
status: implemented
test_file: tests/test_r1036_video_local_ingest.py
depends_on:
  - SPEC-935-R1035
---

# SPEC-935-R1036

## Fonte e autorização

Link `https://youtu.be/02XpQTA-_XE`; oEmbed e página pública identificaram
“Wild Heart Episode 1 (Long Version)”, 7.921 s, 25 fps declarados. O usuário
autorizou o vídeo integral, imagens, vozes e clonagem; documentos não
verificados. Processamento local em CPU, sem publicação, sem API paga e sem
upload de mídia/voz. Preservar a fonte e os masters anteriores.

Um arquivo local de 71 s encontrado em `Downloads` foi descartado por conteúdo
“Terra Ledger”, sem relação com o link. Não foi processado.

## Objetivo desta etapa

Ler a fonte já baixada e produzir a base auditável para as partes:

1. `probe_source` inspeciona arquivo regular, hash, streams, fps racional,
   duração, presença de áudio e contagem de frames. Se o contêiner não declarar
   frames, exige contagem explícita; não estimar silenciosamente.
2. Declarar `cfr_compatible` apenas por confronto entre `avg_frame_rate`,
   `r_frame_rate`, duração e contagem. Isso é compatibilidade de sonda, **não**
   auditoria completa de timestamps. VFR/indeterminado bloqueia o plano CFR.
3. `plan_from_inspection` conecta a inspeção ao planejador R1035, sem inventar
   duração, frames ou candidatos de cena.
4. `extract_parts` faz **stream copy** no muxer `segment` em fronteiras que
   sejam keyframes da fonte, sem recortar contexto, sem reencode e sem
   descartar cauda. Verifica cada saída por contagem de frames, fps, duração,
   áudio, erros de decodificação e hash. Falha fechada se uma fronteira não for
   keyframe ou se o número de arquivos/frames divergir. A edição posterior pode
   reencodar uma parte individual, mas a extração preserva o original.
5. Manifesto e recibos por parte registram extração concluída; edição, QA
   audiovisual, sincronia labial e aprovação permanecem pendentes. Não há
   montagem, dublagem, tradução ou clonagem nesta etapa.

## Invariantes

- Fonte e plano são vinculados por SHA-256; fonte alterada ou plano fora de
  cobertura recusam a extração.
- Saída em diretório novo; nunca sobrescrever partes ou aprovações anteriores.
- `context_start_frame`/`context_end_frame` não são entradas de montagem.
- Toda fronteira planejada precisa ser keyframe da fonte, alinhado a frame.
  Se não for, a execução falha e exige replanejamento; não se arredonda para
  um frame vizinho nem se aceita corte em não-keyframe.
- Pequena defasagem de priming AAC é registrada; não é declarada sincronia
  labial. Aprovação humana continua obrigatória.
- `ffprobe`/`ffmpeg` locais; nenhuma rede. Testes usam fixtures sintéticas e
  não comprovam qualidade do episódio real.

## Aceites

Testes antes do código cobrem: sonda de fixture CFR com áudio; contagem
explícita em contêiner que omite frames; rejeição de arquivo inexistente,
não-mídia e VFR; plano derivado da sonda; extração de múltiplas partes com
frames exatos; recusa de sobrescrita; hash de fonte/plano; verificação de
manifesto; detecção de artefato alterado; parte única; e recusa de plano
adulterado. Fixtures são sintéticas e pequenas.

## Fora de escopo

Detecção semântica de cena, diarização, ASR, tradução, TTS, clonagem, legendas
e montagem. A extração preserva o material, mas não edita nem aprova.

## Estado implementado

`integrations/video_local_ingest.py` implementa sonda, plano derivado,
detecção de keyframes, split por stream copy, recibos e verificação. Onze
testes R1036 passam.

### Correção de método após contraprova no arquivo real

O reencode com `-segment_frames` + `-break_non_keyframes` produziu 1504 + 1505
frames para um plano de 1504 + 1503, ou seja, **duas duplicações**. Forçar
keyframes não removeu a duplicação; a extração por `-ss` + `-frames:v` produziu
1502 frames e não preservou o frame inicial planejado. Essas tentativas foram
descartadas.

O split por **stream copy** no keyframe 149,16 s da fonte produziu exatamente
3.729 + 194.287 = 198.016 frames em 25,18 s, com o primeiro frame keyframe. A
fonte tem 2.155 keyframes alinhados a frame (intervalo máximo de 7 s). Por isso
a extração agora exige fronteiras em keyframes da fonte; a edição posterior é
que reencoda a parte. O trecho de 120 s usado nessa contraprova é diagnóstico,
não uma parte final.

A extração do episódio real ainda não foi executada; depende da transcrição
ASR para escolher keyframes fora de fala e do plano final.

### Correção posterior: GOP aberto e fonte derivada

O plano final tem 107 partes e todas as fronteiras em keyframes. A primeira
extração direta da fonte verificou 52 partes, mas falhou na P0053 com
`mmco: unref short failure`: o keyframe da fonte é de **GOP aberto** e pode
depender do GOP anterior. O diretório dessa tentativa está marcado como
`parts-extracted/DO_NOT_USE.md`.

A correção validada é um intermediário reencodado com
`-flags +cgop -x264-params open-gop=0`, keyframes forçados nas 106 fronteiras e
`-fps_mode cfr`. O intermediário tem 198.016 frames, 1.546 keyframes e todas as
fronteiras presentes. A extração final usa `-ss` por parte + `-c copy` a partir
desse intermediário, com `derived_source` ligando o intermediário ao hash da
fonte original. O manifesto registra fonte e intermediário; a verificação
re-hasheia ambos.

Doze testes R1036 passam, incluindo extração de intermediário derivado. A
extração final tem 107 partes, 198.016 frames e 107 recibos. A verificação
independente do manifesto, com re-hash da fonte/intermediário e re-decode de
cada parte, retornou `{"verified": true}`. O índice está em
`parts-final/PARTS.md`; a montagem continua bloqueada por edição/revisão.

