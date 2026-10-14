from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'modulos'
for original in (ROOT / 'revisao-abnt' / 'original' / 'modulos').glob('*.tex'):
    if original.name != '08-referencias.tex':
        (MOD / original.name).write_bytes(original.read_bytes())

def write(name, content):
    (MOD / name).write_text(content.strip() + '\n', encoding='utf-8')

main = r'''% !TeX program = xelatex
% Revisão editorial e normativa em 10/10/2026; dados autorais pendentes.
\documentclass[12pt,openany,oneside,a4paper,brazil,chapter=TITLE]{abntex2}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\setsansfont{TeX Gyre Termes}
\setmonofont{DejaVu Sans Mono}[Scale=0.82]
\usepackage{amsmath,amssymb,booktabs,tabularx,longtable,array,verbatim,listings}
\usepackage[authoryear,round]{natbib}
\usepackage{xurl}
\setlength{\emergencystretch}{2em}
\setcitestyle{aysep={,},citesep={;}}
\let\cite\citep
\renewcommand{\bibsection}{\chapter*{Referências}\addcontentsline{toc}{chapter}{REFERÊNCIAS}}
\setlength{\bibhang}{0pt}
\setlength{\bibsep}{\baselineskip}
\renewcommand{\ABNTEXchapterfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXchapterfontsize}{\normalsize}
\renewcommand{\ABNTEXsectionfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXsectionfontsize}{\normalsize}
\renewcommand{\ABNTEXsubsectionfont}{\normalfont\bfseries}
\renewcommand{\ABNTEXsubsectionfontsize}{\normalsize}
\setlength{\beforechapskip}{0pt}
\setlength{\afterchapskip}{1.5\baselineskip}
\setlrmarginsandblock{3cm}{2cm}{*}
\setulmarginsandblock{3cm}{2cm}{*}
\checkandfixthelayout[fixed]
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0pt}
\OnehalfSpacing
\makepagestyle{abntsubmissao}
\makeoddhead{abntsubmissao}{}{}{\fontsize{10}{12}\selectfont\thepage}
\makeevenhead{abntsubmissao}{}{}{\fontsize{10}{12}\selectfont\thepage}
\makeoddfoot{abntsubmissao}{}{}{}
\makeevenfoot{abntsubmissao}{}{}{}
\captionnamefont{\fontsize{10}{12}\selectfont}
\captiontitlefont{\fontsize{10}{12}\selectfont}
\captiondelim{ --- }
\captionstyle{\raggedright}
\setlength{\tabcolsep}{4pt}
\lstset{basicstyle=\fontsize{10}{12}\selectfont\ttfamily,breaklines=true,
breakatwhitespace=false,columns=fullflexible,keepspaces=true,showstringspaces=false,
literate={á}{{\'a}}1 {à}{{\`a}}1 {â}{{\^a}}1 {ã}{{\~a}}1 {é}{{\'e}}1 {è}{{\`e}}1 {ê}{{\^e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ô}{{\^o}}1 {õ}{{\~o}}1 {ú}{{\'u}}1 {ç}{{\c c}}1 {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Õ}{{\~O}}1 {Ú}{{\'U}}1 {Ç}{{\c C}}1 {—}{{---}}1 {–}{{--}}1 {°}{{\textdegree}}1 {±}{{$\pm$}}1 {×}{{$\times$}}1 {→}{{$\to$}}1 {≤}{{$\le$}}1 {≥}{{$\ge$}}1 {≠}{{$\ne$}}1}
\titulo{Roteamento inspirado em atenção: formalização do núcleo matemático em Lean 4 e avaliação empírica interna}
\autor{Marcelo Claro Laranjeira}
\local{Porto Alegre}
\data{2026}
\orientador{[nome e titulação do orientador --- preencher]}
\instituicao{Pontifícia Universidade Católica do Rio Grande do Sul}
\tipotrabalho{Dissertação (Mestrado)}
\preambulo{Dissertação apresentada ao Programa de Pós-Graduação em [nome do programa --- preencher] da Pontifícia Universidade Católica do Rio Grande do Sul como requisito parcial para obtenção do título de Mestre em [denominação do título --- preencher]. Área de concentração: [preencher]. Linha de pesquisa: [preencher].}
\hypersetup{hidelinks,pdftitle={Roteamento inspirado em atenção: formalização do núcleo matemático em Lean 4 e avaliação empírica interna},pdfauthor={Marcelo Claro Laranjeira},pdfsubject={Dissertação: revisão editorial e normativa para submissão},pdfkeywords={Lean 4; verificação formal; roteamento; atenção; avaliação empírica}}
\begin{document}
\frenchspacing
\hypersetup{pageanchor=false}
\begin{capa}
\begin{center}
\imprimirinstituicao\par
Programa de Pós-Graduação em [nome do programa --- preencher]\par
\vspace{2cm}
\imprimirautor\par
\vfill
\textbf{\MakeUppercase{\imprimirtitulo}}\par
\vfill
\imprimirlocal\par
\imprimirdata
\end{center}
\end{capa}
\setcounter{page}{1}
\begin{folhaderosto}
\begin{center}
\imprimirautor\par
\vfill
\textbf{\imprimirtitulo}\par
\vfill
\end{center}
\noindent\hspace*{0.5\textwidth}\begin{minipage}{0.5\textwidth}
\SingleSpacing
\imprimirpreambulo\par\vspace{\baselineskip}
Orientação: \imprimirorientador.
\end{minipage}
\vfill
\begin{center}\imprimirlocal\par\imprimirdata\end{center}
\end{folhaderosto}
% Ficha imediatamente após o rosto; esta página não entra na contagem.
\thispagestyle{empty}\vspace*{\fill}
\begin{center}\begin{minipage}{0.8\textwidth}\SingleSpacing
\textbf{Ficha catalográfica}\par
[Inserir a ficha emitida pelo serviço de catalogação da instituição após a confirmação dos dados autorais e da versão final.]
\end{minipage}\end{center}
\vspace*{\fill}\clearpage\addtocounter{page}{-1}
\begin{folhadeaprovacao}
\begin{center}\imprimirautor\par\vspace{\baselineskip}\textbf{\imprimirtitulo}\end{center}
\vspace{\baselineskip}
\noindent\hspace*{0.5\textwidth}\begin{minipage}{0.5\textwidth}\SingleSpacing\imprimirpreambulo\end{minipage}
\vspace{2\baselineskip}
\noindent Data da aprovação: [preencher somente após a defesa].\par
\noindent Banca examinadora: [nomes, titulações, instituições e assinaturas --- preencher].\par
\vspace{2\baselineskip}
\noindent [A aprovação e as assinaturas ainda não foram registradas nesta versão.]
\end{folhadeaprovacao}
\begin{agradecimentos}
Às comunidades Lean e Mathlib, pela manutenção das ferramentas e bibliotecas utilizadas, e às iniciativas de ciência aberta que apoiam a documentação e a consulta das fontes deste trabalho.
\end{agradecimentos}
\begin{resumo}
Este trabalho investiga a formalização do núcleo matemático e a avaliação empírica interna de um mecanismo de roteamento de tarefas entre agentes de software, inspirado na ponderação por atenção. A pesquisa combina provas em Lean 4 com Mathlib, inspeção dos artefatos de execução, uma bancada sintética e testes aleatórios de propriedades numéricas. Os registros locais documentam onze lemas sobre normalização do softmax, limites de combinações convexas, existência de maximizador finito, invariância a deslocamento, pesos positivos, caso de candidato único, monotonicidade, ordenação top-\textit{k}, temperatura e limite superior da exponencial após deslocamento. As provas referem-se à aritmética real exata e não certificam integralmente a implementação em ponto flutuante. Na bancada principal, com 200 decisões distribuídas por cinco sementes, o arrependimento médio registrado foi $0{,}042$, com margem exploratória de $0{,}011$, frente a valores entre $0{,}19$ e $0{,}22$ dos comparadores simples. Ablações em um conjunto distinto de instâncias indicam dependência da confiança, construída como proxy da qualidade latente. A variação do parâmetro do oráculo apenas reescala a perda entre candidatos plenamente elegíveis. Os intervalos desconsideram o agrupamento por piscina de agentes e devem ser interpretados como resumos exploratórios. O relatório numérico registra 20\,000 vetores sem violações acima das tolerâncias examinadas. Conclui-se que os artefatos sustentam propriedades do modelo abstrato e resultados preliminares no simulador, permanecendo pendentes a certificação numérica completa, a análise estatística com agrupamento, a comparação externa e a reprodução independente.
\par\vspace{\baselineskip}
\noindent\textbf{Palavras-chave:} roteamento de agentes; atenção; Lean 4; verificação formal; avaliação empírica; reprodutibilidade.
\end{resumo}
\begin{resumo}[Abstract]
\begin{otherlanguage*}{english}
This dissertation investigates the formalization of the mathematical core and the internal empirical evaluation of a task router for software agents inspired by attention-based weighting. The study combines proofs in Lean 4 with Mathlib, inspection of execution artifacts, a synthetic benchmark, and randomized tests of numerical properties. Local records document eleven lemmas on softmax normalization, convex-combination bounds, existence of a finite maximizer, shift invariance, positive weights, the singleton case, monotonicity, top-\textit{k} ordering, temperature, and an upper bound on shifted exponentials. The proofs concern exact real arithmetic and do not fully certify the floating-point implementation. In the main benchmark, comprising 200 decisions across five seeds, recorded mean regret was $0.042$, with an exploratory margin of $0.011$, compared with values between $0.19$ and $0.22$ for simple baselines. Ablations on a distinct set of instances indicate dependence on confidence, which was constructed as a proxy for latent quality. Changing the oracle parameter only rescales regret among fully eligible candidates. The reported intervals disregard clustering within agent pools and should be interpreted as exploratory summaries. The numerical report records 20,000 vectors with no violations above the tested tolerances. The artifacts support properties of the abstract model and preliminary findings within the simulator. Full numerical certification, statistical analysis accounting for clustering, external comparison, and independent reproduction remain pending.
\par\vspace{\baselineskip}
\noindent\textbf{Keywords:} agent routing; attention; Lean 4; formal verification; empirical evaluation; reproducibility.
\end{otherlanguage*}
\end{resumo}
\pdfbookmark[0]{Lista de tabelas}{lot}
\listoftables*
\begin{siglas}
\item[ABNT] Associação Brasileira de Normas Técnicas
\item[IC] Intervalo de confiança
\item[IEEE] Institute of Electrical and Electronics Engineers
\item[JSON] JavaScript Object Notation
\item[MCP] Model Context Protocol
\item[OSF] Open Science Framework
\item[PUCRS] Pontifícia Universidade Católica do Rio Grande do Sul
\item[Q/K/V] Consulta, chave e valor (\textit{query, key, value})
\item[SDD] Desenvolvimento orientado a especificação
\item[SMT] Satisfatibilidade módulo teorias
\item[TDD] Desenvolvimento orientado a testes
\end{siglas}
\begin{simbolos}
\item[$w_i$] Peso de atenção do candidato $i$
\item[$f_i$] Escore do candidato $i$
\item[$\tau$] Temperatura positiva do softmax
\item[$q$] Qualidade latente do agente no simulador
\item[$q_w$] Peso da qualidade no oráculo sintético
\item[$u(a)$] Utilidade combinada do candidato $a$
\item[$\alpha_h$] Peso fixo da cabeça $h$
\end{simbolos}
\pdfbookmark[0]{Sumário}{toc}
\tableofcontents*
\clearpage
\textual
\pagestyle{abntsubmissao}\aliaspagestyle{chapter}{abntsubmissao}
\hypersetup{pageanchor=true}
\input{modulos/01-introducao}
\input{modulos/02a-preliminares}
\input{modulos/02f-nucleo-matematico}
\input{modulos/02g-curso-embutido}
\input{modulos/02-fundamentacao}
\input{modulos/02b-contexto-atencao}
\input{modulos/02c-lean-tutorial}
\input{modulos/02d-trabalhos-relacionados}
\input{modulos/03-metodo}
\input{modulos/03b-estatistica}
\input{modulos/04-provas}
\input{modulos/04b-provas-detalhadas}
\input{modulos/05-calibracao}
\input{modulos/05b-estudo-caso-reais}
\input{modulos/05c-estrategias}
\input{modulos/06-discussao}
\input{modulos/07-conclusao}
\postextual
\begin{SingleSpacing}
\raggedright
\input{modulos/08-referencias}
\end{SingleSpacing}
\input{modulos/10-apendice-glossario}
\input{modulos/09-apendices}
\end{document}
'''
(ROOT / 'dissertacao.tex').write_text(main, encoding='utf-8')

write('03-metodo.tex', r'''
% Revisão metodológica: artefatos históricos, sem reexecução experimental.
\chapter{Método}\label{cap:metodo}
A pesquisa combina formalização matemática, avaliação em simulador e inspeção documental dos artefatos locais. As etapas e seus limites são descritos a seguir para permitir a reprodução e distinguir os registros históricos da revisão editorial.
\section{Provas formais}
O arquivo \texttt{roteamento\_atencao.lean} (Apêndice~\ref{ap:lean}) foi processado por \texttt{lake env lean} no ambiente registrado, com Lean v4.34.1 e Mathlib rev.\ v4.34.1. A auditoria \texttt{\#print axioms} registra as dependências de cada enunciado. O verificador e a interface MCP incluem controles para \texttt{sorry}, \texttt{admit} e axiomas não declarados. As propriedades formalizadas referem-se a funções sobre os reais; não foi demonstrado um refinamento completo entre o modelo abstrato e todos os componentes da implementação Python.
\section{Bancada sintética e conjuntos de instâncias}
A bancada principal utiliza cinco sementes (11, 22, 33, 44 e 55), cada uma gerando uma piscina de 40 agentes sintéticos e 40 tarefas, totalizando 200 decisões. A qualidade latente $q$ não é fornecida diretamente ao roteador, mas a confiança é construída como uma proxy informativa dessa qualidade. O oráculo atribui utilidade $\mathrm{cobertura}\times((1-q_w)+q_wq)$. Comparam-se o roteador, a seleção aleatória, a escolha de menor carga e a escolha de maior cobertura. Registram-se arrependimento, acerto, latência e desvio da soma dos pesos.
As ablações utilizam as sementes efetivas 10011, 10022, 10033, 10044 e 10055, produzindo outro conjunto de 200 decisões. Incluem média igualitária das cabeças, remoção da confiança e confiança embaralhada, anticorrelacionada ou ruidosa. O pareamento compara estratégias dentro de cada execução das ablações; não vincula essas decisões às instâncias da bancada principal. A coleta de correlações utiliza sua própria sequência de sorteios e também não corresponde integralmente às tarefas das ablações.
Na condição de confiança ruidosa, adiciona-se ruído gaussiano com desvio 0,4, limita-se o resultado a $[0,1]$ e aplica-se arredondamento inteiro, gerando confiança 0 ou 1. O tratamento combina perturbação e discretização binária.
\section{Parâmetro do oráculo}
Nas ablações, avaliam-se $q_w\in\{0{,}3;0{,}6;0{,}9\}$ sobre as mesmas instâncias. O filtro de elegibilidade exige cobertura completa; assim, o oráculo entre candidatos elegíveis reduz-se a $1-q_w+q_wq$. Para $q_w>0$, seu ranking permanece inalterado e o arrependimento é $q_w(q_{\max}-q_{\mathrm{escolhido}})$. A variação descreve a escala da perda, sem testar critérios ou ordenações diferentes do oráculo.
\section{Testes numéricos e estatística exploratória}
O relatório interno registra testes aleatórios de 20\,000 vetores, de tamanho 1--50 e escores de magnitude até $\pm1000$, examinando propriedades da implementação em ponto flutuante. A ausência de violações na amostra não certifica todas as entradas nem substitui a prova de refinamento numérico. A documentação da segunda execução mencionada na versão anterior não foi identificada de forma individualizável nesta revisão; o total aqui relatado restringe-se ao registro local identificado.
Os intervalos foram calculados por aproximação normal com desvio de divisor $n$. As 40 decisões de cada semente compartilham uma piscina de agentes. Como os intervalos não consideram esse agrupamento em cinco piscinas, são resumos exploratórios que podem subestimar a incerteza entre piscinas. Uma análise com agrupamento permanece pendente. Correlações de Pearson descrevem associações lineares; não estabelecem causalidade.
\section{Ameaças à validade e considerações éticas}
\textit{Construção:} o oráculo é arbitrário e a confiança fornece informação sobre a qualidade latente por desenho. A correlação registrada de aproximadamente $+0{,}85$ explicita essa proxy privilegiada. \textit{Validade interna:} o pareamento controla diferenças de dificuldade entre estratégias de uma mesma execução, mas não elimina todos os fatores de confusão. \textit{Validade externa:} os resultados são restritos ao simulador; não há avaliação executada em benchmarks externos nem mensuração de tarefas realizadas por agentes. \textit{Validade de conclusão:} cinco piscinas, comparadores simples e intervalos sem agrupamento limitam a interpretação inferencial.
Não foram utilizados dados de participantes humanos nos experimentos descritos. A declaração ética exigida pelo programa e eventuais dispensas institucionais permanecem sob responsabilidade do autor. O estudo não fundamenta alegações de superioridade externa ou de originalidade validada por avaliadores externos.
\section{Protocolo de desenvolvimento e reprodução}
Os registros de desenvolvimento vinculam as funcionalidades às especificações SPEC-935 e às transcrições de testes preservadas nos apêndices. O protocolo documenta etapas RED--GREEN, auditorias de axiomas e correções de falhas. Esses registros históricos não equivalem à reexecução integral na data desta revisão. As versões, os hashes e as saídas devem acompanhar o depósito final dos artefatos, ainda pendente.
''')

write('03b-estatistica.tex', r'''
\section{Interpretação das métricas}
O arrependimento é a diferença entre a maior utilidade do oráculo e a utilidade do candidato escolhido; zero indica uma escolha ótima segundo esse oráculo. A taxa de acerto é a fração de decisões que atingem esse máximo. A taxa de vitória ou empate nas ablações é a fração de decisões em que a atenção apresenta arrependimento menor ou igual ao comparador. Pearson $r$ mede associação linear, sem demonstrar causalidade ou independência quando próximo de zero. A semente fixa a sequência pseudoaleatória utilizada em cada coleta.
\section{Intervalos registrados e seus limites}
O relato por estimação é apoiado por \cite{cumming2014,wasserstein2016}. Nos scripts deste trabalho, a margem registrada é $1{,}96s_n/\sqrt{n}$, com $s_n$ calculado com divisor $n$. Com $n=200$ e margem $0{,}0105$, obtém-se $s_n\approx0{,}0758$. Essa identidade explica o cálculo preservado, sem validar a independência das decisões. A interpretação comparativa requer considerar o desenho, a dependência entre observações e o intervalo da diferença pareada. A não sobreposição de intervalos isolados não substitui essa análise.
Como cada piscina gera 40 decisões, a análise futura deve considerar o agrupamento por semente. Reamostragem \cite{efron1979} é uma possibilidade, desde que respeite a unidade de agrupamento; cinco piscinas ainda limitam a precisão. Não foi efetuado recálculo inferencial nesta revisão.
\section{Pareamento e calibração probabilística}
Na ablação com $q_w=0{,}6$, a diferença de arrependimento entre média igualitária e atenção é aproximadamente $+0{,}035$, com margem exploratória $0{,}011$. O sinal positivo descreve vantagem na amostra pareada registrada; não demonstra robustez fora desse desenho. A normalização de pesos não é calibração probabilística. Regras de escore próprias \cite{gneiting2007} oferecem fundamentos para outra análise, mas não foram calculadas curvas de calibração, erros de calibração ou escores probabilísticos nesta avaliação.
''')

write('05c-estrategias.tex', r'''
\section{Interpretação das estratégias}
A estratégia de atenção utiliza quatro componentes com pesos fixos declarados, sem aprendizagem desses pesos. No simulador, a confiança é construída a partir da qualidade latente com ruído, constituindo uma proxy informativa por desenho. A média igualitária compara outra ponderação dos mesmos componentes; a remoção da confiança avalia a decisão sem essa informação.
A seleção aleatória sorteia entre elegíveis. A escolha de menor carga utiliza a disponibilidade, que não compõe diretamente a qualidade latente do oráculo. A escolha de maior cobertura encontra empate entre candidatos plenamente elegíveis, pois o filtro já exigiu cobertura completa. Seu resultado não mede discriminação adicional por cobertura.
A remoção da confiança e suas perturbações produziram maior arrependimento nas amostras das ablações. Esse resultado é compatível com a dependência da decisão em relação à proxy. Não demonstra equivalência estatística com o acaso, relação dose--resposta ou ausência de influência das sementes. A condição ruidosa inclui discretização binária, conforme descrito na Seção~\ref{cap:metodo}.
''')

write('06-discussao.tex', r'''
\chapter{Discussão}\label{cap:discussao}
Os resultados articulam duas formas de evidência com alcances diferentes: as provas documentam propriedades do modelo matemático; a bancada descreve o comportamento de uma implementação em instâncias sintéticas. A composição torna explícitos os pressupostos da decisão, mas não fornece uma certificação integral da execução nem uma comparação de desempenho em tarefas reais.
\section{Alcance das garantias formais}
Os onze lemas são propriedades matemáticas elementares, formalizadas sobre o objeto estudado. Não se reivindica originalidade desses fatos. T3 estabelece existência de maximizador finito, enquanto T9 descreve a dominância de um prefixo de lista já ordenada. A correspondência entre essas propriedades e o código exige demonstrar a preservação de hipóteses pelo filtro, pelos escores, pelo desempate e pela aritmética utilizada. T11 limita a exponencial deslocada em reais exatos; erros de arredondamento, underflow, entradas não finitas e operações intermediárias permanecem fora dessa prova.
\section{Dependência do desenho sintético}
A vantagem observada depende da confiança, construída como proxy da qualidade latente. Sua remoção aumenta o arrependimento no conjunto de ablações, sem estabelecer equivalência com a seleção aleatória. Mesmo confiança igual à qualidade latente não garantiria que a utilidade combinada preservasse o ranking do oráculo, pois semântica e carga também influenciam a escolha. Essa configuração não foi avaliada.
Os três valores de $q_w$ reescalam a perda sem mudar o ranking do oráculo entre elegíveis. Sua estabilidade não constitui evidência independente de robustez a outros critérios de utilidade. Os intervalos preservados ignoram a dependência dentro das piscinas; uma análise que considere agrupamento pode alterar as margens e a interpretação comparativa.
\section{Riscos residuais e avaliação interna}
\begin{table}[htbp]\centering
\caption{Limitações identificadas e requisitos de avaliação futura.}\label{tab:riscos}
\begin{tabularx}{\textwidth}{XX}\toprule
Limitação & Requisito futuro \\\midrule
Oráculo arbitrário e proxy privilegiada & Outros critérios de qualidade e confiança sem acesso ao gerador latente \\
Cinco piscinas e intervalos sem agrupamento & Mais piscinas independentes e análise na unidade correta \\
Modelo real e implementação em ponto flutuante & Refinamento formal e tratamento de casos numéricos especiais \\
Comparadores internos & Benchmark externo executado com orçamento e critérios comuns \\
Artefatos locais & Depósito versionado e reprodução independente \\
\bottomrule\end{tabularx}
\end{table}
Duas revisões internas automatizadas examinaram a bancada e os teoremas. Não constituem revisão cega ou validação externa. As objeções sobre proxy, comparadores, analogia Q/K/V e lacuna numérica são compatíveis com as limitações descritas na Tabela~\ref{tab:riscos}. As ablações acrescentam comparações entre ponderações e perturbações, mas não eliminam essas objeções.
\section{Relação com a literatura e perspectivas}
A literatura de calibração por temperatura \cite{komisarenko2024,xuan2025,xie2024} aborda objetivos que não foram medidos aqui: a normalização por softmax não demonstra calibração probabilística. Os estudos de aritmética flutuante \cite{bagnara2019,murray2026} indicam a necessidade de garantias próprias para a execução numérica. Os benchmarks de agentes \cite{agentbench2023,perspectivegap2026,orchrm2026,orchestrator2025} fornecem contextos para comparação futura, sem validar os resultados locais. A interpretação educacional das trilhas auditáveis é uma hipótese de aplicação futura, sem avaliação com estudantes nesta pesquisa.
''')

write('10-apendice-glossario.tex', r'''
\chapter*{Glossário}\addcontentsline{toc}{chapter}{GLOSSÁRIO}\label{ap:glossario}
\begin{description}[style=nextline,leftmargin=0pt,labelindent=0pt]
\item[Ablação.] Alteração ou remoção de um componente para comparar seu efeito dentro de um desenho definido.
\item[Agente.] Programa ao qual uma tarefa pode ser atribuída; o estudo com cartões calcula rankings e não executa os agentes.
\item[Arrependimento.] Diferença entre a melhor utilidade do oráculo e a utilidade da escolha realizada.
\item[Axioma.] Proposição admitida pelo sistema formal. A auditoria registra \texttt{propext}, \texttt{Classical.choice} e \texttt{Quot.sound}, sem demonstrar minimalidade desse conjunto.
\item[Calibração probabilística.] Correspondência entre probabilidades previstas e frequências observadas; não é garantida apenas pela soma unitária do softmax.
\item[Combinação convexa.] Soma ponderada com pesos não negativos de soma unitária.
\item[Comparador.] Estratégia utilizada como referência para avaliação no mesmo desenho.
\item[Intervalo exploratório.] Faixa calculada pela aproximação normal registrada, sem correção para agrupamento nas piscinas deste estudo.
\item[Oráculo.] Critério sintético usado para avaliar as escolhas; não representa qualidade observada em tarefas reais.
\item[Overflow.] Excesso da faixa representável em ponto flutuante. T11 prova um limite da exponencial em reais exatos e não certifica todas as operações da implementação.
\item[Reprodução.] Execução dos procedimentos por outro executor a partir dos artefatos e do ambiente especificado; reprodução independente permanece pendente.
\item[Roteador.] Mecanismo que filtra candidatos e ordena suas utilidades para selecionar um agente.
\item[Semente.] Valor que inicializa uma sequência pseudoaleatória.
\item[Softmax.] Normalização exponencial de uma família finita não vazia de escores. Em reais exatos, seus pesos somam um e são positivos; em ponto flutuante, underflow pode produzir zeros.
\item[Temperatura.] Parâmetro positivo que controla a concentração dos pesos. T10 utiliza pelo menos dois candidatos e maximizador único como hipóteses suficientes.
\item[Top-\textit{k}.] Prefixo de tamanho $k$ de um ranking; T9 pressupõe a ordenação decrescente da lista.
\item[Underflow.] Resultado muito pequeno para ser representado com a precisão ou a faixa disponíveis.
\item[Verificação por máquina.] Checagem de um termo de prova pelo núcleo do assistente, relativa ao enunciado e aos axiomas utilizados; não garante que o enunciado modele integralmente o sistema concreto.
\end{description}
''')

labels = {'01-introducao.tex':'cap:intro','02a-preliminares.tex':'cap:preliminares',
          '02-fundamentacao.tex':'cap:fundamentacao','04-provas.tex':'cap:provas',
          '05-calibracao.tex':'cap:resultados','07-conclusao.tex':'cap:conclusao'}
for path in MOD.glob('*.tex'):
    if path.name == '08-referencias.tex':
        continue
    text = path.read_text(encoding='utf-8')
    if path.name in labels and labels[path.name] not in text:
        text = re.sub(r'(\\chapter\{[^}]*\})', lambda m:m[1]+'\\label{'+labels[path.name]+'}', text, count=1)
    text = text.replace('recunohecimento','reconhecimento').replace('pinas e hashes','pinos e hashes')
    text = text.replace('reprodução publicada','artefatos locais de reprodução').replace('trilha publicada','trilha local de reprodução').replace('trilha pública','trilha local de reprodução')
    text = text.replace('ausência de overflow','limite superior da exponencial após deslocamento').replace('overflow-free','limite da exponencial deslocada')
    text = text.replace('três mundos','três valores do parâmetro do oráculo').replace('3 mundos','3 valores de $q_w$')
    text = text.replace('calibrar internamente um roteamento','avaliar internamente um roteamento')
    text = text.replace('calibrado internamente','avaliado internamente').replace('calibração interna','avaliação interna')
    text = text.replace('Quinze táticas em prosa','Táticas de uso frequente')
    text = text.replace('Capítulo~1','Seção~\\ref{cap:intro}').replace('Capítulo~2','Seção~\\ref{cap:preliminares}').replace('Capítulo~3','Seção~\\ref{cap:fundamentacao}').replace('Capítulo~4','Seção~\\ref{cap:metodo}').replace('Capítulo~5','Seção~\\ref{cap:provas}').replace('Capítulo~6','Seção~\\ref{cap:resultados}').replace('Capítulo~7','Seção~\\ref{cap:discussao}').replace('Capítulo~8','Seção~\\ref{cap:conclusao}')
    text = text.replace('este capítulo','esta seção').replace('Este capítulo','Esta seção').replace('capítulo','seção').replace('Capítulo','Seção')
    text = text.replace('por \\cite{','por \\citet{')
    text = re.sub(r'\\texttt\{([^{}]{25,})\}', lambda m: '\\nolinkurl{' + m[1].replace('\\_','_') + '}' if re.fullmatch(r'[A-Za-z0-9_/.,*:\\ -]+',m[1]) else m[0], text)
    text = text.replace('Contraprovas e calibração estatística','Avaliação empírica e testes numéricos')
    text = text.replace('contraprovas numéricas','testes aleatórios de propriedades numéricas').replace('contraprova empírica','teste empírico de propriedades').replace('contraprova numérica','teste numérico de propriedades').replace('contraprovas','testes de propriedades')
    path.write_text(text,encoding='utf-8')

p=MOD/'01-introducao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('auditoria sem formalismo não é verificável; medição sem incerteza não é evidência','garantias formais exigem hipóteses explícitas; medições requerem análise de incerteza')
t=t.replace('calibração contra baselines','avaliação contra comparadores').replace('Como decidir, por tarefa, qual agente executar sob critérios múltiplos com garantias auditáveis?','Que propriedades do núcleo matemático de um roteador inspirado em atenção podem ser formalizadas, e que comportamento sua implementação apresenta em uma avaliação sintética interna?')
t=t.replace('Cenário-guia (saídas reais)','Cenário-guia de roteamento (saídas registradas)')
t=t.replace('contraprova numérica','teste aleatório de propriedades numéricas')
p.write_text(t,encoding='utf-8')

p=MOD/'02a-preliminares.tex';t=p.read_text(encoding='utf-8')
t=t.replace('dados escores $f_i$, os pesos $w_i=e^{f_i}/\\sum_j e^{f_j}$ formam a distribuição de máxima entropia compatível com a média dos escores','sob uma restrição adequada de média, a solução tem forma $w_i\\propto e^{\\beta f_i}$, com $\\beta$ determinado pela restrição; o softmax usual corresponde ao caso particular $\\beta=1$')
t=t.replace('a soma telescopa em $S/S=1$','a soma com denominador comum reduz-se a $S/S=1$')
t=t.replace('\\textit{Overflow.} Deslocado pelo máximo, todo expoente é $\\leq0$ e cada exponencial fica em $(0,1]$: nenhum estouro possível.','\\textit{Limite da exponencial.} Em reais exatos, deslocar pelo máximo torna cada expoente não positivo e cada exponencial pertence a $(0,1]$. T11 demonstra esse limite; em ponto flutuante, underflow e arredondamento requerem análise própria.')
t=t.replace('Cálculo dito passo a passo','Exemplos de cálculo')
p.write_text(t,encoding='utf-8')

p=MOD/'02g-curso-embutido.tex';t=p.read_text(encoding='utf-8')
t=t.replace('produz $w_i\\propto e^{\\beta f_i}$:','produz $w_i\\propto e^{\\beta f_i}$, com $\\beta$ determinado pela média imposta:')
t=t.replace('logo cada termo fica em $(0,1]$: o estouro torna-se impossível por construção, e a divisão final reescala sem perda de decisão (T4).','logo cada termo fica em $(0,1]$ em aritmética real exata. Esse limite não certifica as operações IEEE-754: exponenciais pequenas podem sofrer underflow, e a invariância exata de T4 não implica igualdade bit a bit para quaisquer entradas.')
t=t.replace('parear estratégias nas mesmas decisões elimina variação de dificuldade','parear estratégias nas mesmas decisões controla diferenças de dificuldade entre comparadores')
t=t.replace('softmax calibra','softmax normaliza').replace('não default','sem presunção de validade')
p.write_text(t,encoding='utf-8')

p=MOD/'02-fundamentacao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('protocolo pronto na Seção~5','protocolo proposto na Seção~\\ref{cap:conclusao}')
t=t.replace('\\section{Ponderação exponencial calibrada}','\\section{Ponderação exponencial normalizada}\nA soma unitária dos pesos não demonstra calibração probabilística. A avaliação deste trabalho mede arrependimento e acerto, sem ajuste de temperatura, aprendizagem de pesos ou estimação de métricas de calibração.')
p.write_text(t,encoding='utf-8')

p=MOD/'02f-nucleo-matematico.tex';t=p.read_text(encoding='utf-8').replace('Afiação por temperatura','Concentração por temperatura')
t=t.replace('o conteúdo numérico de T10','uma ilustração numérica de T10')
p.write_text(t,encoding='utf-8')

p=MOD/'04-provas.tex';t=p.read_text(encoding='utf-8')
t=t.replace('Do protocolo aos enunciados: o que foi demonstrado, em notação matemática, antes da dissecação.','A formalização abrange o núcleo matemático abstrato. Não foi demonstrado um refinamento completo entre esses objetos e a implementação Python, incluindo elegibilidade, representações semânticas, desempate, arredondamento e execução dos agentes. Os registros de auditoria dos onze enunciados são apresentados na Tabela~\\ref{tab:ax}.')
t=t.replace('\\tau_1<\\tau_2\\Rightarrow','0<\\tau_1<\\tau_2\\Rightarrow').replace('(maximizador único)','(maximizador único; ao menos dois candidatos)')
t=t.replace('Os onze enunciados, em notação matemática. Comentário geral, com lastro:','Os enunciados e suas hipóteses são resumidos a seguir:')
t=t.replace('\\begin{equation}','\\begin{equation*}').replace('\\end{equation}','\\end{equation*}')
t=t.replace('axiomas padrão','axiomas registrados na auditoria')
t=t.replace('T11) limite superior da exponencial após deslocamento: expoentes deslocados $\\leq 0$ (caracterização da exponencial)','T11) limite superior da exponencial após deslocamento: expoentes deslocados $\\leq 0$ (caracterização da exponencial real)')
p.write_text(t,encoding='utf-8')

p=MOD/'04b-provas-detalhadas.tex';t=p.read_text(encoding='utf-8')
t=t.replace('produzem os mesmos três pesos bit a bit','produzem os mesmos pesos em aritmética real; os valores arredondados do exemplo coincidem')
t=t.replace('Sem maximizador único (empate), esfriar nada decide --- hipótese exigida pelo compilador.','O enunciado formal adota maximizador único e pelo menos dois candidatos como hipóteses suficientes. Máximos empatados podem ganhar massa quando existem escores inferiores; se todos os escores forem iguais, a temperatura não altera os pesos.')
t=t.replace('Enunciado: expoentes deslocados por majorante ficam $\\leq0$. Derivação: caracterização da exponencial.','Enunciado: se $f_i\\leq M$, então $e^{f_i-M}\\leq1$ em reais exatos. Derivação: monotonicidade da exponencial e $e^0=1$. A prova não certifica subtração, exponenciação, soma ou divisão IEEE-754.')
t=t.replace('T9 estende T3 ao top-\\textit{k}','T9 descreve a ordenação do top-\\textit{k}, sem constituir sozinho prova do algoritmo concreto')
p.write_text(t,encoding='utf-8')

p=MOD/'05-calibracao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('Teoremas provados, hora de medir: esta seção submete a implementação a testes de propriedades e estatística.','Esta seção apresenta os resultados históricos da bancada e das ablações, distinguidos pelos conjuntos de instâncias descritos na Seção~\\ref{cap:metodo}.')
t=re.sub(r'Duas sementes independentes de 20.*?\\section\{Bancada principal e sensibilidade\}',lambda m:r'''O relatório interno registra testes aleatórios de 20\,000 vetores, sem violações acima das tolerâncias examinadas: $10^{-9}$ para a soma e $10^{-12}$ para o deslocamento. O maior desvio registrado da soma foi aproximadamente $2{,}2\times10^{-16}$. A preservação de argmax, os limites, o caso de candidato único e o tratamento do conjunto vazio também foram examinados. A ausência de violações nessa amostra não demonstra correção para todas as entradas. Testes por entradas aleatórias têm antecedentes na avaliação de utilitários Unix \cite{miller1990}.
\section{Bancada principal e variação do parâmetro do oráculo}''',t,flags=re.S)
t=t.replace('Bancada (200 decisões) e sensibilidade do oráculo (diferenças pareadas vs.\\ atenção).','Ablações: arrependimento por parâmetro do oráculo e diferença em relação à atenção (200 decisões por configuração).')
t=t.replace('Mundos adicionais','Outras condições de ablação').replace('Rerreplicação determinística bit a bit confirmada.','Os registros internos relatam reexecução determinística; uma reprodução independente permanece pendente.')
t=t.replace('Arrependimento por estratégia nos três mundos (200 decisões cada).','Arrependimento nas ablações para três valores de $q_w$ (mesmas instâncias; 200 decisões por configuração).')
t=re.sub(r'Ranking estável.*?\\begin\{table\}',lambda m:r'''O ranking das estratégias permanece estável na Tabela~\ref{tab:mundos} porque, entre elegíveis com cobertura unitária, o arrependimento é proporcional a $q_w$. As configurações não representam avaliações independentes de oráculos distintos. As diferenças pareadas e suas margens descrevem as instâncias das ablações, sem correção para agrupamento.
\begin{table}''',t,flags=re.S)
t=t.replace('capability constante pós-gate','capacidade constante após o filtro de elegibilidade').replace('Regressão: 63 testes em 9 suítes; ambiente sem falhas (18/20, 2 advertências pré-existentes).','A transcrição histórica preservada registra 63 testes aprovados em nove suítes. A revisão editorial não reexecutou essa bateria. O diagnóstico preliminar da revisão apresentou 18 verificações aprovadas e duas advertências, sem falhas.')
p.write_text(t,encoding='utf-8')

p=MOD/'05b-estudo-caso-reais.tex';t=p.read_text(encoding='utf-8')
t=t.replace('Estudo de caso com agentes reais','Demonstração de roteamento sobre cartões do catálogo')
t=t.replace('Onze agentes reais do catálogo, cinco tarefas desenhadas no vocabulário efetivo de tags.','Foram utilizados onze cartões extraídos do catálogo local para cinco descrições de tarefas construídas com seu vocabulário de tags. A demonstração avalia elegibilidade e ranking; não executa os agentes nem mede o sucesso na realização das tarefas.')
t=t.replace('comportamento correto, não falha: o roteador recusa em vez de chutar','resultado compatível com o contrato do filtro; a cobertura do vocabulário do catálogo ainda requer avaliação')
p.write_text(t,encoding='utf-8')

p=MOD/'07-conclusao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('Núcleo matemático de onze lemas verificado por máquina, avaliado internamente e auditado até os axiomas, com artefatos locais de reprodução.','A questão da pesquisa foi respondida em dois níveis: os registros documentam onze lemas do modelo matemático formalizados em Lean 4 e uma avaliação preliminar da implementação no simulador, com artefatos locais de reprodução.')
t=t.replace('bancada com intervalos, pareamento e sensibilidade','bancada com intervalos exploratórios, pareamento e variação de escala do oráculo')
t=t.replace('temperatura com limites, benchmark externo','análise com agrupamento por piscina, temperatura com limites, benchmark externo')
p.write_text(t,encoding='utf-8')

# Fontes e composição uniforme das tabelas, sem modificar resultados.
for path in MOD.glob('*.tex'):
    if path.name in ('08-referencias.tex','tabela_historico.tex'):
        continue
    t=path.read_text(encoding='utf-8')
    t=t.replace('\\begin{table}[h]','\\begin{table}[htbp]')
    t=re.sub(r'(\\begin\{table\}\[htbp\])',r'\1\n\\fontsize{10}{12}\\selectfont\\SingleSpacing',t)
    for columns in ('ll','lll'):
        spec='XX' if columns=='ll' else 'lXX'
        t=t.replace('\\begin{tabular}{'+columns+'}','\\begin{tabularx}{\\textwidth}{'+spec+'}')
    t=re.sub(r'(\\begin\{tabularx\}.*?)(\\end\{tabular\})',r'\1\\end{tabularx}',t,flags=re.S)
    t=t.replace('\\end{table}','\\fonte{Elaboração própria (2026), a partir dos artefatos e das fontes identificados no texto.}\n\\end{table}')
    path.write_text(t,encoding='utf-8')

# Histórico extenso deve quebrar entre páginas; sem tabela flutuante truncada.
p=MOD/'tabela_historico.tex';t=p.read_text(encoding='utf-8')
t=t.replace('\\begin{tabular}{lll}',r'\begin{longtable}{p{1.1cm}p{1.2cm}p{12.2cm}}'+'\n'+r'\caption{Ciclos de evolução da linhagem Lean-roteamento (registros históricos).}\label{tab:historico}\\')
t=t.replace('Ciclo & Escore & Objeto --- os homônimos legados (escores $\\approx0{,}9$) são outra linhagem','Ciclo & Escore & Objeto registrado')
t=t.replace('\\parbox[t]{9cm}','\\parbox[t]{12cm}')
t=t.replace('\\midrule','\\midrule\n\\endfirsthead\n\\toprule\nCiclo & Escore & Objeto registrado \\\\\n\\midrule\n\\endhead',1)
t=t.replace('\\end{tabular}',r'\end{longtable}'+'\n'+r'\noindent\fonte{Elaboração própria (2026), a partir do registro evolutivo local. Os escores históricos são autoavaliações internas e não equivalem a validação externa.}')
p.write_text(t,encoding='utf-8')

p=MOD/'09-apendices.tex';t=p.read_text(encoding='utf-8')
t=re.sub(r'\\begin\{table\}\[htbp\].*?\\end\{table\}',lambda m:'\\begin{SingleSpacing}\n\\fontsize{10}{12}\\selectfont\n\\input{modulos/tabela_historico.tex}\n\\end{SingleSpacing}' if 'tabela_historico.tex' in m[0] else m[0],t,flags=re.S)
t=t.replace('Depósito OSF pendente','Depósito público dos artefatos pendente')
t=t.replace('Sementes 11--55; 40 tarefas por semente.','Bancada principal: sementes 11, 22, 33, 44 e 55; 40 tarefas por semente. Ablações: sementes efetivas 10011, 10022, 10033, 10044 e 10055. Os códigos e transcrições reproduzidos são artefatos históricos; a execução integral da fonte atual não foi revalidada nesta revisão editorial.')
p.write_text(t,encoding='utf-8')

# Última leitura editorial dos módulos que compõem o corpo.
p=MOD/'01-introducao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('medir avaliação contra comparadores com intervalos de confiança','comparar arrependimento e taxa de acerto com os comparadores, relatando intervalos exploratórios')
t=t.replace('as testes de propriedades e a calibração','os testes de propriedades e a avaliação empírica')
t=t.replace('os Apêndices trazem código, resultados, especificações e glossário didático','o glossário define os termos principais; os apêndices preservam código, resultados, transcrições e especificações')
p.write_text(t,encoding='utf-8')
p=MOD/'02b-contexto-atencao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('40\\,000 vetores','20\\,000 vetores').replace('e invariância a deslocamento exata','e sem violações da invariância a deslocamento acima da tolerância examinada')
t=t.replace('Contribuímos em dois níveis honestos:','A evidência contempla dois níveis:').replace('após deslocamento após subtrair majorante','após deslocamento por majorante')
p.write_text(t,encoding='utf-8')
p=MOD/'02f-nucleo-matematico.tex';t=p.read_text(encoding='utf-8')
t=t.replace('logo a decisão é reproduzível bit a bit --- fato usado pela rerreplicação','o que torna a seleção determinística quando entradas, ambiente e demais operações permanecem fixos')
t=t.replace('após deslocamento após majorante','após deslocamento por um majorante')
p.write_text(t,encoding='utf-8')
p=MOD/'04b-provas-detalhadas.tex';t=p.read_text(encoding='utf-8')
t=t.replace('Cada retirada acima exibe falha concreta.','As hipóteses delimitam os enunciados formalizados. Os contraexemplos apresentados mostram falhas específicas quando algumas delas são removidas; não demonstram a necessidade individual de todas as hipóteses.')
p.write_text(t,encoding='utf-8')
p=MOD/'05-calibracao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('(Tabela~\\ref{tab:bench}).','Os valores da bancada principal constam de \\nolinkurl{resultado_bancada.json}, reproduzido no Apêndice~\\ref{ap:json}.',1)
t=t.replace('Diferença (IC95)','Diferença $\\pm$ margem exploratória')
t=t.replace('\\begin{table}[htbp]','A Tabela~\\ref{tab:bench} apresenta as médias das ablações para cada valor do parâmetro.\n\\begin{table}[htbp]',1)
t=t.replace('\\caption{Diferenças pareadas por decisão','\\caption{Diferenças pareadas por decisão')
t=t.replace('Os registros internos relatam reexecução determinística; uma reprodução independente permanece pendente.','Os registros internos relatam reexecução determinística; uma reprodução independente permanece pendente. A Tabela~\\ref{tab:pareado} reúne as diferenças pareadas e as taxas de vitória ou empate.')
p.write_text(t,encoding='utf-8')
p=MOD/'02a-preliminares.tex';t=p.read_text(encoding='utf-8')
t=t.replace('relações ao reconhecimento','relações com o reconhecimento')
t=t.replace('\\section{Cálculo dito passo a passo}','\\section{Exemplos de cálculo}')
t=t.replace('\\section{Informação, entropia e exponenciação}','\\section{Informação, entropia e exponenciação}\nOs valores numéricos de pesos apresentados no texto são arredondados a quatro casas decimais; a soma unitária refere-se aos valores antes desse arredondamento.')
p.write_text(t,encoding='utf-8')
p=MOD/'07-conclusao.tex';t=p.read_text(encoding='utf-8')
t=t.replace('\\begin{table}[htbp]','Os objetivos de formalização (OE1), comparação interna (OE2) e auditoria documental (OE3) são sustentados pelos registros locais nos limites explicitados. O objetivo de disponibilização pública (OE4) permanece parcialmente atendido: os artefatos estão organizados localmente, mas o depósito público e sua identificação persistente estão pendentes.\n\\begin{table}[htbp]',1)
t=t.replace('\\begin{table}[htbp]','A Tabela~\\ref{tab:futuro} sintetiza os requisitos de continuidade da pesquisa.\n\\begin{table}[htbp]',1)
p.write_text(t,encoding='utf-8')
p=MOD/'02c-lean-tutorial.tex';t=p.read_text(encoding='utf-8')
t=t.replace('\\begin{table}[htbp]','A Tabela~\\ref{tab:taticas} resume os recursos utilizados nas provas.\n\\begin{table}[htbp]',1)
p.write_text(t,encoding='utf-8')
p=MOD/'09-apendices.tex';t=p.read_text(encoding='utf-8')
t=t.replace('\\appendix','\\apendices',1)
t=t.replace('\\begin{table}[htbp]','A Tabela~\\ref{tab:pins} reproduz os identificadores históricos dos repositórios e das licenças.\n\\begin{table}[htbp]',1)
t=t.replace('\\begin{SingleSpacing}','A Tabela~\\ref{tab:historico} apresenta os ciclos do registro evolutivo, cujos escores são internos.\n\\begin{SingleSpacing}',1)
p.write_text(t,encoding='utf-8')
for path in MOD.glob('*.tex'):
    if path.name=='08-referencias.tex':
        continue
    t=path.read_text(encoding='utf-8')
    for old,new in [('O Seção','A Seção'),('o Seção','a Seção'),('do Seção','da Seção'),('no Seção','na Seção'),('ao Seção','à Seção'),('relações à reconhecimento','relações ao reconhecimento')]:
        t=t.replace(old,new)
    path.write_text(t,encoding='utf-8')
print('Fonte principal e módulos revisados. Referências reservadas ao revisor bibliográfico.')
