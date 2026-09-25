#!/usr/bin/env python3
"""SPEC-935-R210 — Gera VolumeProfissional/main.tex.
Parte A: Sondagem Inicial Minuciosa e Completa (11 dominios x 10 itens).
Parte B: 30 fichas de rastreio sistematico/investigativo (confirmacao).
Parte C: Sintese e fluxo de encaminhamento.
Uso restrito: psicologo, psicopedagogo, neuropsicopedagogo. NAO diagnostica."""
import os

OUT = os.path.join(os.path.dirname(__file__), "main.tex")

def esc(t):
    t = t.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%")
    t = t.replace("#", r"\#").replace("_", r"\_")
    return t

PRE = r"""%% ============================================================
%% VOLUME PROFISSIONAL — SONDAGEM E RASTREIO (SPEC-935-R210)
%% Integrante da colecao Alfabetizar Bem. Uso restrito a:
%% psicologo, psicopedagogo e neuropsicopedagogo.
%% NAO diagnostica; nao reproduz testes protegidos.
%% Faixa de referencia: 6-10 anos.
%% ============================================================
\documentclass[a4paper,11pt]{book}
\RequirePackage[brazil]{babel}
\RequirePackage{geometry}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{array}
\RequirePackage{enumitem}
\RequirePackage{xcolor}
\RequirePackage{fancyhdr}
\geometry{left=2.2cm, right=2.2cm, top=2.4cm, bottom=2.2cm}
\definecolor{cinza}{RGB}{90,90,90}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\itshape Volume Profissional --- Alfabetizar Bem}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\newcommand{\avisolegal}{\par\medskip\noindent\footnotesize\itshape
\color{cinza}Uso restrito a profissionais habilitados. Esta ficha NAO diagnostica;
serve ao rastreio e ao encaminhamento. Testes validados citados por referencia
(SATEPSI/CFP), sem reproducao. Resultados: sigilosos.\color{black}\par}

\begin{document}

\frontmatter
\begin{titlepage}
\begin{center}
\vspace*{1.5cm}
{\Huge\bfseries Volume Profissional}\\[0.7cm]
{\LARGE Sondagem e Rastreio}\\[0.5cm]
{\large Avaliacao do aluno e orientacao de professores}\\[1.2cm]
{\large Alfabetizar Bem --- Metodo Hibrido Fonico-Kumon}\\[2.2cm]
\noindent\rule{9cm}{0.6pt}\\[0.8cm]
{\normalsize\bfseries USO RESTRITO}\\[0.3cm]
{\small Este volume integra a colecao Alfabetizar Bem e destina-se a
psicologos, psicopedagogos e neuropsicopedagogos. Contem: Sondagem Inicial
minuciosa e completa (Parte A, antes da primeira atividade), fichas de
rastreio sistematico e investigativo de confirmacao (Parte B, 30 fichas) e
sintese/encaminhamento (Parte C).}\\[0.6cm]
{\small\itshape Nenhuma ficha deste volume gera diagnostico. Diagnostico e ato
privativo de profissional habilitado (Lei 4.119/1962; Res. CFP 009/2018).
Faixa de referencia: 6--10 anos.}
\end{center}
\end{titlepage}

\tableofcontents
\clearpage
\mainmatter
"""

POST = r"""
\backmatter
\end{document}
"""

# ---------------------------------------------------------------- DOMINIOS
SITUACAO = r"""
\chapter{Sondagem Inicial Minuciosa e Completa}

\section{Instrucoes de Aplicacao}

\begin{enumerate}[leftmargin=2.2em]
\item Aplicar \textbf{antes da primeira atividade} do volume correspondente.
\item Registrar para cada item: \textbf{0} = nao observado nesta faixa;
\textbf{1} = as vezes; \textbf{2} = frequentemente. Usar a coluna
\textit{Observacao} para exemplos objetivos.
\item Completar a leitura com: prova de escrita do nome, leitura de 5 palavras,
escrita de 5 palavras ditadas, copia de 3 frases curtas, contagem e
quantificacao ate 20, desenho da figura humana e nomeacao de 10 figuras.
\item Somar os pontos por dominio. \textbf{Prioridade de investigacao}:
dominio com maior soma. A soma NAO e nota, NAO e diagnostico e NAO substitui
teste validado; indica apenas onde aplicar as fichas de confirmacao (Parte B).
\item Sempre registrar data, idade e turma. Resultados sao sigilosos.
\end{enumerate}

\section{Perfil do Aluno}
\begin{tabular}{@{}ll@{}}
Nome: & \rule{8cm}{0.3pt}\\
Data da sondagem: & \rule{4cm}{0.3pt}\qquad Idade: \rule{2cm}{0.3pt}\qquad Turma: \rule{2cm}{0.3pt}\\
Aplicador (profissional): & \rule{7cm}{0.3pt}\\
Professor(a) colaborador(a): & \rule{6.5cm}{0.3pt}\\
\end{tabular}
\medskip
"""

def dominio(nome, itens, n):
    out = [r"\section{Dominio %d --- %s}" % (n, esc(nome)) + "\n",
           r"\begin{quote}\itshape Escala: 0 = nao observado; 1 = as vezes; 2 = frequentemente.\end{quote}" + "\n",
           r"\begin{tabular}{@{}p{10.5cm}ccc p{0.5cm}@{}}\toprule" + "\n",
           r"Item & 0 & 1 & 2 & Obs. \\\midrule" + "\n"]
    for it in itens:
        out.append(esc(it) + r" & & & & \\" + "\n")
    out.append(r"\bottomrule\end{tabular}" + "\n")
    out.append(r"\vspace{0.2cm}\noindent\small Total do dominio: \rule{1cm}{0.3pt} / %d\par\medskip" % (2*len(itens)) + "\n")
    return "".join(out)

DOMINIOS = [
 ("Leitura", ["Reconhece letras do proprio nome", "Nomeia letras fora de ordem",
  "Le silabas simples (ba, la, me)", "Le palavras com estrutura CVC (pato, bolo)",
  "Le pseudopalavras sem ajuda de adivinhacao", "Segmenta palavras em silabas ao ler",
  "Compreende o que le (reconta ideia central)", "Troca/omite letras ao ler (ex.: pate por pato)",
  "Le devagar, soletrando", "Evita situacoes de leitura"]),
 ("Escrita / Ortografia", ["Escreve o proprio nome sem copiar", "Copia textos sem erros de transposicao",
  "Escreve palavras ditadas com estrutura simples", "Representa todos os fonemas ao escrever",
  "Respeita espacamento entre palavras", "Usa maiuscula no inicio e ponto final",
  "Erros ortograficos regulares persistentes", "Confunde letras de traco similar (b/d, p/q)",
  "Omissao de letras em palavras (fpa por foca)", "Fadiga ou dor ao escrever"]),
 ("Matematica", ["Conta ate 20 de forma estavel", "Relaciona numero a quantidade ate 10",
  "Compara quantidades (mais/menos)", "Soma e subtrai ate 10 com material concreto",
  "Reconhece numeros ate 20 fora de ordem", "Copla padroes e sequencias",
  "Compreende dezena/unidade", "Resolve problemas orais simples",
  "Confunde sinais + e -", "Evita atividades numericas"]),
 ("Consciencia Fonologica", ["Rima palavras (pato/gato)", "Segmenta palavras em silabas",
  "Identifica silaba inicial", "Identifica silaba final", "Aliteracao (mesmo som inicial)",
  "Sintetiza fonemas (f-a-l-a = fala)", "Segmenta fonemas em palavras simples",
  "Manipula fonemas (troca /p/ por /t/ em pato)", "Percebe sons iguais em palavras diferentes",
  "Memoriza sequencias orais (dias, rimas)"]),
 ("Atencao e Funcoes Executivas", ["Mantem atencao em tarefa de 10 minutos", "Atende instrucoes orais de 2 passos",
  "Organiza material e mochila", "Inicia tarefa sem adiamento excessivo",
  "Persiste diante de erro sem desistir", "Controla impulsos (espera vez)",
  "Planeja passos de uma atividade", "Autorregula ritmo de trabalho",
  "Conclui tarefas iniciadas", "Alterna entre atividades com apoio minimo"]),
 ("Linguagem Oral", ["Compreende ordens simples e complexas", "Vocabulario adequado a idade",
  "Narra acontecimentos em sequencia", "Usa frases completas", "Encontra palavras (acesso lexical)",
  "Pronuncia todos os fonemas da lingua", "Compreende perguntas quem/onde/por que",
  "Conta historias com coesao", "Participa de dialogo mantendo o tema",
  "Reconta historias ouvidas com detalhes"]),
 ("Motricidade Fina / Grafomotricidade", ["Segura lápis com preensao funcional", "Recorta com tesoura",
  "Desenha figura humana com partes essenciais", "Copla formas geometricas",
  "Escreve com pressao adequada", "Respeita o espaco da linha ao escrever",
  "Conclui tracados sem inversao exagerada", "Coordena olho-mao em labirintos",
  "Distingue direita/esquerda no proprio corpo", "Apresenta movimentos lentos ou imprecisos"]),
 ("Comportamento e Socioemocional", ["Interage com pares sem conflitos frequentes", "Aceita regras e limites",
  "Expressa emocoes com palavras", "Busca adultos quando necessario",
  "Tolera mudancas de rotina", "Participa de brincadeiras coletivas",
  "Reage com intensidade desproporcional", "Fica retraido ou isolado",
  "Apresenta medos intensos de separacao", "Apresenta preocupacoes repetitivas"]),
 ("Processamento Auditivo", ["Compreende em ambiente ruidoso", "Repete sequencias de 3-4 palavras",
  "Distingue sons semelhantes da fala", "Segue instrucoes longas sem repeticao",
  "Memoriza musicas e rimas", "Apresenta pedidos frequentes de repeticao",
  "Confunde palavras parecidas ao ouvir", "Percebe variacoes de entonacao",
  "Utiliza pistas visuais para compensar", "Demonstra cansaco ao ouvir explicacoes"]),
 ("Processamento Visual / Visomotor", ["Copia do quadro sem erros de posicao", "Completa labirintos sem sair da trilha",
  "Distingue letras e formas parecidas", "Mantem orientacao no papel (nao inverte)",
  "Percebe diferencas em figuras", "Monta quebra-cabecas adequados a idade",
  "Copia figuras com proporcao", "Localiza itens em cena complexa",
  "Escreve respeitando direcao da linha", "Apresenta queixas visuais (dore de cabeca, aperta olhos)"]),
 ("Saude Sensorial (sinais para encaminhamento)", ["Reage a chamado em volume normal", "Percebe sons do ambiente",
  "Acompanha sons para a fonte", "Realiza leitura com distancia adequada",
  "Espreme os olhos para ver o quadro", "Apresenta baixa resposta a sons agudos",
  "Apresenta historico de otites ou perdas", "Usa dispositivo assistivo declarado",
  "Troca letras por dificuldade auditiva", "Apresenta fonemas mal articulados por audicao"]),
]

# ---------------------------------------------------------------- FICHAS
def ficha(n, nome, dominio, sinais, investigar, exclusoes, instrumentos, encaminhamento, adaptacoes, bib):
    out = [r"\chapter{%s}" % esc(nome) + "\n",
           r"\section*{Dominio: %s}" % esc(dominio) + "\n",
           r"\section*{Ficha de rastreio sistematico -- confirmacao}" + "\n",
           r"\subsection*{Sinais de alerta (marque: S = sim, AV = as vezes, N = nao)}" + "\n",
           r"\begin{tabular}{@{}p{11.5cm}ccc@{}}\toprule" + "\n",
           r"Sinal observado & S & AV & N \\\midrule" + "\n"]
    for s in sinais:
        out.append(esc(s) + r" & & & \\" + "\n")
    out.append(r"\bottomrule\end{tabular}" + "\n")
    out.append(r"\subsection*{Como investigar (tarefas sistematicas)}" + "\n\\begin{itemize}\n")
    for i in investigar:
        out.append(r"\item " + esc(i) + "\n")
    out.append(r"\end{itemize}" + "\n")
    out.append(r"\subsection*{Exclusoes e confundidores}" + "\n\\begin{itemize}\n")
    for e in exclusoes:
        out.append(r"\item " + esc(e) + "\n")
    out.append(r"\end{itemize}" + "\n")
    out.append(r"\subsection*{Instrumentos validados para confirmacao (referencia -- aplicar somente por psicologo, conforme SATEPSI; nao reproduzidos aqui)}" + "\n\\begin{itemize}\n")
    for i in instrumentos:
        out.append(r"\item " + esc(i) + "\n")
    out.append(r"\end{itemize}" + "\n")
    out.append(r"\subsection*{Encaminhamento}" + "\n\\begin{itemize}\n")
    for e in encaminhamento:
        out.append(r"\item " + esc(e) + "\n")
    out.append(r"\end{itemize}" + "\n")
    out.append(r"\subsection*{Adaptacoes pedagogicas iniciais (sem rotulo)}" + "\n\\begin{itemize}\n")
    for a in adaptacoes:
        out.append(r"\item " + esc(a) + "\n")
    out.append(r"\end{itemize}" + "\n")
    out.append(r"\subsection*{Bibliografia basica}" + "\n\\begin{itemize}\n")
    for b in bib:
        out.append(r"\item " + esc(b) + "\n")
    out.append(r"\end{itemize}" + "\n\\avisolegal\n")
    return "".join(out)

# dados das 30 fichas: (nome, dominio, sinais, investigar, exclusoes, instrumentos, encaminhamento, adaptacoes, bib)
F = []
F.append(("Dislexia", "Leitura",
 ["Leitura lenta, soletrada, com muitas pausas", "Erros de inversao (fada/dafa), omissao e adicao",
  "Dificuldade de rima e aliteracao persistente", "Nao reconhece palavras familiares de forma automatica",
  "Compreensao prejudicada pelo esforco de decodificacao", "Historico familiar de dificuldade de leitura",
  "Evita ler em voz alta", "Desempenho muito abaixo do esperado para a idade/instrucao",
  "Melhora quando o texto e lido por outra pessoa", "Fadiga rapida em tarefas de leitura"],
 ["Pedir leitura de 5 palavras e 3 pseudopalavras com cronometro", "Rima e segmentacao fonemica oral",
  "Leitura de texto em voz alta com registro de erros", "Comparar com producao de leitura de mesma turma"],
 ["Falta de exposicao a leitura", "Problema visual nao corrigido", "Ansiedade de desempenho pontual",
  "Ensino inicial inconsistente (metodos exclusivamente nao-fonicos)"],
 ["TDE-II (subtestes de leitura) -- SATEPSI", "PROLEC / PROOHFON (perfil fonologico)", "Avaliacao neuropsicologica (psicologo)"],
 ["Psicologo/neuropsicologo para avaliacao formal", "Fonoaudiologo para consciencia fonologica", "Pedagogo especializado se confirmado"],
 ["Leitura compartilhada diaria com apoio fonico", "Letra ampliada e textos curtos", "Ensinar rota fonologica explicita (fonema-grafema)",
  "Prova oral como alternativa a prova escrita", "Tempo adicional nas atividades"],
 ["Shaywitz (2006), Dislexia. Artmed.", "Capovilla & Capovilla (2007), Consciencia Fonologica. Vetor."]))

F.append(("Disortografia", "Escrita/Ortografia",
 ["Erros ortograficos muito alem do esperado para a serie", "Omissao, troca e adicao de letras em palavras regulares",
  "Inversoes e transposicoes (pato/vato)", "Dificuldade com regras contextuais (R/RR, S/SS)",
  "Nao usa acentos e marcadores de nasalidade", "Dificuldade com palavras irregulares de alta frequencia",
  "Escrita lenta e laboriosa", "Contraste entre ideia verbal rica e texto escrito pobre"],
 ["Ditado de 20 palavras regulares e irregulares", "Escrita espontanea (tema curto) e analise de erros",
  "Prova de conhecimento das regras ortograficas", "Comparar com escrita de pares da mesma turma"],
 ["Pouca experiencia de escrita", "Erros de transposicao visual (ver ficha 3)", "Problema de atencao sustentada"],
 ["TDE-II (subteste de escrita)", "Avaliacao de linguagem escrita (psicopedagogo)", "Perfil ortografico (fonoaudioloogia)"],
 ["Psicopedagogo para reeducacao da escrita", "Fonoaudiologo se houver trocas de fonemas", "Psicologo se associado a TDAH/dislexia"],
 ["Reforco das regras contextuais com jogos", "Revisao dialogada do texto (o professor pergunta, aluno encontra)", "Lista pessoal de palavras-alvo",
  "Evitar castigo por erros; focar em 1 padrao por semana", "Uso de corretor ortografico assistido no computador"],
 ["Zorzi (1998), Aprender a escrever. Artmed.", "Scliar-Cabral (2003), Guia pratico de alfabetizacao. Contexto."]))

F.append(("Disgrafia", "Motricidade Fina/Grafomotricidade",
 ["Caligrafia ilegivel ou muito irregular", "Preensao inadequada do lapis com tensao",
  "Formatos de letras inconsistentes", "Distancias entre letras e palavras desiguais",
  "Escrita muito lenta e dolorosa", "Postura inadequada ao escrever",
  "Coordenacao fina pobre (abotoar, recortar)", "Diferenca grande entre texto oral e escrito"],
 ["Observar preensao, postura e velocidade", "Copia de frases com registro de legibilidade",
  "Teste de destreza manual (recorte, enfiar contas)", "Excluir dor/fadiga durante e apos escrita"],
 ["Pressa ou motivacao", "Falta de treino de escrita", "Problema visual", "Dificuldade de consciencia fonologica (disortografia)"],
 ["Avaliacao psicomotora (terapeuta ocupacional/psicomotricista)", "Avaliacao neuropsicologica se necessario"],
 ["Terapeuta ocupacional para reeducacao grafomotora", "Psicopedagogo para estrategias de escrita", "Ortopedista se dor persistente"],
 ["Posicao do papel inclinada e apoio de antebraco", "Instrumentos de escrita ergonomicos (lapis triangular)", "Pauta com linhas de apoio (pauta dupla, Mestra4)",
  "Tempo reduzido de copia, com foco em qualidade", "Uso de teclado/tablet como alternativa"],
 ["Fonseca (2012), Manual de avaliacao psicomotora. Ancora.", "Oliveira (2010), Manual de psicomotricidade. Wak."]))

F.append(("Discalculia", "Matematica",
 ["Dificuldade persistente em contar de forma estavel", "Nao reconhece numeros fora de ordem",
  "Incapacidade de relacionar numero a quantidade alem do concreto", "Erros com valor posicional (dezena/unidade)",
  "Dificuldade com fatos basicos (2+3) sem contagem manual", "Problemas com comparacao (mais/menos) e estimativa",
  "Confusao de sinais e procedimentos apesar de pratica", "Erros de calculo apesar de dominar o procedimento com apoio em calculo e raciocinio",
  "Evita numeros e jogos de conta", "Dificuldade com relogio, dinheiro, medidas"],
 ["Prova de contagem, transcodificacao e calculo mental", "Tarefas de comparacao de quantidades (estimativa)",
  "Resolucao de problemas com apoio concreto", "Observar uso de estrategias (contar nos dedos vs. calculo mental)"],
 ["Ansiedade matematica", "Pouca exposicao a numeros", "Dificuldade atencional (TDAH)", "Problema de linguagem (interpretacao)"],
 ["Avaliacao neuropsicologica (psicologo)", "Testes de desempenho em matematica (TDE-II)", "Raciocinio quantitativo (WISC-V)"],
 ["Psicopedagogo para reeducacao matematica", "Psicologo/neuropsicologo para avaliacao formal"],
 ["Usar material concreto (material dourado, fichas)", "Ensinar uma estrategia por vez com sobrepratica", "Quadro de numeros e reta numerica visiveis",
  "Problemas orais antes de escritos", "Minimizar copia de enunciados longos"],
 ["Butterworth & Yeo (2009), Discalculia. Bookman.", "Kaufmann et al. (2010), Desenvolvimento do calculo. Artmed."]))

F.append(("TDAH -- desatencao", "Atencao e Funcoes Executivas",
 ["Dificuldade de manter atencao em detalhes, erros por descuido", "Nao parece ouvir quando falam diretamente",
  "Nao segue instrucoes e nao conclui tarefas", "Dificuldade de organizar material e tempo",
  "Evita/esforco com tarefas que exigem atencao sustentada", "Perde objetos (material, agendas)",
  "Distrai-se facilmente com estimulos externos", "Esquecimento nas atividades diarias",
  "Sinais presentes em casa e na escola", "Inicio antes dos 12 anos"],
 ["Escalas comportamentais respondidas por pais e professores", "Observacao sistematica em tarefa de 10 minutos",
  "Entrevista de desenvolvimento e historico escolar", "Registrar se os sinais ocorrem em dois contextos"],
 ["Ansiedade (preocupacoes explicam o desatento)", "Ambiente muito estimulante", "Sono inadequado", "Perda auditiva discreta"],
 ["Escalas SNAP-IV / ASRS (triagem; uso profissional)", "WISC-V / testes de atencao (psicologo, SATEPSI)", "Avaliacao psiquiatrica se necessario"],
 ["Psicologo/neuropsicologo para avaliacao", "Pediatra/psiquiatra infantil se confirmado", "Psicopedagogo para organizacao de estudos"],
 ["Cadeira proxima ao professor e longe de fontes de distracao", "Instrucoes curtas e fracionadas (1 passo por vez)",
  "Checklist visual de rotina na carteira", "Pausas motoras programadas (5 min)", "Reforco imediato de comportamento desejado"],
 ["Barkley (2008), Transtorno de deficit de atencao. Artmed.", "Rohde & Mattos (2003), Principios e praticas em TDAH. Artmed."]))

F.append(("TDAH -- hiperatividade/impulsividade", "Atencao e Comportamento",
 ["Remexe-se, batate as maos ou pes", "Levanta-se quando deveria permanecer sentado",
  "Corre/escala em situacoes inapropriadas", "Fala excessivamente e nao brinca em silencio",
  "Responde antes de a pergunta terminar", "Dificuldade de esperar a vez em filas/jogos",
  "Interrompe intromete-se nos outros", "Age sem avaliar consequencias (acidentes)",
  "Apresenta os sinais em mais de um contexto", "Deficit funcional em casa e na escola"],
 ["Escalas SNAP-IV / ASRS (triagem)", "Observacao em fila, roda e atividade livre", "Registro de episodios com antecedentes e consequencias"],
 ["Ansiedade/trauma que aumenta agitacao", "Sono insuficiente", "Temperamento forte sem prejuizo funcional"],
 ["Escalas e entrevista clinica (psicologo)", "Avaliacao psiquiatrica se prejuizo grave"],
 ["Psicologo/psiquiatra infantil", "Terapia comportamental parental se indicado"],
 ["Combinados claros e visuais com consequencias previsiveis", "Pausas motoras regulares", "Lugar estrategico na sala",
  "Ensinar a parar-pensar-executar com cartao", "Reduzir estimulos concorrentes em provas"],
 ["Barkley (2008), Transtorno de deficit de atencao. Artmed.", "DSM-5-TR (2023). Artmed."]))

F.append(("TEA -- nivel 1", "Comportamento/Social",
 ["Dificuldade de reciprocidade social (nao inicia/retribui interacoes)", "Interesses restritos e intensos (trens, espacos, letras)",
  "Rotinas inflexiveis com reacao intensa a mudancas", "Dificuldade de leitura de expressoes e ironia",
  "Fala fluente porem com dificuldade pragmática", "Pouco contato visual funcional",
  "Dificuldade de fazer e manter amigos da mesma idade", "Hipersensibilidade ou hipossensibilidade sensorial",
  "Dificuldade em brincar de faz de conta com pares", "Sinais presentes desde a infancia"],
 ["Observacao estruturada em recreio e atividades livres", "Entrevista de desenvolvimento (marcos sociais/ludio)", "Prova de compreensao pragmatica (ironias, figurativa)"],
 ["Timidez/ansiedade social", "TDL (linguagem) sem compromisso social", "Perfil superdotado com interesses intensos"],
 ["ADOS-2 (referencia internacional; validação brasileira em andamento) / ADI-R (validado no Brasil; Becker et al., 2012)", "Escala SRS-2 (triagem; uso profissional)", "Avaliacao neuropsicologica"],
 ["Psicologo/neuropsicologo para avaliacao formal", "Fonoaudiologo para pragmatica e suporte", "Psiquiatra infantil se necessario"],
 ["Rotina previsivel com aviso de transicoes", "Suportes visuais (agenda, regras)", "Grupo de habilidades sociais",
  "Ensinar explicitamente trocas sociais", "Ajuste sensorial (fones, espaco tranquilo)"],
 ["APA (2023), DSM-5-TR. Artmed.", "Klin, Volkmar & Sparrow (2000). Asperger syndrome. Guilford."]))

F.append(("TEA -- nivel 2/3", "Comportamento/Social/Linguagem",
 ["Atraso marcado ou ausencia de linguagem funcional", "Comunicacao muito reduzida mesmo com gestos alternativos",
  "Respostas sociais ausentes ou minimas", "Interesses e comportamentos repetitivos intensos",
  "Rituais e resistencia intensa a mudanca", "Autoagressao ou agressao quando contrariado (sinais de comunicar)",
  "Pouco uso de olhar, gestos e expressao para comunicar", "Bom progresso com suporte visual intensivo",
  "Ecolalia persistente ale da idade esperada", "Comprometimento severo na participacao escolar"],
 ["Observacao em rotina estruturada", "Entrevista com responsaveis (marcos)", "Avaliacao de comunicacao funcional (pedido, recusa)"],
 ["Deficiencia auditiva nao tratada", "DI moderada sem prejuizo social especifico do TEA"],
 ["ADOS-2 (referencia internacional; validação brasileira em andamento) / ADI-R (validado no Brasil; Becker et al., 2012)", "Avaliacao de linguagem (fonoaudiologo)", "Avaliacao medica/neurologica"],
 ["Neurologista/psiquiatra infantil + psicologo", "Fonoaudiologo intensivo", "Terapeuta ocupacional/ABA se disponivel"],
 ["Comunicacao alternativa (PECS/gestos) se necessaria", "Rotina visual clara com aviso de mudanca", "Espaco sensorial calmo",
  "Fracionar atividades com reforco", "Mentor/mediador de apoio em transicoes"],
 ["APA (2023), DSM-5-TR. Artmed.", "Suzuki & Barros (2009). TEA na escola. Vetor."]))

F.append(("Transtorno Opositivo-Desafiador (TOD)", "Comportamento",
 ["Perde a calma com frequencia", "Discute com adultos e desafia regras",
  "Recusa cumprir pedidos de autoridades", "Irrita deliberadamente pessoas",
  "Culpa os outros pelos proprios erros", "Ressentido ou vingativo",
  "Sinais presentes ha pelo menos 6 meses", "Prejuizo nas relacoes com pares e professores",
  "Comportamentos nao explicados por humor depressivo", "Padrao consistente em casa e/ou escola"],
 ["Registro de episodios (gatilhos, duracao)", "Escala de comportamento (CBCL/TRF -- referencia)", "Entrevista com pais sobre limites e consequencias"],
 ["TDAH com impulsividade", "Depressao/irritabilidade", "Estilo parental inconsistente", "Bullying/ambiente hostil"],
 ["CBCL/TRF (uso profissional)", "Entrevista diagnostica (psicologo/psiquiatra)"],
 ["Psicologo (terapia comportamental/familiar)", "Psiquiatra infantil se comorbidades"],
 ["Reforco positivo frequente (4:1)", "Consequencias previsiveis e imediatas", "Escolhas limitadas (isto ou aquilo)",
  "Ensinar e reforcar habilidades de resolucao de problemas", "Comunicacao com a familia alinhada"],
 ["DSM-5-TR (2023). Artmed.", "Weber (2017), Comportamento infantil. Artmed."]))

F.append(("Transtorno de Conduta", "Comportamento",
 ["Agressao fisica a pares/pessoas", "Mentiras repetidas para obter vantagem",
  "Vandalismo ou destruicao de bens", "Furtos (inclusive na escola)", "Violacao grave de regras (fugas)",
  "Crueldade com animais", "Inicio antes dos 13 anos em alguns casos", "Falta de remorso apos dano",
  "Padrao persistente por 12 meses", "Prejuizo social e academico significativo"],
 ["Registro sistematico de incidentes", "Entrevista com familia e escola", "Avaliacao de contexto (violencia domestica, grupo)"],
 ["TDAH impulsivo", "TOD (sem violacao de direitos)", "Contexto de violencia/negligencia (nao diagnosticar o contexto como transtorno)"],
 ["Avaliacao clinica/psiquiatrica", "Instrumentos de comportamento (CBCL/TRF)"],
 ["Psicologo/psiquiatra infantil", "Rede de protecao (Conselho Tutelar, CRAS) se necessario", "Escola: plano de convivencia"],
 ["Limites claros e consistentes com reparacao de dano", "Ensino de empatia por historias e role-play", "Supervisao positiva e rotina estruturada",
  "Contracto de comportamento com metas", "Articulacao com rede de protecao"],
 ["DSM-5-TR (2023). Artmed.", "Patterson (2002), Antisocial boys. Castalia."]))

F.append(("Ansiedade de Separacao", "Socioemocional",
 ["Medo intenso de separar-se dos pais", "Choro ou crises ao entrar na escola",
  "Sintomas somaticos (dor de barriga, enjoo) em dias de aula", "Preocupacao de que algo aconteca aos pais",
  "Pesadelos sobre separacao", "Recusa de dormir fora de casa", "Segue os pais pela casa",
  "Sintomas ha pelo menos 4 semanas", "Prejuizo na participacao escolar", "Inicio na infancia (antes dos 6 anos tipico)"],
 ["Registro de sintomas em dias de entrada", "Entrevista com pais (contexto e gatilhos)", "Observacao da adaptacao progressiva"],
 ["Falta de rotina de despedida", "Evento estressor recente (luto, mudanca)", "Doenca fisica"],
 ["Escalas de ansiedade infantil (SCARED/CAS -- referencia)", "Entrevista clinica (psicologo)"],
 ["Psicologo (terapia cognitivo-comportamental)", "Fonoaudiologo nao indicado (sem linguagem)"],
 ["Ritual de despedida curto e consistente", "Objeto de conforto (foto, bichinho)", "Chegada gradual com profissional de apoio",
  "Reforco positivo apos periodos de permanencia", "Comunicacao com a familia sobre avancos"],
 ["DSM-5-TR (2023). Artmed.", "Caballo (2007), Manual de TEAs e de transtornos fobicos. VCH."]))

F.append(("Ansiedade Generalizada / de Desempenho", "Socioemocional",
 ["Preocupacoes excessivas sobre desempenho escolar", "Dificuldade de controlar a preocupacao",
  "Sintomas fisicos (tensao, cansaco, insonia) sem causa medica", "Busca constante de aprovacao",
  "Evita tarefas com medo de errar", "Perguntas repetitivas sobre o futuro", "Irritabilidade sob cobranca",
  "Dificuldade de relaxar", "Sinais ha pelo menos 6 meses", "Prejuizo no rendimento e no bem-estar"],
 ["Entrevista com a crianca (percepcoes)", "Escala de ansiedade (SCARED -- referencia)", "Observacao em situacoes de avaliacao"],
 ["Cobranca familiar intensa", "TDAH (procrastinacao por attencao)", "Perfeccionismo adaptativo sem prejuizo"],
 ["SCARED/CAS (uso profissional)", "Avaliacao clinica (psicologo)"],
 ["Psicologo (TCC) se prejuizo funcional", "Pediatra para sintomas somaticos"],
 ["Ambiente de erro permitido e seguro (erro como aprendizagem)", "Instrucoes claras com objetivos pequenos", "Tecnicas de respiracao antes de provas",
  "Reforco de esforco e processo, nao so do resultado", "Reduzir pressao de tempo em avaliacoes quando indicado"],
 ["DSM-5-TR (2023). Artmed.", "Stallard (2010), Ansiedade infantil. Artmed."]))

F.append(("Fobia Escolar / Ansiedade Social", "Socioemocional",
 ["Recusa persistente de ir a escola com reacao intensa", "Angustia antecipatoria ja na noite anterior",
  "Sintomas somaticos fortes na entrada (vomito, dor)", "Medo intenso de situacoes de exposicao (falar na frente)",
  "Evita interacoes sociais com medo de avaliacao", "Fica mudo/a ou colapsa em chamadas orais",
  "Dificuldade de olhar/responder a adultos", "Ausencias frequentes por 'doenca' sem causa", "Escolarizacao em risco",
  "Sintomas presentes em casa com familiares conhecidos (contraste)"],
 ["Registro de padrao de ausencias e sintomas", "Entrevista com pais e crianca", "Observacao em situacoes de exposicao"],
 ["Bullying (investigar antes)", "Ansiedade de separacao", "Dificuldades academicas como gatilho"],
 ["Escalas de ansiedade social", "Avaliacao clinica (psicologo)"],
 ["Psicologo (TCC com exposicao gradual)", "Contato com rede de saude se absenteismo escolar"],
 ["Reentrada gradual com plano de exposicao", "Tarefa de exposicao oral pequena e crescente (dupla, trio, grupo)", "Apoio de profissional em momentos-chave",
  "Reforco positivo de frequencia", "Envolver a familia em plano conjunto"],
 ["DSM-5-TR (2023). Artmed.", "Heyne & Rollings (2003). School refusal. Wiley."]))

F.append(("Depressao Infantil", "Socioemocional",
 ["Tristeza ou irritabilidade persistente", "Perda de interesse em atividades antes prazerosas",
  "Queda no rendimento e na concentracao", "Fadiga, hipoatividade ou agitacao",
  "Mudanca de apetite/sono", "Autodesvalorizacao ('sou incapaz')", "Isolamento social",
  "Lentidao motora ou fala reduzida", "Sintomas ha pelo menos 2 semanas", "Historia de perdas/eventos estressores"],
 ["Entrevista com a crianca e os pais", "Escala de depressao infantil (CDI -- referencia)", "Observacao na rotina escolar"],
 ["Luto reativo recente", "Ansiedade com apatia secundaria", "Hipotireoidismo/anemia (avaliar medico)"],
 ["CDI (uso profissional)", "Avaliacao clinica/psiquiatrica"],
 ["Psicologo/psiquiatra infantil (urgente se risco)", "Acolhimento e rede de apoio"],
 ["Acolhimento individual breve diario", "Tarefas pequenas com alta chance de sucesso", "Reconhecer esforco e presenca",
  "Envolver a familia e a rede (ESF/CRAS)", "Proibido rotular; encaminhamento sigiloso"],
 ["DSM-5-TR (2023). Artmed.", "Bahls (2002), Depressao na infancia e adolescencia. UFPR."]))

F.append(("TOC Infantil", "Socioemocional",
 ["Preocupacoes repetitivas que a crianca tenta ignorar", "Rituais de limpeza, ordem, verificacao ou contagem",
  "Necessidade de simetria nas atividades", "Perda de tempo significativa com ritual", "Angustia se impedido de realizar ritual",
  "Perguntas repetitivas ('e se...?')", "Sinais comecam na infancia (media 7-12 anos)", "Prejuizo academico e social",
  "Tentativas de esconder rituais", "Sintomas consomem mais de 1h/dia"],
 ["Entrevista clinica cuidadosa", "Observacao de rituais na sala", "Excluir transtornos do desenvolvimento"],
 ["Ansiedade geral com verificacao leve", "Tiques simples", "Rotinas normais de infancia (transitorias)"],
 ["Avaliacao clinica/psiquiatrica", "Escalas especificas (CY-BOCS -- referencia)"],
 ["Psiquiatra/psicologo (TCC com prevencao de resposta)"],
 ["Flexibilizar prazos e exigencia de limpeza/ordem", "Sem punicao por rituais; registrar o impacto", "Plano de resposta a estereotipias com profissional",
  "Ambiente estruturado com atividades que engajam a atencao"],
 ["DSM-5-TR (2023). Artmed.", "March & Mulle (1998). OCD in children. Guilford."]))

F.append(("Mutismo Seletivo", "Linguagem/Socioemocional",
 ["Fala em casa e nao fala na escola", "Ausencia de fala em situacoes especificas por mais de 1 mes",
  "Nao fala mesmo quando solicitado ou sob pressao", "Usa gestos, acenos e escrita para responder",
  "Contato visual e postura podem ser normais ou inibidos", "Aparece ao entrar na escola (transicao)",
  "Sinais de ansiedade social associados", "Fala com selecao de pessoas e locais", "Crianca e comunicativa em ambiente seguro",
  "Nao explicado por TEA ou TDL"],
 ["Entrevista com pais (contextos em que fala)", "Observacao em diferentes situacoes (pequeno grupo, recreio)", "Excluir TDL e TEA (comunicacao global)"],
 ["Timidez normal de adaptacao (menos de 1 mes)", "TDL/TEA", "Trauma/refugio"],
 ["Avaliacao clinica (psicologo)", "Fonoaudiologo para excluir TDL"],
 ["Psicologo (terapia com exposicao gradual)", "Fonoaudiologo se comorbidade com TDL"],
 ["Nao pressionar para falar; aceitar comunicacao alternativa", "Situacoes de fala em dupla com colega seguro", "Reforco de qualquer forma de comunicacao",
  "Atividades de resposta nao-verbal inicial (apontar, cartoes)", "Combinado com a familia sobre a escola"],
 ["DSM-5-TR (2023). Artmed.", "Kearney (2010). Helping children with selective mutism. Oxford."]))

F.append(("TPAC (processamento auditivo)", "Processamento Auditivo",
 ["Pedidos frequentes de repeticao", "Dificuldade em ambiente ruidoso", "Confusoes de palavras parecidas ao ouvir",
  "Seguir instrucoes longas com erros", "Dificuldade de aprender rimas e musicas", "Leitura e ortografia prejudicadas por limite fonologico",
  "Atraso em compreender piadas/ironias orais", "Audicao periferica normal (avaliacao otorrinolaringologica)",
  "Melhora com apoio visual", "Cansa ao ouvir explicacoes longas"],
 ["Triagem auditiva formal (OTORRINO) para excluir perda", "Provas de memoria sequencial auditiva", "Observar em sala com e sem ruido"],
 ["Perda auditiva/TDAH (desatencao auditiva)", "TDL", "Ambiente escolar ruidoso"],
 ["Avaliacao fonoaudiologica de PA (somente apos audicao normal)", "Testes de processamento auditivo (fonoaudiologo)"],
 ["Fonoaudiologo especialista em PA", "OTORRINO primeiro"],
 ["Assento proximo ao professor", "Instrucoes curtas e checagem da compreensao", "Reduzir ruido de fundo na sala",
  "Apoio visual em todas as instrucoes orais", "Repetir e reescrever instrucoes de provas"],
 ["Ferreira (2004), Tratado de fonoaudiologia. Roca.", "Pereira & Schochat (2011). PA. Pulso."]))

F.append(("TDL (Transtorno do Desenvolvimento da Linguagem)", "Linguagem Oral",
 ["Atraso no vocabulario e nas combinacoes de frases", "Frases curtas ou agramaticais para a idade",
  "Dificuldade de narrar e relatar fatos", "Problemas de compreensao de ordens complexas", "Uso pobre de conectivos (porque, mas)",
  "Dificuldade de aprender novas palavras", "Prejuizo na leitura/escrita decorrente", "Sem perda auditiva, TEA ou DI que expliquem",
  "Melhora com suporte visual", "Historico de fala tardia"],
 ["Avaliacao de linguagem (fonoaudiologo)", "Prova de vocabulario e narrativa", "Observacao do discurso em sala"],
 ["Perda auditiva", "TEA (pragmatica comprometida global)", "DI (prejuizo global)", "Mutismo seletivo"],
 ["ABFW (referencia; fonoaudiologo)", "Avaliacao de linguagem formal"],
 ["Fonoaudiologo (terapia de linguagem intensiva)"],
 ["Linguagem simplificada e concreta com apoio visual", "Modelar frases completas sem corrigir publicamente", "Antecipar vocabulario novo",
  "Verificar compreensao com perguntas especificas", "Pares mais fluentes em trabalhos em grupo"],
 ["Bishop et al. (2017), TDL. JCPP.", "Hage & Guimaraes (2006). Disturbios de linguagem. Pulso."]))

F.append(("Desvio Fonologico (dislalia)", "Linguagem Oral",
 ["Trocas de fonemas na fala (tato/gato)", "Omissao de silabas ou fonemas", "Fala inteligivel apenas para a familia",
  "Dificuldade de articulacao de vibrante (r)", "Erros fonologicos alem da idade esperada (6 anos: eliminar maioria)",
  "Afeta escrita (troca correspondente)", "Vergonha de falar em publico", "Sem perda auditiva ou alteracao anatomica",
  "Resposta inconsistente (mesma palavra, erros diferentes)", "Persistencia apos ensino explicito"],
 ["Avaliacao fonoaudiologica articulatoria", "Prova de nomeacao de figuras", "Excluir perda auditiva e PA"],
 ["Perda auditiva", "TDL mais amplo", "Variacao regional da fala (nao patologia)"],
 ["ABFW (prova fonologica; fonoaudiologo)", "Avaliacao de PA se necessario"],
 ["Fonoaudiologo (terapia fonologica)"],
 ["Modelar corretamente sem pedir repeticao publica", "Atividades de consciencia fonologica ludicas", "Nao ridicularizar; reforcar tentativas",
  "Registrar erros para a fonoaudiologa", "Leitura de palavras com o fonema-alvo"],
 ["Wertzner (2000), Fonologia. Pulso.", "Lamprecht (2004), Aquisicao fonologica. Artmed."]))

F.append(("Gagueira (tartamudez)", "Fala",
 ["Repeticoes de silabas/sons (mu-mu-muito)", "Prolongamentos (m====aior)", "Bloqueios na fala (fica travado)",
  "Esforco fisico visivel ao falar", "Evita palavras ou situacoes de fala", "Tensao facial ou piscadas frequentes",
  "Gagueira com duracao superior a 6 meses", "Historia familiar de gagueira", "Sinais de frustracao/vergonha",
  "Fluencia varia conforme situacao (leitura, pressa)"],
 ["Observacao em diferentes situacoes de fala", "Registro de tipologia (repeticoes, prolongamentos, bloqueios)", "Entrevista com a familia"],
 ["Disfluencias normais do desenvolvimento (fase prescolare ate 6 anos, sem tensao)", "Fala rapida por ansiedade"],
 ["Avaliacao fonoaudiologica de fluencia", "Encaminhamento precoce (quanto antes, melhor)"],
 ["Fonoaudiologo especialista em fluencia (preferencialmente em ate 12 meses do inicio)"],
 ["Nao interromper, corrigir ou completar a fala", "Dar tempo (esperar sem pressa)", "Reduzir pressao de velocidade em leitura oral",
  "Falar com a crianca em ritmo pausado como modelo", "Evitar humilhacoes publicas; reforcar conteudo"],
 ["Andrade (2006), Fluencia. Roca.", "Nippold (2011), Stuttering. Psychology Press."]))

F.append(("Apraxia de Fala Infantil", "Fala",
 ["Fala muito limitada ou ininteligivel apesar de esforco", "Erros inconsistentes e variaveis na mesma palavra",
  "Dificuldade de organizar sequencias de movimentos da fala", "Piora progressiva em frases longas",
  "Atraso no desenvolvimento motor oral (soprar, estalar labios)", "Historia de dificuldades na alimentacao",
  "Compreensao melhor que producao", "Melhora com apoio visual/silabas modeladas lentamente",
  "Sem alteracao neurologica evidente (excluir paralisia)", "Frustracao comunicativa intensa"],
 ["Avaliacao fonoaudiologica detalhada", "Prova de diadococinesia (repeticao rapida)", "Gravacao de amostra de fala"],
 ["Desvio fonologico (erros consistentes)", "TDL", "Dispraxia geral/TDC"],
 ["Avaliacao fonoaudiologica (especialista em motor da fala)", "Avaliacao neurologica se necessario"],
 ["Fonoaudiologo (terapia motora intensiva)"],
 ["Comunicacao alternativa temporaria se frustracao alta", "Palavras-alvo curtas modeladas lentamente", "Elogiar tentativas, nao exigir perfeicao",
  "Antecipar e verbalizar pelo aluno em situacoes de estresse"],
 ["Strand et al. (2013). CAS. ASHA.", "Dodd (2005), Differential diagnosis. Whurr."]))

F.append(("TDC / Dispraxia (coordenacao)", "Motricidade",
 ["Clumsiness: esbarra, derruba objetos com frequencia", "Dificuldade de aprender habilidades motoras (pular corda, andar de bicicleta)",
  "Escrita muito lenta e desajeitada (ver ficha 3)", "Dificuldade de abotoar, amarrar, usar talheres", "Quedas frequentes sem causa",
  "Desempenho motor muito abaixo do esperado para a idade", "Dificuldade de imitar movimentos", "Evita atividades fisicas por constrangimento",
  "Interfere em atividades da vida diaria e escolar", "Sinais desde cedo (nao adquiridos por falta de pratica)"],
 ["Avaliacao psicomotora (MABC-2 -- referencia)", "Testes de destreza manual e equilibrio", "Observacao em educacao fisica e recreio"],
 ["Falta de pratica/escolarizacao", "Problema visual", "Doenca neurologica (excluir)"],
 ["MABC-2 (uso profissional)", "Avaliacao psicomotora/terapeuta ocupacional"],
 ["Terapia ocupacional/psicomotricidade", "Atividade fisica adaptada"],
 ["Adaptar instrumentos (lapis grosso, antiderrapante)", "Dividir tarefas motoras em etapas pequenas", "Tempo extra em copias",
  "Reforcar desempenho pelo esforco", "Atividades fisicas alternativas de sucesso"],
 ["DSM-5-TR (2023). Artmed.", "Fonseca (2012), Manual de avaliacao psicomotora. Ancora."]))

F.append(("Tiques e Tourette", "Comportamento/Motor",
 ["Movimentos rapidos involuntarios (piscar, sacudir cabeca)", "Vocalizacoes involuntarias (fungar, pigarrear, palavras)",
  "Tiques mudam ao longo do tempo", "Piora com estresse, fadiga e ansiedade", "Crianca consegue suprimir temporariamente",
  "Inicio tipico entre 5-10 anos", "Sinais ha mais de 1 ano para Tourette (motor + vocal)", "Sensacao de alivio apos tique",
  "Prejuizo social e academico", "Tiques nao explicados por medicacao ou substancia"],
 ["Observacao sistematica em sala", "Entrevista com pais (duracao, tipos)", "Registro em diferentes contextos"],
 ["Habitos motores normais", "TDAH com agitacao", "TOC (rituais vs tiques)"],
 ["Avaliacao clinica/neurologica/psiquiatrica", "Escalas de tiques (YGTSS -- referencia)"],
 ["Neurologista/psiquiatra infantil se prejuizo", "Psicologo (TCC-HRT) se indicado"],
 ["Nao chamar atencao para o tique; nao punir", "Reduzir estresse e pressao (gatilhos)", "Permitir pausas de saida quando necessario",
  "Informar colegas de forma natural se a crianca concordar", "Coordenacao com medico"],
 ["DSM-5-TR (2023). Artmed.", "Leckman et al. (2010). Tourette. Guilford."]))

F.append(("Ausencias (sinais para encaminhamento medico)", "Saude/Neuro",
 ["Piscadelas ou olhar fixo sem resposta por segundos", "Paradas breves da atividade com retomada", "Automatsmos (movimentos de mastigacao) durante episodio",
  "Quedas de cabeca sem causa aparente", "Perda de urina em horarios incomuns", "Nao responde a chamados durante o episodio",
  "Lapsos repetidos de 'sonho acordado'", "Parentes descrevem 'desligamentos'", "Ausencias podem ser confundidas com desatencao",
  "Prejuizo de aprendizagem por episodios nao percebidos"],
 ["Registrar com data/hora/doracao dos episodios", "Filmar com celular (com autorizacao) para o medico", "Observar resposta a estimulos durante o episodio"],
 ["Desatencao (TDAH) -- o aluno RESPONDE ao chamado", "Sonolencia por sono ruim", "Transtorno de ausencia precisa confirmacao medica"],
 ["Encaminhamento ao pediatra/neurologista (NUNCA tratar na escola)", "EEG se indicado pelo medico"],
 ["Pediatra/neurologista pediatrico (URGENTE se episodios frequentes)"],
 ["NAO dar diagnostico escolar", "Registrar episodios e repassar a familia/medico", "Avaliar risco de queda",
  "Nao deixar a crianca em altura ou atividades perigosas ate avaliacao", "Manter rotina escolar com apoio"],
 ["DSM-5-TR (2023). Artmed.", "Camfield & Camfield (2005). Pediatric epilepsy. INPE."]))

F.append(("Deficiencia Intelectual leve (sinais escolares)", "Desenvolvimento Global",
 ["Atraso global de aprendizagem em todas as areas", "Dificuldade de generalizar aprendizagens (contexto a contexto)",
  "Linguagem simples, concreta e literal", "Dificuldade de resolver problemas novos", "Memoria de trabalho reduzida",
  "Dependencia de apoio para tarefas cotidianas", "Dificuldade de raciocinio logico e abstrato",
  "Adaptacao escolar necessaria em ritmo proprio", "Sem explicacao por privacao sensorial grave", "Sinais desde a infancia"],
 ["Avaliacao interdisciplinar (pedagogica + psicologica)", "Observacao de autonomia e aprendizagem", "Historia do desenvolvimento"],
 ["Falta de escolarizacao/bilinguismo", "TDAH (atencao afeta todas as areas)", "TDL", "Privacao sociocultural (pobreza, negligencia)"],
 ["WISC-V / avaliacao intelectual (psicologo, SATEPSI)", "Escalas adaptativas (Vineland -- referencia)"],
 ["Psicologo (avaliacao formal) e medico para causas", "AEE (Atendimento Educacional Especializado)"],
 ["Curriculo funcional com metas pequenas e concretas", "Ensino com muitos exemplos e pratica", "Avaliacao oral/adaptada",
  "Apoio de AEE e plano individualizado", "Instrumentos concretos e material visual"],
 ["DSM-5-TR (2023). Artmed.", "Mendonca (2012). DI e escola. Juruá."]))

F.append(("Altas Habilidades / Superdotacao", "Desenvolvimento/Curriculo",
 ["Aprendizagem muito rapida e facil em uma ou mais areas", "Vocabulario avancado e curiosidade intensa",
  "Memoria e raciocinio acima da media", "Interesse intenso e aprofundado por um tema", "Faz perguntas desafiadoras",
  "Perfeccionismo que gera frustracao", "Pode apresentar tedio e desatencao em tarefas repetitivas", "Sensibilidade emocional aumentada",
  "Precisa de desafios para engajar", "Criatividade e solucao original de problemas"],
 ["Observacao de desempenho e interesse", "Anamnese com familia (marcos precoces)", "Avaliacao psicologica se indicado"],
 ["TDAH (desatento por tedio vs desatento por deficit)", "Ansiedade por pressao", "Comportamento de aluno 'esperto' sem excepcionalidade"],
 ["Avaliacao psicologica (psicologo, SATEPSI)", "Testes de inteligencia se indicado (WISC-V)"],
 ["Psicologo (avaliacao formal) se necessario", "Programas de enriquecimento/NAAH/S"],
 ["Enriquecimento curricular (projetos, mentorias)", "Tarefas de nivel avancado (nao so mais do mesmo)", "Grupo de pares com interesses comuns",
  "Apoio socioemocional para perfeccionismo", "Plano de trabalho individualizado"],
 ["Renzulli (2005), Three-ring conception. Kappan.", "Alencar & Fleith (2001). Superdotados. EPU."]))

F.append(("Perfil de Aprendizagem Nao-Verbal (TANV)", "Visomotor/Pragmatica",
 ["TDE verbal/leitura boa, matematica visual-praxia pobre", "Dificuldade de interpretar expressoes e linguagem corporal",
  "Problemas de coordenacao fina (ver ficha 22)", "Dificuldade de organizacao visuoespacial (perder-se, copia ruim)", "Pragmatica social desajeitada",
  "Compreensao literal elevada, ironia dificil", "Dificuldade com conceitos abstratos em matematica (valor posicional)", "Rotina inflexivel com ansiedade a mudanca",
  "Nao e reconhecido por testes verbais comuns", "Sinais de lateralidade e praxia alteradas"],
 ["Observacao de habilidades visuoespaciais", "Avaliacao psicopedagogica com testes verbais vs visuomotores", "Entrevista com pais"],
 ["TEA (pragmatica comprometida em TANV e TEA)", "Disgrafia isolada", "TDL verbal (perfil oposto)"],
 ["Avaliacao neuropsicologica (psicologo)", "Avaliacao perceptomotora (terapeuta ocupacional)"],
 ["Psicologo/neuropsicologo", "Terapeuta ocupacional"],
 ["Ensino explicito de estrategias visuoespaciais", "Organizadores graficos para matematica", "Antecipar mudancas com rotina visual",
  "Ensino de habilidades sociais explicitas", "Tempo extra em tarefas de copia"],
 ["Rourke (1995), NLD. Guilford.", "Margolis (2010). NLD and school. Springer."]))

F.append(("Deficiencia Auditiva (sinais escolares)", "Saude Sensorial",
 ["Nao responde a chamado em volume normal", "Aumenta o volume de TV/rádio", "Pede repeticoes com frequencia",
  "Fala com qualidade alterada (voz, articulacao)", "Dificuldade de compreender em ruido", "Olha atentamente os labios do interlocutor",
  "Historico de otites de repeticao", "Uso de aparelho/implante (verificar funcionamento)", "Atraso academico em leitura e escrita",
  "Sinais detectados em triagem auditiva escolar"],
 ["Triagem auditiva formal (OTORRINO/fonoaudiologo)", "Observacao de respostas a sons agudos e graves", "Verificar funcionamento do dispositivo DI/ATS"],
 ["Distracao/desatencao", "TDL sem perda auditiva", "Ambiente ruidoso"],
 ["Audiometria (OTORRINO/fonoaudiologo)", "Avaliacao de linguagem se perda confirmada"],
 ["OTORRINO + fonoaudiologo (intervencao precoce)", "Professor de educacao especial/AEE"],
 ["Assento estrategico (ouvido bom/visao do professor)", "Falar de frente, com luz no rosto", "Reduzir ruido de fundo",
  "Uso de legendas/apoio visual", "Checklist de funcionamento do ATS/diario"],
 ["Boothroyd (2004). Hearing loss. Plural.", "Bevilacqua (2004). Deficiencia auditiva. Pulso."]))

F.append(("Baixa Visao (sinais escolares)", "Saude Sensorial",
 ["Espreme os olhos ou aproxima muito o papel", "Queixa de dor de cabeca ou vista cansada", "Dificuldade de copiar do quadro",
  "Perde linha ao ler", "Inclina a cabeca para ver", "Sensibilidade a luz ou claridade excessiva",
  "Erros em tarefas de detalhe (labirintos)", "Esbarra ou desvia de obstaculos com frequencia", "Nao percebe objetos distantes",
  "Historico de uso de oculos (verificar atualizacao)"],
 ["Triagem visual (ametropia) com profissional", "Observacao de distancias de trabalho", "Rever data da ultima consulta oftalmologica"],
 ["Dificuldade atencional", "Desinteresse", "Problema motor (nao visual)"],
 ["Avaliacao oftalmologica (exame completo)", "Testes de acuidade visual"],
 ["Oftalmologista (consulta e correcao)", "Professor de educacao especial/AEE se baixa visao confirmada"],
 ["Assento proximo ao quadro com boa iluminacao", "Material ampliado (fonte 16-18pt no livro)", "Contraste alto no material",
  "Uso de recursos de ampliacao (lupa, tela)", "Reduzir brilho e ofuscamento na sala"],
 ["Veitzman (2007). Visao na escola. Santos.", "Colaris (2020). Baixa visao. UFPR."]))

F.append(("Comunicacao Social (TCS) pragmatica", "Linguagem/Social",
 ["Fala fluente mas socialmente desajeitada", "Dificuldade de interpretar figurativo, ironia e ambiguidade", "Troca de turnos pobres na conversa",
  "Discurso monologico sobre interesses", "Dificuldade de adequar registro ao interlocutor", "Problemas para fazer e manter amizades",
  "Sem restricoes de interesses ou comportamentos sensoriais (contraste com TEA)", "Compreensao literal excessiva",
  "Dificuldade de inferencia em textos", "Prejuizo funcional em interacoes"],
 ["Observacao de conversacao em pares", "Prova de compreensao pragmatica (figurativo, ironia)", "Comparar com TEA (ausencia de repeticoes/restricoes)"],
 ["TEA (tem restricoes e padroes sensoriais)", "TDL (gramatica comprometida)", "Timidez/ansiedade social"],
 ["Avaliacao fonoaudiologica de pragmatica", "Avaliacao clinica (psicologo)"],
 ["Fonoaudiologo (pragmatica)", "Psicologo se comorbidade social/emocional"],
 ["Ensinar explicitamente interpretacao de figurativo e ironia", "Role-play de trocas sociais com feedback", "Grupo de conversacao estruturado",
  "Leitura de historias com perguntas inferenciais", "Reforcar tentativas sociais adequadas"],
 ["DSM-5-TR (2023). Artmed.", "Adams (2002). Social communication. Wiley."]))

# ---------------------------------------------------------------- SINTESE
SINTESE = r"""
\chapter{Sintese, Fluxo e Orientacao de Professores}

\section{Folha de Sintese}
\begin{quote}
Preencher apos a Sondagem (Parte A) e as fichas de confirmacao (Parte B).
\end{quote}

\noindent Data: \rule{3cm}{0.3pt}\quad Aluno: \rule{6cm}{0.3pt}\quad Idade: \rule{1.5cm}{0.3pt}

\subsection*{Dominios com prioridade de investigacao (maior soma na Parte A)}
\begin{enumerate}[leftmargin=2.2em]
\item \rule{12cm}{0.3pt}
\item \rule{12cm}{0.3pt}
\item \rule{12cm}{0.3pt}
\end{enumerate}

\subsection*{Fichas de confirmacao aplicadas}
% PAGAR campo
\noindent Ficha(s): \rule{14cm}{0.3pt}

\subsection*{Hipoteses de trabalho (nunca diagnosticos)}
\noindent \rule{15cm}{0.3pt}\\ \rule{15cm}{0.3pt}

\subsection*{Encaminhamentos}
\begin{itemize}
\item Servico de saude / profissional: \rule{6cm}{0.3pt}\quad Data: \rule{2.5cm}{0.3pt}
\item AEE: \rule{10cm}{0.3pt}
\end{itemize}

\subsection*{Aviso de sigilo e uso restrito}
\avisolegal

\section{Fluxo de Encaminhamento}
\begin{enumerate}[leftmargin=2.2em]
\item \textbf{Sondagem Inicial} (Parte A), antes da primeira atividade.
\item Dominios com maior soma -> \textbf{fichas de confirmacao} (Parte B).
\item Ficha com sinais relevantes -> \textbf{encaminhamento} ao profissional habilitado.
\item Professor recebe \textbf{orientacoes de adaptacao} (nao rotulos).
\item Reavaliar apos 2-3 meses de intervencao; registrar progressos.
\end{enumerate}

\section{Orientacoes ao Professor (material do aluno permanece sem avaliacao clinica)}
\begin{itemize}
\item O aluno NAO deve ter contato com este volume.
\item O professor NAO aplica testes; ele observa, registra e adapta.
\item Adaptacoes sao planejamento pedagogico, nao e diagnostico.
\item Qualquer suspeita e comunicada ao profissional responsavel pelo volume.
\item Elogiar esforco e progresso; jamais usar fichas como rotulo ou punicao.
\end{itemize}

\avisolegal
"""

# ---------------------------------------------------------------- REFERENCIAS
REFERENCIAS = r"""
\chapter*{Referencias de Instrumentos Citados}
\addcontentsline{toc}{chapter}{Referencias de Instrumentos Citados}

\section*{Como usar esta tabela}
Esta secao reune, por referencia (SATEPSI/CFP e literatura cientifica), os
instrumentos citados nas fichas da Parte B. Nenhum instrumento e reproduzido
neste volume: o profissional habilitado aplica a versao original adquirida junto
a editora detentora dos direitos. A indicacao de quem aplica segue o SATEPSI
(CFP) e as normas de cada editora. DOIs conferidos na data de producao desta
edicao; revisar antes de citar em laudos.

\section*{Tabela de Referencia}
\setlength{\tabcolsep}{4pt}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{3.0cm}>{\raggedright\arraybackslash}p{3.6cm}>{\raggedright\arraybackslash}p{1.8cm}>{\raggedright\arraybackslash}p{2.7cm}>{\raggedright\arraybackslash}p{4.1cm}@{}}
\toprule
Instrumento & O que avalia & Faixa & Quem aplica & Referencia / DOI \\
\midrule
\endfirsthead
\toprule
Instrumento & O que avalia & Faixa & Quem aplica & Referencia / DOI \\
\midrule
\endhead
TDE-II (Stein, Giacomoni e Fonseca) & Leitura, escrita e aritmetica escolar & 1.o ao 9.o ano & Psicopedagogo, neuropsicopedagogo, psicologo e fonoaudiologo (SATEPSI: nao privativo) & Vetor Editora. Unico instrumento psicopedagogico normalizado para o Brasil. \\
SRS-2 & Responsividade social (triagem TEA) & 2,5 anos a adulto (versoes) & Psicologo & Barbosa et al. (2015). J Bras Psiquiatr. DOI: 10.1590/\hspace{0pt}0047-2085000000083. Otoni et al. (2023). Psic.: Teor. e Pesq. DOI: 10.1590/\hspace{0pt}0102.3772e39nspe11.en. \\
ADI-R & Entrevista diagnostica TEA com responsaveis & Criancas e adolescentes & Psicologo/psiquiatra habilitado & Becker et al. (2012). Arq Neuro-Psiquiatr. DOI: 10.1590/\hspace{0pt}S0004-282X2012000300006. \\
ADOS-2 & Avaliacao observacional padronizada TEA & Criancas e adolescentes & Psicologo/psiquiatra com formacao especifica & Lord et al. (2012). WPS. Em processo de validacao no Brasil; usar normas internacionais com cautela. \\
CARS-BR & Gravidade de sintomas de TEA & 3 a 17 anos & Psicologo/psiquiatra & Traducao/validacao brasileira (LUME UFRGS); alfa de Cronbach 0,82; concordancia com ATA r = 0,89. \\
Mini-TEA & Rastreio de TEA & 2,5 a 12 anos & Profissional de saude habilitado & Escala brasileira recente; ver PubMed 38438070. \\
SNAP-IV & Sintomas de TDAH e TOD (relato de pais e professores) & 4 a 16 anos & Triagem (uso profissional; nao diagnostica) & Mattos et al. (2006). Rev Psiquiatr RS. DOI: 10.1590/\hspace{0pt}S0101-81082006000300008. Costa et al. (2019). J Pediatr (Rio J). DOI: 10.1016/\hspace{0pt}j.jped.2018.06.014. Dominio publico. \\
CBCL/TRF & Problemas de comportamento (internalizantes e externalizantes) & 6 a 18 anos & Psicologo & Achenbach (ASEBA); adaptacao brasileira publicada em periodicos indexados. \\
SDQ & Triagem de saude mental (forcas e dificuldades) & 4 a 17 anos & Uso profissional em triagem & Goodman; versao brasileira validada. \\
ABFW & Linguagem infantil: fonologia, vocabulario, fluencia, pragmatica & Infantil (provas por faixa etaria) & Fonoaudiologo & Andrade, Befi-Lopes, Fernandes e Wertzner. Pro-Fono. \\
PROLEC & Processos de leitura (letras, lexico, sintaxe, semantica) & 2.o ao 5.o ano & Fonoaudiologo, psicologo e professor (adaptacao brasileira) & Cuetos, Rodriguez e Ruano; adapt. Capellini, Oliveira e Cuetos. Hogrefe. Nota: PROLEC-T tem amostra limitada no Brasil (Pinheiro, 2017); uso informal. \\
MABC-2 & Coordenacao motora (destreza manual, mirar e pegar, equilibrio) & 3 a 16 anos (BI2: 7 a 10) & Psicologo, terapeuta ocupacional, fisioterapeuta, educacao fisica, pediatra & Henderson, Sugden e Barnett. Pearson. \\
CDI & Sintomas depressivos (autorrelato) & 7 a 17 anos & Psicologo & Kovacs (1983); adaptacao brasileira Gouveia et al. (1995); versao reduzida em Cruvinel e Boruchovitch (2008). DOI: 10.1590/\hspace{0pt}S1414-98932008000300011. \\
CABI & Comportamento e psicopatologia (relato parental) & 6 a 18 anos & Psicologo (triagem) & Adaptacao brasileira publicada em 2023; ver PMC10373135. Gratuito. \\
WISC-V & Inteligencia e processamento cognitivo & 6 a 16 anos & Psicologo (SATEPSI privativo) & Wechsler. Pearson. \\
\bottomrule
\end{longtable}

\section*{Avisos de rigor}
\begin{itemize}
\item O ADOS-2 ainda nao possui normas brasileiras completas; sua mencao e
referencial, para uso por profissional com formacao especifica.
\item O PROLEC-T (prova de compreensao de texto) apresenta amostra limitada no
Brasil e deve ser usado apenas como avaliacao informal (Pinheiro, 2017).
\item Instrumentos privativos de psicologo (ex.: WISC-V, CDI, CBCL) seguem a
Resolucao CFP n. 009/2018 e o SATEPSI; psicopedagogos e neuropsicopedagogos
aplicam os instrumentos nao privativos (ex.: TDE-II) e entrevistas/observacao.
\item Este volume nao reproduz itens, normas ou materiais de nenhum instrumento;
as fichas da Parte B sao observacao pedagogica propria e rastreio sistematico.
\end{itemize}

\avisolegal
"""

# ---------------------------------------------------------------- BUILD
body = PRE + SITUACAO
for i, (nome, dom) in enumerate(DOMINIOS, 1):
    body += "\n" + dominio(nome, dom, i) + "\n"
body += "\n" + r"\clearpage" + "\n"
body += "\n" + r"\chapter*{Parte B --- Fichas de Rastreio Sistematico e Investigativo (Confirmacao)}" + "\n"
body += r"\addcontentsline{toc}{chapter}{Parte B --- Fichas de Rastreio}" + "\n"
for n, f in enumerate(F, 1):
    body += "\n" + ficha(n, f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8]) + "\n"
body += "\n" + SINTESE + "\n" + REFERENCIAS + "\n" + POST

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(body)
print("gerado:", OUT, "| dominios:", len(DOMINIOS), "| fichas:", len(F))