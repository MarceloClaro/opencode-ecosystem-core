# Modelos e custo de tokens no Core

Comparação de 18/10/2026 para ChatGPT/OpenAI e Gemini/Google. Os catálogos
locais anunciam modelos; uma chamada real é necessária para confirmar acesso.
O padrão atual do Core é `ollama-local/llama3.2`. Esta revisão não o substitui.

## Escolha por tarefa

O candidato de menor tarifa entre os modelos atuais examinados é **GPT-6 Luna**,
adequado como primeira tentativa em tarefas delimitadas com resultado testável.
Para código complexo e revisão crítica, **GPT-6.1 Sol** é um candidato de
escalonamento. Esta é uma recomendação operacional sujeita a medição: preço por
token menor não garante menos tokens, menos tentativas ou maior qualidade.
[Modelos OpenAI](https://developers.openai.com/api/docs/models),
[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).

Do lado Google, **Gemini 3.5 Flash-Lite** é o candidato econômico para trabalho
delimitado; **Gemini 3.8 Flash** oferece uma opção para tarefas agentivas mais
exigentes. Acesso pela conta e pelo cliente precisa ser confirmado.
[Flash-Lite](https://ai.google.dev/gemini-api/docs/generate-content/whats-new-gemini-3.6),
[Gemini 3.8](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.8).

## Tarifa de API — somente referência

Valores publicados por milhão de tokens de texto, processamento padrão e sem
cache. Não são cobranças observadas na conta nem estimativas da franquia OAuth.

| Modelo | Entrada USD | Saída USD | Cenário hipotético: 1M entrada + 100 mil saída |
|---|---:|---:|---:|
| GPT-6 Luna | 0,10 | 0,50 | 0,15 |
| Gemini 3.5 Flash-Lite | 0,30 | 2,50 | 0,55 |
| Gemini 3.8 Flash | 0,75 | 3,75 | 1,125 |

A tarifa de Gemini 3.8 nesta tabela é introdutória, até 31/12/2026; a página
anuncia 1,50/7,50 a partir de 01/01/2027. Os cálculos mantêm a mesma quantidade
hipotética de tokens, sem considerar diferenças de tokenização, raciocínio,
cache, ferramentas, contexto longo ou tentativas. Não constituem benchmark.
[Tarifas OpenAI](https://developers.openai.com/api/docs/models/gpt-6-luna),
[tarifa Gemini 3.8](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.8).

## Assinatura e autenticação

Na tabela de créditos Codex em velocidade padrão, Luna usa 2,5 créditos por
milhão de tokens de entrada e 12,5 de saída; Sol 6.1 usa 50 e 250. A relação
de tarifas é 20:1 para quantidades iguais, sem estimar tarefas incluídas.
Preços de API não calculam a franquia da assinatura. O cliente OpenCode é
terceiro; conferir o consumo efetivo no painel da conta.
[Créditos e limites OpenAI](https://learn.chatgpt.com/docs/pricing).

O Gemini CLI distingue login Google, chave Gemini e Vertex AI. As franquias
e clientes elegíveis dependem do plano. Não trocar automaticamente para uma
chave paga ao encontrar um erro de assinatura.
[Planos e limites Gemini CLI](https://geminicli.com/docs/resources/quota-and-pricing/).

## Medição local e critério de aceite

A revisão executa sondas sintéticas em diretório temporário, sem enviar código
ou documentos do repositório. Uma resposta concluída não basta: o JSON deve
conter os valores corretos para a condição AND, ordem topológica e escopo da
evidência. O [recibo de modelos R916](evidence/r916/model-selection.json)
separa chamadas aceitas, erros, tokens informados e configurações solicitadas.
Uma amostra pequena não demonstra superioridade em produção.

| Sonda sintética | Resultado local | Tokens informados pelo cliente | Tempo total |
|---|---|---:|---:|
| Luna, esforço solicitado `low`, primeiro ensaio | Rejeitada: cinco casos para uma condição com quatro combinações | 1.293 | 8,541 s |
| Luna, esforço solicitado `medium`, ensaio de três itens | Aceita: AND, ordem topológica e limite de evidência corretos | 1.335 | 10,347 s |
| Sol 6.1, esforço solicitado `low`, mesmos três itens | Aceita pelos mesmos critérios | 1.337 | 10,781 s |
| Gemini Flash-Lite, cliente CLI 0.61.0 | Recusa de cliente; sem inferência observada | Indisponíveis | 6,676 s |

Cada linha tem uma execução, sem ferramentas e sem contexto do repositório.
O tempo inclui inicialização do cliente. Modelo e esforço são configurações
solicitadas; não houve atestação independente do backend. A primeira falha de
Luna impede recomendar sua saída sem um gate de qualidade. Esses ensaios não
medem economia em tarefas reais, nem validam raciocínio científico.

O Gemini CLI 0.61.0 recusou a sonda da conta individual com
`UNSUPPORTED_CLIENT`, indicando Antigravity como cliente suportado. A página de
autorização Google não elimina esse gate. O Core não reutiliza tokens em outro
cliente nem contorna a recusa. A elegibilidade de Antigravity e sua inferência
não foram confirmadas por esse erro.

## Como reduzir o consumo

1. Recuperar símbolos e trechos pelo contexto de código; evitar anexar o
   repositório completo ou o catálogo de todos os agentes a cada tarefa.
2. Acionar a fachada do Core e somente ferramentas necessárias. NotebookLM
   possui 53 ferramentas descobertas, mas a entrada central evita exigir que
   todas estejam expostas como ferramentas do modelo principal.
3. Delimitar saída, passos, prazo e critério de aceite. Falha sem progresso
   deve interromper ou escalonar, preservando a evidência.
4. Usar cache e memória com fonte e versão. Não converter síntese anterior em
   fato verificado nem reutilizar contexto desatualizado para economizar.
5. Comparar custo por tarefa aceita: incluir entrada, saída, raciocínio, cache,
   chamadas de ferramentas, falhas e revisões. Não publicar percentual de
   economia antes dessa comparação com qualidade equivalente.

Para seleção manual no OpenCode, use `/models` e escolha
`openai/gpt-6-luna` quando elegível. Isso não altera automaticamente o modelo
dos subagentes nem o adaptador externo Gemini. No Gemini CLI, `/model` e
`--model` controlam o modelo principal, com limites descritos pelo cliente.
[Seleção Gemini CLI](https://geminicli.com/docs/cli/model/).
