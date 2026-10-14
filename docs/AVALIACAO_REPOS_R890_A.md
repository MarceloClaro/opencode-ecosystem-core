# Avaliação de repositórios — R890, lote A

Revisão dirigida de 14 de outubro de 2026. Foram lidos arquivos públicos dos
cinco forks indicados, fixados por commit e hash. Nenhum instalador, treinamento,
modelo, circuito remoto ou script de terceiro foi executado. Os demais dez
repositórios do pedido pertencem aos lotes B e C.

| Repositório | Commit consultado | Decisão |
|---|---|---|
| deepchem | `5dafef7771067f3baddedeafd579e0e179def87f` | Especialista opcional para química/biologia; sem instalar no núcleo. |
| ipleiria-thesis | `faadc18cb4bacc407abc5fec4520c1ea80b2efd0` | Referência de organização editorial; não substitui modelo institucional brasileiro. |
| torchquantum | `57f19172981b8e1d360038a62bec53e157f3a57d` | Adaptar a distinção entre simulação, hardware e evidência no simulador já existente. |
| ai-edge-quantizer | `87cda53576a55a71114a4945b3ff18e27c2fa42b` | Ferramenta futura em ambiente separado, condicionada a modelo/avaliação definidos. |
| AI-ML-Cheatsheets | `65f5a291b42ac3ad8ff27f6db4d439c94b6e18b6` | Referência didática opcional; não é runtime nem evidência de qualidade. |

O [manifesto do lote](repo-reviews-r890-a.json) identifica arquivos amostrados,
hashes, licenças declaradas, dependências, rede e limites.

## Alcance do REA

As cinco árvores GitHub foram recebidas sem truncagem e não contêm arquivos
JavaScript ou HTML. Seus alvos relevantes nesta revisão são Python, TeX e PDF.
O contrato atual de `LocalReaAssistant.inspect` admite JavaScript, HTML, nativo,
.NET, plist, Android, firmware e layout ELF; não oferece análise dedicada para
Python, LaTeX ou PDF. Não foi forçado um parser nativo sobre esses documentos.

O primário `MarceloClaroOrchestrator(auto_load_agents=False).rea_action(status)`
foi executado para registrar o inventário atual: instalação disponível,
`verification=installation_only`. Isso **não é análise dos cinco projetos**.
O recibo `outputs/core-r890/a-rea-capability.json` conserva o resultado e o hash
do contrato inspecionado. A aquisição de fontes consultou GitHub; nenhuma
alegação de isolamento dessa aquisição é feita.

## DeepChem

O [fork fixado](https://github.com/MarceloClaro/deepchem/tree/5dafef7771067f3baddedeafd579e0e179def87f)
é uma biblioteca MIT de aprendizado para química, biologia e materiais. Pode
contribuir como especialista de domínio, não como novo coordenador de agentes.
O [loader MoleculeNet](https://github.com/MarceloClaro/deepchem/blob/5dafef7771067f3baddedeafd579e0e179def87f/deepchem/molnet/load_function/molnet_loader.py)
separa treino/validação/teste e ajusta transformações a partir do treino. Esse
padrão é útil para experimentos e comparações do Core, sem presumir eficácia
clínica ou validade de resultados químicos.

O [setup](https://github.com/MarceloClaro/deepchem/blob/5dafef7771067f3baddedeafd579e0e179def87f/setup.py)
restringe Python a `>=3.7,<3.13`; o ambiente principal usa Python 3.14. Também
fixa `numpy<2` e extras como PyTorch 2.2.1 ou JAX 0.4.30, além de RDKit/SciPy.
A descrição de versões no README é mais estreita que a do setup. Não foi
executado resolvedor nem instalada combinação alternativa.

Os [utilitários de dados](https://github.com/MarceloClaro/deepchem/blob/5dafef7771067f3baddedeafd579e0e179def87f/deepchem/utils/data_utils.py)
contêm download por `urlretrieve` e desserialização pickle/joblib, inclusive
`np.load(..., allow_pickle=True)`. Um futuro adapter deve usar dados explicitamente
confiáveis, origem/hash/split registrados e downloads separados da análise. Não
há base nesta amostra para afirmar ausência de telemetria de dependências;
Weights & Biases aparece como integração opcional de treinamento.

Pontos existentes: `mci/experiment_designer.py`, `mci/preregistration_protocol.py`,
`mci/statistical_validator.py` e `integrations/scientific_plugins.py`. Prioridade
baixa para a orquestração geral; útil quando uma tarefa química concreta exigir.

## ipleiria-thesis

O [template](https://github.com/MarceloClaro/ipleiria-thesis/tree/faadc18cb4bacc407abc5fec4520c1ea80b2efd0)
declara LPPL 1.3c e organização modular de capítulos, estilos, metadados,
elementos pré/pós-textuais e referências. Pode fornecer uma referência de
estrutura para o livro e artefatos acadêmicos do Core. Seu perfil institucional
é o Politécnico de Leiria; não comprova conformidade ABNT ou adequação à PUCRS.

A [configuração bibliográfica](https://github.com/MarceloClaro/ipleiria-thesis/blob/faadc18cb4bacc407abc5fec4520c1ea80b2efd0/Configurations/03-References.sty)
é `authoryear` com biblatex/biber. A [configuração de compilação](https://github.com/MarceloClaro/ipleiria-thesis/blob/faadc18cb4bacc407abc5fec4520c1ea80b2efd0/.latexmkrc)
usa XeLaTeX, `biber --validate-datamodel`, glossários e shell escape, e executa
comandos do sistema. O workflow também habilita shell escape. Esses arquivos
foram lidos; não foram executados nem copiados para os projetos acadêmicos.
Fontes/imagens do template não tiveram seus termos auditados por transitividade.

Adaptação possível: validar metadados/referências e separar configurações de
conteúdo no fluxo existente `integrations/artigo_academico_mcp.py`. Preservar os
modelos institucionais e campos pendentes do usuário; não reformatar manuscritos
como efeito colateral desta curadoria.

## TorchQuantum e lacuna concreta do Core

O [README](https://github.com/MarceloClaro/torchquantum/blob/57f19172981b8e1d360038a62bec53e157f3a57d/README.md)
distingue simulação de circuitos em hardware clássico de execução em máquina
quântica. O código declara MIT, mas exige um conjunto amplo: PyTorch,
TensorFlow, Qiskit 1.4.3, Qiskit Runtime/Aer, PySCF e outros. A declaração genérica
Python>=3.5 não demonstra compatibilidade de todas as dependências com Python3.14.
Não foi feita instalação, acesso IBM ou teste de GPU/QPU.

O [processador Qiskit](https://github.com/MarceloClaro/torchquantum/blob/57f19172981b8e1d360038a62bec53e157f3a57d/torchquantum/plugin/qiskit/qiskit_processor.py#L181)
seleciona serviço IBM quando `use_real_qc=True` e AerSampler no ramo clássico.
Mesmo no ramo clássico, a obtenção de modelo de ruído por nome com token pode
consultar IBM remotamente. Portanto, declarar simulação não demonstra operação
sem rede; backend, fonte do ruído, credenciais e política de rede são dimensões
separadas.

Essa distinção expôs problemas no caminho já existente
`reasoning/engines.py::QuantumReasoningEngine` e `reasoning/quantum.py`:

- A suíte Bell/GHZ/superposição ignora o significado da consulta, mas o motor
  devolvia confiança fixa 0,85 e uma conclusão de experimentos executados.
- A métrica `fidelity` somava frequências no suporte da própria distribuição
  amostrada. Na reprodução com um único shot uniforme, resultou 1, embora a
  distância de variação total em relação à distribuição exata fosse 0,75.
- `entanglement_entropy` calculava Shannon da distribuição de medição, não uma
  medida de emaranhamento de uma partição explicitada.
- A presença de Qiskit liberava mais de 20 qubits, mas o código continuava
  alocando a lista Python de dimensão `2**n`; não havia dispatcher MPS.

O reprodutor `outputs/core-r890/a-core-quantum-reproducer.json` executou somente
código pré-existente do próprio Core, com **2 qubits, 1–8 shots e uma seed**.
Consultas diferentes produziram a mesma conclusão. Não foram executadas
alocações grandes; o problema do limite foi lido no código. Esses resultados
locais não avaliam TorchQuantum nem demonstram equipamento quântico.

Adaptação escolhida na especificação R890: identificar `classical_simulation`,
backend `python_statevector`, hardware quântico ausente e `query_evaluated=false`;
retornar configuração/métricas por seed e digest; separar massa de suporte,
distância amostral e Shannon da medição; impor orçamento antes de alocações e
laços. O primário deve guardar apenas resumo tipado e digest no MetaBus, sem
promover confiança a partir da própria simulação. Isso aproveita a distinção
observada no upstream e corrige o caminho existente, sem instalar outro runtime.

## AI Edge Quantizer

O [quantizador](https://github.com/MarceloClaro/ai-edge-quantizer/tree/87cda53576a55a71114a4945b3ff18e27c2fa42b)
é Apache 2.0, versão fonte 0.3.0, voltado a modelo FP32 LiteRT em FlatBuffer
`.tflite` e uma receita explícita de quantização por operador/escopo. O setup
usa `tf-nightly` e `ai-edge-litert-nightly`; o README lista Python3.9–3.12 em
Linux/macOS. Não é prudente inferir encaixe direto no servidor LiteRT-LM do Core
sem demonstrar formato de entrada, suporte de operações e contrato de execução.

O contrato de [validate](https://github.com/MarceloClaro/ai-edge-quantizer/blob/87cda53576a55a71114a4945b3ff18e27c2fa42b/ai_edge_quantizer/quantizer.py#L297)
é especialmente relevante: sem dados de teste, gera uma amostra normal aleatória
e declara a comparação numérica como **sanity check**, exigindo avaliação da
tarefa para qualidade. Redução de bytes, erro tensorial e desempenho final são
medidas distintas. O resultado compara modelo de referência e quantizado; não
promete que menor artefato conserve a utilidade para qualquer tarefa.

Uma futura avaliação deve fixar modelo original/quantizado, receita, hashes,
dados de calibração separados do teste, backend e orçamento; medir tamanho,
latência e erro/qualidade da tarefa. Esta revisão não converteu modelo, baixou
pesos ou mediu aceleração. A contribuição imediata é a disciplina de medida,
coerente com os limites exigidos para a suíte clássica do Core.

## AI-ML-Cheatsheets

A [árvore consultada](https://github.com/MarceloClaro/AI-ML-Cheatsheets/tree/65f5a291b42ac3ad8ff27f6db4d439c94b6e18b6)
contém nove arquivos: README, licença e sete PDFs de consulta. Não há runtime,
MCP, API de agentes ou pipeline executável para integrar. A licença MIT é uma
declaração na raiz da coleção; a origem e os termos específicos de cada PDF
não foram auditados. Não foram redistribuídos nem usados como evidência de
correção de um motor.

Podem apoiar uma biblioteca didática com autor/título/página/origem/hash
rastreáveis, após triagem documental. Não devem substituir fontes científicas
primárias em manuscritos nem transformar uma lista de fórmulas em validação
externa do raciocínio. Os links promocionais do README são recursos externos,
não uma dependência necessária do Core.

## Decisão e limites

A adaptação de maior utilidade imediata é tornar honesto e delimitado o
simulador já integrado. DeepChem e o quantizador permanecem ferramentas de
domínio futuras em ambientes separados; o template e as folhas de consulta são
referências documentais. Nenhum dos cinco exige um segundo orquestrador.

O levantamento não comprova ganhos de tokens, velocidade, qualidade editorial,
eficácia clínica, desempenho quântico ou ausência integral de falhas. O status
da implementação e os testes finais R890 devem ser consultados no recibo de
fechamento do ciclo; esta revisão preserva separadamente as fontes observadas
e a recomendação que motivou a adaptação.

## Adaptação implementada e verificação local

Após observar RED, o ciclo R890 corrigiu o caminho de simulação já existente.
O statevector impõe 2–20 qubits incondicionalmente, até 10.000 shots e até dez
seeds, cada uma inteira entre zero e `2**63-1`, com tipos estritos e recusa de configuração vazia/inválida antes dos
circuitos. Índices de portas e ângulos inválidos não alteram parcialmente o
estado. A medição prepara pesos cumulativos uma vez e conserva reprodutibilidade.

A evidência do motor agora retorna configuração, contagens por seed, massa de
suporte, distância de variação total e Shannon de medição, com hash canônico do
relatório. O nome legado `entanglement_entropy` permanece somente como alias
depreciado explícito de Shannon. Bell identifica os seus dois qubits, mesmo
quando GHZ/superposição usam a quantidade solicitada. A confiança numérica
legada é zero com indicação de consulta não avaliada, não uma probabilidade.

O primário preserva a evidência no retorno e guarda apenas backend, natureza de
execução, ausência de hardware, ausência de avaliação da consulta, configuração
e digest na memória. Não armazena histogramas nesse resumo nem altera o ledger
por êxito da própria simulação. O caminho direto `quantum_experiment` também
conserva essa separação, sem EMA automática de confiança.

O fechamento dirigido aprovou **291 testes**, incluindo **41 casos novos R890**,
consumidores antigos e regressões R886/R818/R821. Ruff aprovou os arquivos
`quantum.py`, `metacognitive_loop.py` e os novos testes; a checagem de diferenças
não encontrou erros de espaço. Recibos: `outputs/core-r890/a-release-final.xml`,
`a-ruff.txt` e `a-core-after-fix.json`. O reprodutor anterior à correção foi
preservado separadamente. Essa execução não representa aprovação da suíte
integral, ganho de desempenho medido ou validação externa.

A revisão independente do limite de seeds incluiu os valores adversariais `-1`,
`2**63` e `1 << 15000`: todos são recusados antes de construir qualquer circuito.
As fronteiras zero e `2**63-1` permanecem reproduzíveis e serializáveis. O limite
global de conversão de inteiros em texto do Python não foi alterado. O RED
adversarial está em `outputs/core-r890/a-seed-magnitude-red.xml` e os hashes finais
foram atualizados no manifesto e no recibo de execução após essa correção.
