# Bloqueio de qualidade: ASR turco pequeno não sustenta dublagem final

Data: 2026-11-03. Evidência: P0002, `faster-whisper-small` (R1037), tradução
M2M100 local.

## Exemplos observados

| ASR turco | Tradução PT gerada | Problema |
|---|---|---|
| `Gideceksiniz açgın özür dükkân.` | “Você vai para a loja de desculpas com fome.” | ASR sem sentido |
| `Özü değil.` | “Não é essencial.” | perda de sentido |
| `Karnat çocuğum.` | “Meu filho de carnaval.” | palavra inventada |
| `Onu bana demeyeceğim.` | “Não vou me dizer isso.” | gramática/papel errado |
| `Anasına diyeceğim.` | “Eu diria a minha mãe.” | tempo verbal errado |

O OCR inglês do mesmo trecho contém linhas coerentes, por exemplo:

- “It's not the child's eyes that are hungry, but his stomach.”
- “You don't tell this to me, but to your mother.”
- “Let them go outside, and then I'll have problems.”

Isso mostra que o problema predominante é a transcrição turca, não apenas a
tradução. Dublar 1.943 unidades a partir desse texto produziria fala absurda,
mesmo com voz clonada perfeita.

## Decisão

- A tradução automática das 6 primeiras partes foi interrompida e **não** será
  usada para TTS.
- Nenhuma linha foi sintetizada a partir dessas traduções.
- O pipeline de TTS não foi iniciado.

## Caminhos técnicos

1. **OCR multilíngue/inglês das legendas queimadas**: 3–5 frames por unidade,
   filtrar créditos, escolher a melhor linha e revisar. Depois traduzir
   inglês→português. É a rota mais fiel ao texto exibido.
2. **ASR maior** (`faster-whisper-large-v3` ou `large-v3-turbo`): pode melhorar
   o turco, mas ainda exige revisão e não garante o sentido da legenda.
3. **Comparar as duas rotas** em uma amostra de 20–30 unidades antes de
   escalar. Não escolher por fluência isolada.

## Teste com large-v3

O `Systran/faster-whisper-large-v3` (2,9 GB, MIT) foi baixado e testado na
P0002 (75 s):

- 7 segmentos em **113 s** com 8 threads, beam 1 (≈1,5× tempo real).
- Texto visivelmente melhor que o small:
  - “Onu bana demeyeceğim, anasına diyeceğim.” → “Não vou dizer isso a mim,
    vou dizer à mãe dele.”
  - “Gözlü değil, karnat çocuğum.” ainda erra “karnı” (estômago), mas se
    aproxima do OCR “not the child's eyes… but his stomach”.
- Estimativa para as 107 partes: **~3,3 h** só de ASR large, em CPU.

O lote `dub-asr` está rodando em tmux e é retomável por parte. Mesmo assim,
large-v3 não elimina a necessidade de revisão: ele melhora a matéria-prima,
não a aprova.

## Critério para retomar o TTS

Uma unidade só entra no TTS quando tiver:

- texto de origem revisado (OCR/ASR maior + contexto);
- tradução PT-BR revisada;
- personagem/cluster com referência;
- duração compatível com o slot, sem truncar fonema.

Sem isso, o resultado seria apenas um rascunho não publicável.
