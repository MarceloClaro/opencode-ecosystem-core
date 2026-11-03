# Ferramentas e modelos — curadoria R1043

Registro machine-readable: `reports/r1043/toolchain.json`.
Módulo: `integrations/video_toolchain.py`.
Verificado em 2026-11-02 via GitHub API, Hugging Face API e leitura local.
Licença é triagem, não parecer jurídico. **Registro ≠ instalação ≠ execução.**

## Já integrado ou disponível

| Item | Papel | Licença | Estado |
|---|---|---|---|
| FFmpeg | corte, mux, áudio, legenda | LGPL/GPL conforme build | backend `integrations.video_editor` |
| Remotion | composição React/motion | Remotion License (custom) | CLI 4.0.540 instalado; `compositions` verificado; render exige aprovação |
| XTTS v2 | TTS/clonagem | CPML não comercial | usado no piloto; clone local |
| faster-whisper large-v3 | ASR | MIT | usado no piloto |
| Nemotron 3 Diarization | diarização até 8 locutores | OpenMDW-1.1 | instalado no venv `r1044-diarize`; testado no piloto |
| SpeechBrain ECAPA | embedding de locutor | Apache-2.0 | fallback instalado; baixa acurácia em falas curtas/sobrepostas |
| Demucs | stems | MIT | usado no piloto |

Recibo do Remotion: `reports/r1043/remotion-install-receipt.json`. O
`remotion compositions` prova bundle e navegador, não render ou qualidade.

## Candidatos fortes

| Item | Papel | Licença | Observação |
|---|---|---|---|
| OpenTimelineIO | interchange de timeline | Apache-2.0 | exportar/importar EDL/OTIO |
| PySceneDetect | detecção de cortes | BSD-3 | operação de timeline |
| auto-editor | corte por silêncio/movimento | Unlicense | rough cut, não aprovação |
| MoviePy | composição Python | MIT | backend alternativo |
| Motion Canvas | animação por código | MIT | alternativa MIT ao Remotion |
| Editly | edição declarativa | MIT | planos JSON reproduzíveis |
| Chatterbox | TTS/clone | MIT | verificar pt-BR e emoção |
| Kokoro-82M | narração TTS | Apache-2.0 | não clona voz original |
| Wan2.1 VACE | edição/controle de vídeo | Apache-2.0 | GPU alta |
| Wan2.2 T2V | geração de vídeo | Apache-2.0 | GPU alta |
| Mochi 1 | geração de vídeo | Apache-2.0 | GPU alta |
| LatentSync | lip sync | Apache-2.0 + OpenRAIL++ | GPU; revisar pesos |
| SAM 2 | segmentação/tracking | Apache-2.0 | GPU |
| BiRefNet | matting | MIT | GPU opcional |
| SeedVR2 | upscale/restore | Apache-2.0 | GPU |
| Qwen2.5-VL | entendimento de vídeo | Apache-2.0 | GPU |
| Florence-2 | OCR/detecção/caption | MIT | CPU/GPU |

## Referência apenas / bloqueado

| Item | Motivo |
|---|---|
| OpenChatCut | AGPL-3.0; integração exigiria revisão de arquitetura |
| pyvideotrans | GPL-3.0; revisão |
| BaoCut | licença NOASSERTION/ausente |
| Wav2Lip | licença não declarada |
| Hypit | licença custom; instalação explícita |
| HunyuanVideo / LTX-Video / SVD / RMBG | licença custom; revisar termos |
| F5-TTS / Fish Speech / Depth Anything V2 | não comercial |
| Remotion | custom; exige aceite e aprovação de render |

## Escolha por tarefa

- **Diarização**: Nemotron 3 (não gated) > pyannote (gated, exige token) >
  SpeechBrain (fallback). Sempre marcar identidade como hipótese.
- **ASR**: faster-whisper large-v3; testar Whisper turbo/Parakeet no idioma.
- **Voz clonada**: XTTS (não comercial) ou Chatterbox (MIT, validar pt-BR);
  **narração**: Kokoro.
- **Animação**: Remotion (React) ou Motion Canvas (MIT); AnimateDiff/Wan para
  motion generativo.
- **Lip sync**: LatentSync com GPU e licença revisada; Wav2Lip bloqueado.
- **Recorte**: SAM2/BiRefNet; revisar borda, cabelo e oclusão.
- **Restauração/upscale**: SeedVR2; não “melhorar” para falsificar detalhe.
- **Timeline**: OpenTimelineIO para interoperar; FFmpeg para render.
- **Entendimento/seleção**: Qwen2.5-VL/Florence-2; não confundir caption com
  verdade.

## Regras de licença

1. Não integrar licença `unknown`; pedir decisão.
2. AGPL/GPL exigem revisão de arquitetura e aceite explícito.
3. CC-BY-NC só em projeto não monetizado; registrar a restrição.
4. Licença custom (Remotion, Hypit, RMBG, Hunyuan, LTX, SVD) exige aceite
   específico e leitura dos termos atuais.
5. Pesos e código podem ter licenças diferentes; verificar ambos.
6. Direito de uso da mídia, voz, marca e fonte é separado da licença do modelo.

## Limites

- `detect()` verifica o interpretador atual; um módulo pode existir em outro
  venv.
- Download de modelo e execução não são comprovados pelo registro.
- Benchmarks de terceiros não garantem qualidade no seu corpus.
- Modelo generativo não substitui decisão editorial, revisão de direitos ou
  escuta humana.
