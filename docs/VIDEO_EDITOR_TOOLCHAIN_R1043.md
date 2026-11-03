# Ferramentas, modelos e skills para o editor universal — R1043

Data da curadoria: 2026-11-02. Fontes: livros e skills locais em
`biblioteca ai/`, `.claude/skills/`, GitHub API e Hugging Face API.
Nada foi clonado, instalado ou executado sem autorização; o que foi instalado
está marcado. Licença é triagem, não parecer jurídico.

## O que foi extraído dos livros

Os dois livros de Tiago Lemos de Abreu Oliveira (2026) autorizam copiar e
adaptar comandos, modelos e fichas para os próprios projetos:

- **Caixa Preta IA** — 7 skills, 10 modelos, 16 comandos e 4 fichas.
  Capítulos 10–11 (modelos), 12 (comandos), 13 (fichas), 14 (ciclo).
- **Máquina de Edição IA** — custos, tokens, amostra de 8 s, revisão localizada
  e exportação. Capítulos 3–5, 15–16.

As 10 skills `cp-*`/`meia-*` já estão em `.claude/skills` e foram inventariadas
com SHA-256 em
`.opencode/skills/video-editor-universal/references/claude-skills-manifest.json`.
A skill `video-editor-universal` transforma o método em fluxo operacional:
ficha → mapa de cenas → modelo → amostra de 8 s → aprovação → lote → revisão
localizada → exportação.

## GitHub — shortlist

Sinais de estrelas/licença foram lidos na API em 2026-11-02; não são benchmark.

| Repositório | Estrelas | Licença | Papel | Decisão |
|---|---:|---|---|---|
| `OpenCut-app/OpenCut` | 97.176 | MIT | editor completo tipo CapCut | referência de UX/timeline |
| `remotion-dev/remotion` | 70.110 | Remotion License | composição React | integrado com gate |
| `Zulko/moviepy` | 15.077 | MIT | composição Python | candidato |
| `motion-canvas/motion-canvas` | 19.657 | MIT | animação por código | candidato |
| `Huanshere/VideoLingo` | 19.045 | Apache-2.0 | dublagem/legenda | referência |
| `krillinai/OpenCreator` | 14.098 | Apache-2.0 | localização/dublagem | referência |
| `Vincentwei1021/video-shotcraft` | 16.180 | Apache-2.0 | receitas Remotion | referência |
| `kajisho5/ffmpeg-skill` | 4.382 | MIT | 42 ferramentas FFmpeg + MCP | referência para ampliar operações |
| `Breakthrough/PySceneDetect` | 5.321 | BSD-3 | detecção de cortes | candidato |
| `WyattBlue/auto-editor` | 5.721 | Unlicense | corte por silêncio/movimento | candidato |
| `AcademySoftwareFoundation/OpenTimelineIO` | 2.053 | Apache-2.0 | interchange de timeline | candidato |
| `mifi/editly` | 5.577 | MIT | edição declarativa | candidato |
| `bytedance/LatentSync` | 6.236 | Apache-2.0 + OpenRAIL++ | lip sync | candidato GPU |
| `0xsline/OpenChatCut` | 2.861 | AGPL-3.0 | editor conversacional | bloqueado para integração |
| `jianchang512/pyvideotrans` | 19.624 | GPL-3.0 | tradução/dublagem | bloqueado para integração |
| `Rudrabha/Wav2Lip` | 13.263 | não declarada | lip sync | bloqueado |
| `JimLiu/baocut` | 1.652 | NOASSERTION | agente com timeline | bloqueado |
| `hypit-ai/hypit` | 27.564 | Hypit License | workflow de referência | referência, instalação explícita |

## Hugging Face — shortlist

Downloads/likes são sinais de uso, não prova de qualidade.

| Modelo | Downloads | Licença | Papel | Decisão |
|---|---:|---|---|---|
| `hexgrad/Kokoro-82M` | 11.366.340 | Apache-2.0 | TTS narração | candidato |
| `coqui/XTTS-v2` | 5.965.681 | CPML não comercial | TTS/clone | já usado; restrição |
| `openai/whisper-large-v3-turbo` | 5.664.908 | MIT | ASR | candidato |
| `Qwen/Qwen2.5-VL-7B-Instruct` | 5.886.476 | Apache-2.0 | entendimento de vídeo | candidato GPU |
| `pyannote/speaker-diarization-3.1` | 6.918.404 | MIT, gated | diarização | requer token/aceite |
| `Systran/faster-whisper-large-v3` | 1.474.487 | MIT | ASR | já usado |
| `ResembleAI/chatterbox` | 2.203.606 | MIT | TTS/clone | candidato |
| `ByteDance/LatentSync` | 0 | OpenRAIL++ | lip sync | candidato GPU |
| `nvidia/Nemotron-3-Diarization` | 159.900 | OpenMDW-1.1 | diarização até 8 vozes | **instalado/testado** |
| `Wan-AI/Wan2.1-VACE-14B` | 116.242 | Apache-2.0 | edição/controle de vídeo | candidato GPU |
| `Wan-AI/Wan2.2-T2V-A14B` | 3.507 | Apache-2.0 | geração de vídeo | candidato GPU |
| `Lightricks/LTX-Video` | 1.123.672 | custom | geração de vídeo | revisar termos |
| `tencent/HunyuanVideo` | 20.235 | custom | geração de vídeo | revisar termos |
| `genmo/mochi-1-preview` | 3.585 | Apache-2.0 | geração de vídeo | candidato GPU |
| `facebook/sam2-hiera-large` | 13.850 | Apache-2.0 | segmentação/tracking | candidato GPU |
| `ZhengPeng7/BiRefNet` | 828.665 | MIT | matting | candidato |
| `microsoft/Florence-2-large` | 393.250 | MIT | OCR/detecção | candidato |
| `ByteDance-Seed/SeedVR2-7B` | 46.135 | Apache-2.0 | upscale/restore | candidato GPU |
| `briaai/RMBG-2.0` | 395.542 | custom/gated | remoção de fundo | revisar termos |
| `depth-anything/Depth-Anything-V2-Large` | 105.953 | CC-BY-NC-4.0 | profundidade | não comercial |

## O que foi instalado

Ambiente isolado: `~/.cache/opencode-pilot/venvs/r1044-diarize`.

- `torch 2.15.0+cpu`, `torchaudio 2.11.1+cpu`;
- `speechbrain 1.1.2` + `silero-vad 6.2.3` (fallback de embedding/VAD);
- `transformers 5.22.1` + `accelerate`;
- `librosa`, `scikit-learn`, `soundfile`;
- modelo `nvidia/Nemotron-3-Diarization` (não gated; uso comercial permitido
  pelo card, sujeito aos termos OpenMDW-1.1);
- **Remotion CLI 4.0.540** em `editor-workspace/remotion-smoke`, com 244
  pacotes, `--ignore-scripts`, aceite de host em
  `~/.config/opencode/remotion-license-ack.json`.

O Remotion foi verificado com `remotion --version` e
`remotion compositions src/index.ts`: bundle e navegador iniciaram e a
composição `Smoke` (50 frames, 25 fps, 1280×720) foi listada. Render, still,
bundle e qualidade visual **não** foram verificados. Recibo:
`reports/r1043/remotion-install-receipt.json`.

Teste real no piloto P0006: 4 locutores detectados; inferência ~4,8 s para
74 s de áudio em CPU. A separação é uma hipótese: o piloto tem fala
sobreposta e identidades rotuladas por inferência. Não usar o índice do
locutor como nome ou gênero.

## O que ainda não foi instalado

OpenTimelineIO, MoviePy, PySceneDetect, auto-editor, Motion Canvas,
Chatterbox/Kokoro e modelos generativos de vídeo. O backend Remotion existe e
o CLI foi instalado; render continua exigindo aprovação separada.

## Decisões de arquitetura

1. **FFmpeg** é o backend padrão; **Remotion** é backend de composição com
   licença e aprovação; outros entram por `register_backend`.
2. **Nemotron 3** é a diarização principal por ser não gated e permitir uso
   comercial; pyannote fica como alternativa se houver token/aceite.
3. **SpeechBrain ECAPA** fica como fallback, mas não foi confiável em falas
   curtas/sobrepostas do piloto; não usar sozinho para atribuir personagens.
4. **XTTS** continua no piloto, com CPML não comercial; Chatterbox/Kokoro são
   candidatos para reduzir restrição/licença, após teste no corpus.
5. **AGPL/GPL/unknown** não entram no núcleo sem revisão; ficam como
   referência.
6. Diarização, ASR, tradução e emoção produzem **hipóteses**. Aprovação
   continua humana e separada do gate técnico.

## Próximos passos

- As 107 partes já foram diarizadas: 1.943 unidades, 129 bloqueadas (6,6%),
  1.650 segmentos e até 5 locutores por parte. Agrupar locutores globais por
  embedding.
- Extrair referências provisórias dos clusters; não renomear como personagem
  sem revisão.
- Traduzir e sintetizar apenas unidades com locutor e texto revisados.
- Comparar XTTS/Chatterbox/Kokoro em pt-BR antes de trocar o motor.
- Adicionar OpenTimelineIO/PySceneDetect/auto-editor como operações, se
  aprovados.
