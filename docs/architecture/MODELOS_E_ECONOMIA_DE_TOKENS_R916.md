# Modelos locais e custo por tarefa

**Revisão documental:** 2026-10-18 · **Origem do inventário local:** `opencode.json` e `integrations/opencode_provider_models.json` no checkout; confirmar seus hashes no atlas R916 antes de reproduzir esta comparação.

## Catálogo, configuração e acesso são evidências diferentes

No `opencode.json` observado, o modelo padrão permanece `ollama-local/llama3.2`; o bloco do provider OpenCode contém `gpt-6-astra`, `gpt-5.6-luna`, `gemini-3.8-flash`, `gemini-3.7-flash` e `gemini-3.5-flash-lite`. Em paralelo, o recibo de descoberta local `docs/evidence/r916/model-selection.json` lista `openai/gpt-6-luna` e `google/gemini-3.8-flash` no catálogo consultado, mas seu próprio contrato diz `catalog_is_not_entitlement`, e os probes não verificaram a identidade do modelo respondente. A sessão deste ambiente também informa `openai/gpt-6-luna`, e a documentação pública da API lista esse ID; nenhuma dessas evidências prova que o ID esteja habilitado no provider estático ou autenticado no endpoint que executará a próxima tarefa.

O catálogo é uma lista de modelos que a interface pode expor, não uma verificação de autenticação, cota, inferência ou adequação. A disponibilidade deve ser consultada no provider selecionado (por exemplo, `/models` ou `opencode models`) e testada numa chamada delimitada. O `doctor` estrutural não realiza esse teste.

## Tarifa publicada da API não é preço da assinatura

Valores publicados na documentação de API consultada em 2026-10-18, em USD por milhão de tokens. Podem mudar; consulte a página oficial antes de aprovar orçamento. Não incluem necessariamente ferramentas, grounding, região, impostos, armazenamento de cache ou condições promocionais.

| Candidato/API | Entrada | Entrada em cache | Saída | Interpretação |
|---|---:|---:|---:|---|
| OpenAI `gpt-6-luna`, contexto curto | $0,10 | $0,01 | $0,50 | Tarifa publicada; candidato econômico, mas não listado no `opencode.json` local observado. |
| OpenAI `gpt-6-luna`, contexto longo | $0,20 | $0,02 | $0,75 | A categoria de contexto altera a tarifa; use a contagem faturada pelo provider. |
| Gemini `gemini-3.8-flash`, Standard | $0,75 | $0,075 | $3,75 | Modelo Flash mais recente listado na página consultada; confirme status, acesso e preço vigentes. |
| Gemini `gemini-3.5-flash-lite`, Standard | $0,30 | $0,03 | $2,50 | Flash-Lite econômico. A camada gratuita não remove limites de uso. |

As taxas da tabela são **preços por token de API**, não franquia de ChatGPT/Gemini, crédito, seat ou assinatura. O plano gratuito do Gemini pode ter entrada/saída sem tarifa de API segundo a página consultada, mas tem limites de modelo/cota e política de dados própria. A mesma página diferencia tiers pago/gratuito e o uso de dados; confirme as condições da conta e do projeto.

### Discrepância que exige atenção

O aviso recebido nesta sessão para `gemini-3.5-flash-lite` reportou `generate_content_free_tier_input_token_count`, limite de 250.000 e sugestão de retry de aproximadamente 40 segundos. Isso é evidência daquele erro/conta/janela, não uma garantia de limite atual geral. O tratamento seguro é registrar o 429, honrar `Retry-After` se presente, limitar tentativas e parar; não alternar silenciosamente para outro modelo, consumir uma quota paga ou reenviar o mesmo contexto.

## Como escolher sem trocar o padrão automaticamente

O `ModelRouter` existente considera tipo de tarefa, provider, disponibilidade e filtros como `prefer_free`. `prefer_free` usa a curadoria R499, que deriva de uma tarefa matemática específica; ela **não** compara GPT-6 Luna e Gemini Flash, nem comprova qualidade geral. Este guia não adiciona nem ativa um roteador novo e não altera `default_agent`/`model`.

| Classe da tarefa | Política operacional | Condição para escalar |
|---|---|---|
| Extração, classificação ou resumo delimitado e de baixo risco | Pode-se testar Luna ou Flash-Lite como candidatos; usar contexto mínimo e saída limitada. | Falha no critério, incerteza alta ou informação omitida → reavaliar contexto e, se autorizado, testar modelo mais capaz. |
| Código com dependências, análise com múltiplas etapas ou síntese crítica | Comparar Luna, Flash e um modelo de maior capacidade em amostra de tarefas pareadas. | Só escolher por custo depois de medir taxa de aceitação e retrabalho. |
| Decisão de alto impacto, auditoria científica ou informação sensível | Não usar a tarifa menor como critério suficiente; verificar política de dados, revisão humana e requisitos do domínio. | Modelo mais caro não substitui especialista, evidência ou autorização de dados. |

### Métrica de custo útil

Não minimizar tokens de entrada isoladamente. Para o mesmo conjunto de tarefas e o mesmo critério de aceite, registrar por execução:

- provedor/modelo e versão efetivamente respondidos;
- tokens de entrada, saída, cache e raciocínio, quando o provider os fornece;
- se a contagem veio do provider ou é uma estimativa local;
- número de tentativas, erros de contexto/cota, tempo e chamadas de ferramenta;
- resultado do critério de qualidade/aceite e quantidade de retrabalho;
- tarifa e modalidade (API, tier, cache, assinatura), com fonte/data.

Reportar **tokens e custo por tarefa aceita** (e qualidade na mesma tarefa), incluindo todas as tentativas. Se o provider não devolver uso, não apresentar estimativa de caracteres como cobrança real. Sem amostra pareada suficiente, publicar apenas “candidato a avaliação”; não alegar economia ou melhor qualidade.

## Ollama e limites de contexto

Foi feita uma inspeção somente de leitura do daemon local em 2026-10-18: `ollama show --modelfile llama3.2` não mostrou `PARAMETER num_ctx`; o `opencode.json` declara `limit.context=32768` para esse ID. A documentação do Ollama especifica `num_ctx` default de 2048. Portanto existe **divergência entre o limite declarado pelo cliente e o Modelfile observado**, uma explicação plausível para erros de contexto; não prova que todas as chamadas falharam por essa causa. `ollama show --modelfile gemma4:e2b-tuned` mostrou `PARAMETER num_ctx 24576` e `num_thread 4`, coerente com a anotação local. `ollama ps` não mostrou modelo em execução; não houve inferência neste diagnóstico.

O SDK R918 consulta `/api/show` em Ollama loopback antes de gerar, usa o `num_ctx` do Modelfile (ou o default documentado quando ausente), compara com uma estimativa de entrada e pode bloquear antes do POST. A estimativa é bytes UTF-8/3, não tokenizer. Conteúdo não é automaticamente truncado. Se `/api/show` falha, o SDK se abstém, a menos que o operador forneça `context_window`; nesse caso o recibo marca a janela como não verificada no daemon. Esse pré-chequeio **não intercepta chamadas feitas internamente pelo aplicativo OpenCode**; o cliente, Modelfile, modelo e runtime precisam estar alinhados.

Remediação segura, sem mudar o padrão nesta revisão: confira `ollama show --modelfile <modelo>` e `ollama ps`; compare `PARAMETER num_ctx` ao system prompt, entrada e saída reservada. Se optar por criar uma tag local via Modelfile/`ollama create`, faça-a sob ID novo, registre hash/modelo-base/licença/num_ctx e compare respostas com tarefas pareadas antes de usá-la. Não sobrescreva `llama3.2` nem escolha 24576/32768 sem testar memória e estabilidade no host. O procedimento de quantização pesquisado está em [soluções quantizadas no GitHub](QUANTIZACAO_LOCAL_GITHUB_R916.md).

Para uma falha de contexto: (1) manter o erro completo e o modelo selecionado; (2) conferir janela ativa e tamanho do system prompt; (3) reduzir ou dividir explicitamente o material recuperado, sem omitir evidência; (4) limitar a saída quando adequado; (5) testar outra janela/modelo somente com escolha explícita. Uma estimativa baseada em bytes/caracteres não é tokenizador nem garantia de que a chamada caiba.

## Fontes primárias

- OpenAI API — [Pricing](https://platform.openai.com/docs/pricing), consultada em 2026-10-18. Tarifa de API e contexto curto/longo são tabelados separadamente.
- OpenAI API — [Models](https://developers.openai.com/api/docs/models), consultada em 2026-10-18. Identifica GPT-6 Luna como opção para cargas sensíveis a custo; não certifica qualidade na tarefa OCRE.
- OpenAI API — [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits), consultada em 2026-10-18. Limites dependem de organização, projeto, tier e modelo; verificar cabeçalhos/console.
- Gemini API — [Pricing](https://ai.google.dev/gemini-api/docs/pricing), consultada em 2026-10-18. Separa Free/Paid/Enterprise, modalidades Standard/Batch/Flex/Priority e política de uso de dados.
- Gemini API — [Models](https://ai.google.dev/gemini-api/docs/models) e [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), consultadas em 2026-10-18. IDs, estágio de lançamento e limites podem mudar; cotas são específicas do projeto/modelo/nível.
- Ollama — [Modelfile](https://docs.ollama.com/modelfile), consultada em 2026-10-18; `num_ctx` padrão documentado como 2048. [Import](https://docs.ollama.com/import) informa que importar GGUF não faz quantização.
- Soluções quantizadas: inventário e commits GitHub imutáveis em [QUANTIZACAO_LOCAL_GITHUB_R916.md](QUANTIZACAO_LOCAL_GITHUB_R916.md).

**Limite:** documentos consultados e catálogo de configuração não equivalem a benchmark de qualidade, confirmação de acesso por conta, contrato de preço individual ou validação externa. Nenhum padrão foi substituído por esta revisão.
