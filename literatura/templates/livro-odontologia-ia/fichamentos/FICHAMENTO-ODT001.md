# MODELO DE FICHAMENTO — Livro OdontoIA

---

## Dados Bibliográficos
- **ID:** ODT-001
- **Título:** Developments, application, and performance of artificial intelligence in dentistry – A systematic review
- **Autores:** P. S. Khanagar, A. Vishwanathaiah, S. C. Naik, H. H. Al-Kheraif, L. K. Devang, S. B. Divakar
- **Ano:** 2021
- **Revista/Conferência:** Journal of Dental Sciences
- **DOI:** 10.1016/j.jds.2020.06.019
- **URL:** https://doi.org/10.1016/j.jds.2020.06.019
- **Tipo:** revisão sistemática

## Resumo (300+ caracteres)
Revisão sistemática cobrindo duas décadas (2000-2020) de aplicações de IA na odontologia. Analisou 43 artigos após criteriosa seleção em PubMed, Medline, Embase, Cochrane, Google Scholar, Scopus e Web of Science. Documenta a transição de sistemas especialistas baseados em regras para redes neurais e deep learning, com análise de performance usando a ferramenta QUADAS-2. Abrange diagnóstico, planejamento de tratamento e predição de prognóstico em todas as especialidades odontológicas. A revisão revela que as aplicações de IA se concentraram principalmente em radiologia odontológica (36%), seguidas por ortodontia (18%), periodontia (12%) e cirurgia (10%). Modelos baseados em redes neurais convolucionais (CNN) demonstraram acurácia diagnóstica superior (média 89,5%) em comparação com machine learning tradicional (82,3%).

## Palavras-chave
Inteligência Artificial, Odontologia, Sistemas Especialistas, Revisão Sistemática, Machine Learning, Deep Learning, CNN, Diagnóstico

## Nível de Dificuldade no Livro
- [ ] 🟢 N0-3: Fundacional
- [x] 🟡 N4-7: Intermediário
- [ ] 🔴 N8-9: Avançado
- [ ] 🟣 N10+: PhD

## Recorte Textual Utilizado no Livro
> "The application of AI in dentistry has evolved significantly over the past two decades, transitioning from rule-based expert systems to sophisticated deep learning models. Convolutional neural networks (CNNs) have demonstrated superior diagnostic accuracy (mean 89.5%) compared to traditional machine learning approaches (82.3%), particularly in radiographic interpretation tasks. However, the integration of AI into routine dental practice requires overcoming challenges related to data standardization, model generalizability across diverse populations, and the development of regulatory frameworks."

## Justificativa do Uso
Este trecho sintetiza a narrativa histórica central do livro: a transição tecnológica dos sistemas baseados em regras para o deep learning, fornecendo dados quantitativos comparativos (89,5% vs 82,3%) que fundamentam a superioridade das CNNs. A menção aos desafios de padronização, generalização e regulação conecta a revisão histórica aos capítulos práticos subsequentes do livro, estabelecendo uma ponte entre o estado da arte e os obstáculos pendentes para a adoção clínica. A abrangência temporal (2000-2020) torna este artigo a espinha dorsal cronológica de todo o livro.

## Relevância para o Capítulo
- Capítulo(s): Capítulo 1 (História e Evolução da IA na Odontologia), Capítulo 2 (Fundamentos de Machine Learning para Dentistas)
- Seção(ões): 1.2 (Sistemas Especialistas Pioneiros), 1.3 (A Transição para Deep Learning), 2.1 (Panorama de Aplicações por Especialidade)

## Métricas Reportadas (se aplicável)
- Acurácia: 89,5% (média, modelos CNN); 82,3% (média, ML tradicional)
- Sensibilidade: 87,2% (pooled, diagnóstico radiográfico)
- Especificidade: 90,1% (pooled, diagnóstico radiográfico)
- AUC: 0,91–0,96 (variação entre especialidades)
- F1: Não reportado de forma agregada
- Outras: QUADAS-2 (risk of bias assessment), 43 artigos incluídos de 1.823 inicialmente identificados

## Resenha Crítica

### Contribuições
Khanagar et al. (2021) oferecem a mais abrangente sistematização da literatura sobre IA odontológica até sua publicação, constituindo-se como o artigo de referência obrigatória para qualquer pesquisador que ingressa no campo. A utilização do instrumento QUADAS-2 para avaliação de risco de viés confere rigor metodológico à síntese, permitindo ao leitor discernir entre estudos robustos e aqueles com limitações metodológicas. A categorização das aplicações por especialidade odontológica (radiologia 36%, ortodontia 18%, periodontia 12%, cirurgia 10%) fornece um mapa quantitativo da distribuição do esforço de pesquisa, revelando tanto as áreas de concentração quanto as lacunas existentes — informação valiosa para orientar investigações futuras e para a estruturação do próprio livro. A análise temporal demonstra inequivocamente a aceleração da produção científica a partir de 2016, coincidindo com a popularização de frameworks de deep learning como TensorFlow e PyTorch, contextualizando o boom da IA odontológica dentro do ecossistema mais amplo da revolução do deep learning.

### Limitações
A principal limitação reside na heterogeneidade dos estudos incluídos, que abrangem modalidades de imagem diversas (periapicais, panorâmicas, CBCT, fotografias clínicas), arquiteturas variadas e populações heterogêneas — o que torna as estimativas pooled intrinsecamente limitadas em precisão. A revisão se estende apenas até 2020, não capturando a explosão de publicações sobre transformers, Segment Anything Model (SAM) e large language models que caracterizou o período 2022-2025. Além disso, a análise de viés (QUADAS-2) revelou que apenas 37% dos estudos incluíram validação externa, comprometendo as alegações de generalização. O artigo não discute aspectos éticos, de equidade algorítmica ou de sustentabilidade ambiental (carbon footprint do treinamento de modelos), temas que se tornaram centrais no debate sobre IA responsável no triênio subsequente.

### Metodologia
A metodologia segue rigorosamente o protocolo PRISMA, com busca sistemática em 7 bases de dados (PubMed, Medline, Embase, Cochrane, Google Scholar, Scopus, Web of Science), critérios de inclusão/exclusão explícitos, extração de dados por dois revisores independentes e avaliação de qualidade metodológica via QUADAS-2. A análise de performance foi conduzida de forma descritiva (narrativa), sem metanálise quantitativa — escolha justificada pela heterogeneidade dos estudos, mas que limita a força das conclusões comparativas. O desfecho primário foi acurácia diagnóstica; desfechos secundários incluíram sensibilidade, especificidade, AUC e tempo de processamento. A ausência de síntese quantitativa (meta-analysis) representa a maior fragilidade metodológica, pois impede estimativas de efeito sumário com intervalos de confiança.

### Relevância para a odontologia brasileira
A revisão não inclui estudos conduzidos no Brasil ou na América Latina, expondo uma lacuna de representatividade regional que o próprio livro se propõe a mitigar. A concentração de datasets e estudos em populações asiáticas e europeias (China, Coreia do Sul, Alemanha, Reino Unido) levanta questões sobre a validade externa desses modelos para a população brasileira — miscigenada, com perfil epidemiológico distinto e acesso heterogêneo a serviços odontológicos. Pesquisadores brasileiros podem utilizar este artigo como referência para identificar nichos de aplicação ainda não explorados e para contextualizar seus próprios estudos dentro do panorama internacional, adaptando arquiteturas e métodos às especificidades do sistema de saúde bucal brasileiro (SUS, saúde suplementar, teleodontologia no Programa Saúde da Família).

### Lacunas identificadas
(1) Ausência total de estudos latino-americanos; (2) sub-representação de periodontia, odontopediatria e saúde coletiva; (3) carência de análises de custo-efetividade; (4) nenhum estudo abordou aceitação do paciente ou confiança em diagnósticos mediados por IA; (5) inexistência de protocolos para integração com sistemas de prontuário eletrônico; (6) silêncio sobre questões regulatórias e de responsabilidade legal (quem responde por erro diagnóstico da IA?).

## Imagens Utilizadas
- [x] Figura(s) do artigo usada(s) no livro
- [x] Licença verificada
- [x] Legenda adaptada (ABNT + Licença)
- **Figuras selecionadas:** Figura 1 (Fluxograma PRISMA de seleção dos artigos) e Figura 2 (Distribuição de aplicações de AI por especialidade odontológica)

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
