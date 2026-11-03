# Opções GitHub para modelos quantizados locais

**Pesquisa:** 2026-10-18 · **Modo:** leitura de páginas oficiais de repositórios/documentação · **Execução, clone, instalação e download:** não realizados.

## Resumo para este host

O Core já declara Ollama local e apresenta `gemma4:e2b-tuned` e `gemma4:e4b-tuned` como tags existentes/configuradas. A inspeção local mostrou `num_ctx=24576` para o primeiro modelo. Isso é uma base melhor para corrigir o erro de contexto imediato do que baixar outro checkpoint sem diagnóstico; não comprova qualidade da resposta nem custo computacional zero.

Para experimentar outras famílias de quantização, a rota GitHub mais direta é **llama.cpp → GGUF quantizado → importação no Ollama por Modelfile**, mantendo o modelo atual intacto e criando uma nova tag de teste. Ollama declara explicitamente que importar GGUF não quantiza o modelo: a quantização deve ser feita antes, por ferramenta como `llama-quantize`. A alternativa Unsloth é mais ampla (treino/fine-tuning/exportação, inclusive GGUF) e pode ser útil para preparação, mas adiciona outra cadeia de dependências e requisitos de hardware. Nenhum dos três projetos foi executado neste host nesta revisão.

## Comparação dos repositórios

| Projeto e revisão observada | Papel útil | Evidência pública e licença observada | Adequação e limites |
|---|---|---|---|
| [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp/tree/547208dca250ceb3e4c8615598d043f2b602a527), commit `547208dca250ceb3e4c8615598d043f2b602a527` | Inferência C/C++ e conversão/quantização GGUF (`llama-quantize`). O README lista quantização de 1,5/2/3/4/5/6/8 bits; o manual de quantização descreve F32/BF16 → GGUF e quantização, incluindo `Q4_K_M`, `imatrix` e a avaliação de perda por perplexidade/KL. | [README](https://github.com/ggml-org/llama.cpp/blob/547208dca250ceb3e4c8615598d043f2b602a527/README.md); [quantize README](https://github.com/ggml-org/llama.cpp/blob/547208dca250ceb3e4c8615598d043f2b602a527/tools/quantize/README.md); licença MIT declarada no repositório. | Melhor candidato técnico para experimentar quantizações GGUF em CPU. Reduzir bits tende a reduzir tamanho e pode acelerar, mas pode degradar qualidade; resultado depende de arquitetura, formato, hardware e tarefa. Modelo/weights continuam sujeitos à licença própria. |
| [`ollama/ollama`](https://github.com/ollama/ollama/tree/36a6e994d2f6c4ab94b3555185154d069e5dba87), commit `36a6e994d2f6c4ab94b3555185154d069e5dba87` | Serviço local de modelos e API. Modelfile escolhe modelo-base, `num_ctx`, `num_predict`, parâmetros e template; aceita importar GGUF. | [README](https://github.com/ollama/ollama/blob/36a6e994d2f6c4ab94b3555185154d069e5dba87/README.md); documentação [Import](https://docs.ollama.com/import) e [Modelfile](https://docs.ollama.com/modelfile); licença MIT declarada no repositório. | É a camada de execução que o Core já usa. Import não quantiza: quantize fora antes. O valor `num_ctx` efetivo precisa ser conferido no Modelfile/modelo servido, não inferido do `limit.context` de `opencode.json`. A licença dos weights não é a licença do serviço Ollama. |
| [`unslothai/unsloth`](https://github.com/unslothai/unsloth/tree/b4a4855e49c674f1dd375a5f716d901502b97b73), commit `b4a4855e49c674f1dd375a5f716d901502b97b73` | Projeto de treino/fine-tuning e exportação/execução, incluindo GGUF/QLoRA e interface desktop. | [README](https://github.com/unslothai/unsloth/blob/b4a4855e49c674f1dd375a5f716d901502b97b73/README.md); arquivo LICENSE identificado como Apache-2.0. | Candidato para preparar/adaptar modelos; não é o runtime atual do Core. O README contém afirmações de desempenho do mantenedor, não medições independentes deste host. Treino/quantização e weights podem ter requisitos e licenças distintos. |

Arquivos de licença nos commits identificados: [llama.cpp/LICENSE (MIT)](https://github.com/ggml-org/llama.cpp/blob/547208dca250ceb3e4c8615598d043f2b602a527/LICENSE), [ollama/LICENSE (MIT)](https://github.com/ollama/ollama/blob/36a6e994d2f6c4ab94b3555185154d069e5dba87/LICENSE) e [unsloth/LICENSE (Apache-2.0)](https://github.com/unslothai/unsloth/blob/b4a4855e49c674f1dd375a5f716d901502b97b73/LICENSE). Os SHAs e metadados de licença acima foram consultados na API pública GitHub em 2026-10-18. Branches `main`/`master` são móveis; os links desta tabela apontam aos commits observados. Inspecionar a licença da **família de modelo/weights** antes de uso ou redistribuição — a licença do código não a substitui.

## Fluxo de experimento recomendado (não executado)

1. **Preservar o atual:** registrar modelo, digest/tag, Modelfile, licença, tamanho do arquivo, `num_ctx`, parâmetros e hash; não substituir `llama3.2` nem `gemma4:e2b-tuned`.
2. **Escolher weights elegíveis:** confirmar arquitetura e licença dos weights, procedência, safetensors/GGUF original, tokenizer, template e encoder multimodal se houver.
3. **Gerar uma candidata nova:** selecionar quantização (por exemplo, Q4_K_M e Q5_K_M), documentar comando/versão/seed e arquivo de imatrix quando usado; guardar SHA-256 e metadados. Não quantizar novamente um GGUF quantizado sem reconhecer a perda adicional.
4. **Importar em tag separada:** criar ModelFile apontando ao GGUF, definir `PARAMETER num_ctx` e `num_predict` explicitamente, e usar `ollama create nome-candidato`. Não executar este passo sem autorização para ler/gravar arquivos de modelos e consumir armazenamento.
5. **Benchmark pareado:** comparar original e candidata com as mesmas tarefas, prompt/system, template, contexto, temperatura, seed, saída máxima e ferramentas. Incluir casos negativos e critérios de aceite definidos antes do teste.
6. **Medir custo local total:** taxa de saída, latência/prefill, pico de memória/RAM/VRAM, tokens por tarefa aceita, erro de contexto, taxa de resposta válida e retrabalho. Em modelos locais, preço API pode ser zero, mas tempo, energia, memória, download e trabalho de revisão não são zero.
7. **Aprovação manual:** somente alterar configuração padrão após avaliação de qualidade/taxa de falhas e confirmação de que o contexto do daemon comporta system prompt + entrada + saída reservada.

O host descrito nos comentários locais do catálogo é CPU i5-1035G1, 4c/8t, 11,8 GB RAM e sem GPU; velocidades ali registradas são observações do host/data daquela medição, não benchmark desta pesquisa. A saída local no modo leitura mostrou `ollama ps` sem modelos ativos. Assim, não afirmo que quantizar este host produzirá determinada velocidade, qualidade ou redução de custo.

## Referências

- `llama.cpp` `tools/quantize/README.md` no commit acima: pipeline GGUF, `llama-quantize`, `Q4_K_M`, `imatrix` e ressalva explícita de perda de qualidade possível.
- Ollama [`Importing models`](https://docs.ollama.com/import): importação GGUF sem quantizar no importador; preparar GGUF quantizado antes.
- Ollama [`Modelfile`](https://docs.ollama.com/modelfile): `num_ctx` e `num_predict`; documentação observa default de contexto `2048`.
- OCRE `integrations/opencode_cli.py`: catálogo local e observações de host, inclusive contexto/threads declarados; não verifica sozinha o daemon atual.

**Não alegação:** a existência desses repositórios, compatibilidade de formato, licença do código ou quantização não prova qualidade equivalente, resposta correta, autorização de dados ou desempenho aceitável para uma tarefa científica.
