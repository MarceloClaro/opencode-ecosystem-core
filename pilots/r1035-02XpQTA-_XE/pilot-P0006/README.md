# Piloto P0006 — revisão antes de dublar

**Parte:** `02XpQTA-_XE-P0006`, 373,52–447,96 s, 1.861 frames, 74,44 s.
**Fonte:** episódio integral R1035; partes finais vêm do intermediário em GOP
fechado, não do stream copy direto marcado como diagnóstico.

## Ordem executada

1. ASR turco com timestamps de palavra.
2. Revisão-fonte: ASR confrontado com as legendas inglesas queimadas na
   imagem (OCR multi-quadro + leitura manual) e o contexto da cena.
3. Revisão PT-BR por função conversacional, com atenção especial a frases
   curtas.
4. Texto de dublagem em `dialogue-dub.json`; nenhum TTS usa o ASR cru.
5. TTS XTTS v2 CPU a partir do texto revisado.
6. Mixagem e render ainda pendentes.

## Arquivos e marcação de personagens

- `REVIEW.md`: tabela ASR × inglês de tela × PT-BR e decisões.
- `source-review.json`: 26 unidades com confiança e notas.
- `dialogue-dub.json`: texto PT-BR revisado e tempos relativos à parte.
- `dialogue-dub-characters.json`: as 26 falas marcadas com `character_id`.
- `speaker-map.json`: `spk1..spk4` → `char_male_a`, `char_cagla`,
  `char_ruya`, `char_mother`.
- `../voices/voices.json`: registro global; cada personagem tem **uma única**
  referência/hash. Dois personagens não podem compartilhar referência; dois
  locutores não podem apontar para o mesmo personagem sem fusão/revisão.
- `voice-receipt.json` e `voice-receipt-v2.json`: recibos que provam 4
  personagens, uma referência por personagem e 26 falas cobertas.
- `speakers.json` e `references/`: referências locais com hash; a spk1 foi
  limpa e a spk3 foi compactada para evitar pausas longas no TTS.
- `ocr-multiframe/`: quadros e OCR das legendas inglesas.
- `tts-v2/` e `tts-manifest-v2.json`: TTS character-aware; cada fala usa a
  referência do seu `character_id`. `tts/` é o lote anterior, diagnóstico.
- `subtitles-v2/`: legendas PT-BR de nível de linha, geradas depois do TTS.
- `render-v2/`: variantes com faixa inferior e soft subs, quando renderizadas.

Personagem novo ou locutor não mapeado **bloqueia** o TTS; não se cria uma
segunda voz para o mesmo papel. A identidade e o nome continuam não
verificados; os IDs são de consistência de voz, não de biometria.

## Decisões de sentido

- “Same.” → “O mesmo.”; “Reason?” → “Por quê?”; “Good and you?” → “Bem, e você?”.
- “Chagla, go and get treatment…” → “Çağla, vá se tratar.”
- “Learn to have fun, if you can't, at least show it.” → “Aprenda a se divertir;
  se não der, ao menos demonstre.”
- U0019–20 separados em “Por que não atende?” e “Ligo há horas, quase enlouqueci.”
- U0024–25 separados em “Sua voz está estranha.” e “Algo errado?”.
- U0010 usa o ASR turco (“Está indo bem.”) porque a legenda de tela parecia
  adiantada/duplicada; confiança média.

## Limites

- O inglês de tela é uma tradução e pode simplificar o turco.
- A revisão PT-BR é assistida, não certificada por falante nativo.
- Locutores são inferidos por cena; não há identificação biométrica.
- O TTS é uma amostra; sincronia labial não foi tentada.
- A variante “bar” cobre os últimos 140 px e queima PT-BR; a “soft” mantém o
  inglês original visível.
- Nada foi aprovado, publicado ou montado.
