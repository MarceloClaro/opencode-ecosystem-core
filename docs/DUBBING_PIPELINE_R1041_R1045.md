# Pipeline de dublagem, editor universal e animação — R1041–R1045

Este documento descreve a infraestrutura criada a partir do piloto P0006 do
episódio `02XpQTA-_XE`. Ele separa **capacidade implementada**, **evidência
coletada** e **entrega aprovada**; nenhuma das três é equivalente.

## Componentes

| Módulo | Função | Estado |
|---|---|---|
| `integrations.video_editor` | projeto/timeline, FFmpeg, Remotion, legendas, áudio, render com recibo | implementado |
| `integrations.video_editor_mcp` | 5 ferramentas MCP; render exige aprovação | implementado |
| `integrations.dubbing_batch` | prepara 107 partes/1.943 unidades, cache e retomada | implementado |
| `integrations.dubbing_evidence` | OCR de evidência por unidade | 106 partes, 1.997 frames |
| `integrations.dubbing_synth` | síntese com cache, hash e limite estrito | implementado |
| `integrations.dubbing_xtts` | XTTS com latentes em cache e lote por parte | implementado; TTS não iniciado |
| `integrations.dubbing_translate_batch` | tradução M2M100 em lote | implementado; 6 partes antigas descartadas |
| `integrations.video_diarization` | VAD Silero + ECAPA fallback | implementado |
| `integrations.video_diarization_nemotron` | diarização local não gated | 107 partes |
| `integrations.video_speaker_cluster` | clusters globais + referências provisórias | parcial 54/107 |
| `integrations.video_toolchain` | catálogo de 46 ferramentas/modelos | implementado |
| `multitrack` | Compositor FFmpeg | camadas, transformação, opacidade, áudio explícito |
| `transition` | xfade/acrossfade | 10 efeitos allowlisted; corte por frames |
| `color_grade` | eq/colorbalance | brilho, contraste, saturação, gamma e balanço RGB |
| `video-editor-universal` | skill de direção, 10 modelos, 16 comandos | disponível |

## Fluxo por parte

1. **Fonte**: ASR/OCR/contexto; a fala real é revisada antes da tradução.
2. **Unidades**: uma unidade por intervalo temporal; IDs estáveis.
3. **Locutor**: diarização + cluster global + referência; identidade é hipótese.
4. **Tradução**: texto PT-BR revisável; máquina não é aprovação.
5. **Voz**: XTTS/alternativa com cache; duração estrita, sem truncar fonema.
6. **Música**: Demucs/stems separados; diálogo e música em pistas distintas.
7. **Mix**: ducking, EQ, de-esser; preservar inteligibilidade.
8. **Legendas**: SRT/VTT por parte e do episódio.
9. **Render**: bar/soft, frames, loudness, recibo e hash.
10. **Montagem**: união somente após todas as partes validadas.

## Estado real do episódio

| Etapa | Resultado |
|---|---|
| Partes extraídas | 107 |
| Evidência OCR | 106 partes; 1.997 frames; 0 erros |
| Diarização | 107 partes; 1.943 unidades; 1.650 segmentos |
| Unidades bloqueadas | 129 (6,6%) |
| ASR large-v3 | concluído; 107 partes, 1.854 segmentos, 7.773 palavras |
| Clustering global | 54/107 embeddings |
| Tradução | 6 partes antigas descartadas por ASR ruim |
| TTS | 0 linhas |
| Mix/render | 0 partes |
| Montagem | não feita |
| Publicação | proibida nesta rodada |

## Gates

- **Fonte**: ASR/OCR é rascunho; não iniciar TTS em texto sem sentido.
- **Locutor**: cluster sem referência/identidade bloqueia; não inventar nome.
- **Duração**: amostras excedentes bloqueiam; sem tolerância editorial.
- **Voz**: uma referência por personagem; troca exige reconciliar todas as falas.
- **Render**: `rendered` não é `approved`; ASR não é escuta.
- **Publicação**: exige direito de distribuição e credenciais; ver
  `reports/r1045/UPLOAD-BLOCKERS.md`.

## Piloto R1026 (R1047)

Além do lote de 107 partes, o piloto R1026 recebeu uma dublagem PT-BR de 20 s
com XTTS local `speed 1.0`, slide traduzido, SRT/ASS e sem cartão. ASR
large-v3: WER lexical 2,17%; loudness −16,10 LUFS; true peak −2,16 dBTP.
O vídeo base tem lip sync anterior; a nova locução **não** foi re-sincronizada.
Ver `reports/r1047/QUANTUM-DUB-EVIDENCE.md`.

## Comandos

```bash
# preparar/retomar o lote
python3 -m integrations.dubbing_batch prepare --root pilots/r1035-02XpQTA-_XE

# evidência OCR
python3 -m integrations.dubbing_evidence --root pilots/r1035-02XpQTA-_XE

# diarização
python3 -m integrations.video_diarization_nemotron --root pilots/r1035-02XpQTA-_XE

# ASR large (modelo local)
python3 -m integrations.dubbing_asr_batch \
  --root pilots/r1035-02XpQTA-_XE \
  --model-dir ~/.cache/opencode-pilot/models/faster-whisper-large-v3

# tradução
python3 -m integrations.dubbing_translate_batch \
  --root pilots/r1035-02XpQTA-_XE \
  --model-dir ~/.cache/opencode-pilot/models/m2m100-418m

# TTS (depois de clustering/revisão)
python3 -m integrations.dubbing_xtts \
  --root pilots/r1035-02XpQTA-_XE \
  --snapshot ~/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/345b56f6fbe25cca7103f7f34e471b8fe8e4945f
```

## Limites

- 1.943 unidades e 107 partes não foram revisadas por falante nativo.
- A diarização identifica clusters, não nomes; a similaridade não é biometria.
- large-v3 melhora o turco, mas ainda erra nomes/expressões.
- XTTS é CPML não comercial; verificar licença antes de monetizar.
- Demucs é estimativa; vazamento de música/voz pode ocorrer.
- Nenhum MP4 final, montagem ou upload foi produzido nesta rodada.
