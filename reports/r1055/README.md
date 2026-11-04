# R1055 — “O que é um qubit?” (16:9 e 9:16)

- **Status:** renderizado e aprovado no QC técnico; revisão humana pendente
- **Data:** 2026-11-04
- **Piloto:** `pilots/r1055-qubit/`
- **Spec:** `specs/SPEC-1055-video-qubit-didatico.md`
- **Roteiro:** `pilots/r1055-qubit/SCRIPT.md`
- **Referências:** `pilots/r1055-qubit/REFERENCES.md`
- **Câmera/motion:** `docs/CINEMATIC_REMOTION_R1055.md`

## 1. Entregáveis

| Arquivo | Formato | Duração | Frames | Tamanho | SHA-256 |
|---|---|---|---|---|---|
| `pilots/r1055-qubit/out/r1055-qubit-16x9.mp4` | 1920×1080, 30 fps | 109,73 s | 3292 | 23,27 MB | `b66837179b77e7f415bed44026b1d7ba683c11b8391d448b8e91fbf93cd218e0` |
| `pilots/r1055-qubit/out/r1055-qubit-9x16.mp4` | 1080×1920, 30 fps | 109,73 s | 3292 | 22,04 MB | `e396ef824a0773e2329781703e102469cf35c45b76dd956097b28bd5e81077d6` |

Os masters têm áudio AAC 48 kHz estéreo, loudness −14,49 LUFS e true peak
−4,42 dBTP. Os arquivos de vídeo são ignorados pelo git (`.gitignore`,
`pilots/**/*.mp4`); recibos, planos e QC ficam versionados; os contatos PNG são locais.

## 2. O que mudou nesta iteração

1. **Voz natural:** troca do XTTS (Sofia Hellen) pela voz neural Edge
   `pt-BR-FranciscaNeural`, sem clonagem. Fim da verbalização de “ponto”.
2. **Roteiro emocional:** 26 batidas curtas, pausas de 0,20–0,60 s e ritmo
   variável; sequência curiosidade → explicação → surpresa → síntese →
   agradecimento.
3. **Mapa de origem:** cena 06 com Natural Earth (domínio público), câmera
   Europa → EUA → Atlântico e pontos pulsantes sincronizados às cinco
   batidas da narração.
4. **Câmera cinematográfica:** `SceneCamera` com zoom/pan/foco/shake nas
   cenas 02–05, ancorado no início das legendas.
5. **Esferas de Bloch 3D:** wireframe, fase, brilho, estado misto e projeção;
   feixe de correlação pulsante no emaranhamento.
6. **Oscilações:** ondas com cursor luminoso e brilho; barra de decoerência
   com halo.
7. **Legendas por batida:** 26 blocos, grafia “Bell”, “qubit”, “Aspect”,
   “Clauser”, “Zeilinger”.

## 3. QC técnico

### Master 16:9 — `out/qa-camera-16.json`

```json
{
  "frame_count": {
    "ok": true,
    "expected": 3292,
    "actual": 3292
  },
  "fps": {
    "ok": true,
    "expected": "30/1",
    "actual": "30/1"
  },
  "loudness": {
    "ok": true,
    "target": -14.0,
    "tolerance": 1.0,
    "actual": -14.49
  },
  "true_peak": {
    "ok": true,
    "max": -1.5,
    "actual": -4.42
  },
  "silence": {
    "ok": true,
    "max_allowed": 4.0,
    "longest": 2.961
  },
  "black": {
    "ok": true,
    "max_allowed": 0.2,
    "longest": 0.0
  },
  "contact_sheet": {
    "ok": true,
    "path": "pilots/r1055-qubit/out/contact-camera-16.png"
  }
}
```

### Master 9:16 — `out/vertical-qa-camera-9.json`

```json
{
  "frame_count": {
    "ok": true,
    "expected": 3292,
    "actual": 3292
  },
  "fps": {
    "ok": true,
    "expected": "30/1",
    "actual": "30/1"
  },
  "loudness": {
    "ok": true,
    "target": -14.0,
    "tolerance": 1.0,
    "actual": -14.49
  },
  "true_peak": {
    "ok": true,
    "max": -1.5,
    "actual": -4.42
  },
  "silence": {
    "ok": true,
    "max_allowed": 4.0,
    "longest": 2.961
  },
  "black": {
    "ok": true,
    "max_allowed": 0.2,
    "longest": 0.0
  },
  "contact_sheet": {
    "ok": true,
    "path": "pilots/r1055-qubit/out/vertical-contact-camera-9.png"
  }
}
```

## 4. ASR e prosódia

ASR com `faster-whisper-large-v3` (CPU, int8), 33 segmentos:

- sem a palavra “ponto” falada;
- “Aspect, Clauser e Zeilinger” reconhecidos;
- “Copenhague, Viena e Leipzig” reconhecidos;
- “Schumacher” e “Feynman” reconhecidos.

Comparação de prosódia:

| Métrica | XTTS Sofia (anterior) | Edge Francisca (final) |
|---|---|---|
| Duração | 87,50 s | 109,72 s |
| F0 mediana | 184,7 Hz | 243,8 Hz |
| F0 desvio | 47,4 Hz | 51,8 Hz |
| Faixa F0 (5–95%) | 146,6 Hz | 175,9 Hz |
| RMS CV | 0,904 | 0,912 |
| Fração de pausa | 26,1% | 32,6% |

A voz final tem maior faixa tonal e mais pausas; o roteiro ficou mais longo
para acomodar a respiração e a sequência didática. O ASR é diagnóstico, não
aprovação perceptual.

## 5. Pesquisa de câmera e motion

Foram estudados padrões e licenças de:

- **Claude Remotion Skill** (MIT) — Ken Burns, parallax, stagger, respiração,
  regra “render → inspecionar → corrigir”.
- **Remotion Docs** — `interpolate`, `spring`, `Easing`.
- **Motion Canvas** (MIT), **Manim** (MIT), **Theatre.js** (Apache-2.0),
  **OpenTimelineIO** (Apache-2.0), **Blender** (GPL), **GSAP** (licença
  padrão, não open source).

Nenhum plugin novo foi instalado. O módulo `cinematic.tsx` é original e usa
somente APIs já presentes. Detalhes em `docs/CINEMATIC_REMOTION_R1055.md`.

## 6. Implementação técnica

- `pilots/r1055-qubit/generate_audio_edge.py` — TTS por batida, cache de
  WAVs, timeline, SRT.
- `pilots/r1055-qubit/build_remotion_timeline.py` — timeline TypeScript com
  cenas e legendas.
- `pilots/r1055-qubit/render_world_map.py` — mapa Natural Earth 4096×1354.
- `editor-workspace/remotion-smoke/src/r1055-qubit/cinematic.tsx` —
  `SceneCamera`, `useSceneCamera`, `TravelingPulse`.
- `.../QubitExplainer.tsx` — 16:9, `BlochSphere`, `CorrelationBeam`.
- `.../QubitVertical.tsx` — 9:16 nativo.
- `.../QubitMap.tsx` — mapa, câmera, pontos pulsantes, timeline.
- `.../timeline.ts` — 7 cenas, 26 legendas, 3292 frames.

## 7. Tempos de render

- 16:9: 641,89 s; pico de RSS 753.468 KB; plano `remotion-plan-camera-16b.json`.
- 9:16: 588,96 s; pico de RSS 1.033.932 KB; plano `vertical-plan-camera-9.json`.
- Os renders usam Remotion 4.0.540 em Chrome headless; o tempo varia com a carga da máquina.

## 8. Limitações

- QC técnico não é aprovação estética nem científica.
- O mapa é ilustrativo; as cautelas históricas estão em `REFERENCES.md`.
- A voz é sintética; a prosódia foi ajustada, mas não substitui locução
  humana.
- O vídeo não foi publicado; a entrega é para revisão humana.
- O cartão do autor usa a foto pública do próprio autor no GitHub; o QR
  aponta para o perfil.

## 9. Reprodução

```bash
# 1. áudio (usa cache de WAVs; requer edge-tts)
/home/marceloclaro/.cache/opencode-pilot/venvs/edge-tts/bin/python \
  pilots/r1055-qubit/generate_audio_edge.py

# 2. timeline
python3 pilots/r1055-qubit/build_remotion_timeline.py

# 3. mapa
python3 pilots/r1055-qubit/render_world_map.py

# 4. stills de controle
cd editor-workspace/remotion-smoke
node node_modules/@remotion/cli/remotion-cli.js still \
  src/r1055-qubit/EntryQubit.tsx QubitExplainer /tmp/still.png --frame=1600

# 5. render + mux + QC estão descritos em SCRIPT.md e no plano JSON
```

## 10. Decisões

- **Voz:** Francisca em vez de Sofia Hellen/XTTS; maior faixa tonal e
  pronúncia limpa, sem “ponto”.
- **Mapa:** Natural Earth em vez de NASA Blue Marble; o host NASA não
  respondeu, e a Natural Earth é profissional e de domínio público.
- **Vertical:** composição nativa, não corte com blur.
- **Câmera:** zoom ancorado nas legendas, sem plugin externo; o render
  permanece determinístico.
- **Legendas:** por batida, não por cena inteira; reduz carga de leitura.
