# Efeitos e motion

## Efeitos com função

| Efeito | Função | Cuidado |
|---|---|---|
| `spring` de entrada | indicar o que chegou | deslocamento curto, sem bounce exagerado |
| barra de progresso | orientar a duração | não competir com a legenda |
| ponto na linha do tempo | mostrar mudança | para quando a linha termina |
| marcador na escala | localizar um limite | não sugerir precisão inexistente |
| palavra-chave colorida | fixar conceito | 1–2 por bloco, manter CPS |
| cartão de abertura | dar roadmap | narração deve citar os itens |
| cartão de encerramento | recapitular | 3 ideias, não 10 |
| retrato com zoom lento | ancorar a apresentadora | não simular fala; usar recorte |

## O que evitar

- zoom contínuo ou tremor;
- partículas e brilho sem função;
- contagem animada que parece medição;
- transições longas que atrasam a fala;
- texto sobre rosto ou slide com informação;
- mais de uma cor de destaque por cena.

## Arquitetura

- **Remotion** para motion graphics e cartões; renderize em vídeo e componha.
- **FFmpeg** para corte, cor, áudio, legendas e concatenação.
- **ASS/libass** para legendas; preserve SRT para reedição.
- **Máscara** para aplicar o slide sem cobrir a apresentadora.

## Armadilhas técnicas

- Remotion arredonda a largura para par: 935 → 934; escale para 935 antes do
  `alphamerge`.
- SAR pode divergir (10240:10239 vs 1:1); use `setsar=1` antes do `concat`.
- O demuxer `concat` pode desalinhar segmentos com durações de áudio/vídeo
  diferentes; use o filtro `concat` com `apad/atrim`.
- Áudio de cartão mais curto que o vídeo: preencha com silêncio para manter a
  duração.
