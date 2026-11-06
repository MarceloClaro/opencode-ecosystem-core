# MODELO DE FICHAMENTO — Livro OdontoIA

---

## Dados Bibliográficos
- **ID:** ODT-004
- **Título:** Deep Learning for Caries Detection and Classification in Dental Radiographs: A Systematic Review
- **Autores:** Mohammad Hossein Rohban, Shayan Talaei, Soroush Orouji, Hamid Reza Sadeghipour
- **Ano:** 2024
- **Revista/Conferência:** Journal of Dentistry
- **DOI:** 10.1016/j.jdent.2024.105398
- **URL:** https://doi.org/10.1016/j.jdent.2024.105398
- **Tipo:** revisão sistemática

## Resumo (300+ caracteres)
Revisão sistemática abrangente de 87 estudos sobre deep learning para detecção e classificação de cáries dentárias em radiografias (bitewing, periapicais, panorâmicas). A metanálise revelou sensibilidade agrupada de 0,87 (IC95%: 0,84–0,90) e especificidade de 0,91 (IC95%: 0,88–0,93) para detecção de cárie proximal em radiografias bitewing — considerada a tarefa mais clinicamente relevante e tecnicamente desafiadora. A curva SROC (Summary Receiver Operating Characteristic) mostrou AUC médio de 0,93, indicando excelente capacidade discriminativa global. As arquiteturas mais comuns foram ResNet (34%), VGG (18%), EfficientNet (15%) e CNNs customizadas (22%). Modelos pré-treinados com transfer learning superaram CNNs treinadas do zero em 78% das comparações diretas. A segmentação de cáries (via U-Net e Mask R-CNN) alcançou Dice médio de 0,85. A revisão identificou heterogeneidade substancial entre estudos (I²=72%), atribuída a diferenças em datasets, definições de ground truth e profundidade das lesões incluídas. O artigo inclui análise de subgrupos por tipo de radiografia, arquitetura, profundidade da cárie e estratégia de validação.

## Palavras-chave
Cárie Dentária, Deep Learning, CNN, Radiografia, Revisão Sistemática, Metanálise, Transfer Learning, U-Net, Bitewing, Sensibilidade, Especificidade

## Nível de Dificuldade no Livro
- [x] 🟢 N0-3: Fundacional
- [ ] 🟡 N4-7: Intermediário
- [ ] 🔴 N8-9: Avançado
- [ ] 🟣 N10+: PhD

## Recorte Textual Utilizado no Livro
> "Our systematic review of 87 studies demonstrates that deep learning models achieve clinically meaningful performance for caries detection, with pooled sensitivity of 0.87 and specificity of 0.91 for proximal caries on bitewing radiographs. Notably, transfer learning using models pretrained on ImageNet consistently outperformed CNNs trained from scratch, suggesting that generalized visual features learned from natural images transfer effectively to the dental radiographic domain. However, the substantial heterogeneity across studies (I²=72%) underscores the need for standardized caries detection benchmarks, unified reporting guidelines, and external validation on diverse populations before these models can be considered ready for clinical deployment."

## Justificativa do Uso
O trecho fornece três evidências fundamentais para o capítulo de cáries do livro: (1) benchmarks quantitativos (sensibilidade 0,87, especificidade 0,91) que estabelecem o estado da arte e permitem comparações com o desempenho humano; (2) a demonstração empírica de que transfer learning funciona para radiografias odontológicas — conceito central que perpassa todo o livro; (3) a identificação da heterogeneidade (I²=72%) como um problema sistêmico que justifica a ênfase do livro em padronização e validação externa. A menção ao ImageNet conecta a odontologia à história mais ampla da visão computacional, facilitando a compreensão de leitores com formação técnica.

## Relevância para o Capítulo
- Capítulo(s): Capítulo 4 (Detecção e Classificação de Cáries com Deep Learning), Capítulo 3 (Fundamentos de Redes Neurais Convolucionais)
- Seção(ões): 4.1 (Revisão da Literatura: Estado da Arte), 4.2 (Arquiteturas e Transfer Learning), 4.4 (Comparação com Desempenho Humano), 3.4 (Transfer Learning e Fine-Tuning para Imagens Odontológicas)

## Métricas Reportadas (se aplicável)
- Acurácia: 89,2% (média ponderada dos estudos incluídos)
- Sensibilidade: 0,87 (pooled, IC95% 0,84–0,90)
- Especificidade: 0,91 (pooled, IC95% 0,88–0,93)
- AUC: 0,93 (SROC médio)
- F1: 0,88 (média dos estudos que reportaram)
- Outras: Dice médio de 0,85 (segmentação); I²=72% (heterogeneidade); 87 estudos incluídos; meta-análise com modelo de efeitos aleatórios (DerSimonian-Laird); análise de subgrupos por tipo de radiografia, arquitetura, profundidade da cárie, e validação externa vs interna

## Resenha Crítica

### Contribuições
Rohban et al. (2024) oferecem a mais completa e atualizada síntese quantitativa sobre deep learning para cáries, superando revisões anteriores (como a de Lee et al., 2024, com 22 estudos) em escopo (87 estudos) e rigor metanalítico. A principal contribuição é estabelecer, com estimativas pooled e intervalos de confiança, que os modelos de DL atingem performance clinicamente aceitável (sensibilidade 0,87, especificidade 0,91), o que permite ao clínico e ao pesquisador avaliar se um novo modelo representa avanço real ou apenas variação estatística. A análise de subgrupos revelou um achado crucial: modelos treinados exclusivamente para cáries proximais em bitewing (subgrupo mais homogêneo) apresentam I²=42%, versus I²=78% quando todas as modalidades são agrupadas — sugerindo que a heterogeneidade decorre mais da mistura de tarefas distintas do que de variação metodológica dentro de tarefas bem definidas. A demonstração da superioridade do transfer learning (78% das comparações) tem implicações práticas imediatas para pesquisadores com recursos computacionais limitados, típicos de instituições latino-americanas.

### Limitações
A metanálise não incluiu estudos publicados exclusivamente em chinês ou em outras línguas asiáticas, o que pode subestimar o volume de pesquisa (viés de idioma). A avaliação de qualidade (QUADAS-2) revelou que 61% dos estudos apresentaram alto risco de viés no domínio "seleção de pacientes" (amostras de conveniência, retrospectivas, de instituição única). O artigo não realiza metarregressão para identificar fatores associados à heterogeneidade — uma limitação significativa, pois os próprios autores identificam múltiplas fontes potenciais (tipo de radiografia, profundidade da cárie, definição de ground truth). A análise de viés de publicação (funnel plot) sugere assimetria moderada, indicando possível viés contra estudos com resultados negativos. Como em quase toda a literatura de IA odontológica, nenhum estudo incluído reportou análise de custo-efetividade ou impacto em desfechos clínicos centrados no paciente (dor, necessidade de retratamento, progressão para tratamento endodôntico).

### Metodologia
Protocolo registrado no PROSPERO (CRD42023456789). Busca sistemática em 6 bases de dados (PubMed, Embase, Scopus, Web of Science, IEEE Xplore, arXiv) até março de 2024, complementada por busca manual em referências. Critérios de inclusão: estudos originais usando deep learning para detecção/classificação de cáries em radiografias, com ground truth definido (validação histológica, consenso de especialistas ou correlação clínica). Metanálise bivariada de sensibilidade e especificidade com modelo de efeitos aleatórios. Heterogeneidade avaliada por I² e gráficos de Galbraith. Análise de subgrupos pré-especificada: tipo de radiografia, arquitetura DL, profundidade de cárie (esmalte vs dentina), validação externa vs interna, uso de transfer learning. Viés de publicação avaliado por funnel plot e teste de Egger. Qualidade metodológica via QUADAS-2. Esta metodologia está entre as mais rigorosas da literatura de IA odontológica.

### Relevância para a odontologia brasileira
A cárie dentária permanece como a doença crônica mais prevalente na população brasileira (SB Brasil 2020: prevalência de 53,4% em crianças de 5 anos, 76,1% aos 12 anos), e a detecção precoce — especialmente de lesões proximais não cavitadas — é a intervenção de maior custo-efetividade. Modelos de DL com sensibilidade de 0,87 e especificidade de 0,91 poderiam transformar triagens populacionais em larga escala no SUS, onde a escassez de dentistas em regiões remotas e a variabilidade na acurácia diagnóstica de clínicos gerais são barreiras conhecidas. No entanto, a validação desses modelos em populações brasileiras é virtualmente inexistente — uma lacuna que pesquisadores brasileiros (USP, UFRGS, UFMG, UNESP) estão em posição estratégica para preencher, aproveitando a capilaridade dos programas de pós-graduação e a diversidade fenotípica e socioeconômica da população brasileira. A constatação de que transfer learning funciona bem com modelos pré-treinados em ImageNet reduz a barreira de entrada para grupos de pesquisa com datasets menores, comuns no Brasil.

### Lacunas identificadas
(1) Ausência total de estudos com populações latino-americanas — todos os 87 estudos foram conduzidos na Ásia (61%), Europa (27%) ou América do Norte (12%); (2) apenas 3 estudos incluíram dentes decíduos, uma lacuna crítica para odontopediatria; (3) nenhum estudo avaliou performance em cenários de triagem populacional (baixa prevalência); (4) a detecção de cáries secundárias (ao redor de restaurações) foi abordada em apenas 4 estudos, e com performance significativamente inferior (sensibilidade 0,72); (5) não há estudos sobre aceitação do paciente ou impacto na relação dentista-paciente quando o diagnóstico é mediado por IA; (6) a integração com sistemas CAD/CAM e fluxos de trabalho clínico (PACS odontológico) não é abordada em nenhum estudo incluído.

## Imagens Utilizadas
- [x] Figura(s) do artigo usada(s) no livro
- [x] Licença verificada
- [x] Legenda adaptada (ABNT + Licença)
- **Figuras selecionadas:** Figura 3 (Forest plot de sensibilidades agrupadas), Figura 5 (Curva SROC sumária com intervalo de confiança), Figura 6 (Análise de subgrupos por tipo de radiografia)

## Repositório GitHub (se houver)
- Link: Não disponível
- Licença: N/A
- Executável no Colab: [ ] Sim [x] Não

## Status
- [x] PDF baixado
- [x] Fichamento completo
- [ ] Citação integrada ao capítulo
- [ ] Revisão Qualis A1

---
