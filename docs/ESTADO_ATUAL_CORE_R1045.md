# Estado atual do Core — R1045 (03/11/2026)

Retrato local, não certificação. Contagens derivam de `opencode.json` e do
diagnóstico; testes verdes não provam qualidade editorial, científica ou
disponibilidade de provedores.

## Superfície

| Item | Valor |
|---|---:|
| Agentes em `opencode.json` | 333 |
| Servidores MCP (diretos + `mcp.servers`) | 29 |
| Comandos | 35 |
| Skills em `.opencode/skills` | 41 |
| Checks do `doctor` | 22/22 |
| Testes R1033–R1045 + instalador | **245** |
| Testes R1033–R1046 + instalador | **303** + 1 opcional (render real R1026; 58 novos) |
| Specs formais | 291 |

O `doctor` está **healthy** em modo estrutural; isso não autentica CLIs,
modelos ou serviços externos.

## Entregas R1035–R1047

- **Editor universal** (`video_editor`, `video_editor_mcp`): timeline,
  FFmpeg, Remotion, legendas, áudio, render com recibo e retomada.
- **Composição avançada R1046** (`video_editor_advanced`): multifaixa,
  transições e cor SDR paramétrica, com hash de fontes e recibo técnico separado
  de aprovação audiovisual/tradução/ciência.
- **Dublagem R1047** (`pilots/r1026-quantum/r1047-dub`): XTTS local `speed 1.0`,
  4 blocos PT-BR, slide traduzido, SRT/ASS, sem cartão; WER ASR 2,17% e
  −16,10 LUFS. Lip sync anterior não re-sincronizado; revisão humana pendente.
- **Dublagem** (`dubbing_batch`, `dubbing_evidence`, `dubbing_synth`,
  `dubbing_xtts`): preparação, OCR, cache e TTS por linha.
- **Diarização** (`video_diarization`, `video_diarization_nemotron`): Silero
  VAD, ECAPA fallback e Nemotron 3 (não gated).
- **Clusters/referências** (`video_speaker_cluster`): agrupamento global e
  referências provisórias; parcial.
- **Catálogo** (`video_toolchain`): 46 ferramentas/modelos GitHub/Hugging Face.
- **Skills** (`video-editor-universal`): 10 modelos, 16 comandos e método dos
  livros de Tiago Lemos, com atribuição.
- **Instalador one-click** (`install.sh`, `installer/oneclick/`): check e apply
  seguro; manuais para apt/curl-pipe.

## Estado do episódio 02XpQTA-_XE

| Etapa | Resultado |
|---|---|
| Partes | 107 |
| Evidência OCR | 106 partes; 1.997 frames; 0 erros |
| Diarização | 107 partes; 1.943 unidades; 1.650 segmentos |
| Unidades bloqueadas | 129 (6,6%) |
| Embeddings de locutor | 54/107 |
| ASR large-v3 | 107 partes; 1.854 segmentos; 7.773 palavras; aguarda revisão |
| Tradução | 6 partes antigas descartadas |
| TTS | 0 |
| Mix/render | 0 |
| Montagem | não feita |
| Publicação | não feita |

O piloto P0006 continua **reprovado para montagem**; ver
`pilots/r1035-02XpQTA-_XE/STATUS.md`.

## Bloqueios

1. **Fonte textual**: `faster-whisper-small` gerou turco sem sentido em parte
   do corpus. Large-v3 melhora, mas ainda exige revisão; TTS não foi iniciado.
2. **Locutores**: clusters são hipóteses; identidade e referência precisam de
   revisão. Unidades ambíguas bloqueiam.
3. **Duração**: TTS deve caber no slot sem truncar fonema; o gate antigo
   tolerava 0,35 s e foi retirado.
4. **Publicação**: direito de distribuição não verificado e sem credenciais
   OAuth. Nada foi publicado.
5. **Remotion**: CLI instalado e `compositions` verificado; render não foi
   executado nem aprovado.
6. **Multifaixa/transições/cor (R1046)**: implementados e testados em CPU com
   FFmpeg; conformidade de fps, presets e raio de canto; não há UI NLE, LUT/HDR,
   keyframes, multicam ou aprovação perceptual. Render técnico não valida
   tradução nem validade científica. Aceite real em R1026: 600 frames,
   30000/1001, áudio 48 kHz; ver `reports/r1046/QUANTUM-REAL-EVIDENCE.md`.

## Como reproduzir o diagnóstico

```bash
.venv/bin/python -m marceloclaro.cli doctor
./install.sh --check
python3 -m pytest -q tests/test_r1041_* tests/test_r1042_* \
  tests/test_r1043_* tests/test_r1044_* tests/test_r1045_*
```

## Documentos relacionados

- [Pipeline de dublagem](DUBBING_PIPELINE_R1041_R1045.md)
- [Editor universal](EDITOR_VIDEO_UNIVERSAL_R1042.md)
- [Catálogo de ferramentas](VIDEO_EDITOR_TOOLCHAIN_R1043.md)
- [Instalador one-click](../installer/ONECLICK.md)
- [Bloqueios de upload](../reports/r1045/UPLOAD-BLOCKERS.md)
- [Qualidade de ASR](../reports/r1045/ASR-QUALITY-BLOCKER.md)
