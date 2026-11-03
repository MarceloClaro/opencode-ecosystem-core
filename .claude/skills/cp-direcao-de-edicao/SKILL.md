---
name: cp-direcao-de-edicao
description: Transforme uma fala ou edição dispersa em uma sequência visual com intenção, foco e continuidade. Use para decidir o que mostrar, quando mudar a cena e como alternar apresentador, demonstração e apoio visual; não para apenas preencher um briefing ou corrigir legendas.
---

# Direção de edição

Faça a imagem conduzir a compreensão da fala. Uma cena deve ter uma ação principal reconhecível; elementos de apoio podem coexistir, mas não exigir atenção simultânea.

## Decida a partir do material

Assista ao vídeo e confira o áudio antes de desenhar a edição. Use a transcrição real para localizar as ideias, preservando hesitações úteis, intenção, oferta e tom. Se houver apenas roteiro, trate os tempos como previsão até receber a gravação. Reaproveite o briefing e as decisões já fornecidos; pergunte apenas pelo que muda uma escolha importante e não pode ser inferido.

Separe a fala em unidades de sentido, não em intervalos iguais. Para cada unidade, escolha:

- **O que entender:** uma conclusão concreta para quem assiste.
- **O que olhar:** pessoa, objeto, ação, evidência ou palavra que transmite essa conclusão.
- **O que muda:** a transformação visível que acompanha a ideia, se ela for necessária.
- **O que permanece:** voz, objeto, enquadramento ou posição que conecta a próxima cena.

Se não houver uma função clara para uma inserção, preserve a imagem original. Mudar o layout a cada frase não é um objetivo.

## Escolha a composição

Use o apresentador em tela cheia quando expressão, confiança ou demonstração corporal carregarem a mensagem. Dê tela cheia a uma demonstração quando o detalhe precisar de área. Use moldura ou composição compartilhada quando pessoa e explicação precisarem ser percebidas juntas. Não coloque o apresentador em um canto por padrão.

Quando uma interface, produto ou resultado for protagonista, reserve área suficiente para enxergar seu conteúdo real. Um painel pequeno com texto ilegível não demonstra o produto. Apresente o processo por estados e ações, evitando transformar uma explicação em vários cartões estáticos.

Crie contraste de atenção com tamanho, posição, luz ou movimento; escolha o recurso que resolve a cena. Não anime todos ao mesmo tempo. Durante uma ação principal, mantenha apoios estáveis e reduza a ênfase do que já foi explicado.

Para cenas cheias, mudanças de enquadramento ou explicações com várias etapas, leia [Decisões de montagem](references/decisoes-de-montagem.md).

## Construa e verifique a direção

Antes de escalar um padrão novo, implemente uma amostra que contenha sua transição mais importante, uma explicação completa e o retorno à fala. Escolha pela dificuldade, não apenas pelos primeiros segundos. Use a duração suficiente para verificar esse conjunto.

Se o usuário já autorizou concluir a edição ou o lote, a amostra é uma validação interna: confira os critérios e prossiga dentro do escopo. Se ele pediu aprovar o estilo primeiro, apresente a amostra e aguarde essa decisão. Não peça novamente uma autorização já dada.

Em Remotion, derive o movimento do frame da composição. Não use CSS animations, transitions ou relógios de execução para avançar a cena. Preserve a relação entre tempo do arquivo original e tempo da edição; valide cortes e transições no vídeo renderizado. Consulte a [documentação de animação](https://www.remotion.dev/docs/animating-properties) quando precisar implementar ou conferir a API da versão instalada. Para criação, render, still e requisitos de ambiente, leia [Remotion: CLI e API verificados](references/remotion-cli-e-api.md). A prévia interativa vem antes do render, e renderizar exige pedido explícito; leia [Curadoria R1023 — Remotion para edição audiovisual](references/curadoria-r1023.md). Para avaliar um executor externo de produção, leia [Hypit como caminho externo opcional](references/ecossistema-hypit.md); instalação e uso dependem de autorização e da licença do projeto. Antes de renderizar, descreva cortes, faixas, crop e legenda em um plano e valide com [Plano de edição auditável](references/plano-de-edicao-auditavel.md).

## Critérios de aceite

- Em cada mudança, é possível apontar o foco principal e relacioná-lo à fala.
- A demonstração mostra algo acontecendo; o resultado permanece visível tempo suficiente para ser compreendido.
- O mesmo objeto mantém identidade, posição coerente e continuidade entre estados.
- Rosto, conteúdo demonstrado e legenda não disputam a mesma área.
- O convite final preserva informação e tempo de leitura, sem corte provocado pelo efeito de saída.

Entregue a edição solicitada e uma nota curta sobre as decisões que alteram a percepção. Se houver impedimento, identifique o trecho e a alternativa possível. Não contrate serviços pagos, publique ou amplie o lote sem autorização que cubra essa ação.

Respeite direitos, licença, consentimento e privacidade de pessoas, vozes, imagens e materiais de terceiros. Não use uma referência como licença para copiar conteúdo protegido.

## Salvaguardas adicionais

- Preserve os arquivos originais e não sobrescreva a versão aprovada; grave novas saídas em destino distinto.
- Não envie mídia, voz, rosto, transcrição ou material confidencial a serviços externos, gratuitos ou pagos, sem autorização específica que cubra a transferência.
- Respeite direitos, licença, consentimento e privacidade; uma referência não concede licença para copiar conteúdo de terceiros.
