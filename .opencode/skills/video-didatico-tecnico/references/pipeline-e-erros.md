# Pipeline e erros

## Pipeline

1. **ASR**: faster-whisper local; `small` em CPU; WAV 16 kHz mono.
2. **Tradução**: revisão humana; legenda condensada, não verbatim.
3. **Voz**: Piper (MIT) ou XTTS v2 (CPML, não comercial) com referência e
   consentimento.
4. **Lip sync**: Wav2Lip em blocos, ou MuseTalk/LatentSync em GPU.
5. **Slides**: Remotion `SlideSequence`; 3 cenas; transições no silêncio.
6. **Legendas**: ASS com CPS e destaque de palavras-chave.
7. **Composição**: máscara do slide; preservar a apresentadora.
8. **Concatenação**: filtro `concat`, `apad/atrim`, `setsar=1`.
9. **QC**: ffprobe, loudness, frames, escuta humana.

## Receita CPU-safe

- 640×360 para detecção facial; 960×540 estourou 7,1 GB.
- Blocos de 5 s; 2 threads; `nice`/`ionice`.
- Watchdog de 4,5 GB; lock; retomada por `done-N`.
- Sobrepor só o rosto ao original 1080p com máscara elíptica.
- Pico observado: 3,48 GB.

## Apresentadora falando nos cartões

Para a apresentadora **dublar** a abertura/encerramento:

1. Separe o áudio da narração e a duração do cartão.
2. Rode o Wav2Lip em blocos de 5 s, 640×360, com watchdog e retomada.
3. Componha a boca sincronizada sobre o vídeo 1080p, só na região do rosto.
4. Recorte em cabeça e ombros (560×700) para excluir mãos/frestas claras.
5. Calcule a matte por frame com `V*(1-S)`: fundo claro → alfa 0; cabelo/pele/blusa
   → alfa alto.
6. Componha sobre o gradiente do cartão e aplique fade inferior.
7. No Remotion, use `<Video muted>` e mantenha o `<Audio>` separado.
8. Verifique boca/frames em vários instantes; o MP4 não prova sincronia.

## Erros observados

| Erro | Causa | Correção |
|---|---|---|
| Wav2Lip travou | 1080p/960p e dois processos | 640×360, um processo, watchdog |
| Slide trocado no fim | demuxer `concat` com durações diferentes | filtro `concat` + `apad/atrim` |
| 9:16 falhou | SAR 10240:10239 vs 1:1 | `setsar=1` |
| Slide 1 px menor | Remotion arredonda para par | `scale=935:864` |
| Narração não citava item 3 | roteiro incompleto | frase adicional e atraso da linha |
| Frase de 6 palavras com 6 s | ritmo do XTTS | encurtar texto ou aceitar pausa |
| Halo branco no cartão | matte binária no cabelo | matte suave `V*(1-S)` + fade |
| Manchas brancas nas mãos | recorte incluía frestas da base | fechar em cabeça/ombros 560×700 |
| Congelamento a cada 5 s | blocos Wav2Lip com 146 frames/5 s | passada contínua + `tpad` |
| “M” branco ao lado do ombro | fundo claro na borda esquerda | máscara de borda + decontaminação |
| Miolo antigo no cenário novo | concatenação com base antiga | novo miolo escuro (`didactic-middle`) |

## Registro

Cada correção deve virar uma descoberta com evidência, impacto e decisão. Não
registre “funcionou” sem dizer em qual resolução, com qual licença e com qual
verificação.
