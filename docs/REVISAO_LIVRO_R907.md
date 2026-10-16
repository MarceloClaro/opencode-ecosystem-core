# Revisão do livro ampliado — R901/R907

O diagnóstico estrutural inicial de 15/10/2026 aprovou 22 checks. Seu alcance é instalação/estrutura; não certifica o livro nem a execução de todos os provedores.

## Conteúdo conservado e corrigido

Foram mantidas as vinte seções de aprofundamento acrescentadas em R903–R906. A revisão independente por amostragem dirigida confrontou as fórmulas com as fontes locais e identificou os seguintes ajustes:

- Requisito crítico prevalece sobre porcentagem de checklist.
- A razão verdadeira/falsa de 0,1 significa uma hipótese verdadeira para dez falsas.
- EMA usa nota contínua no exemplo e exige domínio limitado como pré-condição; o caminho automático R886 não promove confiança.
- A atenção matricial do Transformer é uma analogia. A rota local combina utilidade dos critérios e softmax escalar, sem Q/K/V nessa operação.
- O exemplo do softmax distingue posições de cada linha e empate dentro da linha.
- Argmin por custo e janela de lances são modelos ilustrativos; não descrevem o CFP atual como leilão implementado.
- O exemplo de seleção conserva apenas candidatos que passaram todos os critérios de elegibilidade.
- O fator de congestionamento usa blocos de dez tarefas abertas.
- Instalação não é disponibilidade operacional; o exemplo de presença de executores é hipotético.
- Proporções exigem denominador positivo; universo vazio fica não aplicável. O teto de Amdahl exige fração serial positiva.
- A contabilidade PRISMA declara suas simplificações e distingue registro, relatório e estudo.
- DOI temporariamente indisponível exige triagem; não demonstra identificador inválido.
- A reconciliação do catálogo preserva identidade canônica; remover apenas um alias pode não remover a correspondência.

As contas locais verificadas na revisão foram 0,88592196 para pelo menos um erro independente, PPV 0,285714/0,615385 e Amdahl 3,823529. Esses cálculos validam os exemplos sob suas hipóteses; não são medições de desempenho do Core.

## Apresentação e manutenção

Tabelas textuais agora permitem quebra dentro da largura local. Identificadores longos podem quebrar sem extravasar as caixas. Os novos recursos visuais têm explicação de mecanismo, justificativa, limites e origem. O mapa de responsabilidades não pretende ser um grafo de todas as chamadas; os mapas completos de dependências do snapshot permanecem referências externas ao papel A4.

A ampliação didática do catálogo foi migrada para o gerador autoritativo, com números derivados da geração. O gate histórico R617 foi atualizado para verificar a dependência matemática real: o autor acrescentou amsmath para as deduções; referências a comandos desse pacote continuam reprovadas quando o pacote não é carregado. Os casos negativos distinguem comentário e nome parecido de carregamento real.

Os resultados finais de compilação, coordenadas, inspeção visual e testes estão no manifesto [verification-book-r907.json](verification-book-r907.json). Contagem de desenhos e testes são inventário e verificação local, sem medição de eficácia pedagógica ou validação editorial externa.
