# Repositórios complementares: análise em leitura

Os links foram inspecionados, não instalados ou executados. A integração
explicitamente aprovada foi AI Edge Quantizer com toy sintético. Esta análise
não autoriza download de modelos, APKs, execução de notebooks ou agentes.

## Papéis e limites

| Repositório e revisão | Licença raiz | Papel potencial | Estado da análise |
|---|---|---|---|
| MarceloClaro/gallery — df56977f720a110e00ffff2c2a90626dde32c536 | Apache-2.0 | Aplicativo consumidor on-device/Android e interface de avaliação | README dessa revisão documenta importação .task; não comprova importação do toy .tflite nem .litertlm |
| MarceloClaro/OpenManus — fcb43dcb00291ce846192eded67a911733c65bb4 | Unlicense | Referência de UI/workflow e possível executor auxiliar após correções | Código contém placeholders e inconsistências; não é agente autônomo pronto para substituir o Core |
| MarceloClaro/lqc-textbook — e32d5c5da3ed99c218af0c7d0cf09073c1441af1 | MIT, copyright Diego Emilio Serrano 2024 | Material educacional/referência rastreável de computação quântica com Python/Qiskit | Livro/notebooks, não runtime de orquestração nem algoritmo de quantização neural |

Licença raiz deve ser preservada e direitos de imagens/material citado precisam
ser conferidos antes de redistribuição ou criação de dataset. Um fork não prova
compatibilidade atual com o upstream ou validação dos resultados.

## Gallery

O fork vem de google-ai-edge/gallery. É aplicativo Android/Kotlin experimental;
o README promete funcionamento local após carregar modelos, Prompt Lab, chat e
avaliação. Esses recursos são declarados, não foram medidos em aparelho nesta
sessão. A revisão fornecida documenta modelos .task e LLM Inference API.

Integração futura requer modelo/arquitetura e empacotamento compatíveis, tokenizer,
licença dos pesos e teste real no dispositivo. O fluxo do quantizador gera um
FlatBuffer .tflite: isso sozinho não o torna pacote .task/.litertlm nem modelo
conversacional. Não foi instalado APK ou Android SDK.

## OpenManus: distinguir nome, README e implementação

Este fork tem parent emeryinlover/OpenManus e o README referencia henryalps;
não deve ser confundido automaticamente com outras implementações homônimas.
Evidências de código na revisão fixa:

- src/llms/llm.py retorna `PlaceholderLLM`, cujo invoke devolve string, não uma
  integração LLM operacional.
- src/agents/coordinator.py contém plano placeholder fixo para example.com,
  independentemente da tarefa, e retorna status success genericamente.
- browser_agent.py apenas encaminha mensagens ao placeholder.
- nodes/browser_node.py espera resultado indexável por messages, incompatível
  com a string retornada; também usa Command sem import no arquivo inspecionado.

São achados estáticos, não incidentes de execução medidos. O README descreve
uma arquitetura e ambições; não demonstra GAIA, autonomia equivalente ao Manus,
isolamento ou correção. Não foi iniciado docker-compose, browser, executor de
código ou serviço HTTP. Se futuramente integrado, MarceloClaro permanece o
primário, com contratos A2A, orçamento/permissões e recibos — nunca execução livre
de prompts ou ferramentas por mera importação.

## LQC Textbook

Fork de learn-quantum/lqc-textbook, apresentado como *Learn Quantum Computing
using Python*, Diego Emilio Serrano (2024), com capítulos, Jupyter Book e Qiskit.
Bom candidato a bibliografia/estudo com referência por capítulo e revisão fixa.
Não foi indexado automaticamente para RAG, usado em fine-tuning ou executado.
Notebooks podem executar código: qualquer ensaio deve ter ambiente e células
explicitamente selecionados. Quantização de redes e computação quântica são
problemas diferentes; o livro não substitui o quantizador neural.

## Fontes primárias consultadas

- https://github.com/MarceloClaro/gallery/tree/df56977f720a110e00ffff2c2a90626dde32c536
- https://github.com/MarceloClaro/OpenManus/tree/fcb43dcb00291ce846192eded67a911733c65bb4
- https://github.com/MarceloClaro/lqc-textbook/tree/e32d5c5da3ed99c218af0c7d0cf09073c1441af1
- README, LICENSE e árvores Git via API; nos achados OpenManus, os arquivos de
  código acima foram lidos na revisão identificada, sem executar suas instruções.
