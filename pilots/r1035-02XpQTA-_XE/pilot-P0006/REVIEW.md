# Revisão-fonte e de sentido — P0006

**Escopo:** 26 falas de 373,52–447,96 s. A revisão compara o ASR turco, as
legendas em inglês queimadas na imagem (OCR + leitura manual) e o contexto da
cena. O texto PT-BR abaixo é uma **revisão assistida**, não uma certificação
de falante nativo.

## Decisões principais

- Frases curtas foram traduzidas pela **função conversacional**, não pela
  palavra isolada: “Same.” → “O mesmo.”; “Reason?” → “Por quê?”;
  “Good and you?” → “Bem, e você?”.
- Onde o ASR divergiu da legenda de tela, a legenda foi usada como contraprova:
  - U0003: “Don't stress so much, calm down.” → “Não se estresse tanto, calma.”
  - U0004: “Learn to have fun, if you can't, at least show it.” →
    “Aprenda a se divertir; se não der, ao menos demonstre.”
  - U0006: “Chagla, go and get treatment, you are impossible to bear.” →
    “Çağla, vá se tratar. Você é insuportável.”
  - U0013: “Ryuya, let's leave.” → “Rüya, vamos embora.”
  - U0019–20: “why aren't you following the calls? I've been calling you for
    so many hours, I almost went crazy.” → “Por que não atende?” /
    “Ligo há horas, quase enlouqueci.”
  - U0024–25: “Your voice is strange, is something wrong?” →
    “Sua voz está estranha.” / “Algo errado?”
- U0010: a legenda de tela parece adiantada/duplicada; foi usado o ASR turco
  “Vallahi güzel gidiyor.” → “Está indo bem.” (confiança média).
- Nomes preservados: Rüya, Çağla, Alaz. “Chagla/Ryuya” do OCR foram corrigidos.

## Tabela de revisão

| ID | Locutor | ASR turco | Inglês de tela | PT-BR revisado | Confiança |
|---|---|---|---|---|---|
| U0001 | spk1 | İnanılmazsın ya. | It's impossible to believe you. | Inacreditável. | alta |
| U0002 | spk2 | Yapma böyle ya. | Do not do that. | Não faça isso. | alta |
| U0003 | spk1 | Kızım bir gelme ortam bir sakin ol. | Don't stress so much, calm down. | Não se estresse tanto, calma. | média |
| U0004 | spk1 | Yani inanmıyor öğrense ne… | Learn to have fun, if you can't, at least show it. | Aprenda a se divertir; se não der, ao menos demonstre. | média |
| U0005 | spk2 | Canımı acıtıyorsun. | You're hurting me. | Você está me machucando. | alta |
| U0006 | spk1 | Çağla git öte de ağla… | Chagla, go and get treatment, you are impossible to bear. | Çağla, vá se tratar. Você é insuportável. | média |
| U0007 | spk2 | Rüya, ne haber nasılsın? | Ryuya, how are you? | Rüya, como você está? | alta |
| U0008 | spk3 | İyiyim senden ne haber? | Good and you? | Bem, e você? | média |
| U0009 | spk2 | İyiyim ben de nasıl gidiyor? | Fine. How's it going? | Bem. E aí? | média |
| U0010 | spk3 | Vallahi güzel gidiyor. | Okay, what about you? | Está indo bem. | média |
| U0011 | spk2 | Sen nasıl gidiyor? | Okay, what about you? | E você? | alta |
| U0012 | spk3 | Olur ne olsa. | Same. | O mesmo. | média |
| U0013 | spk2 | Rüya, alayım benim. | Ryuya, let's leave. | Rüya, vamos embora. | alta |
| U0014 | spk3 | Sebeb kızım. | Reason? | Por quê? | alta |
| U0015 | spk2 | Sebeb, sebeb, sebeb. | Reason. Reason. Reason. | Por quê? Por quê? Por quê? | alta |
| U0016 | spk3 | Sıkıldım hadi. | I'm bored. Let's... | Estou entediada. Vamos. | alta |
| U0017 | spk2 | Ben de senden sıkıldım arkadaşım. | I'm tired of you, friend. | Também cansei de você, amiga. | alta |
| U0018 | spk4 | Alo, Çağla. | Hello. | Alô, Çağla. | alta |
| U0019 | spk4 | Niye telefondan bakmıyorsun? | Chagla, why aren't you following the calls? | Por que não atende? | alta |
| U0020 | spk4 | Saatlerdir sizi arıyorum… | I've been calling you for so many hours… | Ligo há horas, quase enlouqueci. | alta |
| U0021 | spk2 | Yok bir şey anne her şey yolunda. | There's nothing, mom. Everything is fine. | Nada, mãe. Está tudo bem. | alta |
| U0022 | spk4 | Alaz. | Alaz? | Alaz? | alta |
| U0023 | spk2 | Alaz iyi, keyfi yerinde. | Alaz is fine. Good mood. | Alaz está bem. De bom humor. | alta |
| U0024 | spk4 | Senin sesin tuhaf geliyor. | Your voice is strange… | Sua voz está estranha. | alta |
| U0025 | spk4 | Bir şey mi oldu? | …is something wrong? | Algo errado? | alta |
| U0026 | spk2 | Anne ne olabilir ki… | Mom, nothing. Just having fun. | Mãe, nada. Só estamos nos divertindo. | alta |

## Limites

- A legenda inglesa é, ela mesma, uma tradução e pode simplificar o turco.
- O OCR foi corrigido manualmente onde estava parcial; ainda pode haver
  diferença de pontuação ou de fala sobreposta.
- A atribuição de locutores é heurística por cena; não é identificação
  biométrica.
- O texto PT-BR precisa de revisão de falante nativo antes de publicação.
- Nenhum TTS, mixagem ou aprovação audiovisual está concluído nesta revisão.
