# Matriz e manifesto de fontes

Leia para lotes, substituição de take ou entrega que precisa ser reproduzida por outra pessoa.

## Matriz de decisão

Use uma linha por variante. Um exemplo hipotético de estrutura:

| ID | Base | Hipótese | Variável | Mudança | Preservar | Fonte nova |
| --- | --- | --- | --- | --- | --- | --- |
| B | A aprovada | Explicitar o problema pode facilitar a compreensão da abertura | Título | Título genérico para problema específico confirmado na fala | Take, corpo, oferta, CTA, cores e áudio | Nenhuma |
| C | A aprovada | Uma pergunta falada pode tornar a abertura mais direta | Take inicial | Trocar somente a fala inicial por nova gravação | Corpo, oferta, CTA e identidade | Novo take autorizado |

Essas hipóteses não representam resultados medidos. A variação C demanda nova transcrição e pode mudar o tempo da junção; registre isso sem classificar a atualização necessária da legenda como uma segunda hipótese independente.

## Manifesto mínimo

Escolha JSON, CSV ou Markdown conforme o projeto. Registre:

- **Projeto e base:** identificador da edição e versão preservada.
- **Fontes:** identificador, caminho relativo, tipo, papel na edição e origem. Para conteúdo de terceiros, registre a autorização ou licença conhecida, sem presumir direitos.
- **Uso temporal:** intervalo de origem utilizado e posição na variante; unidade declarada em segundos ou frames, com FPS quando necessário. Mudanças de velocidade precisam constar.
- **Variantes:** identificador, hipótese, mudanças, fontes utilizadas e caminho de saída.
- **Estado:** planejada, renderizada, revisada ou aprovada, conforme a evidência existente. Se houver aprovação, registre sua origem; não promova o estado automaticamente após renderizar.

Para fontes com risco de troca de arquivo, acrescente um hash. Não é necessário gerar hashes ou um banco de dados para um exercício simples. Não inclua senhas, tokens, caminhos pessoais absolutos ou dados de conta no manifesto distribuído.

Use nomes que expliquem a diferença, como `abertura-pergunta-v01.mp4` e `titulo-problema-v01.mp4`. Não use apenas “final2” ou “novo”. O manifesto deve permitir localizar o original usado em cada saída sem depender de memória da conversa.

## Compare o que realmente foi testado

Quando houver dados reais de campanha, registre fonte, período, métrica e diferenças de público, distribuição ou verba conhecidas. Não trate uma comparação desbalanceada como prova isolada de que o título causou o resultado. Se o pedido for apenas produção de arquivos, encerre com os materiais e as hipóteses; publicar anúncios ou iniciar testes não está implícito.
