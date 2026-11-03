---
spec_id: SPEC-935-R1042
title: Núcleo de editor de vídeo universal, local e auditável
component: integrations.video_editor
status: specified
test_file: tests/test_r1042_video_editor.py
depends_on:
  - SPEC-935-R1024
  - SPEC-935-R1041
---

# SPEC-935-R1042

## Objetivo

Generalizar o trabalho do piloto para **qualquer vídeo**: ingerir, descrever,
planejar operações de timeline, pré-visualizar, renderizar em lote, retomar e
auditar. Dublagem, tradução, legendas, separação de stems e QA entram como
operações/plug-ins, não como caminhos fixos de um episódio.

## Modelo

- `Project`: fontes com SHA-256 e probe; timeline com taxa racional, resolução,
  sample rate; faixas `video`, `audio`, `subtitle`; clipes com `in_frame`,
  `out_frame`, `start_frame`, `source`, `speed` e volume.
- Frames são a unidade de corte. `25/1`, `30000/1001` e VFR são representados;
  VFR nunca é tratado como CFR silenciosamente.
- Um clipe pertence a uma faixa; sobreposição na mesma faixa é inválida.
  Lacunas são permitidas e preenchidas explicitamente (preto/silêncio) quando
  a operação exigir.
- Operações são plugins com `validate(params)` e `plan(project, params)`.
  Nenhum plano executa FFmpeg; `render` é etapa separada.
- Todo plano declara insumos, args, saída esperada, frames/duração, avisos e
  limitações. `{output}` é o único placeholder de saída.

## Operações mínimas

`probe`, `trim`, `concat`, `scale`, `pad`, `crop`, `extract_audio`,
`replace_audio`, `mix_audio`, `subtitles` (burn/soft), `export`.
`dub` só existe quando um adaptador de dublagem é registrado; sem adaptador,
bloqueia em vez de inventar voz.

## Backends e “outros”

- **FFmpeg** é o backend padrão para corte, concatenação, escala, crop/pad,
  áudio, mux e legendas.
- **Remotion** é o backend para composições React/Remotion: overlays, motion
  graphics, legendas animadas, cartões e cenas programáticas. O plano exige
  `project_path`, `composition_id`, `entry_point`, `props`, `license_ack` e
  `render_approved`; usa `npx --no-install` e a política do
  `remotion_guard`. A licença Remotion não é OSI e o render é decisão humana.
- Outros motores entram como plugins/adaptadores explícitos: Demucs (stems),
  XTTS (voz), faster-whisper (ASR), Tesseract (OCR), Rubberband (tempo/pitch),
  Qiskit/Remotion etc. Nenhum é importado ou instalado implicitamente; ausência
  do plugin bloqueia a operação.
- Um plano declara `backend`; `render` só executa backend conhecido e
  autorizado. FFmpeg e Remotion compartilham o mesmo gate de saída, recibo,
  retomada e conferência de frames.

## Invariantes

1. Nada sobrescreve saída existente. Retomada só reutiliza saída cujo recibo e
   SHA-256 conferem; recibo adulterado bloqueia.
2. Render usa arquivo temporário, confere frames/duração/canais/sample rate e
   só então promove atomicamente. Falha preserva o anterior.
3. Nenhum upload, download, shell arbitrário ou execução de hooks de terceiros.
   Caminhos de legenda/insumo são confinados ao projeto; symlink bloqueia.
4. Dimensões de vídeo são pares; conversão explícita. Crop/scale/pad não
   inventam enquadramento: registram parâmetros e limitações.
5. Legendas queimadas exigem arquivo local e escape; legenda soft não altera
   o vídeo. Nenhuma legenda é declarada sincronizada sem QA temporal.
6. `rendered` significa que o arquivo passou pelo gate técnico, **não** que
   conteúdo, voz, emoção, lip sync ou qualidade editorial foram aprovados.
7. O projeto é serializável em JSON com schema, hashes das fontes e versão do
   planejador. Projeto sem hash de fonte não é renderizável em modo estrito.
8. Operações desconhecidas ou plugin ausente bloqueiam; não há fallback mudo.

## Aceites testáveis

- Racional reduzido; VFR sinalizado; rotação troca dimensões; sem vídeo bloqueia.
- Timeline: sobreposição, clipe fora da fonte, faixa inválida e ID duplicado
  bloqueiam; lacuna permitida é explícita.
- `trim` e `concat` preservam contagem de frames esperada; `scale/pad/crop`
  recusam dimensão ímpar; `subtitles` recusa caminho externo e aspas.
- `render --dry-run` não executa; render real com runner falso grava recibo;
  segunda chamada reutiliza; saída/recibo adulterado bloqueia; saída existente
  sem recibo não é sobrescrita.
- `dub` sem adaptador bloqueia com motivo; com adaptador registrado, apenas
  planeja e delega, sem sintetizar no núcleo.
- `remotion` sem `license_ack`/`render_approved` bloqueia; com ambos, planeja
  e renderiza via runner injetado, grava recibo `backend=remotion` e não
  declara qualidade visual. Composição ausente no scan bloqueia.
- Backend desconhecido bloqueia; plugin ausente não cai para FFmpeg.
- Regressões R1024/R1035/R1041 continuam verdes.

## Limites

O núcleo não prova compatibilidade com todos os codecs/containers; operações
não implementadas devem ser recusadas. Qualidade perceptual, sincronia labial,
direitos e revisão humana permanecem externos. CPU é o alvo padrão; GPU não é
presumida.
