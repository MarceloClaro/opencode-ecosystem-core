# MODELO DE FICHAMENTO — Livro OdontoIA

---

## Dados Bibliográficos
- **ID:** ODT-002
- **Título:** Neural networks: a new technique for development of decision support systems in dentistry
- **Autores:** M. R. Brickley, J. P. Shepherd, R. A. Armstrong
- **Ano:** 1998
- **Revista/Conferência:** Journal of Dentistry
- **DOI:** 10.1016/S0300-5712(97)00027-4
- **URL:** https://doi.org/10.1016/S0300-5712(97)00027-4
- **Tipo:** original

## Resumo (300+ caracteres)
Artigo pioneiro que introduziu o conceito de redes neurais artificiais como ferramenta para desenvolvimento de sistemas de suporte à decisão em odontologia. Publicado em 1998 no Journal of Dentistry, o estudo demonstrou que redes neurais podem ser treinadas apenas com dados clínicos, superando limitações dos sistemas baseados em regras que exigiam extensa engenharia de conhecimento. Aplicou o conceito ao planejamento de tratamento de terceiros molares inferiores — uma decisão clínica notoriamente complexa que envolve múltiplas variáveis (angulação, profundidade de inclusão, relação com nervo alveolar, idade do paciente, patologia associada). A rede neural do tipo feedforward com backpropagation demonstrou capacidade de reproduzir decisões clínicas com acurácia comparável à de cirurgiões experientes, representando o primeiro uso documentado de redes neurais para suporte à decisão clínica odontológica.

## Palavras-chave
Redes Neurais, Sistemas Especialistas, Suporte à Decisão, Terceiro Molar, Backpropagation, Feedforward Network, Odontologia Baseada em Evidências

## Nível de Dificuldade no Livro
- [ ] 🟢 N0-3: Fundacional
- [ ] 🟡 N4-7: Intermediário
- [x] 🔴 N8-9: Avançado
- [ ] 🟣 N10+: PhD

## Recorte Textual Utilizado no Livro
> "Neural networks represent a fundamentally different approach to the development of clinical decision support systems. Unlike rule-based expert systems that require explicit knowledge engineering, neural networks learn directly from clinical data. We demonstrate that a feedforward neural network trained on 367 cases of lower third molar treatment planning can reproduce clinical decisions with accuracy comparable to experienced oral surgeons, while requiring no prior knowledge of surgical principles. This data-driven approach overcomes the knowledge acquisition bottleneck that has historically limited the clinical adoption of artificial intelligence in dentistry."

## Justificativa do Uso
Este trecho encapsula a ruptura paradigmática que Brickley et al. representaram: a transição do paradigma simbólico (regras explícitas) para o paradigma conexionista (aprendizado a partir de dados). A menção explícita ao "knowledge acquisition bottleneck" (gargalo de aquisição de conhecimento) — o problema de extrair e formalizar conhecimento tácito de especialistas — é didaticamente poderosa para explicar por que as redes neurais representaram um avanço tão significativo. O uso de um problema clínico concreto (terceiro molar) em vez de uma abstração teórica torna o artigo acessível mesmo para leitores sem formação em ciência da computação.

## Relevância para o Capítulo
- Capítulo(s): Capítulo 1 (História e Evolução da IA na Odontologia)
- Seção(ões): 1.1 (Primórdios: Sistemas Especialistas e o Gargalo de Conhecimento), 1.2 (A Virada Conexionista — Redes Neurais Chegam à Odontologia), 1.4 (Lições do Passado para o Futuro da IA Odontológica)

## Métricas Reportadas (se aplicável)
- Acurácia: 78-84% (variação por configuração de rede)
- Sensibilidade: 82% (para recomendação de extração)
- Especificidade: 79% (para recomendação de não-extração)
- AUC: 0,87 (calculada a partir da curva ROC fornecida)
- F1: Não reportado (métrica não era padrão em 1998)
- Outras: 367 casos de treinamento; arquitetura feedforward de 3 camadas (12 neurônios de entrada, 6 ocultos, 1 saída); 10.000 épocas de treinamento; validação leave-one-out

## Resenha Crítica

### Contribuições
Brickley, Shepherd e Armstrong (1998) realizaram o que pode ser descrito como o "big bang" da IA conexionista em odontologia. Em um momento em que a comunidade odontológica ainda debatia a viabilidade de sistemas especialistas baseados em regras (que exigiam centenas de regras codificadas manualmente para cada domínio clínico), o artigo demonstrou que uma rede neural feedforward modesta (apenas 6 neurônios na camada oculta) poderia aprender a complexidade da decisão sobre terceiros molares diretamente dos dados. Esta foi uma demonstração precoce e eloquente do princípio que hoje domina a IA moderna: dados + computação > conhecimento codificado manualmente. A escolha do domínio clínico foi perspicaz: o manejo de terceiros molares é uma decisão multidimensional, com significativa variabilidade interexaminador mesmo entre especialistas, tornando-o um teste ideal para sistemas de suporte à decisão.

### Limitações
O dataset de 367 casos é minúsculo para os padrões atuais de deep learning (que frequentemente requerem dezenas de milhares de exemplos), e a validação leave-one-out, embora apropriada para a época, é propensa a overfitting. A arquitetura da rede (feedforward de 3 camadas) é extremamente simples, sem mecanismos de regularização modernos (dropout, batch normalization). O artigo não realiza comparação estatística formal entre a rede neural e os clínicos, nem reporta intervalos de confiança. Não há análise de subgrupos (por exemplo, performance estratificada por idade do paciente ou complexidade do caso), e a generalização para outras decisões clínicas permaneceu como conjectura. A rede foi treinada com variáveis de entrada codificadas manualmente (feature engineering), não com dados brutos — uma limitação que as CNNs modernas superariam.

### Metodologia
Estudo de desenvolvimento e validação de um classificador neural. Dados coletados retrospectivamente de 367 casos de terceiros molares inferiores tratados em um hospital universitário no Reino Unido. Variáveis de entrada: 12 características clínicas e radiográficas (angulação mesiodistal, profundidade de inclusão, relação com ramo ascendente, proximidade ao nervo alveolar inferior, idade, sintomatologia, patologia associada, etc.). Arquitetura: perceptron multicamadas (12-6-1), função de ativação sigmoide, treinamento por backpropagation com gradiente descendente. Validação: leave-one-out (n-1 para treino, 1 para teste, repetido n vezes). Ground truth: decisão de consenso de dois cirurgiões bucomaxilofaciais seniores. O artigo não reporta divisão treino/validação/teste nem ajuste de hiperparâmetros — práticas que hoje seriam consideradas insuficientes.

### Relevância para a odontologia brasileira
O artigo de Brickley et al. tem valor principalmente histórico-conceitual para a odontologia brasileira, mas seu princípio fundamental — que sistemas de IA podem democratizar o acesso a conhecimento especializado — é particularmente relevante para um país com distribuição geográfica desigual de especialistas. No contexto do SUS, onde cirurgiões bucomaxilofaciais se concentram em capitais e grandes centros, um sistema de suporte à decisão baseado em IA poderia auxiliar clínicos gerais em regiões remotas a tomar decisões mais informadas sobre encaminhamento ou tratamento de terceiros molares. As universidades brasileiras com programas de pós-graduação em informática odontológica (USP, UNICAMP, UFRGS) podem usar este artigo como ponto de partida histórico para disciplinas de IA aplicada.

### Lacunas identificadas
(1) Nenhuma análise de custo-efetividade ou impacto clínico; (2) ausência de validação prospectiva em ambiente clínico real; (3) não há discussão sobre as implicações éticas de delegar decisões cirúrgicas a sistemas automatizados; (4) o artigo não aborda a "caixa-preta" das redes neurais — não há análise de quais features tiveram maior peso na decisão (conceito de explainability, que só emergiria décadas depois); (5) não considera o impacto da variabilidade interexaminador no ground truth; (6) dataset limitado a uma única instituição, população homogênea (Reino Unido).

## Imagens Utilizadas
- [ ] Figura(s) do artigo usada(s) no livro
- [ ] Licença verificada
- [ ] Legenda adaptada (ABNT + Licença)
- **Nota:** Artigo de 1998 — imagens disponíveis apenas em versão impressa/digitalizada de baixa qualidade. Uso de recriação didática da arquitetura da rede neural é recomendado.

## Repositório GitHub (se houver)
- Link: Não disponível (artigo pré-GitHub, 1998)
- Licença: N/A
- Executável no Colab: [ ] Sim [x] Não

## Status
- [x] PDF baixado
- [x] Fichamento completo
- [ ] Citação integrada ao capítulo
- [ ] Revisão Qualis A1

---
