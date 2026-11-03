# Dublagem PT-BR R1047 — piloto R1026

Gerado em 2026-11-03T23:36:41Z com XTTS local, sem serviço externo e sem publicação.

## Fonte e voz

| Item | Valor |
|---|---|
| Vídeo base | `/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/presenter-middle-r1047-1080.mp4` |
| SHA-256 do vídeo base | `3711ef75f7b32c56983af84803b22acb1dc7cdfef7eb4b843634a23377b7e674` |
| Cartão | **ausente** (`presenter_card_present=false`) |
| Referência de voz | `/home/marceloclaro/.cache/opencode-pilot/refs/presenter-ref.wav` |
| SHA-256 da referência | `3149691d6094caca9cf1ca3516172a5c91a7d5513cf80cf16f3fb4f2d8ed8ae0` |
| Modelo | `tts_models/multilingual/multi-dataset/xtts_v2` |
| Licença | Coqui Public Model License (CPML), uso não comercial |
| Consentimento | operador declarou consentimento escrito; não verificado pelo Core |
| Velocidade XTTS | 1.0 |

## Roteiro e tempos

| # | Fala | Início | Fim da fala | Duração |
|---|---|---:|---:|---:|
| 1 | A IBM ampliou o acesso a processadores quânticos com mais de cem qubits. | 0.25 s | 5.19 s | 4.94 s |
| 2 | Os processadores menores saíram de linha para abrir espaço aos maiores. | 5.37 s | 9.47 s | 4.10 s |
| 3 | A razão é prática: alguns tamanhos ainda são simuláveis em computadores clássicos. | 9.65 s | 14.86 s | 5.21 s |
| 4 | Os maiores permitem atacar problemas que a simulação não alcança. | 15.04 s | 19.49 s | 4.45 s |

Fator de tempo aplicado: **1.059126×** (1,0 = sem aceleração).

## Áudio e legenda

- Áudio: `/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/r1047-dub/out/dub-r1047.pt-BR.wav`, 20.00 s, 48 kHz estéreo.
- Loudness medido: `input_i=-16.08` LUFS, `input_tp=-2.16` dBTP.
- SRT: `/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/r1047-dub/out/captions-r1047.pt-BR.srt` (SHA-256 `adbffbfa50111dd785d65ad238661d63c24ba47080b6343097982ccbc2e2d58f`).
- ASS: `/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/r1047-dub/out/captions-r1047.pt-BR.ass` (SHA-256 `de7a8b0752d40b4e312e124c5d73ea797da972f1a5cec27cfdbfe6fbf9204df5`).
- CPS máximo: **16.77**.

## Vídeo final

| Item | Valor |
|---|---|
| Arquivo | `/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/r1047-dub/out/quantum-ptbr-r1047.mp4` |
| SHA-256 | `93f074a3e258f12371b34540a0a8b574a1b47f7bba6c140da774e5f8289f3ed5` |
| Tamanho | 3852259 bytes |
| Vídeo | h264 1920×1080, 30/1 fps |
| Áudio | aac 48000 Hz, 2 canais |
| Duração | 20.000000 s |

## Alegações e limites

| Alegação | Valor |
|---|---|
| `voice_clone_generated` | `true` |
| `subtitle_generated` | `true` |
| `slide_translated` | `true` |
| `presenter_card_present` | `false` |
| `lip_sync_resynchronized` | `true` |
| `audiovisual_approved` | `false` |
| `translation_human_reviewed` | `false` |
| `scientific_validity_verified` | `false` |
| `published` | `false` |

Limitações registradas:

- A voz é sintética e pode conter artefatos; revisão auditiva humana pendente.
- Lip sync refeito com Wav2Lip nesta rodada; revisão visual humana pendente.
- A tradução do slide e da fala é interpretativa; revisão bilíngue humana pendente.
- Testes técnicos não aprovam estética, naturalidade, emoção ou validade científica.
- Uso não comercial; XTTS/CPML e consentimento declarado, não verificado.

## Verificação ASR

- Modelo: faster-whisper large-v3, CPU/int8.
- Idioma detectado: `pt` (probabilidade 1).
- WER lexical contra o roteiro: **2.17%**.
- Hipótese: “A IBM ampliou o acesso a processadores quânticos com mais de 100 qubits. Os processadores menores saíram de linha para abrir espaço aos maiores. A razão é prática. Alguns tamanhos ainda são simuláveis em computadores clássicos. Os maiores permitem atacar problemas que a simulação não alcança.”
- ASR é triagem lexical; não prova naturalidade, emoção ou identidade.

## Reprodução

```bash
cd pilots/r1026-quantum/r1047-dub
~/.cache/opencode-pilot/venvs/xtts/bin/python build_dub.py
```

O script não sobrescreve o original, não publica e mantém as flags de
aprovação humana em `false`.
