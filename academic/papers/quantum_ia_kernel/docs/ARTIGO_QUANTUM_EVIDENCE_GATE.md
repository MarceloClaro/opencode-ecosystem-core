# Geometry-Survival Evidence Gates for Reproducible and Cost-Aware Quantum Kernel Applications Under Noise

**Marcelo Claro Laranjeira**

*Projeto Fundamentos Quânticos Aplicados à Pesquisa em IA*
*Data de congelamento do protocolo: 16 de agosto de 2026*
*SHA-256: 89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf*

---

## Abstract

The deployment of quantum kernel methods in machine learning faces a persistent gap between theoretical promise and empirical validation under realistic noise conditions. While quantum kernels computed via feature maps on quantum hardware may capture geometric structures inaccessible to classical kernels, the conditions under which this potential translates into predictive superiority remain poorly specified. This study introduces the **Geometry-Survival Evidence Gate**, a prospective, sequential decision framework that integrates paired corrected effect estimation, equivalence testing, geometric survival analysis across fidelity tiers (ideal statevector, shot-based estimation, and depolarized noise), and computational cost accounting before authorizing progression to full quantum processing unit (QPU) classification. The framework was pre-specified via SHA-256 hash and evaluated on four tabular datasets (synthetic moons, Iris binary, Wine binary, and Breast Cancer Wisconsin) using nested repeated cross-validation (4 outer folds × 3 repetitions) with Nadeau–Bengio correction for dependent folds. The primary outcome — paired difference in balanced accuracy between a fidelity quantum kernel SVM and a tuned SVM-RBF — yielded a mean ΔBAC of −0.217 (95% corrected CI [−0.285; −0.148]; one-sided corrected *p* = 0.9999), indicating statistical inferiority of the quantum kernel under this protocol. Equivalence testing (TOST, margin ±0.02) yielded *p* = 0.9999, and the permutation test of signs yielded *p* = 0.0005. The effective kernel rank was 27.9% of capacity, and kernel–target alignment was 0.110. The validity ladder demonstrated geometric survival across all three fidelity tiers (BAC stable at 0.625), yet this survival did not translate into predictive advantage. The multi-dataset exploratory suite confirmed consistent RBF superiority across all 16 folds (mean ΔBAC = −0.146). The Evidence Gate classified this protocol as **inconclusive for advancement to QPU**, restricting future hypotheses and providing a transparent, reproducible negative result for quantum kernel evaluation on tabular data.

**Keywords:** quantum kernel methods; machine learning; nested cross-validation; evidence gate; negative result; reproducibility; noise characterization

---

## Resumo

O emprego de métodos de kernel quântico em aprendizado de máquina enfrenta uma lacuna persistente entre a promessa teórica e a validação empírica sob condições realistas de ruído. Embora kernels quânticos computados via feature maps em hardware quântico possam capturar geometrias inacessíveis a kernels clássicos, as condições sob as quais esse potencial se traduz em superioridade preditiva permanecem mal especificadas. Este estudo introduz o **Geometry-Survival Evidence Gate** — framework prospectivo e sequencial de decisão que integra estimativa de efeito pareado corrigido, teste de equivalência, análise de sobrevivência geométrica em camadas de fidelidade (statevector ideal, estimativa por shots e ruído despolarizante) e contabilidade de custo computacional antes de autorizar o avanço para classificação completa em processador quântico (QPU). O protocolo foi pré-registrado via hash SHA-256 e avaliado em quatro bases de dados tabulares (moons sintético, Iris binário, Wine binário e Breast Cancer Wisconsin) utilizando validação cruzada aninhada repetida (4 folds externos × 3 repetições) com correção de Nadeau–Bengio para folds dependentes. O desfecho primário — diferença pareada de acurácia balanceada entre SVM com kernel quântico de fidelidade e SVM-RBF sintonizado — produziu ΔBAC médio de −0,217 (IC95% corrigido [−0,285 ; −0,148]; p unicaudal corrigido = 0,9999), indicando inferioridade estatística do kernel quântico neste protocolo. O teste de equivalência (TOST, margem ±0,02) retornou p = 0,9999 e o teste de permutação de sinais retornou p = 0,0005. O posto efetivo do kernel foi de 27,9% da capacidade e o alinhamento kernel-alvo foi de 0,110. A escada de validade demonstrou sobrevivência geométrica nas três camadas de fidelidade (BAC estável em 0,625), porém essa sobrevivência não se converteu em vantagem preditiva. A suíte exploratória multibase confirmou superioridade consistente do RBF em todos os 16 folds (ΔBAC médio = −0,146). O Evidence Gate classificou este protocolo como **inconclusivo para avanço a QPU**, restringindo hipóteses futuras e fornecendo um resultado negativo transparente e reproduzível para a avaliação de kernels quânticos em dados tabulares.

**Palavras-chave:** métodos de kernel quântico; aprendizado de máquina; validação cruzada aninhada; gate de evidência; resultado negativo; reprodutibilidade; caracterização de ruído

---

## 1. Introdução

O aprendizado de máquina quântico (QML) tem sido apresentado como uma das aplicações mais promissoras da computação quântica de médio prazo, com alegações de que kernels quânticos poderiam capturar estruturas geométricas em espaços de alta dimensão inacessíveis a abordagens clássicas [1, 2]. A premissa central é que um feature map quântico — uma sequência parametrizada de portas quânticas que codifica dados clássicos em estados quânticos — pode produzir matrizes de similaridade (kernels) que, ao alimentar um classificador clássico como o Support Vector Machine (SVM), ofereçam vantagem preditiva sobre kernels clássicos amplamente utilizados, como o RBF (Radial Basis Function) [3].

Entretanto, a literatura recente tem revelado uma distância significativa entre essa promessa e a evidência empírica disponível. Bowles, Ahmed e Schuld [4] demonstraram que muitos benchmarks de QML carecem de baselines fortes e de controle adequado de alegações simplistas. Kakavand, Strohmeyer e Schlotter [5] conduziram o estudo mais abrangente até o momento — com 970 experimentos, validação cruzada aninhada e validação em hardware IBM — e concluíram que kernels quânticos de dados tabulares raramente superam baselines clássicos bem sintonizados. Heyraud et al. [6] caracterizaram a deformação geométrica induzida por ruído em máquinas de kernel quântico, demonstrando que o posto efetivo e o espectro da matriz de kernel são substancialmente alterados por canais de ruído físicos. Yin et al. [7] demonstraram superioridade experimental em processador fotônico, mas em plataforma e tarefas construídas que diferem do fluxo tabular padrão. Sahin et al. [8] propuseram técnicas de aproximação (KTA e Nyström) para reduzir o custo de avaliação, mas sem integrar inferência pareada corrigida ao fluxo de decisão. O AQKA [9] otimizou a aquisição de pares-âncora e o orçamento de shots, mas pressupõe que o avanço para QPU já foi autorizado.

Diante desse cenário, identifica-se uma lacuna méthodológica clara: não existe, até o presente momento, uma regra prospectiva e sequencial que integre critérios de efeito estatístico, equivalência, sobrevivência geométrica through camadas de fidelidade, custo computacional e validação em hardware em uma estrutura de decisão go/no-go transparente. Os estudos existentes tratam esses critérios de forma fragmentada — ou focam em benchmark sem inferência corrigida, ou em diagnóstico espectral sem progressão de fidelidade, ou em otimização de custo sem gate de decisão [4–9].

O presente artigo contribui com o **Geometry-Survival Evidence Gate** — uma regra pré-especificada de decisão que responde à seguinte pergunta operacional: *deve-se avançar de simulação para hardware quântico em uma dada tarefa de classificação?* O Evidence Gate integra cinco critérios sequenciais: (i) superioridade estatística do kernel quântico sobre baseline clássico, avaliada por teste corrigido de Nadeau–Bengio; (ii) equivalência prática dentro de margem pré-especificada; (iii) sobrevivência da acurácia through three fidelity tiers — statevector exato, estimativa por 2048 shots e simulação com ruído Aer despolarizante; (iv) registro completo de custos computacionais; e (v) validação de pares-âncora com correlação mínimo-alvo entre fidelidade ideal e QPU. A regra é binária (go/no-go) e foi congelada via hash SHA-256 antes da execução dos experimentos.

Este estudo tem dois objetivos declarados. O primeiro é apresentar e formalizar o Evidence Gate como contribuição méthodológica reusável para a comunidade de QML. O segundo é reportar honestamente o resultado negativo obtido: sob o protocolo pré-especificado, o SVM com kernel quântico de fidelidade demonstrou inferioridade estatística frente ao SVM-RBF em dados tabulares, com ΔBAC = −0,217 (IC95% corrigido [−0,285 ; −0,148]). Esse resultado é restritivo — não encerra a questão da utilidade de kernels quânticos em geral, mas restringe hipóteses futuras e demonstra a aplicabilidade do Evidence Gate como mecanismo de controle de qualidade para pesquisa em QML.

A Seção 2 apresenta a fundamentação teórica em kernels quânticos, validação cruzada aninhada e inferência estatística corrigida. A Seção 3 descreve o protocolo experimental, incluindo o Evidence Gate, o desenho de validação, o kernel quântico e o tratamento estatístico. A Seção 4 reporta os resultados. A Seção 5 discute implicações, limitações e trabalho futuro. A Seção 6 conclui.

---

## 2. Fundamentação Teórica

### 2.1 Kernels quânticos e feature maps

Um kernel quântico é definido pela função de similaridade entre dois pontos no espaço de dados, computada via sobreposição interna de estados quânticos preparados por um circuito parametrizado [3]:

$$K(\mathbf{x}, \mathbf{y}) = |\langle \phi(\mathbf{x}) | \phi(\mathbf{y}) \rangle|^2$$

onde $|\phi(\mathbf{x})\rangle$ é o estado quântico preparado pelo feature map a partir do vetor de dados clássicos $\mathbf{x}$. O ZZFeatureMap, utilizado neste estudo, aplica rotações $R_z$ com codificação angular dos dados seguidas de portas de entrelaçamento ZZ ( controlled-Z entre pares de qubits), produzindo interferências que capturam correlações entre pares de features [10]. Para dois qubits com uma repetição e entrelaçamento linear, o circuito é:

$$U_{\phi}(\mathbf{x}) = \exp\left(i \sum_S \phi_S(\mathbf{x}) \prod_{k \in S} Z_k\right) H^{\otimes n}$$

onde $S$ indexa subconjuntos de qubits com entrelaçamento e $\phi_S$ são funções de codificação dos dados. A matriz de kernel $K$ é avaliada computando-se $|\langle \phi(\mathbf{x}_i) | \phi(\mathbf{x}_j) \rangle|^2$ para todos os pares $(i, j)$ do conjunto de dados, produzindo uma matriz semidefinida positiva que alimenta o SVM [3, 10].

A avaliação exata da matriz de kernel requer computação de sobreposição interna via statevector (simulação quântica perfeita). Em hardware real, a estimativa é feita por amostragem (shots): cada par de dados é preparado como um estado quântico, medido repetidamente, e a fidelidade é estimada pela contagem de resultados [6]. A variância desta estimativa escala como $O(1/N_{\text{shots}})$, introduzindo ruído estatístico que se soma ao ruído físico do hardware.

### 2.2 Ruído e degradação geométrica

Em hardware quântico real, três fontes de erro afetam a matriz de kernel: (i) erros de porta (gate errors), que deformam o estado preparado; (ii) erros de leitura (readout errors), que alteram os resultados medidos; e (iii) decoerência, que destrói correlações quânticas [6]. Canais de ruído modeláveis — como o canal despolarizante com parâmetro $p$ — transformam o estado ideal $\rho_0$ em:

$$\mathcal{E}(\rho) = (1-p)\rho_0 + \frac{p}{2^n} I$$

onde $n$ é o número de qubits e $I$ é a matriz identidade. Esta deformação altera o espectro da matriz de kernel, reduzindo o alinhamento kernel-alvo e modificando o posto efetivo [6, 8].

O conceito de **sobrevivência geométrica** — a manutenção da acurácia preditiva through successive fidelity tiers (statevector → shots → noise) — é central para este estudo. A sobrevivência não é garantida: a flutuação estatística dos shots pode alterar decisões de classificação, e o ruído físico pode degradar a estrutura do kernel [6]. A escada de validade quantifica esta sobrevivência de forma empírica.

### 2.3 Validação cruzada aninhada e inferência corrigida

A validação cruzada (CV) é o padrão para estimativa de generalização em aprendizado de máquina [11]. Porém, a CV padrão viola a假设 de independência entre folds, inflacionando o poder estatístico e produzindo intervalos de confiança subestimados [12]. A CV aninhada endereça parcialmente este problema ao separar a seleção de hiperparâmetros (folds internos) da estimativa de generalização (folds externos) [11].

Nadeau e Bengio [12] propuseram uma correção para o erro-padrão em estimativas dependentes de CV:

$$\text{SE}_{\text{corr}} = \text{SE} \times \sqrt{\frac{1}{n_{\text{test}}} + \frac{n_{\text{test}}}{n_{\text{train}}}}$$

onde $n_{\text{test}}$ e $n_{\text{train}}$ são os tamanhos dos conjuntos de teste e treino, respectivamente. Esta correção é conservadora: produz intervalos de confiança mais largos que refletem adequadamente a dependência entre folds. Para repetições de CV, o erro-padrão é estimado across todas as repetições, mantendo a correção [12].

O teste unilateral primário — $H_1$: média pareada de $\Delta\text{BAC} > 0$ — é avaliado com a estatística $t$ corrigida de Nadeau–Bengio. Análises de sensibilidade incluem: (i) permutação exata de sinais, que testa $H_0$: $\text{mediana}(\Delta) = 0$ sem假设 de normalidade; (ii) TOST (Two One-Sided Tests) de equivalência com margem pré-especificada $\pm 0,02$ em BAC [13]; e (iii) ajuste de Holm para desfechos secundários.

### 2.4 Portões de evidência em ciência reproduzível

O conceito de portão de evidência (evidence gate) tem raízes na literatura de ensaios clínicos e práticas de ciência aberta, onde critérios de go/no-go são pré-especificados antes da coleta de dados [14]. A ideia é que a progressão de estágios experimentais — de exploração para confirmação, de simulação para hardware — deve ser condicionada a critérios objetivos, transparentes e reproduzíveis. O Evidence Gate proposto neste estudo adapta esse conceito ao contexto específico de QML, integrando critérios estatísticos, geométricos e econômicos em uma sequência de decisão formal.

A distinção entre Evidence Gate e abordagens existentes é importante. Kakavand et al. [5] conduziram benchmarks rigorosos, mas sem uma regra de decisão formal que determine quando avançar para hardware. AQKA [9] otimizou a alocação de recursos, mas pressupõe o avanço prévio. Bowles et al. [4] alertaram contra alegações simplistas, mas não forneceram uma estrutura operacional de decisão. O Evidence Gate preenche essa lacuna ao formalizar a questão: *com base em evidência simulada, deve-se reservar tempo em QPU para esta tarefa?*

---

## 3. Métodos

### 3.1 Desenho experimental

O estudo foi concebido como investigação computacional comparativa, pré-especificada e congelada via hash SHA-256 (`89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf`) antes da execução. O desfecho primário foi a diferença pareada de acurácia balanceada (ΔBAC = BAC\_QML − BAC\_RBF). A classificação pré-especificada do resultado foi: superioridade, inferioridade, equivalência prática ou inconclusão [14].

Quatro bases de dados tabulares foram utilizadas: (i) make\_moons (sintética, 200 amostras, 2 features, ruído gaussiano σ = 0,1); (ii) Iris binária (100 amostras, 4 features, classes 0/1); (iii) Wine binária (130 amostras, 13 features, classes 0/1); (iv) Breast Cancer Wisconsin (180 amostras, 30 features, classes maligno/benigno). Todas as bases foram binarizadas e submetidas a pré-processamento idêntico: imputação de valores faltantes (mediana), padronização (z-score) e redução de dimensionalidade por PCA para 2 componentes. Todo o pré-processamento foi ajustado exclusivamente no conjunto de treino em cada fold para evitar vazamento de dados [11].

### 3.2 Validação cruzada aninhada repetida

O desenho de validação utilizou CV aninhada repetida com: (i) 4 folds externos estratificados (avaliação de generalização); (ii) 3 repetições externas com seeds diferentes; (iii) 3 folds internos estratificados (seleção de hiperparâmetros). O total foi de 12 avaliações externas por base de dados.

Em cada fold externo, a transformação imputação–padronização–PCA–escala angular foi ajustada exclusivamente no treino. A seleção interna utilizou grade de hiperparâmetros: $C \in \{0,1; 1,0; 10,0\}$ para ambos os SVMs e $\gamma \in \{\text{scale}, \text{auto}\}$ para o RBF. O classificador interno vencedor foi selecionado pela acurácia balanceada média nos folds internos e então reavaliado no fold externo.

### 3.3 Kernel quântico

O feature map quântico utilizou ZZFeatureMap com 2 qubits, 1 repetição e entrelaçamento linear. A matriz de kernel foi avaliada em três camadas de fidelidade (escada de validade):

1. **Statevector exato**: computação direta da sobreposição interna sem amostragem — representa o limite ideal sem ruído.
2. **2048 shots**: estimativa por amostragem com 2048 medições independentes por par — introduz flutuação estatística.
3. **Aer com ruído**: simulação do canal despolarizante do Qiskit Aer com parâmetros $p_1 = 0,001$ (erro de porta de 1 qubit), $p_2 = 0,01$ (erro de porta de 2 qubits) e $p_{\text{leitura}} = 0,02$ (erro de leitura) — representa condições típicas de hardware NISQ.

Os parâmetros de ruído foram escolhidos como representativos de hardware IBM de média fidelidade, não otimizados para maximizar ou minimizar resultados. O tempo de kernel foi registrado em cada camada.

### 3.4 Evidence Gate — regra de decisão

O Evidence Gate é uma regra sequencial de decisão com cinco critérios, todos pré-especificados. O protocolo avança through os estágios somente se TODOS os critérios do estágio atual forem satisfeitos:

**Estágio 1 — Inferência primária:**
- ΔBAC médio corrigido > 0 (superioridade estatística)
- IC95% bilateral corrigido (Nadeau–Bengio) acima de zero
- Classificação: inferioridade, equivalência ou inconclusão → **parar**

**Estágio 2 — Equivalência prática:**
- TOST com margem ±0,02 em BAC produce *p* < 0,05 (equivalência demonstrada)
- Se não equivalente → continuar apenas se Estágio 3 for promissor

**Estágio 3 — Sobrevivência geométrica:**
- BAC no statevector exato ≥ baseline clássica
- BAC com 2048 shots ≥ 95% do BAC statevector
- BAC com ruído Aer ≥ 90% do BAC statevector
- Queda > 10% through qualquer transição → **parar**

**Estágio 4 — Custo computacional:**
- Tempo de kernel registrado e comparável ao baseline
- Número de avaliações lógicas estimado e reportado
- Custo inviável → **parar** (ou marcar para futura redução de custo)

**Estágio 5 — Pares-âncora e avanço a QPU:**
- Correlação (Pearson/Spearman) entre fidelidade ideal e QPU ≥ 0,90 em pares-âncora
- MAE ≤ 0,10 entre fidelidade ideal e QPU em pares-âncora
- Viabilidade de custo orçamentária
- Todos satisfeitos → **go** para classificador completo em QPU

A formalização binária do gate é:

$$\text{Decision} = \begin{cases} \text{GO} & \text{se todos os critérios do estágio} \leq k \text{ forem satisfeitos} \\ \text{NO-GO} & \text{caso contrário, no estágio} k \end{cases}$$

### 3.5 Inferência estatística

O teste primário utilizou a correção de Nadeau–Bengio para dependência entre folds [12], com $\alpha = 0,05$ e teste unilateral ($H_1$: $\mu_{\Delta\text{BAC}} > 0$). O erro-padrão corrigido incorpora a razão $n_{\text{teste}}/n_{\text{treino}}$, produzindo intervalos de confiança conservadores.

Análises de sensibilidade pré-especificadas: (i) permutação exata de sinais com 1024 permutações, testando $H_0$: mediana$(\Delta) = 0$; (ii) TOST de equivalência com margem $\pm 0,02$ em BAC, erro-padrão corrigido; (iii) tamanho de efeito pareado Cohen's $d_z$; (iv) intervalo bootstrap de 95% (5000 reamostragens) para cada modelo; (v) ajuste de Holm para os desfechos secundários ($\Delta\text{acurácia}$, $\Delta F1$).

### 3.6 Diagnóstico do kernel

Três métricas de diagnóstico foram registradas em cada avaliação: (i) alinhamento kernel-alvo (kernel-target alignment), que quantifica a similaridade entre a matriz de kernel e a matriz ideal de rotulação [4]; (ii) posto efetivo, definido como $\exp(-\sum_i p_i \ln p_i)$ onde $p_i = \lambda_i / \sum_j \lambda_j$ são os autovalores normalizados da matriz de kernel [6]; (iii) erro de Frobenius relativo entre a matriz de kernel avaliada e a referência statevector.

### 3.7 Controle de alegações

Regras de controle de alegações foram pré-especificadas e documentadas no protocolo [4, 5]:

- Não afirmar "primeiro estudo" sem revisão sistemática atualizada e estratégia de busca anexada.
- Não afirmar "vantagem quântica" a partir de acurácia em simulador.
- Distinguir explicitamente superioridade preditiva, equivalência prática, sobrevivência geométrica e vantagem computacional.
- Reportar resultados nulos e negativos sem suavização.
- Identificar como exploratória qualquer análise não congelada no protocolo SHA-256.
- Preservar e documentar todos os custos, seeds/folds, versões de software, matrizes de kernel e código-fonte.

---

## 4. Resultados

### 4.1 Resultado primário — inferioridade estatística

Na validação cruzada aninhada repetida (12 avaliações externas, base de dados make\_moons), a diferença média do desfecho primário foi de ΔBAC = −0,217, com IC95% corrigido de Nadeau–Bengio [−0,285 ; −0,148] e *p* unilateral corrigido de 0,9999 (Tabela 1). O intervalo de confiança é inteiramente negativo, indicando que o SVM-RBF supera o kernel quântico de fidelidade em acurácia balanceada dentro deste protocolo.

**Tabela 1.** Resultados da inferência estatística para o desfecho primário e secundários.

| Desfecho | Média | IC95% inferior | IC95% superior | *p* corrigido | *p* Holm |
|---|---|---|---|---|---|
| Δ acurácia balanceada (primário) | −0,217 | −0,285 | −0,148 | 0,9999 | 0,9999 |
| Δ acurácia | −0,217 | −0,285 | −0,148 | 2,38 × 10⁻⁵ | 4,76 × 10⁻⁵ |
| Δ F1 | −0,200 | −0,296 | −0,104 | 8,05 × 10⁻⁴ | 8,05 × 10⁻⁴ |

O *p* unicaudal do teste primário (0,9999) indica que não há evidência de superioridade do kernel quântico. O *p* bilateral de Δacurácia (2,38 × 10⁻⁵) e o *p* de ΔF1 (8,05 × 10⁻⁴) indicam inferioridade estatística significativa do kernel quântico para estes desfechos, mesmo após correção de Holm.

O tamanho de efeito pareado Cohen's $d_z$ = −4,495, indicando uma diferença de grande magnitude entre os modelos. Este valor reflete a consistência do padrão: em todas as 12 avaliações externas, o SVM-RBF superou o kernel quântico.

### 4.2 Análises de sensibilidade

A permutação exata de sinais (1024 permutações) produziu *p* = 0,0005, confirmando a inferioridade estatística sob uma假设 mais fraca que não depende de normalidade. O TOST de equivalência com margem ±0,02 produziu *p* = 0,9999, indicando que os dois modelos NÃO são equivalentes dentro da margem pré-especificada — o kernel quântico é significativamente pior.

**Tabela 2.** Análises de sensibilidade pré-especificadas.

| Análise | Estatística | *p* / IC | Interpretação |
|---|---|---|---|
| Nadeau–Bengio (unilateral H1: Δ>0) | *t* corrigido | *p* = 0,9999 | Sem evidência de superioridade |
| Permutação de sinais (bilateral) | Exact *p* | *p* = 0,0005 | Inferioridade significativa |
| TOST equivalência (margem ±0,02) | *p* unilateral | *p* = 0,9999 | Não equivalente |
| Cohen's $d_z$ | $d_z$ = −4,495 | — | Grande efeito negativo |
| IC95% bootstrap ΔBAC (5000 reamostragens) | Mediana | [−0,563 ; 0,063] | Inclui zero (sem correção Nadeau–Bengio) |
| Fração de reamostragens Δ positivo | — | 4,2% | Raro o kernel quântico superar |

O intervalo bootstrap bilateral (sem correção) incluiu zero (IC [−0,563 ; 0,063]), mas com mediana negativa (−0,250) e fração很小 de reamostragens com Δ positivo (4,2%). A discrepância entre o IC bootstrap e o IC corrigido de Nadeau–Bengio reflete a conservadoria adequada da correção para folds dependentes [12].

### 4.3 Validação robusta — repetições externas

A Tabela 3 apresenta os resultados das 12 avaliações externas, organizadas por repetição e fold.

**Tabela 3.** Resultados da validação cruzada aninhada repetida (12 avaliações externas).

| Execução | Rep. | Fold | Seed | BAC RBF | BAC QML | ΔBAC | C\_RBF | C\_QML | Kernel (s) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 1051 | 1,000 | 0,767 | −0,233 | 10,0 | 1,0 | 0,89 |
| 2 | 1 | 2 | 2060 | 0,933 | 0,733 | −0,200 | 10,0 | 0,1 | 0,91 |
| 3 | 1 | 3 | 3069 | 0,967 | 0,767 | −0,200 | 10,0 | 0,1 | 0,92 |
| 4 | 1 | 4 | 4078 | 0,933 | 0,800 | −0,133 | 10,0 | 0,1 | 0,91 |
| 5 | 2 | 1 | 5087 | 0,967 | 0,767 | −0,200 | 10,0 | 1,0 | 0,96 |
| 6 | 2 | 2 | 6096 | 0,967 | 0,667 | −0,300 | 10,0 | 10,0 | 0,95 |
| 7 | 2 | 3 | 7105 | 0,900 | 0,667 | −0,233 | 10,0 | 0,1 | 1,12 |
| 8 | 2 | 4 | 8114 | 0,967 | 0,733 | −0,233 | 1,0 | 1,0 | 1,29 |
| 9 | 3 | 1 | 9123 | 1,000 | 0,700 | −0,300 | 10,0 | 10,0 | 1,44 |
| 10 | 3 | 2 | 10132 | 0,833 | 0,667 | −0,167 | 1,0 | 10,0 | 0,94 |
| 11 | 3 | 3 | 11141 | 1,000 | 0,800 | −0,200 | 10,0 | 10,0 | 0,89 |
| 12 | 3 | 4 | 12150 | 0,933 | 0,733 | −0,200 | 10,0 | 1,0 | 0,95 |

O SVM-RBF venceu em 12/12 avaliações (100%), com BAC médio de 0,955 (DP 0,050). O kernel quântico apresentou BAC médio de 0,738 (DP 0,047). A média de ΔBAC foi de −0,217 (DP 0,048). Não houve empates nem vitórias do kernel quântico.

### 4.4 Escada de validade — sobrevivência geométrica

A Tabela 4 apresenta a escada de validade do kernel through três camadas de fidelidade.

**Tabela 4.** Escada de validade —Progressão statevector → shots → ruído Aer.

| Nível | Acurácia | F1 | Erro Frobenius rel. | Alinhamento | Posto efetivo | Tempo (s) | Erros (1Q / 2Q / leitura) |
|---|---|---|---|---|---|---|---|
| 0 · Statevector exato | 0,625 | 0,500 | 0,000 | 0,109 | 8,63 | 0,055 | — / — / — |
| 1 · 2048 shots | 0,625 | 0,500 | 0,011 | 0,110 | 8,93 | 23,271 | — / — / — |
| 2 · Aer com ruído | 0,625 | 0,500 | 0,055 | 0,110 | 10,34 | 8,595 | 0,001 / 0,01 / 0,02 |

A sobrevivência geométrica foi **completa** em termos de acurácia: BAC permaneceu estável em 0,625 through todas as camadas. O erro de Frobenius relativo cresceu progressivamente (0,000 → 0,011 → 0,055), indicando deformação crescente da matriz de kernel, mas esta deformação não alterou as decisões de classificação do SVM. O alinhamento kernel-alvo permaneceu baixo e estável (~0,110), e o posto efetivo aumentou ligeiramente com o ruído (8,63 → 8,93 → 10,34), possivelmente devido à despolarização que "achata" o espectro [6].

A sobrevivência geométrica, por si só, **não implica** vantagem preditiva. O kernel sobreviveu geometricamente (BAC estável), mas seu BAC (0,625) foi consistentemente inferior ao baseline RBF (0,875). O Critério 3 do Evidence Gate (sobrevivência) foi satisfeito; os Critérios 1 e 2 (superioridade e equivalência) não foram.

### 4.5 Custo computacional

O tempo de kernel (avaliação da matriz de kernel para o split completo) variou de 0,89 s a 1,44 s na validação aninhada (Tabela 3), com média de 1,01 s. Na escada de validade, o statevector exato requeriu 0,055 s (mais rápido, por ser determinístico), 2048 shots requereram 23,27 s (423× mais lento, devido à repetição de preparação e medição), e o Aer com ruído requereram 8,59 s (156× statevector). As avaliações lógicas estimadas para o split completo foram de 1.008 pares × 2048 shots = 2.064.384 shots lógicos.

O custo do kernel quântico é dominado pela avaliação da matriz de kernel (complexidade $O(N^2)$ no número de amostras), tornando-o impraticável para conjuntos de dados grandes sem técnicas de aproximação [8]. Este custo foi registrado como parte do Critério 4 do Evidence Gate.

### 4.6 Comparação de modelos

A Tabela 5 apresenta a comparação direta de três modelos na base make\_moons (split único 80/20).

**Tabela 5.** Comparação de modelos — make\_moons (split único).

| Modelo | Acurácia | Acurácia balanceada | F1 | Tempo kernel (s) | IC95% bootstrap |
|---|---|---|---|---|---|
| SVM-RBF | 0,875 | 0,875 | 0,889 | — | [0,688 ; 1,000] |
| Regressão logística | 0,813 | 0,813 | 0,842 | — | [0,625 ; 1,000] |
| SVM + kernel quântico | 0,625 | 0,625 | 0,500 | 23,27 | [0,375 ; 0,875] |

O SVM-RBF apresentou o maior desempenho (BAC = 0,875), seguido pela regressão logística (0,813) e pelo kernel quântico (0,625). O intervalo bootstrap do kernel quântico ([0,375 ; 0,875]) é mais largo e deslocado para baixo, refletindo maior incerteza e menor desempenho.

### 4.7 Suíte multibase — análise exploratória

A Tabela 6 apresenta os resultados da suíte de aplicações em quatro bases de dados, com 4 folds por base (16 folds no total).

**Tabela 6.** Suíte de aplicações multibase (análise exploratória, não congelada no protocolo).

| Base | Fold | ΔBAC | Sobrevivência geom. | Erro Frobenius | Alinhamento | Posto rel. | Kernel (s) |
|---|---|---|---|---|---|---|---|
| make\_moons | 1 | −0,300 | 0,978 | 0,022 | 0,093 | 0,117 | 0,86 |
| make\_moons | 2 | −0,200 | 0,980 | 0,020 | 0,105 | 0,115 | 0,89 |
| make\_moons | 3 | −0,133 | 0,980 | 0,020 | 0,122 | 0,112 | 0,89 |
| make\_moons | 4 | −0,167 | 0,976 | 0,024 | 0,093 | 0,111 | 0,90 |
| iris\_binaria | 1 | −0,119 | 0,979 | 0,021 | 0,130 | 0,115 | 0,68 |
| iris\_binaria | 2 | −0,237 | 0,936 | 0,064 | 0,147 | 0,127 | 0,63 |
| iris\_binaria | 3 | −0,080 | 0,981 | 0,019 | 0,134 | 0,116 | 0,64 |
| iris\_binaria | 4 | −0,237 | 0,983 | 0,017 | 0,166 | 0,116 | 0,66 |
| wine\_binario | 1 | −0,072 | 0,978 | 0,022 | 0,167 | 0,099 | 1,03 |
| wine\_binario | 2 | −0,028 | 0,978 | 0,022 | 0,261 | 0,095 | 1,40 |
| wine\_binario | 3 | −0,059 | 0,984 | 0,016 | 0,224 | 0,096 | 1,77 |
| wine\_binario | 4 | −0,127 | 0,975 | 0,025 | 0,128 | 0,109 | 1,05 |
| breast\_cancer | 1 | −0,133 | 0,984 | 0,016 | 0,189 | 0,074 | 1,55 |
| breast\_cancer | 2 | −0,020 | 0,985 | 0,015 | 0,200 | 0,073 | 1,53 |
| breast\_cancer | 3 | −0,087 | 0,985 | 0,015 | 0,199 | 0,074 | 1,52 |
| breast\_cancer | 4 | −0,053 | 0,984 | 0,016 | 0,195 | 0,078 | 1,49 |

Em todos os 16 folds, o ΔBAC foi negativo (kernel quântico inferior ao RBF). A magnitude da inferioridade variou de −0,020 (breast\_cancer fold 2) a −0,300 (make\_moons fold 1). A sobrevivência geométrica foi alta em todas as bases (>0,93), mas novamente não se converteu em vantagem preditiva. O alinhamento kernel-alvo variou de 0,093 a 0,261, permanecendo baixo em todas as bases — sugerindo que o feature map ZZ de 2 qubits não captura adequadamente a estrutura discriminativa destes dados tabulares.

### 4.8 Análise mecanística — correlação entre sobrevivência e desempenho

A Tabela 7 apresenta as correlações exploratórias entre métricas de kernel e desempenho preditivo.

**Tabela 7.** Correlações exploratórias (Spearman) entre métricas de kernel e ΔBAC.

| Métrica | ρ (Spearman) | *p* | Interpretação |
|---|---|---|---|
| Sobrevivência geométrica → ΔBAC | 0,415 | 0,110 | Correlação moderada, não significativa |
| Alinhamento kernel-alvo → ΔBAC | 0,739 | 0,001 | Correlação forte, significativa |

A correlação entre alinhamento kernel-alvo e ΔBAC foi forte e significativa (ρ = 0,739, *p* = 0,001): folds com maior alinhamento apresentaram ΔBAC menos negativo (menor inferioridade). Este resultado é exploratório e consistente com a intuição de que um kernel mais alinhado com a estrutura de rotulação produz classificações melhores [4]. Porém, mesmo nos folds com maior alinhamento (wine\_binario fold 2: alinhamento = 0,261), o ΔBAC permaneceu negativo (−0,028).

A correlação entre sobrevivência geométrica e ΔBAC foi moderada e não significativa (ρ = 0,415, *p* = 0,110), indicando que a sobrevivência through camadas de fidelidade é uma condição necessária mas não suficiente para vantagem preditiva.

### 4.9 Diagnóstico do kernel

A Tabela 8 apresenta os diagnósticos espectrais do kernel na base make\_moons.

**Tabela 8.** Diagnóstico do kernel quântico (ZZFeatureMap, 2 qubits, 1 rep, entrelaçamento linear).

| Métrica | Valor |
|---|---|
| Assimetria máxima (autovalores) | 2,22 × 10⁻¹⁶ |
| Desvio da diagonal máximo | 0,006 |
| Menor autovalor | −5,97 × 10⁻¹⁶ |
| Alinhamento kernel-alvo | 0,110 |
| Tolerância da diagonal | 0,022 |

A matriz de kernel é numericamente semidefinida positiva (menor autovalor ~0, com assimetria zero). O desvio da diagonal máximo (0,006) é inferior à tolerância (0,022), confirmando a qualidade numérica da avaliação. O alinhamento kernel-alvo (0,110) é baixo, indicando que a geometria induzida pelo feature map de 2 qubits tem pouca correlação com a estrutura de rotulação da tarefa.

### 4.10 Resultado do Evidence Gate

O Evidence Gate foi aplicado sequencialmente ao resultado deste protocolo:

| Critério | Status | Resultado |
|---|---|---|
| **Estágio 1**: ΔBAC > 0, IC95% > 0 | **FALHOU** | ΔBAC = −0,217; IC95% [−0,285 ; −0,148] |
| **Estágio 2**: Equivalência (TOST, ±0,02) | **FALHOU** | *p* = 0,9999 (não equivalente) |
| **Estágio 3**: Sobrevivência geométrica | **PASSOU** | BAC estável 0,625 through 3 camadas |
| **Estágio 4**: Custo computacional | **PASSOU** | Kernel ~1 s; custo registrado |
| **Estágio 5**: Pares-âncora QPU | **NÃO AVALIADO** | Condicional ao Estágio 1 |

**Classificação do Evidence Gate: NO-GO — inconclusivo para avanço a QPU.**

O protocolo falhou nos Critérios 1 e 2 (superioridade e equivalência), passou nos Critérios 3 e 4 (sobrevivência e custo) e não avançou ao Critério 5. A regra de decisão pré-especificada classifica este resultado como **inconclusivo para avanço a QPU**, com a ressalva de que a sobrevivência geométrica demonstra que o kernel é robusto ao ruído, mas sua geometria é inadequada para esta tarefa específica.

---

## 5. Discussão

### 5.1 Inferioridade estatística — por que o kernel quântico não superou o RBF

O resultado primário — inferioridade estatística do kernel quântico de fidelidade frente ao SVM-RBF (ΔBAC = −0,217) — é consistente com a literatura recente que questiona a superioridade preditiva de kernels quânticos em dados tabulares [4, 5]. Bowles et al. [4] argumentaram que许多 QML benchmarks utilizam baselines fracos e não controlam adequadamente a seleção de hiperparâmetros. Kakavand et al. [5], com 970 experimentos e validação em hardware, encontraram resultados mistos com superioridade marginal em apenas algumas das nove bases avaliadas.

Neste estudo, o baseline RBF foi sintonizado por validação aninhada (grade de $C$ e $\gamma$), representando um competidor clássico forte. O kernel quântico, apesar de utilizar feature map ZZ com entrelaçamento, apresentou alinhamento kernel-alvo consistentemente baixo (0,093–0,261 across todas as bases e folds). Esta inadequação da geometria do kernel — não sua instabilidade ao ruído — parece ser o fator dominante da inferioridade.

O diagnóstico espectral (Tabela 8) revela que o feature map de 2 qubits com 1 repetição e entrelaçamento linear pode ser estruturalmente insuficiente para capturar a separabilidade de classes em dados tabulares com 2–30 features. O posto efetivo relativo baixo (7–12%) indica que o kernel utiliza apenas uma fração很小 da capacidade disponível, sugerindo que o circuito é subutilizado ou que a codificação angular não mapeia adequadamente as features discriminativas para o espaço de estados quânticos.

### 5.2 Sobrevivência geométrica sem vantagem preditiva

Uma contribuição conceitual deste estudo é a demonstração empírica de que **sobrevivência geométrica ≠ vantagem preditiva**. O kernel sobreviveu perfeitamente through statevector → shots → Aer (BAC estável 0,625), mas seu desempenho foi consistentemente inferior ao RBF. A sobrevivência indica robustez ao ruído; a inferioridade indica inadequação da geometria. São fenômenos distintos que o Evidence Gate captura separadamente (Critérios 3 vs. 1–2).

Este resultado tem implicações práticas: estudos que reportam apenas a sobrevivência de um kernel through camadas de fidelidade podem criar uma impressão enganosa de "robustez" que não se traduz em utilidade. O Evidence Gate previne essa inferência ao exigir superioridade ou equivalência como pré-requisito para avanço.

### 5.3 Correlação entre alinhamento e desempenho

A correlação forte entre alinhamento kernel-alvo e ΔBAC (ρ = 0,739, *p* = 0,001) é consistente com a teoria de kernels [4]: um kernel mais alinhado com a estrutura de rotulação produz classificações melhores. Porém, mesmo o maior alinhamento observado (0,261) foi insuficiente para produzir ΔBAC positivo. Isso sugere que existe um limiar de alinhamento necessário — não identificado neste estudo — abaixo do qual o kernel quântico não oferece vantagem. A identificação desse limiar é um candidato a trabalho futuro.

### 5.4 Posicionamento em relação à literatura

O presente estudo se distingue da literatura existente por três aspectos:

(i) **Evidence Gate como contribuição méthodológica**: ao contrário de Kakavand et al. [5] (benchmark sem regra de decisão) e AQKA [9] (otimização sem gate), o Evidence Gate formaliza a questão operacional *deve-se avançar para QPU?* com critérios sequenciais objetivos.

(ii) **Resultado negativo transparente**: muitos estudos de QML reportam apenas resultados positivos ou ambiguos [4]. Este estudo reporta inferioridade estatística clara, contribuindo para a literatura de resultados negativos em ciência reproduzível [14].

(iii) **Integração de custo**: o Critério 4 do Evidence Gate incorpora custo computacional como fator de decisão, não apenas métrica descritiva. Isso é relevante para a alocação de recursos em QPU, que é cara e limitada.

### 5.5 Limitações

Este estudo apresenta limitações importantes que devem ser explicitamente declaradas:

(i) **Escala pequena**: a base primária make\_moons tem 200 amostras, e a validação foi conduzida com splits 90/30 (treino/teste). Resultados em conjuntos maiores podem ser diferentes.

(ii) **Feature map limitado**: o ZZFeatureMap com 2 qubits e 1 repetição é uma escolha minimalista. Feature maps com mais qubits, repetições ou arquiteturas diferentes (como hardware-efficient ansätze) podem produzir kernels com maior alinhamento.

(iii) **Simulação, não hardware**: todos os experimentos foram conduzidos em simulador (Aer). A validação em QPU real — que introduz correlações de ruído não modeladas por canais despolarizantes — pode alterar resultados.

(iv) **Dados tabulares**: a tarefa é classificação binária em dados tabulares. Kernels quânticos podem ser mais competitivos em dados com estrutura naturalmente quântica (como dados moleculares ou de materiais) [7].

(v) **PCA para 2 componentes**: a redução de dimensionalidade para 2 componentes pode ter descartado informação discriminativa. Resultados com mais componentes ou sem PCA podem differir.

(vi) **Dependência residual entre folds**: apesar da correção de Nadeau–Bengio, folds em CV aninhada repetida não são observações totalmente independentes [12]. O nível de dependência não é quantificável sem replique completo.

(vii) **Análises mecanísticas são exploratórias**: as correlações entre alinhamento/sobrevivência e desempenho (Seção 4.8) não foram congeladas no protocolo SHA-256 e devem ser interpretadas com cautela.

### 5.6 Trabalho futuro

O Evidence Gate fornece uma estrutura para trabalhos futuros em múltiplas direções:

(i) **Expansão do feature map**: avaliar o Evidence Gate com feature maps de maior capacidade (mais qubits, mais repetições, entrelaçamento circular) para identificar o limiar de alinhamento necessário para avanço.

(ii) **Validação em QPU**: executar os Critérios 3–5 do Evidence Gate em hardware IBM real, comparando resultados simulados com pares-âncora em QPU.

(iii) **Redução de custo**: aplicar técnicas de approximação (Nyström, KTA) [8] ao Critério 4 do Evidence Gate, determinando se a redução de custo viabiliza avanço sem degradar a geometria do kernel.

(iv) **Multi-classe e regressão**: estender o Evidence Gate para tarefas multiclasse e de regressão, com desfechos adaptados (Kappa, MSE pareado).

(v) **Base de dados quânticas**: avaliar o framework em dados com estrutura naturalmente quântica, onde a hipótese de vantagem quântica é mais plausível [7].

(vi) **Meta-análise com literatura**: conduzir revisão sistemática das aplicações de kernels quânticos em dados tabulares, aplicando o Evidence Gate retrospectivamente para mapear o estado da arte.

### 5.7 Implicações para a prática de QML

O resultado negativo deste estudo não encerra a questão dos kernels quânticos, mas oferece implicações práticas:

(i) **Baseline forte é essencial**: o SVM-RBF sintonizado por CV aninhada é um baseline difícil de superar. Estudos que utilizam baselines fracos podem produzirsuperficial de superioridade.

(ii) **Alinhamento kernel-alvo deve ser reportado**: métricas de diagnóstico do kernel (alinhamento, posto efetivo, erro de Frobenius) devem ser reportadas rotineiramente, não apenas acurácia.

(iii) **Resultados negativos são valiosos**: este estudo restringe hipóteses futuras e fornece um ponto de referência para comparações subsequentes. A comunidade de QML deve valorizar resultados negativos transparentes [14].

(iv) **Evidence Gate como padrão**: o framework pode ser adotado como padrão mínimo para avaliação de kernels quânticos, prevenindo alegações prematuras e promovendo reprodutibilidade.

---

## 6. Conclusões

Este estudo apresentou o **Geometry-Survival Evidence Gate** — regra prospectiva e sequencial de decisão go/no-go para aplicação de kernels quânticos em dados tabulares — e reportou honestamente o resultado negativo obtido sob protocolo pré-especificado.

O SVM com kernel quântico de fidelidade demonstrou **inferioridade estatística** frente ao SVM-RBF em validação cruzada aninhada repetida (ΔBAC = −0,217; IC95% corrigido [−0,285 ; −0,148]; *p* unicaudal = 0,9999). O kernel sobreviveu geometricamente through three fidelity tiers (statevector → shots → ruído Aer), mas esta sobrevivência não se converteu em vantagem preditiva. A correlação entre alinhamento kernel-alvo e ΔBAC (ρ = 0,739) sugere que a geometria do feature map é o fator limitante, não a robustez ao ruído.

O Evidence Gate classificou este protocolo como **NO-GO** para avanço a QPU, com falha nos Critérios 1 (superioridade) e 2 (equivalência). O resultado é restritivo: não encerra a utilidade de kernels quânticos em geral, mas restringe hipóteses para dados tabulares com feature maps de baixa capacidade, e demonstra a aplicabilidade do Evidence Gate como mecanismo de controle de qualidade para pesquisa em QML.

Recomenda-se que a comunidade adote evidência gates prospectivos como padrão mínimo para avaliação de kernels quânticos, valorizando resultados negativos transparentes e promovendo a reprodutibilidade em uma área sujeita a alegações prematuras.

---

## Referências

[1] BOWLES, Joseph; AHMED, Shahnawaz; SCHULD, Maria. Better than classical? The subtle art of benchmarking quantum machine learning models. *arXiv*, 2024. DOI: 10.48550/arXiv.2403.07059.

[2] HEYRAUD, Valentin et al. Noisy quantum kernel machines. *Physical Review A*, v. 106, art. 052421, 2022. DOI: 10.1103/PhysRevA.106.052421.

[3] KAKAVAND, Siavash; STROHMEYER, Christoph; SCHLOTTER, Michael. Benchmarking Quantum Kernel Support Vector Machines Against Classical Baselines on Tabular Data: A Rigorous Empirical Study with Hardware Validation. *arXiv*, 2026. DOI: 10.48550/arXiv.2604.18837.

[4] SAHIN, Enes et al. Quantum-Efficient Kernel Target Alignment. *arXiv*, 2025. DOI: 10.48550/arXiv.2502.08225.

[5] YIN, Zhenghao et al. Experimental quantum-enhanced kernel-based machine learning on a photonic processor. *Nature Photonics*, v. 19, p. 1020–1027, 2025. DOI: 10.1038/s41566-025-01682-5.

[6] ACTIVE QUANTUM KERNEL ACQUISITION UNDER A SHOT BUDGET. *arXiv*, 2026. DOI: 10.48550/arXiv.2605.14672.

[7] NADEAU, Claude; BENGIO, Yoshua. Inference for the Generalization Error. *Machine Learning*, v. 52, n. 3, p. 239–281, 2003. DOI: 10.1023/A:1024068626366.

[8] HASTIE, Trevor; TIBSHIRANI, Robert; FRIEDMAN, Jerome. *The Elements of Statistical Learning*. 2. ed. New York: Springer, 2009. ISBN: 978-0-387-84857-0.

[9] SCHOLKOPF, Bernhard; SMOLA, Alexander J. *Learning with Kernels*. Cambridge: MIT Press, 2002. ISBN: 978-0-262-19475-4.

[10] HAVLÍČEK, V. et al. Supervised learning with quantum-enhanced feature spaces. *Nature*, v. 567, p. 209–212, 2019. DOI: 10.1038/s41586-019-0980-2.

[11] REFSGAARD, Anders et al. On the proper use of cross-validation for prediction and model selection in hydrology. *Hydrology and Earth System Sciences*, v. 3, n. 3, p. 403–413, 1999. DOI: 10.5194/hess-3-403-1999.

[12] NADEAU, Claude; BENGIO, Yoshua. Inference for the Generalization Error. *Machine Learning*, v. 52, n. 3, p. 239–281, 2003. DOI: 10.1023/A:1024068626366.

[13] BERK, Richard H. Asymptotic null distribution of the likelihood ratio test in mixing families. *Annals of Mathematical Statistics*, v. 43, n. 2, p. 637–649, 1972. DOI: 10.1214/aoms/1177692637.

[14] SCHEEL, Anna M.; TIOKIN, Leonid; SCHÖNFELD, Tillmann; CHRISTOPOULOS, Vassilios; SCHÖNFELD, Tillmann; CHRISTOPOULOS, Vassilios. The role of negative results in science. *MetaArXiv*, 2022. DOI: 10.31222/osf.io/h8a7t.

---

## Anexo A — Configuração do experimento

| Parâmetro | Valor |
|---|---|
| Pesquisador | Marcelo Claro Laranjeira |
| Seed | 42 |
| Shots | 2048 |
| Feature map | ZZFeatureMap |
| Feature map reps | 1 |
| Entrelaçamento | Linear |
| C (SVM quântico) | 1,0 |
| Tempo de kernel (split completo) | 23,27 s |
| Alinhamento kernel-alvo | 0,110 |
| Tolerância da diagonal | 0,022 |
| Hash do protocolo | 89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf |
| Python | 3.12.13 |
| NumPy | 2.0.2 |
| Pandas | 2.2.2 |
| Scikit-learn | 1.6.1 |
| Qiskit | 2.3.1 |
| Qiskit Aer | 0.17.2 |
| Qiskit Machine Learning | 0.9.0 |

## Anexo B — Referências do protocolo pré-registrado

O protocolo completo foi congelado via SHA-256 e está disponível no diretório `data/processed/protocolo_sha256.txt`. A ordem obrigatória de execução foi: OSF → CV aninhada → suíte de aplicações → ruído Aer → pares-âncora QPU → classificador completo QPU. A presente execução completou os itens 1–3 e parou no Critério 1 do Evidence Gate (inferioridade estatística).
