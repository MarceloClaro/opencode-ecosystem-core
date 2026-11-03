---
name: cp-motion-explicativo
description: Construa motion graphics que tornam relações e processos compreensíveis por ações visuais sincronizadas à fala. Use para demonstrar etapas, causa e efeito, comparações, camadas ou relações espaciais; não para apenas decorar cenas com títulos e ícones.
---

# Motion explicativo

Converta a ideia em uma mudança observável. O espectador deve perceber o que mudou, por qual ação e com qual consequência, sem precisar ler uma lista de instruções.

## Defina a lógica visual

Leia ou transcreva a fala real. Para cada trecho que pede explicação, identifique o estado inicial, a ação, o estado final e o elemento que precisa continuar reconhecível. Use a relação expressa pelo conteúdo; não transforme correlação em causalidade nem ilustração em dado medido.

Escolha uma representação pela relação que ela esclarece:

- **Processo:** uma peça percorre etapas e muda de estado; evite exibir todas as etapas como cartões equivalentes.
- **Causa e efeito:** a ação precede o resultado, com vínculo visível entre ambos.
- **Comparação:** preserve escala, enquadramento e base de comparação; destaque a diferença relevante.
- **Partes de um todo:** separe e reúna os mesmos componentes, mantendo correspondência entre eles.
- **Relação espacial:** use profundidade quando distância, volume, oclusão ou ponto de vista forem parte da explicação.

Se a ideia não pede transformação, uma imagem clara pode bastar. Não acrescente movimento apenas para preencher a duração.

## Coreografe pela compreensão

Apresente o objeto antes de exigir que a pessoa acompanhe sua transformação. Sincronize a mudança com a frase correspondente. Reserve um intervalo estável para perceber o resultado antes da próxima ação. O início, o efeito e a conclusão precisam existir na montagem final, sem cortes que escondam a etapa difícil.

Use um movimento principal por vez. Um ícone deve executar uma ação ligada ao significado: componentes se conectam, um trajeto se percorre, uma seleção altera o resultado. Dar escala a um ícone estático não explica o processo por si só.

Números, proporções, eixos e rótulos devem vir de dados confirmados. Sem dados, construa uma ilustração qualitativa e identifique esse caráter quando a aparência puder sugerir medição.

## Escolha e implemente a técnica

Use SVG, formas e composição 2D para relações planas. Perspectiva e paralaxe podem organizar camadas, mas não comprovam geometria tridimensional. Se volume ou mudança de ponto de vista justificarem 3D genuíno, leia [Volume e fallback](references/volume-e-fallback.md) antes de implementar.

Em Remotion, estados, trajetórias e câmera devem depender dos frames. Não use CSS animations, transitions, timers ou `useFrame` como relógio de movimento. Confira a [documentação de animação](https://www.remotion.dev/docs/animating-properties) para a versão do projeto quando precisar da API. Não diga que usou uma skill, biblioteca ou ferramenta que não está disponível.

Teste uma amostra com a relação mais difícil antes de multiplicar as cenas. Se a execução completa já estiver autorizada, valide e continue; se a aprovação de estilo estiver pendente por pedido do usuário, apresente o teste. Serviços pagos adicionais exigem autorização correspondente.

## Aceite observável

- A ação visual corresponde à frase e não sugere uma informação nova não confirmada.
- Objetos mantêm identidade e continuidade; não mudam de forma ou de lugar para esconder um erro.
- A relação fica clara em reprodução normal e em tamanho de celular.
- Texto e elementos essenciais permanecem legíveis durante o movimento.
- O arquivo renderizado apresenta a mesma transformação da prévia, sem telas vazias, saltos ou animação ausente.

Entregue a cena solicitada e identifique qualquer simplificação técnica que altere a representação. Não apresente uma alternativa 2D como cumprimento de um pedido explícito de 3D.

Respeite direitos, licença, consentimento e privacidade de dados, imagens e materiais de terceiros. Preserve o original e não sobrescreva a edição aprovada. Não fabrique número, medida ou relação causal para tornar a animação mais convincente.

## Salvaguardas adicionais

- Preserve os arquivos originais e não sobrescreva a versão aprovada; grave novas saídas em destino distinto.
- Não envie mídia, voz, rosto, transcrição ou material confidencial a serviços externos, gratuitos ou pagos, sem autorização específica que cubra a transferência.
- Respeite direitos, licença, consentimento e privacidade; uma referência não concede licença para copiar conteúdo de terceiros.
