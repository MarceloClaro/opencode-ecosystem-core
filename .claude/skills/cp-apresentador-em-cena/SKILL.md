---
name: cp-apresentador-em-cena
description: Componha um apresentador real com demonstrações e motion sem cortar rosto ou gestos importantes. Use para alternar tela cheia e moldura, acompanhar o sujeito em recortes dinâmicos ou integrar recorte alfa verdadeiro à cena; não é um gerador de avatares.
---

# Apresentador em cena

Mantenha a presença humana confortável enquanto a cena abre espaço para a explicação. A moldura é uma escolha de composição, não o destino obrigatório do apresentador.

## Observe antes de enquadrar

Inspecione o trecho em movimento, incluindo a maior inclinação da cabeça e os gestos relevantes. Confira dimensões, orientação, cortes existentes e relação entre tempo de origem e tempo da montagem. Um frame isolado não comprova que um recorte funciona durante a fala.

Defina quais regiões precisam ser preservadas: cabeça inteira e rosto como mínimo; mãos, objeto demonstrado ou postura quando carregarem informação. Posicione o rosto de forma confortável dentro da área disponível, normalmente próximo ao centro horizontal, sem perseguir cada micromovimento. Não assuma que o centro do arquivo coincide com o centro da pessoa.

Use tela cheia em falas pessoais e demonstrações corporais. Use moldura quando a explicação precisar dividir a tela. Dê tela cheia à demonstração quando reduzir ambos tornaria o conteúdo ilegível; a voz pode continuar conduzindo esse intervalo.

## Faça o recorte acompanhar a composição

Ao mudar tamanho, proporção ou posição da moldura, recalcule o recorte interno. Animar apenas o contêiner pode deslocar o rosto ou cortar a testa no meio da transição. Mantenha uma trajetória coerente do rosto aparente entre origem e destino.

Se houver movimento relevante ou conversão de formato, leia [Rastreamento e enquadramento](references/rastreamento-e-enquadramento.md). Se não for possível preservar as regiões importantes com corte, reduza a ampliação, mude a composição ou use a imagem inteira com um fundo de apoio.

Reserve áreas distintas para fala legendada, informação visual e rosto. Escolha a moldura pela função da cena; borda, sombra e inclinação devem separar planos sem distorcer a pessoa. Não aplique zoom contínuo ou reenquadramento nervoso como preenchimento.

## Use transparência apenas quando ela existir

Para texto atrás do corpo, pessoa fora da moldura ou troca real de fundo, leia [Recorte alfa verificável](references/recorte-alfa.md). A ordem de camadas só produz oclusão correta se houver uma silhueta válida. Uma máscara oval, retangular ou desenhada por aproximação não é remoção de fundo.

Se não houver recorte utilizável, preserve o vídeo original em uma composição que funcione. Quando a remoção de fundo for requisito explícito, comunique o impedimento e apresente a alternativa sem tratá-la como tarefa concluída.

## Valide a presença em movimento

Em Remotion, controle moldura, crop, posição e escala pelo frame, sem CSS animations, transitions ou timers. Pré-calculados de rastreamento e alfa devem mapear para o mesmo tempo de origem do vídeo, inclusive após cortes. Reutilize esses resultados ao mudar apenas a composição.

Renderize a transição e o trecho com maior gesto. Se a edição completa já estiver autorizada, essa verificação não cria uma aprovação extra. Pare para uma decisão somente quando houver uma escolha pendente que altere o resultado solicitado. Não envie mídia a serviços pagos ou externos sem autorização que cubra esse processamento.

O resultado passa quando cabeça e gestos necessários cabem em todos os estados, o rosto não salta nas transições, a voz permanece sincronizada e a composição pode ser lida no tamanho final. Se houver alfa, inclua os critérios de contorno da referência. Entregue as limitações reais junto do arquivo solicitado.

Respeite direitos de imagem, voz, licença, consentimento e privacidade. Não gere avatar, troque a identidade da pessoa nem use gravação de terceiros sem autorização verificável.

## Salvaguardas adicionais

- Preserve os arquivos originais e não sobrescreva a versão aprovada; grave novas saídas em destino distinto.
- Não envie mídia, voz, rosto, transcrição ou material confidencial a serviços externos, gratuitos ou pagos, sem autorização específica que cubra a transferência.
- Respeite direitos, licença, consentimento e privacidade; uma referência não concede licença para copiar conteúdo de terceiros.
