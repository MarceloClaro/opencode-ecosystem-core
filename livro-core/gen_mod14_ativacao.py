#!/usr/bin/env python3
"""gen_mod14_ativacao.py — injeta em cada módulo do manual um bloco
'Ativação e cálculo' (R613) com: gatilho, rota, função, cálculo, justificativa
teórica, citação \citref (recorte original + tradução + página) e limitação.

Idempotente: se o arquivo já contém o marcador 'ATIVACAO-R613', ignora.
Execução: python3 gen_mod14_ativacao.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MARKER = "% ATIVACAO-R613"

# (arquivo, título da seção, gatilho, rota, funcao, calculo, justificativa,
#  limite, citacao ref, doi, pagina, just_cit, trecho, traducao)
MODULES = [
    (
        "mod-01-fundacoes.tex", "Fundamentos",
        "Gatilho: primeira leitura do manual (rota linear capa \\textrightarrow{} sumário \\textrightarrow{} módulos).",
        "Rota: leitura sequencial; gate: capítulo introdutório.",
        "Função: fixar as bases conceituais (metacognição, agentes, determinismo) antes de qualquer ativação operacional.",
        "Cálculo: completude conceitual = 9 princípios declarados; o manual exige domínio dos 9 antes dos Módulos 2 em diante.",
        "Justificativa: a triade reatividade/proatividade/socialidade transforma o gatilho textual em roteamento real.",
        "Limite: dominar o vocabulário não garante execução correta; a execução depende do pipeline E1--E7.",
        "Wooldridge, M.; Jennings, N. R. (1995). Intelligent agents: theory and practice. \\emph{The Knowledge Engineering Review}, 10(2), 115--152.",
        "10.1017/S0269888900008122", "p.~115--152 (resumo, p.~115)",
        "é o lastro da triade que define quando um gatilho é de fato uma ativação de agente: reatividade, proatividade e habilidade social são as propriedades que o pipeline E1--E7 converte em regras de roteamento.",
        "The concept of an agent has become important in both artificial intelligence and mainstream computer science",
        "O conceito de agente tornou-se importante tanto na inteligência artificial quanto na ciência da computação.",
    ),
    (
        "mod-01b-historia.tex", "História e linhas do tempo",
        "Gatilho: consulta cronológica (\"quando foi criado\", \"linha do tempo\").",
        "Rota: navegação temporal direta pelo capítulo.",
        "Função: situar cada componente do ecossistema na linha do tempo da IA e da engenharia de software.",
        "Cálculo: janelas temporais = 4 (pré-1980, 1980--2000, 2000--2020, 2020--hoje); cada janela mapeada a marcos verificáveis.",
        "Justificativa: o campo de agentes apresenta, no próprio roteiro de pesquisa, a organização histórica por conceitos e aplicações.",
        "Limite: linha do tempo é didática; datas de DOI/impressão podem diferir das datas de publicação on-line.",
        "Jennings, N. R.; Sycara, K.; Wooldridge, M. (1998). A roadmap of agent research and development. \\emph{Autonomous Agents and Multi-Agent Systems}, 1(1), 7--38.",
        "10.1023/A:1010090405266", "p.~7--38 (resumo, p.~7)",
        "é a moldura histórica e conceitual: o roteiro do campo identifica conceitos-chave e aplicações e como se relacionam — exatamente a função deste módulo para o ecossistema.",
        "It aims to identify key concepts and applications, and to indicate how they relate to one-another",
        "O objetivo é identificar conceitos-chave e aplicações e indicar como eles se relacionam entre si.",
    ),
    (
        "mod-01c-instalacao.tex", "Instalação e ambiente",
        "Gatilho: ``instalar'', ``ambiente mínimo'', ``doctor''.",
        "Rota: linha de comando; gate: \\pth{python3 -m marceloclaro.cli doctor} com checks\\_failed = 0.",
        "Função: garantir ambiente reprodutível antes de qualquer ativação de agente ou skill.",
        "Cálculo: saúde do ambiente = 1 se checks\\_failed = 0, senão 0; o manual não segue com 0.",
        "Justificativa: alegações computacionais exigem padrão mínimo de reprodução do ambiente.",
        "Limite: ambiente verde não implica qualidade de resultado — apenas reprodutibilidade do processo.",
        "Peng, R. D. (2011). Reproducible research in computational science. \\emph{Science}, 334(6060), 1226--1227.",
        "10.1126/science.1213847", "p.~1226--1227 (resumo, p.~1226)",
        "ancora o gate de instalação: reprodutibilidade é o padrão mínimo para julgar alegações quando a replicação integral não é possível — o que o doctor verifica antes de todo pipeline.",
        "Reproducibility has the potential to serve as a minimum standard for judging scientific claims when full independent replication of a study is not possible",
        "A reprodutibilidade tem o potencial de servir como padrão mínimo para julgar alegações científicas quando a replicação independente completa de um estudo não é possível.",
    ),
    (
        "mod-02-orquestracao.tex", "Orquestração",
        "Gatilho: tarefa multi-passo publicada no Blackboard.",
        "Rota: \\pth{marceloclaro/orchestrator.py}; rota (b) inline ou (c) voluntariado.",
        "Função: coordenar E1--E7 sem executar; escolher o executante com maior escore de ativação.",
        "Cálculo: $A(a) = |K \\cap C_a|/|K \\cup C_a|$ (Jaccard ponderado entre tokens do gatilho e capacidades declaradas); tie-break por prioridade de categoria.",
        "Justificativa: o modelo blackboard emprega quadros visíveis e especialistas que reagem a anúncios — a base do roteamento por oportunidade.",
        "Limite: escore alto mede casamento semântico, não qualidade da entrega; gate SDD/TDD permanece obrigatório.",
        "Smith, R. G. (1980). The Contract Net Protocol: high-level communication and control in a distributed problem solver. \\emph{IEEE Transactions on Computers}, C-29(12), 1104--1113.",
        "10.1109/TC.1980.1675516", "p.~1104--1113 (resumo, p.~1104)",
        "é o fundamento do voluntariado por anúncio/leilão usado na ETAPA 3: nós com tarefas anunciam, nós capazes avaliam e licitam, e o manager escolhe o mais adequado — análogo ao casamento de capacidades do Blackboard.",
        "The contract net protocol has been developed to specify problem-solving communication and control for nodes in a distributed problem solver",
        "O protocolo da rede de contratos foi desenvolvido para especificar comunicação e controle de resolução de problemas para nós em um solucionador distribuído de problemas.",
    ),
    (
        "mod-03-memoria-mci.tex", "Memória metacognitiva",
        "Gatilho: consulta ao MetaBus/Global Workspace por lições e confiança.",
        "Rota: MCP \\pth{metacognitive-interconnect}; gate: memória auditável.",
        "Função: prover contexto e histórico de confiança para que a ativação não repita erros registrados.",
        "Cálculo: confiança do agente = média ponderada dos scores dos ciclos (score por ciclo dividido pela soma dos pesos); lições com mesmo tema agrupadas no MetaBus.",
        "Justificativa: o arcabouço de metamemória de dois níveis — meta-nível que monitora e controla o objeto-nível — é o desenho do MetaBus sobre o estado do ecossistema.",
        "Limite: memória descreve o passado; não prediz o futuro (validação externa continua necessária).",
        "Nelson, T. O.; Narens, L. (1990). Metamemory: a theoretical framework and new findings. In: BOWER, G. H. (ed.), \\emph{The Psychology of Learning and Motivation}, v.~26, p.~125--173.",
        "10.1016/S0079-7421(08)60053-5", "p.~125--173 (resumo do capítulo, p.~125)",
        "é a base do desenho meta-nível/objeto-nível do MetaBus: o meta-nível adquire informação do objeto-nível (monitoramento) e o altera (controle) — exatamente o fluxo entre memória compartilhada e ativação dos agentes.",
        "This eventuated in the present theoretical framework that emphasizes the role of control and monitoring processes",
        "Isso resultou no presente arcabouço teórico que enfatiza o papel dos processos de controle e monitoramento.",
    ),
    (
        "mod-04-qualidade-sdd.tex", "Qualidade SDD/TDD",
        "Gatilho: ``implemente'', ``corrija'', ``teste''.",
        "Rota: spec \\textrightarrow{} teste \\textrightarrow{} código; gate R610 (spec com teste).",
        "Função: exigir especificação formal e testes antes da entrega; transformar alegações em evidências executáveis.",
        "Cálculo: cobertura SDD = specs com teste / specs totais; ciclo RED--GREEN--REFACTOR = $1$ se testes verdes, senão $0$.",
        "Justificativa: nenhuma bala de prata existe — melhoria de produtividade e confiabilidade vem de disciplina acumulada, não de ferramenta única.",
        "Limite: teste verde não generaliza para produção; gate não mede mérito científico.",
        "Brooks, F. P. (1987). No Silver Bullet: essence and accidents of software engineering. \\emph{Computer}, 20(4), 10--19.",
        "10.1109/MC.1987.1663532", "p.~10--19 (trecho inicial, p.~11)",
        "é o aviso contra otimismo de ferramenta única: o protocolo SDD/TDD do Core traduz a disciplina de passo a passo que Brooks recomenda — nenhum agente entrega ordem de magnitude por si só.",
        "There is no single development, in either technology or management technique, which by itself promises even one order-of-magnitude improvement within a decade in productivity, in reliability, in simplicity",
        "Não há um único desenvolvimento, seja em tecnologia ou técnica de gestão, que por si só prometa uma melhoria de uma ordem de magnitude em produtividade, confiabilidade e simplicidade dentro de uma década.",
    ),
    (
        "mod-05-raciocinio.tex", "Raciocínio formal",
        "Gatilho: ``resolva'', ``prove'', ``modele''.",
        "Rota: motores \\pth{Z3}, \\pth{SymPy}, \\pth{Kanren} com roteamento automático.",
        "Função: obter prova/modelo/solução por métodos formais e simbólicos; quantificar solvabilidade.",
        "Cálculo: solvabilidade = tarefas com modelo/prova / tarefas totais; speedup teórico limitado pela fração sequencial (Lei de Amdahl).",
        "Justificativa: a Lei de Amdahl explica por que paralelizar só parte do pipeline não acelera o todo — a fração sequencial manda.",
        "Limite: modelo formal válido não é prova de relevância empírica.",
        "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. \\emph{AFIPS Conference Proceedings}, 30, 483--485.",
        "10.1145/1465482.1465560", "p.~483--485 (recorte do texto integral, p.~484)",
        "é o limite fundamental da aceleração: esforço em paralelismo sem ganho sequencial é desperdiçado — princípio que o roteamento de motores aplica ao escolher o motor mais adequado em vez de paralelizar tudo.",
        "The effort expended on achieving high parallel processing rates is wasted unless it is accompanied by achievements in sequential processing rates of very nearly the same magnitude",
        "O esforço despendido para alcançar altas taxas de processamento paralelo é desperdiçado a menos que seja acompanhado por conquistas em taxas de processamento sequencial de magnitude muito próxima.",
    ),
    (
        "mod-06-ciencia.tex", "Ciência e MASWOS",
        "Gatilho: ``pesquisa'', ``revisão sistemática'', ``artigo''.",
        "Rota: 16 estágios MASWOS; gate: escaneadores + rubrica.",
        "Função: conduzir e auditar pesquisa com relato transparente e completo.",
        "Cálculo: SRI 0--100 (Índice de Rigor Científico) e cobertura de checklist item a item; falha em item crítico => falha do gate.",
        "Justificativa: relato transparente e completo permite ao leitor avaliar a confiança e a aplicabilidade dos achados — o mesmo requisito de qualquer revisão do ecossistema.",
        "Limite: relatar bem não torna o achado verdadeiro; mérito requer validação externa.",
        "Page, M. J. et al. (2021). PRISMA 2020 explanation and elaboration: updated guidance and exemplars for reporting systematic reviews. \\emph{BMJ}, 372, n160.",
        "10.1136/bmj.n160", "p.~n160 (resumo, p.~n160)",
        "é a norma de transparência de relato usada no Módulo 6: sem relato completo não há como julgar confiança e aplicabilidade — princípio estendido ao relato dos ciclos de evolução e das fichas.",
        "The methods and results of systematic reviews should be reported in sufficient detail to allow users to assess the trustworthiness and applicability of the review findings",
        "Os métodos e resultados de revisões sistemáticas devem ser relatados em detalhe suficiente para permitir aos usuários avaliar a confiabilidade e a aplicabilidade dos achados da revisão.",
    ),
    (
        "mod-07-integracoes.tex", "Integrações externas",
        "Gatilho: ``executor externo'', ``MCP'', ``CLI''.",
        "Rota: bridges tolerantes em \\pth{integrations/*}; ausência do binário gera warn, não crash.",
        "Função: compor CLIs externas como executores orquestráveis e tolerantes; manter proveniência de dados.",
        "Cálculo: saúde da integração = executores disponíveis / executores declarados; cada bridge valida presença e versão antes do uso.",
        "Justificativa: a delegação entre nós com anúncio, licitação e contrato é o mecanismo de composição que as bridges implementam para executores externos.",
        "Limite: resultado externo nunca é verificado sem validação do Core (R110).",
        "Smith, R. G. (1980). The Contract Net Protocol: high-level communication and control in a distributed problem solver. \\emph{IEEE Transactions on Computers}, C-29(12), 1104--1113.",
        "10.1109/TC.1980.1675516", "p.~1104--1113 (resumo, p.~1104)",
        "é o padrão de delegação usado nas bridges: anunciar a tarefa, receber licitações e firmar contrato com o executor mais adequado — o que \\pth{integrations/*} faz com gemini, goose, plandex e reasonix.",
        "Task distribution is affected by a negotiation process, a discussion carried on between nodes with tasks to be executed and nodes that may be able to execute those tasks",
        "A distribuição de tarefas é efetuada por um processo de negociação, uma discussão conduzida entre nós com tarefas a executar e nós que possam ser capazes de executar essas tarefas.",
    ),
    (
        "mod-08-ecossistema.tex", "Ecossistema e economia de tokens",
        "Gatilho: \\pth{/economy}, staking, slashing.",
        "Rota: Token Economy + Trust Engine; gate: trust $< 0.3$ exige supervisão.",
        "Função: alinhar incentivos entre ativação, reputação e punição de entregas reprovadas.",
        "Cálculo: stake final = stake inicial - slashing proporcional ao score reprovado; fee market regula prioridade de ativação.",
        "Justificativa: a racionalidade do ecossistema é limitada, não global: agentes decidem com informação e capacidade computacional disponíveis, o que o Trust Engine modela com histórico.",
        "Limite: incentivos não substituem validação externa; economia mede reputação, não verdade.",
        "Simon, H. A. (1955). A Behavioral Model of Rational Choice. \\emph{The Quarterly Journal of Economics}, 69(1), 99--118.",
        "10.2307/1884852", "p.~99--118 (trecho do texto integral, p.~99)",
        "é a fundação do desenho de incentivos do ecossistema: substituir a racionalidade global — que pressupõe informação e computação ilimitadas — por um comportamento compatível com o histórico e a capacidade reais dos agentes registrados no Trust Engine.",
        "Broadly stated, the task is to replace the global rationality of economic man with a kind of rational behavior that is compatible with the access to information and the computational capacities that are actually possessed by organisms",
        "Em termos amplos, a tarefa é substituir a racionalidade global do homem econômico por um tipo de comportamento racional compatível com o acesso à informação e com as capacidades computacionais efetivamente possuídas pelos organismos.",
    ),
    (
        "mod-09a-comparada.tex", "Comparação e benchmarking",
        "Gatilho: ``compare'', ``benchmark'', ``segunda opinião''.",
        "Rota: avaliação multi-agente; gate: ponderação igual e ablação.",
        "Função: comparar agentes/motores com critérios justos e reproducíveis.",
        "Cálculo: média ponderada igual entre geradores; ablação isola cada componente; seeds fixas garantem determinismo.",
        "Justificativa: comparar exige reportar o processo — só há mérito comparável se o relato do método é completo.",
        "Limite: comparação interna não substitui avaliação por pares externa.",
        "Ioannidis, J. P. A. (2005). Why most published research findings are false. \\emph{PLoS Medicine}, 2(8), e124.",
        "10.1371/journal.pmed.0020124", "p.~e124 (resumo, p.~e124)",
        "é a âncora do ceticismo estruturado do benchmarking: a maioria dos achados publicados é falsa; comparar sem controle de vieses de desenho e relato reproduz o mesmo problema.",
        "There is increasing concern that most current published research findings are false",
        "Há preocupação crescente de que a maioria dos resultados de pesquisa atualmente publicados seja falsa.",
    ),
    (
        "mod-09-infra.tex", "Infraestrutura",
        "Gatilho: \\pth{doctor}, serviços MCP, integrações de dados.",
        "Rota: serviços determinísticos; gate: rastro e proveniência por operação.",
        "Função: executar serviços de suporte com rastro completo e disponibilidade mensurável.",
        "Cálculo: disponibilidade = operações com rastro / operações totais; proveniência = metadados de origem/versão por artefato.",
        "Justificativa: a proveniência detalhada e o rastro por operação são o que torna a infraestrutura auditável.",
        "Limite: rastro documenta, não garante correção do mundo externo.",
        "Wilkinson, M. D.; Dumontier, M.; Aalbersberg, I. J. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. \\emph{Scientific Data}, 3, 160018.",
        "10.1038/sdata.2016.18", "p.~160018 (resumo, p.~160018)",
        "é o padrão de auditabilidade dos serviços de infraestrutura: todo dado usado pelo Core deve ser localizável, acessível, interoperável e reutilizável — o que o rastro de operações materializa.",
        "Good data management is not a goal in itself, but is the key conduit leading to knowledge discovery and innovation",
        "O bom gerenciamento de dados não é um fim em si mesmo, mas o principal canal que conduz à descoberta de conhecimento e à inovação.",
    ),
    (
        "mod-10-catalogo.tex", "Catálogo de agentes",
        "Gatilho: \\pth{/agents}, inventário, registro de card.",
        "Rota: \\pth{agents/catalog/*.md}; gate R608 (frontmatter tolerante, descrição não vazia).",
        "Função: inventariar 212+ cards com capacidades declaradas e proveniência.",
        "Cálculo: parseabilidade = 212/212 cards com YAML válido; taxa de cards com descrição = 100\% após R608/R609.",
        "Justificativa: um card só é ativável se descreve capacidades enxergáveis — a proveniência dos cards é o mesmo princípio FAIR aplicado a agentes.",
        "Limite: card parseável não implica desempenho; implica participação no casamento de capacidades.",
        "Wilkinson, M. D.; Dumontier, M.; Aalbersberg, I. J. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. \\emph{Scientific Data}, 3, 160018.",
        "10.1038/sdata.2016.18", "p.~160018 (resumo, p.~160018)",
        "é o critério de governança dos cards: registros encontáveis e reutilizáveis, com metadados completos; o reparo R608/R609 restaurou a encontrabilidade dos 212 cards para o casamento de capacidades.",
        "Findability is the first step in the reuse of data",
        "A localização (encontrabilidade) é o primeiro passo para a reutilização dos dados.",
    ),
    (
        "mod-11-apendices.tex", "Biblioteca de citações",
        "Gatilho: consulta à biblioteca auditada; nova citação candidata.",
        "Rota: biblioteca \\pth{referencia} + metodologia R110.",
        "Função: manter apenas fontes verificadas, com recorte conferido, tradução fiel e página.",
        "Cálculo: taxa de ativação = DOIs ativos / DOIs da biblioteca; DOIs quebrados são removidos na próxima auditoria.",
        "Justificativa: relato transparente inclui documentar o processo de verificação de cada referência.",
        "Limite: verificação atesta disponibilidade do DOI, não a verdade do conteúdo.",
        "Page, M. J. et al. (2021). PRISMA 2020 explanation and elaboration: updated guidance and exemplars for reporting systematic reviews. \\emph{BMJ}, 372, n160.",
        "10.1136/bmj.n160", "p.~n160 (resumo, p.~n160)",
        "é o padrão de transparência da própria biblioteca: assim como revisões sistemáticas exigem relato completo, a biblioteca do manual exige que cada citação declare justificativa, recorte, tradução e página.",
        "reports of systematic reviews should be transparent and complete",
        "os relatos de revisões sistemáticas devem ser transparentes e completos.",
    ),
    (
        "mod-12-fichas-nucleo.tex", "Leitura das fichas",
        "Gatilho: leitura de ficha; aula; consulta de referência.",
        "Rota: ficha 13 dimensões; gate: conferir cada recorte no DOI reabrindo o link.",
        "Função: dar leitura ativa e auditável das dimensões de cada conceito do núcleo.",
        "Cálculo: cobertura de dimensões = dimensões preenchidas / 13; o leitor confere 13/13 antes de aceitar a ficha.",
        "Justificativa: o monitoramento ativo da própria compreensão é o coração da metacognição aplicada ao estudo do manual.",
        "Limite: ficha completa não equivale a validação externa do conceito.",
        "Flavell, J. H. (1979). Metacognition and cognitive monitoring: a new area of cognitive-developmental inquiry. \\emph{American Psychologist}, 34(10), 906--911.",
        "10.1037/0003-066X.34.10.906", "p.~906--911 (resumo, p.~906)",
        "é o lastro da leitura ativa das fichas: a metacognição como monitoramento ativo e regulação dos próprios processos cognitivos — o leitor monitora se entendeu cada dimensão da ficha antes de seguir.",
        "Metacognition refers, among other things, to the active monitoring and consequent regulation and orchestration of these processes",
        "A metacognição refere-se, entre outras coisas, ao monitoramento ativo e à consequente regulação e orquestração desses processos.",
    ),
]


def render(entry) -> str:
    (file, title, gatilho, rota, funcao, calculo, justificativa, limite,
     citacao, doi, pagina, just_cit, trecho, traducao) = entry
    label = file.removesuffix(".tex")[len("mod-"):len("mod-") + 4].replace("-", "") or "xx"
    label = "ativ-" + label
    # Campos já chegam prontos para LaTeX (\\pth, \\emph, $...$, \\textrightarrow);
    # nenhum escape adicional é aplicado para preservar as macros intencionais.
    return f"""% ============================================================
{MARKER}
%  Gerado por gen_mod14_ativacao.py (R613) — seção de ativação e cálculo
%  para o módulo {file}. Edições manuais são preservadas nas próximas
%  execuções (marcador impede reescrita).
% ============================================================

\\section[Ativação e cálculo]{{Ativação e cálculo — {title}}}
\\elemento{{{label}}}{{\\metainfo{{Ciclo}}{{R613}} \\hfill \\metainfo{{Módulo}}{{{file}}}}}

\\begin{{processo}}
GATILHO. {gatilho}
ROTA. {rota}
FUNÇÃO. {funcao}
\\end{{processo}}

\\begin{{resultado}}
CÁLCULO. {calculo}
\\end{{resultado}}

\\begin{{descricao}}
JUSTIFICATIVA TEÓRICA. {justificativa} O lastro teórico vem da citação que
segue: recorte conferido em 29/09/2026, com a página de origem e tradução livre
e fiel.
\\end{{descricao}}

\\begin{{aviso}}
LIMITE E ANTI-OVERCLAIM. {limite} A verificação atesta a existência e a
localização da fonte (R110), não o mérito da afirmação.
\\end{{aviso}}

A citação que segue conecta a ativação e o cálculo deste módulo à literatura
verificada na biblioteca do Módulo 11:

\\citref{{{citacao}}}{{{doi}}}{{{pagina}. {just_cit}}}{{{trecho}}}{{{traducao}}}
"""


def main() -> None:
    changed = []
    for entry in MODULES:
        fname = entry[0]
        path = ROOT / fname
        if not path.exists():
            print(f"!! arquivo ausente: {fname}")
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"== já processado: {fname}")
            continue
        block = render(entry)
        new = text.rstrip() + "\n\n" + block
        path.write_text(new, encoding="utf-8")
        changed.append(fname)
    print(f"OK: {len(changed)} módulos atualizados -> {', '.join(changed) or 'nenhum'}")


if __name__ == "__main__":
    main()