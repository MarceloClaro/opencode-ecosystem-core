# Achado controlado: ponto final no XTTS

Data: 2026-11-02. Fonte: `pilots/r1035-02XpQTA-_XE/pilot-P0006/references-clean/char_cagla-compact.wav`.
Modelo: XTTS v2 local, CPU, `temperature=0.75`, `repetition_penalty=10`,
`top_k=50`, `top_p=0.85`, `speed=1.0`, `enable_text_splitting=False`,
`max_new_tokens=220`, semente fixa por caso. ASR: faster-whisper small int8,
pt, beam 5. Comparação lexical exata (não aprovação auditiva).

| Caso | Texto | Duração | ASR | Exato |
|---|---|---:|---|---|
| c01 | Inacreditável. | 2,411 s | INDACREDITÁVEL PONTO | não |
| c02 | Inacreditável | 1,291 s | inacreditável. | sim |
| c03 | Você está me machucando. | 2,133 s | Você está me machucando, pôntulo. | não |
| c04 | Você está me machucando | 1,803 s | você está me machucando | sim |
| c05 | Não faça isso. | 1,856 s | Não faça isso. | sim |
| c06 | Não faça isso | 1,429 s | Não faça isso! | sim |
| c07 | Mãe, nada. A gente se diverte. | 3,989 s | Mãe, a gente se diverte! | não (omitiu “nada”) |
| c08 | Mãe, nada. A gente se diverte | 3,435 s | Mãe, nada. A gente se diverte. | sim |

## Interpretação

- O ponto final é um gatilho observado de fala excedente, omissão e aumento de
  duração. Não é a única causa possível nem foi testado em todas as vozes.
- Remover **apenas o ponto final** não altera palavras e resolveu os três
  casos em que o ponto produziu erro. Interrogação e exclamação não foram
  removidas.
- ASR exato continua sendo triagem lexical, não inteligibilidade, emoção,
  identidade ou sincronia labial.
- A regra foi implementada em `integrations/dubbing_synth.normalize_tts_text`
  e registrada em cada recibo (`final_period_removed`).

## Limites

- Uma voz (Çağla compacta) e oito tomadas; não generaliza para todas as vozes.
- ASR pode normalizar pontuação e não detecta todos os artefatos.
- A escuta humana e a revisão nativa continuam pendentes.
