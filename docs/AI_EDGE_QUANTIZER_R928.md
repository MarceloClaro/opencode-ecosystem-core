# AI Edge Quantizer no Core — R928

## Escopo aprovado e origem

Integração por composição do fork `MarceloClaro/ai-edge-quantizer`, commit
`87cda53576a55a71114a4945b3ff18e27c2fa42b` (Alpha 0.3.0, Apache-2.0).
O usuário aprovou ambiente isolado e ensaio pequeno/sintético em CPU, sem
checkpoint externo. Não autorizou executar os agentes dos outros links.

Foram adquiridos 53 arquivos selecionados de código/receitas/licença, com
conferência de Git blob SHA1 e SHA256, sem baixar modelos binários/test fixtures
do repositório. LICENSE e cabeçalhos permanecem preservados. O fonte é montado
read-only no worker, não se executa setup.py nem se instala outro quantizador
PyPI no lugar do fork. A instalação local fica em `.ai-edge-quantizer/`, ignorada
no Git; adaptador, worker, lock e testes são código/artefatos originais do Core.

## Ambiente separado

Python 3.12.14 em `.ai-edge-quantizer/venv`, independente dos ambientes Core e
ITS-FINE. Dependências observadas:

| Pacote | Versão fixada e sondada |
|---|---|
| tf-nightly | 2.23.0.dev20261018 |
| ai-edge-litert-nightly | 2.4.0.dev20261018 |
| numpy | 2.2.6 |
| immutabledict | 4.3.1 |
| backports.strenum | 1.2.8 |

O resolvedor inicialmente escolheu backports-strenum 1.3.1, cujo Requires-Python
é <3.11; pip check recusou o ambiente. Um perfil intermediário com LiteRT 1.4.0
também resolveu a mesma dependência e não foi aceito. A solução foi fixar a
versão 1.2.8 publicada como compatível com 3.12, não ignorar requires-python,
reescrever metadados ou declarar sucesso apesar da checagem.

Lock com hashes: `integrations/ai-edge-quantizer-locks/py312.txt`.
Histórico de compatibilidade: compatibility-profile.json na mesma pasta.
Algumas consultas JSON web do PyPI foram bloqueadas por robots.txt; não foram
tratadas como páginas consultadas com sucesso. A preparação usou o resolvedor,
os metadados das distribuições e pip check, sem instalar no Python do Core.

O sandbox precisou montar o alias de Python declarado pelo uv, apontando apenas
para o mesmo prefixo read-only. Não foi montado o workspace inteiro para resolver
esse problema. Runtime sem rede via bwrap, fonte/venv/worker read-only, somente
diretório de saída privado read-write; CUDA desabilitado. Não foram desativadas
as proteções para fazer o ensaio passar.

## Ensaio realmente executado

Modelo local determinístico `relu(x @ W + b)`, entrada [1,32], saída [1,64],
pesos FP32 constantes, sem fit/otimizador/model zoo. Conversão para TFLite FP32,
receita real `dynamic_wi8_afp32` e execução dos dois modelos no intérprete LiteRT
CPU, usando 16 entradas sintéticas e seed42.
INT8 aqui se refere à quantização dinâmica dos pesos; entradas/saídas e
ativações do contrato continuam FP32, não é promessa de grafo integralmente inteiro.

| Medida | Resultado observado | Gate congelado |
|---|---:|---:|
| FP32 convertido vs fórmula: max_abs | 4,76837158203125e-7 | <=1e-4 |
| INT8 vs FP32: MSE | 2,9257122141732527e-5 | <=1e-3 |
| INT8 vs FP32: max_abs | 0,022112131118774414 | <=0,1 |
| Tensores INT8 encontrados | 2 | >=1 |
| Tamanho FP32 | 9.424 bytes | medição, não gate de qualidade |
| Tamanho quantizado | 4.104 bytes | medição, não gate de qualidade |

O arquivo desse toy ficou com 43,55% do tamanho original (redução de 56,45%).
Não foi medido ganho de velocidade e não se generaliza esse resultado para LLMs,
voz, classificação real ou dispositivos Android. Sanity check numérico não é
preservação de qualidade semântica. O método validate() aleatório upstream não
foi usado como substituto de avaliação da tarefa.

O Core revalida hashes, tamanhos, marcador TFL3 e recomputa os erros a partir
de evaluation.json em stdlib antes de publicar o relatório. Fonte de pesos foi
o próprio programa, não um checkpoint externo. A execução interrompida não
deixou artefato ou processo ativo; isso foi inspecionado antes da retomada.

Artefatos do run synthetic-int8: float.tflite, quantized.tflite, recipe.json,
evaluation.json, metrics.json e manifest.json, em `.ai-edge-quantizer/runs/`.
Relatórios e métricas exportáveis ficam em `outputs/core-r928/` no fechamento.

## Interface

```bash
python3 -m marceloclaro.cli edge-quantizer status
python3 -m marceloclaro.cli edge-quantizer source-plan
python3 -m marceloclaro.cli edge-quantizer acquire-source --confirm
python3 -m marceloclaro.cli edge-quantizer environment-plan
python3 -m marceloclaro.cli edge-quantizer prepare --confirm
python3 -m marceloclaro.cli edge-quantizer demo-plan --run-id synthetic-int8
python3 -m marceloclaro.cli edge-quantizer demo --run-id synthetic-int8 --confirm
python3 -m marceloclaro.cli edge-quantizer report --run-id synthetic-int8
```

API primária: `ai_edge_quantizer_action(config)` com operações fechadas; planos
não ganham metadados após o selo. Efeitos exigem confirmação. O comando
`/edge-quantizer` requer reiniciar o OpenCode para descoberta.
Status de ambiente é verificação de recibos, não prova de quantização executada.
Só o demo validado declara synthetic_inference_executed=true. Falha incerta
não é promovida a sucesso nem afirma falsamente que nada foi executado.

## Limites

- Esta primeira integração aceita o toy e receita INT8 fixos, não modelos,
  caminhos de datasets, scripts ou receitas arbitrários.
- Não implementa conversor genérico PyTorch/LoRA/GGUF → TFLite.
- .tflite, .task e .litertlm não são intercambiáveis. Este toy não é um LLM
  importável no Gallery por simples troca de extensão.
- Preparação usa rede para código/dependências oficiais; runtime fica sem rede.
- Sem treino, dados do usuário, alteração de policy.json ou validação científica
  externa. Licença do código não relicencia modelos de terceiros.
- Revisão externa delegada excedeu o prazo e não foi contabilizada como parecer
  concluído. Mudanças concorrentes R929 foram preservadas; runners recusaram
  snapshots alterados em vez de falsificar histórico estável.

## Fechamento local

- 27 casos focais R928 e seleção ampliada de **469 testes**, sem falhas, erros
  ou skips; não é suíte integral do repositório.
- SpecVerifier: **6/6 critérios**, software_delivery_gate, RED
  `tdd-dbbad3858b1940ee96c115b0c86eee5a` e GREEN
  `tdd-7a988ff52b9f42679efc208f075d15ec`, emitidos pelo runtime local.
- Relatórios recusam alegação externa indevida, métricas divergentes dos arrays
  e deriva dos artefatos mesmo se o selo JSON for recalculado. A fachada não
  acrescenta metadados dentro de resultados já selados.
- A seleção R929 de 643 casos e seus recibos permanecem separados, em
  `docs/REVISAO_CORE_R929.md` e `docs/evidence/r929/`.
- Doctor estrutural: 21 verificações aprovadas, 1 advertência por 78 entradas
  históricas preservadas/não modeladas e 0 falhas. Nenhuma conversão inferida
  dessas entradas foi feita para remover a advertência.

Evidências: `outputs/core-r928/final-gates.json`, `regressions-final.json`,
`selected-tests-final.xml` e `demo-report.json`. Aceite computacional local,
sem validação científica externa ou medição em aparelho Android.
