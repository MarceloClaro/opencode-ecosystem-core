# Auditoria de Codigo Cientifico

## Finalidade

Este documento define como auditar codigo, scripts, notebooks e pipelines usados no artigo para que eles sejam:

- tecnicamente corretos;
- documentalmente ancorados;
- cientificamente justificaveis;
- rastreaveis;
- reproduziveis.

## Hierarquia de verificacao

Sempre auditar nesta ordem:

1. documentacao oficial;
2. referencia oficial da linguagem ou biblioteca;
3. repositorio oficial do projeto;
4. testes, exemplos e recipes oficiais;
5. artigo metodologico original;
6. discussoes de mantenedores;
7. fontes secundarias.

## Regras para documentacao oficial

- usar documentacao oficial como ancora primaria de assinatura, comportamento esperado e limitacoes;
- registrar a pagina, secao, classe, funcao ou operador relevante;
- distinguir claramente API estavel de recurso experimental;
- nao inferir comportamento a partir de exemplo isolado sem checar a especificacao.

## Regras para auditoria de repositorio

Quando a documentacao oficial for insuficiente, verificar no repositorio oficial:

- README principal;
- exemplos mantidos;
- testes automatizados;
- docs internas;
- changelog;
- issues ou discussions apenas quando a ambiguidade persistir.

## Regras para GitHub e repositorios de terceiros

- priorizar repositorios oficiais, da organizacao mantenedora ou dos autores do metodo;
- snippets de terceiros so podem ser usados com nota de adaptacao e validacao propria;
- codigo de terceiros nunca pode entrar como caixa-preta inquestionada;
- repositorio popular nao substitui documentacao oficial.

## Pacote minimo de auditoria por trecho de codigo

Para cada trecho relevante, registrar:

- objetivo do trecho;
- origem tecnica;
- linguagem e biblioteca;
- funcao, classe, metodo ou operador usado;
- ancora documental principal;
- ancora complementar em repositorio ou paper;
- adaptacoes feitas;
- riscos conhecidos;
- efeito desse trecho no resultado cientifico.

## Itens obrigatorios de verificacao

### Corretude tecnica

- a chamada de API existe e corresponde ao uso reportado;
- os parametros criticos foram usados de forma compativel;
- o tipo de entrada e o tipo de saida fazem sentido;
- o trecho nao contradiz a documentacao oficial.

### Corretude cientifica

- o codigo implementa o metodo que o texto afirma implementar;
- a metrica calculada corresponde a definicao metodologica reportada;
- os dados usados pelo codigo correspondem ao dataset declarado;
- as seeds e configuracoes explicam a variabilidade reportada.

### Corretude de reproducibilidade

- dependencias e versoes estao declaradas;
- existe instrucao minima de execucao;
- os outputs esperados sao conhecidos;
- falhas ou restricoes foram registradas.

## Linguagens e ecossistemas cobertos

Este protocolo vale, sem se limitar a:

- Python, R, Julia, MATLAB, Octave, SAS, Stata, SPSS;
- SQL e motores analiticos;
- PyTorch, TensorFlow, Keras, JAX, scikit-learn, statsmodels, xgboost;
- Bioconductor, Scanpy, Seurat, pysam, samtools, bcftools;
- RDKit, OpenMM, DeepChem, bibliotecas de quimioinformatica e simulacao;
- spaCy, NLTK, transformers, gensim, stanza e stacks de NLP;
- OpenCV, torchvision, detectron2, MONAI e stacks de visao;
- Qiskit, Cirq, PennyLane e bibliotecas quanticas correlatas.

## Casos que exigem congelamento imediato

- snippet sem origem verificavel;
- incompatibilidade entre codigo e metodo descrito;
- dependencia critica sem identificacao;
- metrica calculada de forma diferente da descrita no manuscrito;
- notebook irreprodutivel sem script, pipeline ou passo equivalente;
- uso de API experimental sem nota de risco;
- resultado numerico que nao fecha com o registro de experimento.

## Resultado esperado da auditoria

A auditoria de codigo deve entregar um parecer que diga, de modo rastreavel:

- o que foi auditado;
- contra quais fontes tecnicas;
- com quais ressalvas;
- com qual impacto sobre o artigo;
- e se o codigo esta apto, apto com ressalvas ou bloqueado.
