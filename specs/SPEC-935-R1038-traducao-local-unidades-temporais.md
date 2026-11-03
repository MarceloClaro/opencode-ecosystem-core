---
spec_id: SPEC-935-R1038
title: Tradução local de diálogo em unidades temporais auditáveis
component: integrations.video_translation
status: implemented
test_file: tests/test_r1038_video_translation.py
depends_on:
  - SPEC-935-R1034
  - SPEC-935-R1035
---

# SPEC-935-R1038

## Objetivo

Converter a transcrição turca em unidades de tradução PT-BR com tempos e IDs
estáveis, usando um adaptador de tradução local. Esta etapa não sintetiza voz,
não edita áudio, não cria legendas finais e não aprova tradução.

## Regras

- Cada unidade preserva `start`, `end` e o texto de origem; IDs `U0001` etc.
- Segmentos vazios são ignorados e contados; não criar unidade sem texto.
- Tempos devem ser finitos, não negativos, ordenados e dentro da duração.
- O adaptador recebe lotes de textos e devolve exatamente a mesma quantidade
  de textos não vazios; qualquer divergência falha.
- `M2M100Translator` exige diretório local explícito com `config.json`,
  tokenizer e pesos; `local_files_only=True`; nunca baixar durante a execução.
- Registrar SHA-256 do ASR de entrada e metadados do modelo. Saída em arquivo
  novo; nunca sobrescrever.
- Estado `translated_pending_review`; não declarar qualidade, fluência ou
  adequação cultural. Nomes, apelidos, ironia e referências exigem revisão.

## Aceites

Testes antes do código: unidades e IDs; segmento vazio; tempos inválidos;
lote com ordem preservada; contagem errada; saída vazia; batch inválido;
diretório de modelo ausente; recibo com hash do ASR; recusa de sobrescrita.
O adaptador falso não mede tradução real. O modelo M2M100 418M é MIT; sua
qualidade ainda não foi avaliada no episódio.

## Gate de revisão antes de dublar

`translate_asr` é um **rascunho automático** e não deve alimentar diretamente
a dublagem. Para o piloto, a ordem foi:

1. ASR turco com timestamps;
2. revisão-fonte confrontando ASR, legendas inglesas de tela (OCR e leitura
   manual) e contexto;
3. tradução PT-BR revisada por função conversacional, com atenção a frases
   curtas;
4. `dialogue-dub.json` revisado;
5. só então TTS e mixagem.

Exemplo: “Same.” → “O mesmo.”, “Reason?” → “Por quê?”, “Good and you?” →
“Bem, e você?”, “Chagla, go and get treatment…” → “Çağla, vá se tratar.”.
A revisão de P0006 está em `pilot-P0006/REVIEW.md`; ainda não é certificação
de falante nativo.

## Limites

Tradução automática pode errar nomes próprios, gírias, gênero, tratamento e
humor. Não usar a saída como legenda final antes de revisão humana. Não
declarar sincronia labial, dublagem ou aprovação audiovisual.

## Estado implementado

`integrations/video_translation.py` implementa unidades temporais, adaptador
local M2M100 somente de arquivos existentes, validação de lote e recibo com
hash do ASR. Os 14 testes R1038 passam com tradutor falso. O modelo real
M2M100 418M (MIT) ainda não foi baixado nem avaliado no episódio; nenhuma
qualidade de tradução foi declarada.

