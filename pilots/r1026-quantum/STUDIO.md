# Estúdio técnico de vídeo e animação — arquitetura

## Princípio

Separar **direção**, **edição**, **motion graphics**, **áudio**, **legenda** e
**QC**. Cada etapa produz um artefato verificável; nenhuma etapa "faz tudo" num
único comando opaco. O estudo técnico exige reprodutibilidade, não apenas um
MP4 bonito.

## Pipeline

| Etapa | Ferramenta | Saída | Verificação |
|---|---|---|---|
| 1. Ingestão | FFmpeg/ffprobe | `source.mp4`, hash | duração, codec, resolução, direitos |
| 2. Transcrição | faster-whisper | `transcript-en.json` | idioma, segmentos, palavras |
| 3. Tradução/legenda | revisão + ASS/SRT | `captions.pt-BR.srt` | CPS, 2 linhas, safe area |
| 4. Voz | Piper ou XTTS v2 | `dub-pt-BR.wav` | loudness, timing, consentimento |
| 5. Lip sync | Wav2Lip CPU/GPU ou MuseTalk | `lipsync-540.mp4` | inspeção visual, chunks |
| 6. Master | FFmpeg | `master-16x9.mp4` | ffprobe, loudness |
| 7. Motion | Remotion (overlay alfa) | `overlay.webm` | prévia, frame, alpha |
| 8. Composição | FFmpeg | `final-16x9.mp4` | overlay, legendas, áudio |
| 9. Variantes | FFmpeg | 16:9, 9:16, 1:1 | matriz de render |
| 10. QC | R1024/R1025 + olho/ouvido | relatório | metadados + revisão humana |

## Motion graphics com Remotion

Para qualidade profissional, renderize o motion em **camada separada**:

1. composição Remotion 1920×1080, fundo transparente, 20 s;
2. lower-third animado com `spring`, barra de progresso e tipografia em duas
   hierarquias;
3. render com alfa (`vp9` + `yuva420p` ou ProRes 4444);
4. composição no FFmpeg com `overlay`, preservando o master e as legendas.

Vantagens: o motion pode ser reutilizado em 16:9, 9:16 e 1:1; a legenda não é
queimada duas vezes; o master continua editável. O plugin `remotion-guard`
continua exigindo aprovação explícita para render.

## Receita CPU-safe

O Wav2Lip em 1080p travou porque a detecção facial em resolução cheia consome
CPU e memória. A receita estável é:

- reduzir a fonte para **960×540** (ou 640×360 em máquinas menores);
- processar em **blocos de 5 s**, com retomada por marcador `done-N`;
- limitar a **2 threads** (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS`, `NUMBA_NUM_THREADS`, `WAV2LIP_THREADS`);
- `nice -n 19` e `ionice -c3` para não competir com o desktop;
- watchdog de RSS: abortar acima de **6 GB**;
- lock com `flock`: nunca rodar duas instâncias;
- timeout por bloco (30 min) e log por bloco;
- recompor o 1080p só no final, com Lanczos.

Script: `render-lipsync-cpu.sh`. Ele recusa rodar se já houver instância ativa e
retoma blocos concluídos.

## Padrões de entrega

- 1080p, 30 fps, H.264 High, `yuv420p`, `+faststart`.
- Áudio AAC 192 kbps, 48 kHz, estéreo.
- Loudness **−16 LUFS**, true peak **−1,5 dBTP**.
- Legenda: até 2 linhas, ≤17 CPS, margem segura de 5–10%.
- 16:9, 9:16 e 1:1 com o mesmo master e a mesma trilha.
- Nome: `projeto-variante-versao.mp4`; manifesto com SHA-256 e `ffprobe`.

## Licenças

| Componente | Licença | Uso |
|---|---|---|
| FFmpeg | LGPL-2.1+ (GPL opcional) | edição/encode |
| Remotion | Remotion License | pessoa física/ONG/≤3 funcionários; acima, licença comercial |
| Piper | MIT | TTS genérico |
| XTTS v2 | CPML | não comercial |
| Wav2Lip | não comercial | estudo/pesquisa |
| MuseTalk | MIT (código/pesos) | GPU; testdata não comercial |
| LatentSync | Apache-2.0 | GPU; conferir pesos |
| OpenTimelineIO | Apache-2.0 | intercâmbio de timeline |

## Quando usar GPU

Lip sync em CPU é viável apenas em baixa resolução e blocos. Para 1080p com
qualidade e tempo previsível, use GPU NVIDIA:

- Wav2Lip com CUDA;
- MuseTalk (MIT) para 30 fps;
- LatentSync para difusão.

O script `render-lipsync-gpu.sh` recusa rodar sem `nvidia-smi`.

## Limites

- Metadados, frames e níveis de áudio provam presença e formato. Não provam
  sincronia labial, inteligibilidade, naturalidade da voz ou qualidade editorial.
  Esses pontos exigem reprodução com áudio, escuta e revisão humana.
- Wav2Lip não é um dublador profissional; a boca pode tremer e a qualidade cai
  em perfis/ângulos difíceis.
- Voz clonada exige consentimento e identificação como sintética.
- Nada aqui substitui direitos de imagem/voz e licença da obra.

## Skill operacional

O fluxo está especializado em `.opencode/skills/video-didatico-tecnico/`, com
princípios didáticos, efeitos, pipeline, erros observados e registro de
descobertas.
