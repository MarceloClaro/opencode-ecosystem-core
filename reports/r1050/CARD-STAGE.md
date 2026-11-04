# Palco completo com cartão da apresentadora — R1047

Data: 2026-11-03. Teste real de uma mudança total de cenário: palco escuro em
1920×1080, título editorial, conteúdo didático à esquerda e a apresentadora em
um cartão à direita. Áudio, voz, legendas e lip sync existentes foram
preservados. Nada foi publicado.

## Composição

- Fonte: `editor-workspace/remotion-smoke/src/r1047-slide/R1047Stage.tsx`.
- Entrada: `editor-workspace/remotion-smoke/src/r1047-slide/EntryStage.tsx`.
- Remotion 4.0.540; composição `R1047Stage`, 600 frames, 30 fps, 1920×1080.
- Cartão: `presenter-middle-card.mp4`, 560×700, vídeo de lip sync anterior.
- Cenário: fundo escuro com gradientes, grade, grão determinístico, vinheta,
  título **“Do acesso ao limite”**, trilha Acesso → Mudança → Limite e card com
  borda cônica animada.
- Conteúdo: as três cenas didáticas do R1047, sem o fundo original da
  apresentadora e sem o slide branco original.

## Efeitos selecionados

Pesquisa: documentação oficial do Remotion (`motion-blur`, `noise`,
`transitions`), `IskakovDamir/apple-motion` (medidas de tipografia e springs),
`lifeprompt-team/remotion-scenes` (catálogo de cenas) e
`vshukla7/remotion-captions-themes` (tipografia cinética). Nenhum código foi
copiado; os efeitos foram implementados no Core.

| Efeito | Uso |
|---|---|
| Spring calibrado | entradas com `damping 15.35`, `stiffness 115`, `mass 1` |
| Cascata | chips entram individualmente, sem bloco único |
| Borda cônica | moldura animada do cartão da apresentadora |
| Paralaxe/tilt | cartão com leve inclinação e deslocamento |
| Grão + vinheta | textura cinematográfica determinística |
| Crossfade com blur | transições entre atos sem corte seco |
| Tipografia cinética | título com destaque em verde e entrada por spring |
| Contador | 100+ com escala e barra de progresso |

## Render e composição

```bash
cd editor-workspace/remotion-smoke
PYTHONPATH=/home/marceloclaro/opencode-ecosystem-core \
  python3 -m integrations.video_editor render r1047-stage-plan-v2.json
```

O palco foi renderizado pelo backend auditável `video_editor` com
`license_ack` e `render_approved`; depois recebeu áudio e ASS via FFmpeg.

## Resultados

| Item | Valor |
|---|---|
| Palco renderizado | `editor-workspace/remotion-smoke/r1047-stage-v2.mp4` |
| SHA-256 do palco | `7c0089cf72fc0fe7a6ef65f43d905e483856f5670d06b83bd31aa096ba1fb9ac` |
| Plano | `a8fe8afc79d928805137f99642316d6061bda71fcefabf136ff2157cd8ec6b5e` |
| Vídeo final | `pilots/r1026-quantum/r1047-dub/out/quantum-ptbr-r1047-card-scene.mp4` |
| SHA-256 do vídeo | `7765afc04f2ee5354296d341c313a2f7c997fb1b5b03921c9a5538637bbef581` |
| Formato | 1920×1080, 30 fps, 600 frames, 20,00 s |
| Áudio | AAC 48 kHz, estéreo |
| Loudness | **−16,10 LUFS** |
| True peak | **−2,16 dBTP** |
| Cartão | presente, com a apresentadora |
| Legenda | ASS queimada; SRT preservado |
| QC | `pass` em frames, fps, loudness, silêncio e pretos |

Recibo: `reports/r1049/card-scene-qa.json`.
Contato: `reports/r1049/card-scene-contact.png`.

## Limites

- O cartão usa `presenter-middle-card.mp4`, cujo lip sync é anterior à nova
  locução. A boca pode não corresponder exatamente às palavras novas.
- O movimento e o cenário são didáticos; não provam retenção ou estética.
- Remotion License continua aplicável; render não é aprovação de licença.
- A leitura visual, a naturalidade da voz e a decisão editorial exigem revisão
  humana.
- Versões anteriores (slide estático, slide claro e slide escuro) permanecem
  como fallback.
- Nada foi publicado.
