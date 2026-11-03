# Piloto P0006 — vozes clonadas, emoção e áudio separado

**Parte:** `02XpQTA-_XE-P0006`, 373,52–447,96 s, 1.861 frames, 74,44 s.
**Fonte:** 107 partes finais em `parts-final/`; verificação independente
`verified: true`. O piloto é um derivado, não uma aprovação.

## Vozes: clone + gênero + idade

| Personagem | Gênero | Faixa | Perfil | Voz |
|---|---|---|---|---|
| `char_male_a` | masculino | adulto jovem | `adult_male_01` | clone Demucs limpo |
| `char_cagla` | feminino | adulto jovem | `adult_female_01` | clone compacto limpo |
| `char_ruya` | feminino | adulto jovem | `adult_female_02` | clone Demucs limpo |
| `char_mother` | feminino | adulto / meia-idade | `adult_female_03` | clone Demucs limpo |

- `voice-profiles.json` + `voice-profiles-receipt.json`: 1 masculino,
  3 femininos, 4 adultos; nenhum criança/idoso identificado neste piloto.
- O esquema suporta `crianca`, `adulto`, `idoso`; um novo personagem exige
  referência própria e revisão. Não se fabrica idade por pitch.
- Uma referência por personagem; 25 turnos.
- **Correção R1041:** a alegação anterior de “25/25 aprovadas” veio de um gate
  permissivo (similaridade ≥ 0,45 e tolerância de 0,35 s). A reauditoria
  encontrou **14 divergências lexicais** e **4 falas acima do limite**. O
  piloto permanece **reprovado para montagem** até correção e escuta.
- O ponto final enviado ao XTTS foi identificado como gatilho de “ponto”,
  omissão e alongamento; ver `reports/r1041/punctuation-finding.md`.
- `registry_sha256 = d49c9ba6…ec90`.

## Emoção, ironia e intenção

`EMOTION-REVIEW.md` marca cada turno com emoção, intensidade, ironia e
evidência. Exemplos:

- T001 “Inacreditável.” — exasperação/ironia, intensidade 4.
- T003B “Aprenda a se divertir…” — ironia/crítica.
- T014 “Por quê? Por quê?” — deboche/ironia.
- T015 “Estou entediada. Vamos.” — tédio.
- T016 “Também cansei de você, amiga.” — deboche/cansaço.
- T017A/B — preocupação/urgência, intensidade 4–5.
- T018/T022 — tranquilização, com tensão/leveza.
- T021A/B — preocupação/apreensão.

A prosódia aplicada é conservadora: tempo 0,94–1,11×, pitch ±2,4%, ganho
±1,6 dB. É uma aproximação de intenção, não emoção certificada.

## Telefonema: correções

- T018 era **ruído**, não fala; refeita com a referência limpa da Çağla,
  ASR 1,00.
- T017B “Horas ligando” era mal pronunciado; reescrito para
  “Chamei várias vezes, quase enlouqueci.”, ASR 0,91.
- T021 dividida em “Sua voz está estranha.” e “Aconteceu algo?”.
- T022 encurtada para “Mãe, nada. A gente se diverte.”, ASR 0,77.
- Fades de 10/30 ms por linha removem cliques de cauda.

## Música e canais

- `stems/music-clean.wav`: Demucs `drums+bass+other` com cortes em
  2,5/6,5/10 kHz, low-pass 15 kHz, denoise, compressão e limiter.
- `render-final6/dialogue-processed.wav`: vozes com EQ, compressor e de-esser.
- `render-final6/mix-48k.wav`: música + diálogo, sidechain ducking.
- Centroid espectral da música: **1.165,7 → 847,9 Hz**; energia 6–12 kHz:
  **1,20% → 0,318%**. Reduz estridência; não prova ausência de artefatos.

## Render final6

- `render-final6/P0006-ptbr-final-bar.mp4`: barra y=540–720 cobre o inglês
  e queima PT-BR.
- `render-final6/P0006-ptbr-final-soft.mp4`: legenda PT-BR `mov_text`;
  inglês queimado visível.
- Ambos: **1.861 frames**, **48 kHz**, **−16,5 LUFS**, pico **−1,43 dBFS**.
- Sem lip sync; nenhuma aprovação humana/nativa.

## Limites

O ASR é proxy, não escuta humana. Nomes turcos ainda variam (“Çağla”/“Sala”,
“Alaz”/“Alas”). A emoção é aproximada por prosódia, não atuação certificada.
As outras 106 partes continuam bloqueadas para TTS até o mapeamento de
personagens; isso evita duas vozes para o mesmo papel.
