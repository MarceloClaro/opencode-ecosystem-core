# Rastreamento e enquadramento

Leia para conversão de formato, movimento lateral ou moldura que muda de proporção.

## Separe movimento da pessoa e movimento do layout

Registre regiões do rosto e dos gestos em coordenadas do vídeo de origem. Pode usar rastreamento disponível ou pontos de controle manuais em trechos curtos. Confira os extremos e refine onde houver movimento; não invente detecções quando o rosto estiver oculto.

Associe esses dados ao tempo do arquivo original. Um corte na montagem, uma mudança de velocidade ou uma sequência que reinicia o frame local alteram esse mapeamento. Evite aplicar o ponto de rastreamento do segundo da montagem ao mesmo segundo do arquivo sem verificar a edição.

## Calcule um recorte que caiba

Com origem de largura `W` e altura `H`, e área de destino `w` por `h`, um preenchimento sem distorção começa com escala `s = max(w/W, h/H)`. A janela visível na origem mede `w/s` por `h/s`. Posicione essa janela ao redor da região de interesse e limite suas bordas ao tamanho da origem.

Faça a conta novamente enquanto a moldura muda. Se a janela não comportar a região obrigatória, não há posição que resolva o problema: diminua o corte, altere o destino ou use encaixe com margens. Nunca comprima a largura da pessoa para fazê-la caber.

Suavize trajetórias com pontos estáveis e uma zona de tolerância. Reaja a deslocamentos relevantes sem reproduzir tremores de detecção. Se o rastreamento se perder, mantenha uma composição conservadora até o próximo ponto confiável; não salte para o centro por um único frame.

## Teste os intervalos difíceis

Verifique entrada e saída da moldura, gesto máximo, inclinação da cabeça e junções entre cortes. A borda da cabeça deve manter folga visual; gestos com significado precisam continuar reconhecíveis. Teste o vídeo em reprodução, além dos frames críticos: uma coleção de quadros bons ainda pode esconder uma trajetória ruim entre eles.
