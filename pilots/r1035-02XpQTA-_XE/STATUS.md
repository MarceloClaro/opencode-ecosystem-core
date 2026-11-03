# Status R1035–R1044 — 02XpQTA-_XE

## Fonte, plano e partes

- “Wild Heart Episode 1 (Long Version)”; 7.920,698 s; 1280×720; 25 fps;
  198.016 frames; SHA-256 `d76a36a4…58cb`.
- Plano final: **107 partes**, 66,52–89,60 s, 0 cortes dentro de fala;
  106 fronteiras em keyframes; SHA-256 `1743f7ae…bf50`.
- `parts-final/`: 107 partes; verificação independente `verified: true`;
  índice `parts-final/PARTS.md`.

## Testes

| Spec | Componente | Testes |
|---|---|---:|
| R1035 | plano e gate de montagem | 57 |
| R1036 | sonda, keyframes, fonte derivada, extração | 12 |
| R1037 | pausas ASR | 15 |
| R1038 | tradução local | 14 |
| R1040 | vozes, personagens e perfis gênero/idade | 18 |
| R1041 | lote, MCP, evidência OCR, síntese e gate estrito | 39 |
| R1042 | editor universal FFmpeg/Remotion/MCP | 17 |
| R1043 | registro de ferramentas/modelos e licenças | 5 |
| R1044 | diarização Nemotron/VAD/ECAPA | 9 |
| R1034 | núcleo CPU multivoz | 31 |
| R1033 | pesquisa anterior | 6 |

Regressão: **223 testes passando**.

## Piloto P0006 — final6

- 25 turnos, 4 personagens, **uma referência clonada por personagem**.
- Perfis: 1 masculino, 3 femininos; 4 adultos (mãe “meia-idade”);
  nenhum criança/idoso neste piloto; esquema suporta as faixas.
- `voice-profiles.json` + `voice-profiles-receipt.json`; registro
  `d49c9ba6…ec90`.
- Emoção/intenção: 25 marcações, 5 ironias; prosódia conservadora.
- O gate ASR antigo dizia **25/25**, mas usava similaridade ≥ 0,45 e
  tolerância de 0,35 s. A reauditoria R1041 encontrou **14 divergências
  lexicais** e **4 overruns**; o piloto está **reprovado para montagem**.
- Causa parcial isolada: ponto final no texto do XTTS gerava “ponto”/omissão.
  A correção remove só o ponto final e registra isso no recibo.
- Telefonema: T018 (ruído) refeita, T017B reescrita, T021 dividida,
  T022 encurtada; cliques de cauda reduzidos por fade 10/30 ms.
- Música: stems Demucs limpos; centroid 1.165,7 → 847,9 Hz; energia
  6–12 kHz 1,20% → 0,318%.
- Render: `render-final6/P0006-ptbr-final-bar.mp4` e `...-soft.mp4`;
  1.861 frames, 48 kHz, −16,5 LUFS, pico −1,43 dBFS.
- Sem lip sync; ASR é proxy; sem aprovação humana/nativa.

## Evidência e diarização

- `integrations.dubbing_batch` preparou **107 partes / 1.943 unidades** em uma
  chamada, com cache por hash e retomada; `dubbed_parts = 0`.
- `integrations.dubbing_evidence` processou **106 partes** (P0006 excluído),
  **1.997 frames**, **0 erros**; o recibo declara
  `source_evidence_collected_not_dubbed`.
- `integrations.video_diarization_nemotron` usa **Nemotron 3 Diarization**
  (não gated, OpenMDW-1.1) em CPU. As **107 partes** foram diarizadas:
  **1.943 unidades**, **1.650 segmentos**, **129 unidades bloqueadas (6,6%)**
  — 69 por cobertura baixa, 43 sem sobreposição e 17 ambíguas; 5 partes sem
  fala detectada; até 5 locutores por parte. Identidade continua hipótese.
- Fallback `SpeechBrain ECAPA` foi instalado, mas não é confiável sozinho em
  falas curtas/sobrepostas.

## Editor universal

- `integrations.video_editor`: projeto/timeline, `trim`, `concat`, `scale`,
  `pad`, `crop`, áudio, legendas, Remotion e plugins; render com recibo,
  retomada e conferência de frames.
- `integrations.video_editor_mcp`: 5 ferramentas; render real exige arquivo
  de aprovação do operador.
- `integrations.video_toolchain`: 46 ferramentas/modelos com licença, papel e
  status; dossiê em `reports/r1043/toolchain.json`.
- Remotion CLI **4.0.540** instalado em `editor-workspace/remotion-smoke`;
  `remotion compositions` listou `Smoke` (50 frames, 25 fps, 1280×720).
  Render/still/bundle seguem exigindo `REMOTION_RENDER_APPROVED=1`.
  Recibo: `reports/r1043/remotion-install-receipt.json`.
- Skill `video-editor-universal` e dossiê `docs/VIDEO_EDITOR_TOOLCHAIN_R1043.md`
  extraem o método dos livros e o catálogo GitHub/Hugging Face.

## Bloqueios

As outras **106 partes não foram dubladas**. A diarização produz hipóteses de
locutor; o agrupamento global parou em **54/107** embeddings e ainda precisa
terminar. A tradução automática das 6 primeiras partes foi **interrompida**
porque o ASR turco pequeno produz frases sem sentido; dublar a partir dele
seria fluência sobre texto errado. Evidência:
`reports/r1045/ASR-QUALITY-BLOCKER.md`.

O TTS **não foi iniciado**. Antes, é preciso escolher e validar uma fonte
textual melhor (OCR das legendas inglesas em vários frames ou ASR maior) e
revisar uma amostra.

O `faster-whisper-large-v3` foi baixado e testado na P0002: texto bem melhor
que o small, 7 segmentos em 113 s (≈1,5× tempo real). O lote das 107 partes
está rodando em tmux (`dub-asr`) e é retomável; estimativa ~3,3 h só de ASR.
Depois dele ainda faltam atualização das unidades, tradução, clustering,
TTS, stems/mix, render e montagem. Nenhuma montagem final ou publicação;
o pedido atual é explicitamente **não publicar**.

O upload ao YouTube também está bloqueado por direitos de distribuição não
verificados e ausência de credenciais OAuth; ver
`reports/r1045/UPLOAD-BLOCKERS.md`.
