# Diarização local — R1044

## O que foi instalado

Ambiente isolado `~/.cache/opencode-pilot/venvs/r1044-diarize`:

- `torch 2.15.0+cpu`, `torchaudio 2.11.1+cpu`;
- `transformers 5.22.1`, `accelerate`, `librosa`;
- `speechbrain 1.1.2`, `silero-vad 6.2.3`;
- `scikit-learn`, `soundfile`.

Modelo principal: `nvidia/Nemotron-3-Diarization` (OpenMDW-1.1, não gated,
até 8 locutores). Fallback: `speechbrain/spkrec-ecapa-voxceleb` (Apache-2.0).

## Teste no piloto P0006

- Áudio: `stems/vocals.wav`, 74,54 s.
- Inferência: ~4,8 s em CPU, depois de carregar o modelo.
- Saída: 4 locutores e 21 segmentos (`pilot-nemotron.json`).
- O piloto tem fala sobreposta e rótulos de personagem inferidos; **não** foi
  possível validar identidade por escuta nesta rodada.
- ECAPA sozinho mostrou baixa separação em falas curtas/sobrepostas; não é
  suficiente para nomear personagens.

## Como interpretar

Os índices `Speaker 0..7` são **locais à parte** e ordenados pela primeira
aparição. Eles não são `char_cagla`, `char_mother` ou qualquer nome. A
atribuição a personagens exige:

1. agrupar locutores entre partes por embedding;
2. comparar com referências originais;
3. revisar humano/escuta;
4. registrar referência e hash por personagem.

## Resultado das 107 partes

- 107 partes diarizadas; **1.943 unidades ASR**.
- **1.650 segmentos** de locutor; até **5 locutores** por parte.
- **129 unidades bloqueadas (6,6%)**: 69 por cobertura baixa, 43 sem
  sobreposição e 17 ambíguas.
- **5 partes sem fala detectada** (não é prova de ausência de fala; o VAD pode
  falhar em música/sussurro).
- Resumo legível por máquina: `diarization-summary.json`.
- Nenhuma identidade foi atribuída; os índices são locais à parte.

## Comando

```bash
/home/marceloclaro/.cache/opencode-pilot/venvs/r1044-diarize/bin/python \
  -m integrations.video_diarization_nemotron \
  --root pilots/r1035-02XpQTA-_XE
```

Saída em `pilots/r1035-02XpQTA-_XE/.dubbing-diarization/{part_id}.json`.
Cada unidade ASR recebe `speaker`, `coverage`, `margin`, `blocked` e
`verified: false`. Cobertura baixa ou margem pequena bloqueiam o TTS.

## Limites

- Não é reconhecimento biométrico nem prova de identidade.
- Sobreposição de fala pode fundir ou trocar locutores.
- Música/ruído e trechos curtos reduzem a confiança.
- O resultado precisa de revisão; `blocked` não é falha a esconder.
