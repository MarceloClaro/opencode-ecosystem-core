# Slide dinâmico Remotion sobre o R1047

Data: 2026-11-03. Teste real de um slide **dinâmico e didático** sobre o vídeo
R1047 com lip sync, áudio e legendas preservados. Não houve publicação.

## Composição

- Fonte: `editor-workspace/remotion-smoke/src/r1047-slide/R1047Slide.tsx`.
- Entrada isolada: `editor-workspace/remotion-smoke/src/r1047-slide/Entry.tsx`.
- Remotion 4.0.540; composição `R1047Slide`, 600 frames, 30 fps, 935×864.
- Render H.264 produzido em 934×864 (dimensão par do encoder); o slide foi
  escalado para 935×864 e mascarado antes da composição.
- Cenas:
  1. 0,0–5,2 s: acesso ampliado, contador 100+ e cards Eagle/Heron;
  2. 5,2–9,6 s: chips menores saem de linha, chips maiores entram;
  3. 9,6–20,0 s: limite da simulação e o que muda com 100+ qubits.

## Render e composição

```bash
cd editor-workspace/remotion-smoke
PYTHONPATH=/home/marceloclaro/opencode-ecosystem-core \
  python3 -m integrations.video_editor render r1047-slide-plan-v2.json
```

O backend `video_editor` exigiu `license_ack` e `render_approved` no plano e
confirmou 600 frames. O MP4 final foi composto sobre
`presenter-middle-r1047-1080.mp4`, com a máscara existente, áudio
`dub-r1047.pt-BR.wav`, ASS `captions-r1047.pt-BR.ass` e o rótulo
“voz sintética • PT-BR”.

## Resultados

| Item | Valor |
|---|---|
| Slide renderizado | `editor-workspace/remotion-smoke/r1047-slide-v2.mp4` |
| SHA-256 do slide | `14c1aac725687ae7e29ebd11d99e2f65a24c2744cfc3bd90263757317a152f70` |
| Plano | `51aa71f388018072896de0cc41ed97b93d8ba7ca970423a2f4d7d6b96d04d910` |
| Vídeo final dinâmico | `pilots/r1026-quantum/r1047-dub/out/quantum-ptbr-r1047-dynamic-slide.mp4` |
| SHA-256 do vídeo | `d4c8a34dc07b9ab0bd77315086f45ec3ef9f2f451421e293895e7491c9f0fc1d` |
| Formato | 1920×1080, 30 fps, 600 frames, 20,00 s |
| Áudio | AAC 48 kHz, estéreo |
| Loudness | **−16,10 LUFS** |
| True peak | **−2,16 dBTP** |
| Cartão | ausente |
| Legenda | ASS queimada; SRT preservado |
| QC | `pass` em frames, fps, loudness, true peak, silêncio e pretos |

Recibo do QC: `reports/r1049/dynamic-slide-qa.json`.
Contato: `reports/r1049/dynamic-slide-contact.png`.

## Comparação

- `quantum-ptbr-r1047.mp4` — slide estático, SHA
  `93f074a3e258f12371b34540a0a8b574a1b47f7bba6c140da774e5f8289f3ed5`;
- `quantum-ptbr-r1047-dynamic-slide.mp4` — slide dinâmico, SHA
  `d4c8a34d…f0fc1d`.

O áudio e a locução são os mesmos; o slide dinâmico muda a camada visual.

## Limites

- O movimento é didático; não prova qualidade estética, compreensão ou retenção.
- A composição usa Remotion License; render não é aprovação de licença.
- A “cena 02” mostra o cartão “Antes” desbotando de propósito; a leitura visual
  ainda exige revisão humana.
- Não houve nova sincronização labial nem nova locução nesta etapa.
- Nada foi publicado.
