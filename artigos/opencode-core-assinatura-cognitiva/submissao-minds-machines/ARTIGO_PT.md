# A casa que ajuda a pensar: próteses cognitivas autorais, IA agêntica e os limites da soberania epistêmica

**Subtítulo:** Um estudo de caso filosófico de um sistema agêntico autoconstruído

**Autor:** Marcelo Claro Laranjeira

**E-mail:** marcelolclaro@gmail.com

**ORCID:** [0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)

**Data:** 10 de novembro de 2026

**Versão:** português — versão de leitura e de referência. A versão em inglês (`MANUSCRIPT_MINDS_MACHINES.md`) é a preparada para a *Minds and Machines*.

> **Nota de cuidado.** O relato de saúde que motiva este artigo é do próprio autor. A AH/SD não é doença; risco de Alzheimer não é diagnóstico; este texto não é aconselhamento médico. Nenhuma parte do sistema foi validada como intervenção neuroprotetora.

---

## Resumo

Este artigo examina um enigma filosófico levantado por sistemas de IA autoconstruídos: quando uma pessoa projeta um sistema agêntico para compensar suas próprias vulnerabilidades cognitivas, quem é o autor da cognição resultante e que tipo de artefato é esse? O artigo desenvolve um estudo de caso de um sistema agêntico autoconstruído, designado como o Core: um monorepo para orquestração agêntica, externalização de memória e verificação, construído por um pesquisador que relata altas habilidades/superdotação e risco elevado de Alzheimer. Defende uma **conta moderada da prótese cognitiva**: o sistema não é parte literal da mente, mas um andaime robusto que transforma a tarefa, redistribui o trabalho epistêmico e materializa um estilo de responsabilidade. Introduz o conceito de **assinatura cognitiva** como uma configuração situada de escolhas documentáveis, não um biomarcador. Identifica três riscos epistêmicos — falsa objetividade, viés de automação e perda de habilidades — e três riscos éticos — dependência, burocratização do cuidado e desigualdade epistêmica. Propõe uma epistemologia N-of-1 para testar alegações sobre a prótese sem excesso de confiança. Conclui que o valor de uma prótese autoral não está em substituir a pessoa, mas em preservar agência, contestabilidade e a capacidade de parar.

**Palavras-chave:** prótese cognitiva; mente estendida; IA agêntica; dependência epistêmica; autoria; assinatura cognitiva.

---

## 1. Introdução: o enigma da cognição autoral

Imagine uma pessoa que constrói uma casa para a própria mente. A casa tem cômodos para a memória, para o trabalho, para a verificação e para o ensino. A casa não é um experimento mental: é um sistema de software, construído pela pessoa que o usa, para compensar vulnerabilidades cognitivas que ela conhece por dentro. O sistema registra o que foi decidido, o que foi testado e o que permanece incerto. Delega tarefas a agentes, verifica suas saídas e se recusa a chamar uma alegação de “verificada” sem validação externa. É, em uma palavra, uma prótese.

O enigma não é se esse sistema é útil. É que tipo de coisa ele é, e quem responde pelo que ele faz. O sistema é uma extensão da mente, no sentido defendido por Clark e Chalmers (1998)? É uma mera ferramenta, causalmente útil mas cognitivamente externa? É um andaime que transforma a tarefa sem se tornar parte do sistema cognitivo, como sugere Sterelny (2010)? Ou é um novo tipo de agente epistêmico, cujas saídas são coautoradas pelo humano que o projetou e pelos agentes artificiais que o executam? Essas perguntas não são ociosas. Elas afetam como avaliamos o sistema, como atribuímos responsabilidade por seus erros e como cuidamos da pessoa que depende dele.

Este artigo defende três teses. Primeiro, o Core é mais bem compreendido como uma **prótese cognitiva autoral**: um andaime robusto que carrega parte da carga cognitiva e transforma a tarefa, mas não constitui a mente. Segundo, sua **assinatura cognitiva** é uma configuração situada de escolhas documentáveis — um estilo de responsabilidade, não uma impressão digital. Terceiro, o ideal de **soberania epistêmica** que motiva esse sistema é necessariamente limitado: a prótese administra a dependência de agentes, modelos e registros, mas não pode eliminá-la. Por soberania epistêmica, entendo o ideal de autogoverno sobre a própria vida cognitiva: a capacidade de decidir o que acreditar, o que lembrar e o que contar como evidência, sem dependência indevida dos outros. O ideal é atraente, mas é necessariamente limitado pela dependência epistêmica. A tarefa ética é tornar essa dependência visível, contestável e tratada com cuidado.

O caso é o **Core**, um monorepo para orquestração agêntica, pesquisa científica e produção de evidência. O sistema conecta agentes, servidores MCP, especificações formais, testes, registros de evolução, um livro, um pipeline científico e uma camada de memória metacognitiva. Sua regra de ouro é incomum: nenhuma entrega sem especificação, teste e evidência. A pergunta central do projeto não é “quantos agentes existem?”, mas “o que foi executado, com qual fonte, qual hash e qual limite?” (Core Project, 2026b). O criador relata altas habilidades/superdotação e risco elevado de Alzheimer. A AH/SD é frequentemente associada a pensamento sistêmico, hiperfoco, reconhecimento rápido de padrões e padrões intelectuais altos; também pode vir acompanhada de sobrecarga executiva, perfeccionismo e dificuldade de parar. O risco de Alzheimer torna saliente a finitude da memória e dá urgência ao ato de deixar rastros. A arquitetura responde a esse duplo contexto com memória externalizada, contratos, verificação e retomada.

O artigo faz quatro contribuições. Primeiro, oferece uma **conta moderada da prótese cognitiva**, distinta tanto da tese forte da mente estendida quanto da visão deflacionária da ferramenta. Segundo, introduz a **assinatura cognitiva** como conceito interpretativo com critérios explícitos de aplicação, não como biomarcador ou ornamento literário. Terceiro, desenvolve uma **epistemologia da prótese**, centrada na diferença entre dispositivos de coordenação e garantias epistêmicas, e na virtude da humildade epistêmica institucionalizada. Quarto, propõe uma **ética do autodesign**, centrada em cuidado, desigualdade epistêmica e contestabilidade. O artigo também responde a cinco objeções, incluindo a acusação de que o caso é apenas um sistema de gestão do conhecimento pessoal e a de que um autoestudo não pode sustentar teses filosóficas.

O método é um estudo de caso filosófico. Combina análise documental do repositório com o relato em primeira pessoa do autor e com literatura sobre cognição estendida, artefatos cognitivos, cognição distribuída, dependência epistêmica e ética do cuidado. Não oferece avaliação clínica, neuropsicológica ou experimental. A informação de saúde é um autorrelato, não um diagnóstico. O artigo não afirma que o sistema previne, trata ou diagnostica Alzheimer; não afirma que a AH/SD causa Alzheimer; e não oferece aconselhamento médico. O caso é ilustrativo, não representativo: serve para iluminar um fenômeno e gerar hipóteses, não para estabelecer uma lei geral.

O percurso é o seguinte. A Seção 2 apresenta o caso e o método. A Seção 3 pergunta o que é uma prótese cognitiva e defende uma conta moderada. A Seção 4 examina autoria e assinatura cognitiva. A Seção 5 desenvolve a epistemologia da prótese. A Seção 6 discute a ética do autodesign. A Seção 7 responde a objeções. A Seção 8 propõe uma epistemologia N-of-1 para testar alegações sobre a prótese. A Seção 9 conclui.

## 2. O caso e o método

### 2.1 O caso

O Core é um monorepo público mantido pelo autor. Neste artigo, “autor” e “criador” designam a mesma pessoa, que projetou o sistema e escreveu este relato. O checkout local analisado em 10 de novembro de 2026 (base Git `1ce6ae98`) registra 35 servidores MCP, 35 comandos e 374 entradas de agente em `opencode.json`. O bloco reconciliado do `README.md` registra 366 agentes e 35 MCPs; a divergência entre as contagens é um lembrete de que um inventário não é um retrato único e de que a documentação também tem história. O repositório contém 681 arquivos de especificação no padrão `SPEC-*.md`, 646 arquivos de teste e 845 ciclos de evolução. São contagens de arquivos ou de configuração. Nenhuma delas mede qualidade, disponibilidade, autenticação, inferência ou validação externa.

O Core organiza a operação em um ciclo de seis movimentos: Perceber → Especificar → Delegar → Executar → Verificar → Refletir. O ciclo não é uma sequência rígida; é uma gramática de governança (Core Project, 2026b, 2026c). Cada movimento tem mecanismos, artefatos e limites. A arquitetura inclui uma CLI, um orquestrador, uma camada de especificação e teste, uma camada de memória metacognitiva, uma camada de confiança e incentivos, um catálogo de agentes e uma camada de apresentação e documentação. Os detalhes estão no material suplementar; o argumento filosófico exige apenas sua função.

Três características do Core importam para o argumento. Primeiro, ele **externaliza a memória**: o MetaBus armazena memória episódica e semântica, um livro de confiança e eventos que podem ser consultados antes de uma nova decisão. Segundo, ele **externaliza a verificação**: especificações, testes, um SpecVerifier, um BehavioralGate, um gate metacognitivo e um `CORRIGENDUM.md` público governam as condições sob as quais uma alegação pode ser chamada de verificada. Terceiro, ele **externaliza a gestão da interrupção**: o TaskRuntime assume que uma tarefa pode ser interrompida e retomada, em vez de exigir presença contínua. Essas características não são apenas técnicas. Elas encarnam uma postura normativa: o sistema é desenhado como se a memória pudesse falhar, a convicção pudesse enganar e a pessoa pudesse precisar parar.

### 2.2 Método

O artigo adota o estudo de caso instrumental (Yin, 2018): o Core importa menos por si do que pelo fenômeno que ilumina — a construção de uma prótese cognitiva por seu próprio usuário. O corpus inclui:

- documentos de arquitetura e operação (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md`, `CORRIGENDUM.md`);
- o prefácio R909 sobre assinatura cognitiva e sua especificação;
- módulos de memória, orquestração, verificação, confiança, economia e evolução;
- registros de evolução e contagens de especificações e testes;
- literatura externa sobre cognição, aprendizagem, AH/SD e demência.

A análise é documental, não experimental. Não houve execução do sistema para medir desempenho, nem aplicação de testes cognitivos no autor, nem acesso a prontuário, biomarcadores ou avaliação neuropsicológica. As afirmações sobre o código são verificáveis nos arquivos citados. As afirmações sobre a cognição do autor são interpretações baseadas em seu autorrelato e em sua produção textual, não diagnósticos. O manuscrito foi preparado com auxílio de IA para rascunho preliminar, edição estrutural e formatação de referências. O autor revisou, reescreveu e verificou o texto e assume plena responsabilidade pelo conteúdo. Uma declaração detalhada está nas Declarações.

### 2.3 Posição e viés

O criador é também o principal usuário do sistema. Isso produz uma vantagem — acesso ao processo de projeto — e um risco: o viés de confirmação, a tendência a buscar e interpretar informações de modo a sustentar crenças prévias (Nickerson, 1998). O próprio Core incorpora uma resposta a esse risco: o `CORRIGENDUM.md`, documento público de autocorreção de alegações; o gate metacognitivo, que não retorna “verificado” sem validação externa explícita; e a exigência de especificação, teste e recibo. Esses mecanismos não eliminam o viés. Eles o tornam visível e contestável — o máximo que uma arquitetura pode prometer.

### 2.4 Limites

Os limites são explícitos. Primeiro, este é um caso único; não pode ser generalizado para outras pessoas com AH/SD, outros criadores ou outras formas de risco neurocognitivo. Segundo, não há dados clínicos: o risco de Alzheimer é relatado, não diagnosticado. Terceiro, as contagens são sensíveis ao tempo: especificações, testes e ciclos mudam a cada commit. Quarto, as pontuações dos ciclos são autoavaliação, não benchmark externo (Core Project, 2026e). Quinto, nenhum desfecho cognitivo, funcional ou clínico foi medido. Sexto, uma metáfora não é um mecanismo: chamar módulos de “memória”, “atenção” ou “metacognição” não os torna medidas da mente humana (Poldrack, 2011). A fronteira entre descrição e diagnóstico exige cautela; o RDoC, por exemplo, é um quadro de pesquisa, não um instrumento clínico (Insel et al., 2010).

### 2.5 O caso situado: AH/SD e risco neurocognitivo

Argumentos filosóficos sobre próteses cognitivas são frequentemente ilustrados com casos hipotéticos. Este artigo usa um caso situado, com todas as limitações que isso implica. O autor relata altas habilidades/superdotação e risco elevado de Alzheimer. O relato não é um diagnóstico e não é oferecido como fato clínico. É o pano de fundo contra o qual as escolhas de design se tornam inteligíveis.

A AH/SD designa um perfil de potencial elevado, com manifestações heterogêneas em domínios específicos, combinado com criatividade e envolvimento com a tarefa (Renzulli, 1978). Modelos desenvolvimentais acrescentam que o talento se constrói ao longo do tempo, em condições de aprendizagem, apoio e reconhecimento (Gagné, 2004). No Brasil, a legislação educacional reconhece a AH/SD como categoria da educação especial (Brasil, 1996, 2008), o que confirma que se trata de uma questão educacional e de desenvolvimento, não de uma patologia. A expressão “sofrer de superdotação”, comum na fala cotidiana, captura o sofrimento que pode acompanhar a assincronia entre capacidade e ambiente, mas não nomeia uma categoria nosológica. O artigo usa a formulação mais precisa: o autor relata AH/SD.

O perfil é associado, no relato do autor, a pensamento sistêmico, reconhecimento rápido de padrões, hiperfoco e padrões altos. São recursos, mas também têm custos: o hiperfoco pode apagar a percepção do tempo e das necessidades básicas; os padrões altos podem transformar cada entrega em dívida; a velocidade associativa pode produzir uma sensação de evidência que os dados ainda não sustentam. Esses custos não são universais nem diagnósticos. São hipóteses de trabalho que explicam por que certas escolhas arquiteturais aparecem no Core: orçamentos, timeouts, checkpoints, especificações, testes, recibos.

O segundo elemento é o risco de Alzheimer. É importante distinguir três planos. A **doença de Alzheimer** é, na pesquisa contemporânea, definida por um continuum biológico, com marcadores que podem preceder os sintomas por décadas (Jack et al., 2018). A **demência** é uma síndrome clínica com impacto funcional. O **risco** é uma estimativa probabilística que combina genética, fatores vasculares e metabólicos, escolaridade, atividade física, audição, vida social, depressão e outros fatores (Livingston et al., 2020). Risco não é destino; diagnóstico não é prognóstico; prognóstico não é sentença.

A noção de **reserva cognitiva** ajuda a pensar o problema sem prometer milagres. A hipótese é que experiências de vida — educação, trabalho intelectual, engajamento social, atividades complexas — podem permitir que uma pessoa lide melhor com a patologia antes que os sintomas se tornem incapacitantes (Stern, 2002). Isso não significa que uma atividade específica previna a doença. A literatura é observacional, heterogênea e sujeita a causalidade reversa. Nenhum software foi validado como intervenção neuroprotetora. Um sistema como o Core pode, no máximo, reduzir demandas ambientais, apoiar rotinas, externalizar memória e preservar continuidade. Esses efeitos são plausíveis, mas precisam ser medidos. O artigo os trata como hipóteses de pesquisa, não como resultados.

A combinação de AH/SD e risco neurocognitivo não é uma afirmação causal. Não há evidência de que a AH/SD cause Alzheimer, e o artigo não especula sobre esse vínculo. A combinação é uma **restrição de projeto**: explica por que uma pessoa com alta demanda cognitiva e medo de perda construiria um sistema para externalizar memória, estabilizar critérios e tornar a interrupção sobrevivível. A pergunta filosófica não é se o sistema cura ou previne alguma coisa. É que tipo de artefato essa resposta produz e como ele deve ser avaliado.

## 3. O que é uma prótese cognitiva?

### 3.1 A tese da mente estendida

Clark e Chalmers (1998) propuseram que processos cognitivos podem se estender para além do crânio. O exemplo clássico é o caderno de Otto, que funciona como memória externa confiável e acessível. O “princípio de paridade” sugere que, se um processo externo desempenha a mesma função que um processo interno, ele merece o mesmo status cognitivo. A tese é filosófica, não clínica: desloca a unidade de análise do cérebro para o sistema pessoa–ambiente. Nessa visão, uma memória externa bem projetada não é mera ajuda à cognição; é parte do processo cognitivo.

A tese tem apelo intuitivo para o caso. O Core não apenas armazena informação; participa da produção de decisões. Ele guarda o contexto que o autor teria de reconstruir, os critérios que definem o que conta como feito e os registros que tornam uma alegação contestável. Se a tese da mente estendida estiver certa, o Core não está fora da cognição do autor; é uma de suas condições materiais.

A linhagem importa. O memex de Bush (1945) e o programa de Engelbart (1962) para aumentar o intelecto humano já imaginavam sistemas externos que ajudariam as pessoas a pensar. O Core pertence a essa linhagem, mas acrescenta uma característica distintiva: não é apenas uma ferramenta de armazenamento ou recuperação de informação; governa as condições sob as quais uma alegação pode ser feita, uma tarefa pode ser retomada e uma memória pode ser confiável.

### 3.2 Os críticos

A tese também tem críticos sérios. Rupert (2004) argumenta que a cognição estendida não explica adequadamente a integração e a persistência dos processos internos. Sterelny (2010) propõe uma alternativa mais modesta: a mente é **andaimeada** por estruturas externas, mas nem todo andaime se torna parte do sistema cognitivo. Adams e Aizawa (2001) fazem um ponto relacionado: o fato de um processo externo estar acoplado a um interno não mostra que o externo seja constituído pelo mesmo tipo de atividade cognitiva. Acoplamento não é constituição.

Essas objeções importam para o caso. O Core está acoplado à cognição do autor de muitas maneiras: armazena seu contexto, estrutura suas tarefas e verifica suas alegações. Mas o acoplamento, por si só, não resolve a questão metafísica. Um caderno pode ser parte de um processo cognitivo em um contexto e um mero objeto em outro. A diferença não é apenas causal; é normativa. O caderno importa porque é confiável, consultado e integrado a uma prática. O mesmo vale para o Core.

### 3.3 Artefatos cognitivos e affordances

Norman (1991) mostrou que artefatos cognitivos não apenas armazenam informação: transformam a tarefa. Uma lista de verificação não é um lembrete passivo; reorganiza a sequência, reduz a dependência da memória de trabalho e torna o erro mais visível. O mesmo vale para uma especificação, um teste automatizado ou um recibo com hash. Esses artefatos não “pensam” pelo usuário; mudam a economia da atenção. A teoria da carga cognitiva explica por que isso importa: a memória de trabalho é limitada, e artefatos que reduzem a carga extrínseca liberam recursos para a tarefa (Sweller, 1988). A descarga cognitiva é o fenômeno geral de usar o ambiente para reduzir a demanda interna (Risko & Gilbert, 2016).

O Core é um artefato cognitivo de um tipo particular. Não apenas representa o que deve ser feito; define **quando** algo pode ser considerado feito. Não apenas armazena um resultado; armazena a evidência que torna o resultado contestável. É a diferença entre um caderno e um sistema de governança. O caderno ajuda a lembrar; o Core ajuda a decidir se você tem direito a afirmar que lembra corretamente.

### 3.4 Cognição distribuída

Hutchins (1995) mostrou que a cognição de uma cabine de avião não está apenas na cabeça dos pilotos: está distribuída entre pessoas, instrumentos, procedimentos e representações. Hollan, Hutchins e Kirsh (2000) estenderam essa abordagem para a interação humano–computador. A unidade de análise é o sistema coordenado, não o indivíduo isolado.

O Core é um sistema cognitivo distribuído: o autor, os agentes, os servidores MCP, as especificações, os testes e os registros formam uma rede que produz decisões. Mas há uma assimetria ética: apenas o autor responde pelo que o sistema faz. A distribuição da cognição não distribui a responsabilidade. Essa assimetria é o fundamento da Seção 4.

### 3.5 Uma conta moderada

Com base nessas tradições, o artigo defende uma **conta moderada** da prótese cognitiva. O Core não é parte literal da mente, mas é mais do que uma ferramenta neutra. É um **andaime robusto** que satisfaz três critérios:

1. **Portante.** Carrega parte da carga cognitiva: memória, sequenciamento, verificação e gestão da interrupção.
2. **Transformador da tarefa.** Muda as affordances da tarefa, não apenas a velocidade de execução. Torna certos erros visíveis, certas alegações contestáveis e certas formas de continuidade possíveis.
3. **Normativamente integrado.** Está embutido em práticas de confiança, verificação e cuidado. O agente depende dele de um modo que molda sua agência epistêmica e prática.

O Core satisfaz esses critérios. É portante porque o autor teria de reconstruir contexto, critérios e evidência sem ele. É transformador da tarefa porque converte uma intenção vaga em especificação, uma especificação em teste e um teste em alegação contestável. É normativamente integrado porque o autor confia nele, corrige-o e depende dele. Mas nada disso o torna parte literal da mente. O conceito de prótese captura esse status intermediário: mais que uma ferramenta, menos que um constituinte.

### 3.6 Uma taxonomia das próteses cognitivas

É útil distinguir quatro tipos de prótese cognitiva:

1. **Próteses de armazenamento** estendem a memória: cadernos, calendários, bancos de dados e sistemas de gestão do conhecimento pessoal.
2. **Próteses procedurais** estendem a função executiva: listas de verificação, fluxos de trabalho, gerenciadores de tarefas e modelos.
3. **Próteses epistêmicas** estendem a verificação e o julgamento: especificações, testes, gates de evidência, revisão por pares e trilhas de auditoria.
4. **Próteses agênticas** estendem a agência: sistemas que delegam tarefas, executam ações e coordenam múltiplos agentes.

O Core não é apenas uma prótese de armazenamento. É uma **prótese epistêmica agêntica**: combina a capacidade de delegar e executar com a capacidade de verificar e governar. Essa combinação é o que o torna filosoficamente interessante. Um caderno ajuda a lembrar; uma lista de verificação ajuda a sequenciar; um agente ajuda a agir. Mas um sistema que delega, executa e verifica levanta uma nova pergunta: quem responde pelo resultado? A resposta não pode ser “o sistema” sozinho, porque o sistema não tem o tipo de responsabilidade que a prestação de contas exige. A resposta deve ser o humano que projetou o processo e aceitou o resultado, mesmo que a contribuição causal seja distribuída.

A taxonomia também esclarece os riscos éticos. Próteses de armazenamento e procedurais levantam principalmente questões de dependência e habilidade. Próteses epistêmicas levantam questões de confiança e falsa objetividade. Próteses agênticas levantam questões de agência e responsabilidade. O Core combina as quatro, e é por isso que é um caso exigente: concentra as questões epistêmicas e éticas que normalmente estão distribuídas entre tecnologias diferentes.

### 3.7 Por que “prótese” não é metáfora

A palavra “prótese” não é metáfora. É uma analogia funcional. Uma prótese substitui ou apoia uma função que a pessoa não consegue desempenhar, ou não consegue desempenhar de modo confiável, sozinha. Precisa se ajustar à pessoa, ser mantida e ser integrada a uma prática. Pode restaurar agência, mas também criar dependência, desconforto e novas formas de vulnerabilidade. O mesmo vale para uma prótese cognitiva.

A analogia tem limites. Uma prótese médica é tipicamente prescrita por um profissional e avaliada por critérios clínicos. Uma prótese cognitiva é frequentemente autodesenhada, autoajustada e autoavaliada. É precisamente por isso que a epistemologia e a ética do autodesign importam. A pessoa que constrói a prótese é também a que a usa e a que a avalia. O risco de excesso de confiança está embutido na situação. A resposta do artigo não é abandonar a prótese, mas construir práticas que tornem o excesso de confiança mais difícil.

## 4. Autoria e assinatura cognitiva

### 4.1 O problema da autoria composta

O Core não é produto de uma única mente. Usa bibliotecas, modelos, dados, práticas herdadas e contribuições de agentes artificiais. O autor projetou a arquitetura, escolheu os critérios e escreveu as especificações; os agentes executam tarefas, geram texto e propõem soluções; os modelos são treinados em corpora que nenhuma pessoa sozinha escreveu. Quem, então, é o autor das saídas do sistema?

É útil distinguir quatro noções. **Contribuição causal** é a mais ampla: muitas entidades contribuem para uma saída. **Agência** é a capacidade de agir e produzir efeitos; um agente artificial pode ter agência nesse sentido fino. **Autoria** é a capacidade de projetar o processo, definir os critérios e decidir o que conta como resultado bem-sucedido; é uma capacidade normativa, não apenas causal. **Responsabilidade** é a prestação de contas pelas consequências do processo; é a capacidade de responder pelo que foi feito.

O autor tem autoria e responsabilidade, mesmo quando a contribuição causal é distribuída. Os agentes têm contribuições causais e, em sentido fino, agência; não têm autoria ou responsabilidade no sentido relevante. Isso não é uma negação da agência artificial. Como argumentam Floridi e Sanders (2004), agentes artificiais podem ser moralmente relevantes sem serem pessoas morais. Também não é uma negação da moralidade distribuída: como argumenta Floridi (2013), a responsabilidade moral pode ser distribuída por um sistema de agentes e artefatos. Mas distribuição não é desaparecimento. O humano permanece o ponto em que a responsabilização se localiza, porque é ele quem pode ser chamado a justificar o design, os critérios e a decisão de aceitar o resultado.

Essas distinções importam para a assinatura cognitiva. Se a autoria fosse reduzida à contribuição causal, a assinatura seria um produto coletivo sem dono. Se fosse reduzida ao controle autoral, seria uma intenção puramente mental sem traço material. O caso interessante está no meio: a assinatura é materializada na arquitetura, mas não se esgota nas intenções do autor. É um **estilo de responsabilidade** que emerge da interação entre o autor, os agentes e os artefatos.

### 4.2 A assinatura cognitiva

O prefácio de design do projeto define a **assinatura cognitiva autoral** como “esta configuração situada de escolhas documentáveis” (Core Project, 2026a). A definição é deliberadamente modesta. Não afirma que o código revela a mente do autor; afirma que o código preserva marcas de suas perguntas, critérios, representações e decisões. A versão forte — que qualquer ecossistema revelaria, de modo único e recuperável, a cognição de um único criador — excede a evidência disponível. A atribuição estilística a partir de artefatos técnicos tem limites; pode preservar regularidades, mas não mede personalidade ou cognição (Caliskan et al., 2018).

O conceito tem quatro critérios de aplicação. Primeiro, **documentabilidade**: as escolhas devem ser observáveis no artefato, não apenas inferidas do testemunho do autor. Segundo, **recorrência**: as escolhas devem aparecer em contextos diversos, não em uma única decisão isolada. Terceiro, **contraevidência**: a interpretação deve ser contestável por escolhas que contradigam o padrão. Quarto, **poder explicativo**: a assinatura deve explicar algo sobre o comportamento do sistema que de outro modo seria enigmático. Esses critérios não fazem da assinatura uma medição científica. Fazem dela uma hipótese interpretativa com restrições públicas.

### 4.3 Cinco marcas

Cinco marcas são documentáveis no Core. Elas não esgotam a assinatura; são um recorte interpretativo.

**1. A memória tratada como frágil.** O sistema é construído como se a memória pudesse falhar. Há memória compartilhada, livro de confiança, especificações, recibos, hashes, âncoras de estado. Essa escolha não é apenas técnica: é uma postura existencial. O design não confia na lembrança; confia no registro. A frase “o que foi executado, com qual fonte, qual hash e qual limite?” é uma resposta à possibilidade de esquecimento.

**2. O contrato antes do impulso.** A regra “nenhuma entrega sem especificação” subordina a inspiração a uma forma. Para um criador com alta fluência e hiperfoco, isso é contraintuitivo: a vontade de fazer vem antes do contrato. A arquitetura inverte a ordem. O contrato não nega o impulso; protege-o de si mesmo, impedindo que o entusiasmo redefina o critério de sucesso no meio do caminho.

**3. A verificação contra a própria convicção.** O gate anti-overclaim, o `CORRIGENDUM.md` e a exigência de validação externa são uma resposta à tendência de confundir coerência com verdade. É talvez a marca mais distintiva do Core. Não se trata de desconfiar dos outros; trata-se de desconfiar da própria capacidade de construir uma narrativa convincente. A arquitetura transforma essa desconfiança em procedimento.

**4. A arquitetura da interrupção.** O runtime assume que a tarefa pode ser interrompida; o MetaBus assume que o contexto pode se perder; o `doctor` assume que o ambiente pode estar quebrado. O sistema é feito para retomar, não para exigir presença contínua. Essa marca é especialmente significativa em um contexto de risco neurocognitivo: a arquitetura não promete memória perfeita, mas promete um caminho de volta.

**5. A vocação didática.** O livro, o manual, o MIRA, os explicadores e a preocupação com a “democratização do conhecimento” mostram que a assinatura não está apenas no código. Está na vontade de ensinar o que foi aprendido. Essa marca tem uma dimensão ética: o conhecimento não é tratado como propriedade, mas como algo que deve ser tornado acessível — com limites, fontes e avisos.

**Tabela 1. Cinco marcas da assinatura cognitiva**

| Marca | Evidência no Core | Interpretação | Contraevidência |
|---|---|---|---|
| Memória tratada como frágil | MetaBus, hashes, recibos, âncoras de estado | Desconfiança da lembrança; confiança no registro | O sistema guarda apenas os últimos 1.000 eventos |
| Contrato antes do impulso | Especificações, critérios de aceite, TDD | Proteção da intenção contra a volatilidade | Uma spec pode se tornar burocracia |
| Verificação contra a convicção | Gate anti-overclaim, `CORRIGENDUM.md` | Desconfiança de narrativas coerentes | A autoavaliação continua sendo autoavaliação |
| Arquitetura da interrupção | DAGs, leases, checkpoints, retomada | Design para fadiga e perda de contexto | O usuário ainda pode se sobrecarregar |
| Vocação didática | Livro, manual, MIRA, explicadores | Conhecimento como bem comum | Documentação não é eficácia pedagógica |

### 4.4 A assinatura como estilo de responsabilidade

A assinatura não é uma impressão digital. É um **estilo de responsabilidade**: uma maneira característica de responder à incerteza. O autor responde à incerteza documentando, testando, corrigindo e pedindo revisão. Isso não é um traço psicológico; é uma postura normativa materializada na arquitetura. A mesma postura poderia ser adotada por alguém com personalidade diferente, e a mesma personalidade poderia produzir uma postura diferente. A assinatura é a postura, não a pessoa. A hipótese da “mirroring” sugere que a modularidade de um sistema pode refletir o estilo de coordenação de quem o produz (MacCormack et al., 2012). Isso sustenta uma leitura composta da assinatura: ela não é um retrato do autor, mas o resultado de uma interação entre autor, ferramentas, modelos e comunidade.

Isso tem uma consequência importante para a ética da IA. Se a assinatura é um estilo de responsabilidade, a pergunta relevante não é “quem é o autor?” em sentido metafísico, mas “quem responde?” em sentido prático. O humano que projeta o processo e aceita o resultado responde, mesmo que a saída seja coproduzida por agentes. Os agentes podem ser causalmente relevantes sem serem responsáveis. A assinatura é o traço dessa responsabilização.

### 4.5 O risco de mito

Toda interpretação da autoria corre o risco de se tornar mito. O mito tem três formas. A primeira é a **celebração**: transformar a arquitetura em prova de genialidade. A segunda é a **justificação**: usar a assinatura para explicar ou desculpar falhas. A terceira é a **prisão**: acreditar que o autor só pode criar de uma maneira, e que a assinatura é um destino.

O artigo recusa as três. A assinatura é uma hipótese interpretativa, não uma essência. A generalização a partir de um caso único exige cautela (Yarkoni, 2022). Ela pode ser contestada por contraexemplos: escolhas que contradizem o padrão, contribuições que vêm de outros, momentos em que o sistema falha. A própria existência do `CORRIGENDUM.md` é uma contraprova à tentação de celebrar. Um sistema que se corrige publicamente não é um monumento; é uma obra em andamento.

## 5. A epistemologia da prótese

### 5.1 Memória externalizada

O MetaBus é descrito como um “barramento unificado de eventos metacognitivos” e uma “memória compartilhada” entre agentes. Mantém memória episódica, memória semântica e um **livro de confiança** — um registro de confiança por agente ou tópico. A inspiração declarada é a Global Workspace Theory, o framework Reflexion (Shinn et al., 2023) e a memória colaborativa em sistemas multiagente (Core Project, 2026f). Na prática, o MetaBus publica eventos, permite que agentes se inscrevam neles e persiste um estado que pode ser consultado antes de uma nova decisão. A memória é seletiva: o código mantém os últimos 1.000 eventos episódicos. É uma escolha de projeto, não um detalhe. Um sistema que tentasse lembrar tudo teria custo, ruído e risco de contaminação. A seletividade é uma forma de esquecimento produtivo.

A função cognitiva externalizada é o **contexto**. O autor não precisa reconstruir de memória o que já foi decidido, testado ou descartado. Mas o MetaBus não é um backup da mente. Registra traços, não experiência vivida. A diferença importa: um traço pode ser consultado; uma experiência precisa ser interpretada. O risco é que o registro pareça mais completo do que é. Uma memória seletiva pode produzir uma falsa sensação de continuidade. O autor pode lembrar o registro e esquecer as lacunas.

### 5.2 Verificação

A verificação é o coração epistêmico do Core. O TDDRunner produz evidência de teste; o SpecVerifier confere critérios; o BehavioralGate autoriza ou bloqueia ações com base em confiança; o gate metacognitivo classifica o grau de uma alegação e **não retorna “verificado” sem validação externa explícita**. O `CORRIGENDUM.md` registra alegações que soaram mais fortes do que a evidência disponível e propõe a leitura correta. A prática de escrever o teste antes da implementação é a base do TDD (Beck, 2002).

A função cognitiva externalizada é o **teste de realidade**. O sistema não impede o autor de acreditar em algo; torna mais difícil declarar que algo foi provado quando não foi. Para alguém com alta capacidade de construir narrativas coerentes, isso é um contrapeso necessário. A coerência interna de uma explicação não é prova de sua verdade; um teste que passa não é prova de que o teste mede o que deveria medir; uma pontuação alta não é prova de mérito.

O limite é o mesmo de qualquer sistema de verificação: ele só verifica o que foi especificado. Um teste pode confirmar uma hipótese errada, uma especificação pode formalizar um critério inadequado, um gate pode bloquear uma ação correta. A verificação é uma prática, não uma máquina de certeza. A literatura sobre reprodutibilidade mostra que resultados aparentes podem não se sustentar (Ioannidis, 2005). A resposta do Core não é reivindicar certeza, mas institucionalizar a possibilidade de correção.

### 5.3 Confiança e falsa objetividade

O Blackboard implementa um quadro compartilhado no qual agentes se voluntariam para tarefas com base em **Agent Cards** — descrições de capacidades, esquema de entrada e status. O padrão blackboard é clássico em sistemas de IA (Nii, 1986), e a noção de agente como sistema autônomo que percebe e age em um ambiente vem da literatura de agentes (Wooldridge & Jennings, 1995). A seleção pondera capacidades declaradas, confiança histórica e carga. O Trust Engine mantém pontuações por ação, aplica um gate comportamental e registra resultados. A Token Economy acrescenta stake, slashing e um mercado de taxas (Core Project, 2026f).

Há dois riscos. O primeiro é a **falsa objetividade**: uma pontuação de confiança não é uma medida de verdade. Um agente pode ter alta confiança e produzir uma resposta errada com segurança. O segundo é o **falso mérito**: o stake mede compromisso, não competência. A economia de tokens é um dispositivo de coordenação, não uma epistemologia. O mesmo vale para a pontuação de confiança. É útil para alocar atenção e tarefas; não é uma garantia para a crença. No momento em que um dispositivo de coordenação é tratado como garantia epistêmica, a prótese se torna uma máquina de produzir falsa confiança. Dois riscos adicionais decorrem disso. O **viés de automação** é a tendência de aceitar a saída de um agente porque ela é fluente e confiante, mesmo quando a evidência é fraca. A **perda de habilidades** é a perda das capacidades que a prótese deveria apoiar: memória, julgamento e verificação. Ambos são riscos epistêmicos, não apenas práticos. São o preço da descarga cognitiva e precisam ser monitorados, não negados.

### 5.4 Dependência epistêmica

O Core não elimina a dependência epistêmica; redistribui-a. O autor depende de agentes, modelos, registros e da própria arquitetura. Isso não é um defeito. Toda cognição é epistemicamente dependente, no sentido de que se apoia em outros, em instituições e em artefatos (Hardwig, 1985). A pergunta é se a dependência é **objeto de prestação de contas**. O autor consegue rastrear a fonte de uma alegação? Consegue contestá-la? Consegue sair do sistema? Consegue perceber quando o sistema está errado?

A diferença entre confiar em uma pessoa, em uma ferramenta e em um sistema é importante. Confiar em uma pessoa envolve atribuir competência e honestidade; confiar em uma ferramenta envolve depender de sua confiabilidade causal; confiar em um sistema envolve depender de uma rede de pessoas, artefatos e procedimentos. O Core é um sistema nesse sentido. Sua confiabilidade não é propriedade de um único componente; é propriedade do arranjo inteiro. É por isso que a arquitetura de verificação importa. Não basta que o sistema seja confiável; ele precisa ser **contestável**.

Hardwig (1985) argumenta que a dependência epistêmica não é uma falha de racionalidade, mas uma condição dela. Não podemos verificar tudo sozinhos; dependemos de especialistas, instituições e testemunho. O Core generaliza essa dependência para artefatos e agentes. A pergunta não é se devemos depender, mas como tornar a dependência objeto de prestação de contas. Isso exige distinguir **confiança** de **dependência fática**. Dependência fática é uma expectativa causal: espero que o sistema funcione. Confiança é uma atitude normativa: espero que o sistema seja digno de dependência e estou disposto a responder por essa expectativa. O Core convida às duas. Seus testes e gates tornam a dependência fática mais confiável; seu corrigendum e sua validação externa tornam a confiança mais contestável. O risco é confundir as duas — tratar um sistema confiável como digno de confiança, ou um sistema digno de confiança como infalível.

### 5.5 Humildade epistêmica como virtude de design

A característica epistêmica mais distintiva do Core não é sua capacidade de verificar, mas sua capacidade de recusar. O gate metacognitivo não retorna “verificado” sem validação externa. O `CORRIGENDUM.md` registra os excessos do próprio sistema. O design assume que o autor pode estar errado, que os agentes podem estar errados e que os testes podem estar errados. É uma forma de **humildade epistêmica institucionalizada**.

Humildade, aqui, não é um sentimento. É um conjunto de práticas: documentar fontes, distinguir níveis de evidência, convidar crítica e corrigir em público. O Core materializa algumas dessas práticas. Não garante que o autor será humilde; torna a humildade mais fácil de praticar e mais difícil de falsificar. É nesse sentido que a prótese pode ser uma virtude epistêmica: não porque torna a pessoa virtuosa, mas porque estrutura a prática em que a virtude pode ser exercida.

## 6. A ética do autodesign

### 6.1 Cuidado e dependência

A prótese pode se tornar uma **segunda doença**. Um sistema que exige especificações, testes, revisões, atualizações e manutenção pode consumir a vida que deveria proteger. O autor pode passar mais tempo cuidando da arquitetura do que vivendo o que a arquitetura deveria possibilitar. O hiperfoco, que é uma força, pode se aliar ao perfeccionismo e transformar o Core em um labirinto. O repositório tem 681 especificações, 646 testes e 845 ciclos. A riqueza é real; o custo também.

A ética do cuidado é relevante aqui. Cuidado não é apenas ajudar; é sustentar as condições em que o outro pode florescer sem ser absorvido pela ajuda (Tronto, 1993). Uma prótese que exige atenção constante não é cuidado; é uma nova forma de fardo. O resultado é uma **burocratização do cuidado**: o sistema exige documentação, manutenção e justificação, e a pessoa se torna administradora do próprio suporte. A arquitetura precisa de **regras de parada** — critérios explícitos para parar, publicar, descansar e deixar algo imperfeito. Também precisa de **padrões humanos**: quando o sistema falha, deve oferecer uma explicação, uma alternativa, um contato humano, um caminho para continuar. A arquitetura da verificação precisa ser acompanhada de uma arquitetura do cuidado.

Tronto (1993) distingue quatro fases do cuidado: atenção (notar uma necessidade), responsabilidade (assumir a obrigação de atendê-la), competência (ter capacidade de atendê-la) e responsividade (responder à resposta do outro). O Core pode apoiar atenção e responsabilidade: registra necessidades, tarefas e compromissos. Mas também pode distorcê-las. Pode tornar o autor atento às necessidades do sistema em vez das próprias; pode torná-lo responsável por manter o sistema em vez de cuidar de si. Uma prótese que consome o cuidador não é uma prática de cuidado. A arquitetura deve ser julgada pelos mesmos critérios: ela ajuda o autor a notar suas necessidades, assumir responsabilidade por elas, atendê-las com competência e responder aos próprios limites?

### 6.2 Desigualdade epistêmica

Próteses cognitivas não são igualmente acessíveis. Exigem hardware, energia, tempo, conhecimento técnico e certa liberdade para experimentar. A licença MIT do Core, a ênfase local-first e a documentação aberta são respostas parciais a essa desigualdade. Não a resolvem. Uma pessoa que não pode pagar o hardware, ou que não tem tempo para construir e manter o sistema, está excluída dos benefícios.

Essa é uma questão de **injustiça epistêmica** (Fricker, 2007). A distribuição de próteses cognitivas pode reforçar desigualdades existentes no acesso ao conhecimento, à saúde e ao cuidado. O modelo open-source pode mitigar o problema, mas também pode criar uma nova divisão entre quem pode construir e quem só pode consumir. A tarefa ética não é apenas tornar a prótese disponível; é torná-la **adaptável**, **mantenível** e **contestável** pelas pessoas que precisam dela.

### 6.3 A ética da autoexperimentação

O autor é ao mesmo tempo pesquisador e sujeito. O protocolo N-of-1 proposto na Seção 8 é uma tentativa de testar a prótese sem excesso de confiança. Mas a autoexperimentação levanta questões éticas. Quem protege o sujeito? Quem interpreta os resultados? Quem decide quando parar? A pessoa que constrói a prótese não está em boa posição para avaliá-la sozinha. O protocolo, portanto, exige pré-registro, supervisão clínica e revisão independente. O fato de a intervenção ser pessoal não torna as salvaguardas éticas menos necessárias; torna-as mais necessárias.

### 6.4 Contestabilidade

A prótese precisa estar aberta à crítica, à reprodução e à modificação. A “casa” precisa ter portas. A mediação tecnológica materializa valores e escolhas, mas não garante que eles sejam virtuosos (Verbeek, 2006). É por isso que a contestabilidade importa: o artefato pode encarnar uma boa intenção e ainda produzir um efeito ruim. Um sistema que só pode ser entendido por seu criador não é uma contribuição ao conhecimento; é uma linguagem privada. A documentação, os testes e a correção pública do Core são tentativas de manter as portas abertas. Não são suficientes. O teste final da prótese é se outra pessoa consegue usá-la, questioná-la e modificá-la.

## 7. Objeções e respostas

### 7.1 “Isso é apenas um sistema de gestão do conhecimento pessoal”

**Objeção.** O Core é uma coleção de notas, tarefas e scripts. Chamá-lo de prótese cognitiva inflaciona uma prática familiar em uma tese filosófica.

**Resposta.** A diferença não é a presença de notas, mas a **arquitetura normativa** que as governa. Um sistema de gestão do conhecimento pessoal ajuda a armazenar e recuperar informação. O Core governa as condições sob as quais uma alegação pode ser chamada de verificada, uma tarefa pode ser retomada e uma memória pode ser confiável. Inclui especificações, testes, um verificador, um gate comportamental, um corrigendum público e um gate metacognitivo que recusa “verificado” sem validação externa. Não são recursos de armazenamento; são procedimentos epistêmicos. O conceito de prótese captura essa diferença. É um conceito funcional, não metafísico.

### 7.2 “A tese da mente estendida é falsa; o Core é apenas uma ferramenta”

**Objeção.** A tese da mente estendida foi criticada em bases metafísicas. Se a tese é falsa, o Core é uma ferramenta, e a linguagem da prótese é enganosa.

**Resposta.** O artigo não depende da tese forte da mente estendida. Adota uma **conta moderada**: o Core é um andaime robusto que transforma a tarefa e redistribui o trabalho epistêmico, mas não constitui a mente. Essa conta é compatível com os críticos. Rupert (2004) e Sterelny (2010) têm razão ao dizer que acoplamento não é constituição. Mas o significado normativo da prótese não depende da constituição. Uma ferramenta pode ser portante, transformadora da tarefa e normativamente integrada sem ser parte da mente. O conceito de prótese ocupa esse espaço intermediário.

### 7.3 “A assinatura cognitiva não é empiricamente testável”

**Objeção.** A assinatura cognitiva é uma interpretação literária. Não pode ser medida, falsificada ou generalizada. Não é um conceito científico.

**Resposta.** A assinatura não é um biomarcador, e não pretende ser. É uma hipótese interpretativa com restrições públicas: documentabilidade, recorrência, contraevidência e poder explicativo. Essas restrições não a tornam uma medição, mas a tornam contestável. A assinatura pode ser avaliada como outras alegações interpretativas nas ciências sociais interpretativas e nas humanidades: por coerência, poder explicativo e abertura à contraevidência. O artigo não afirma que a assinatura é um tipo natural. Afirma que é um conceito útil para entender como valores e escolhas se materializam em artefatos.

### 7.4 “O autoestudo é enviesado e não pode sustentar teses filosóficas”

**Objeção.** O autor é o criador e o usuário do sistema. O caso é subjetivo, seletivo e autopromocional. Não pode sustentar um argumento filosófico geral.

**Resposta.** O caso é instrumental, não representativo. Serve para iluminar um fenômeno e gerar hipóteses, não para estabelecer uma lei geral. Os vieses são declarados, e o próprio sistema incorpora mecanismos que tornam alguns vieses visíveis: o corrigendum público, o gate anti-overclaim, a exigência de validação externa. Esses mecanismos não eliminam o viés, mas tornam o caso mais contestável do que um relato puramente autobiográfico. O artigo também convida a contraexemplos e revisão independente. Um autoestudo pode ser um método filosófico legítimo se for conduzido com humildade e transparência adequadas.

### 7.5 “Usar IA para escrever sobre cognição coautorada por IA é circular”

**Objeção.** O artigo foi rascunhado com um assistente de IA. Usar IA para analisar um sistema que usa IA é circular. O argumento entra em contradição.

**Resposta.** A IA é uma ferramenta, não um autor. O autor projetou o argumento, selecionou as fontes, verificou as alegações e assume a responsabilidade pelo texto. O uso de IA está declarado no método e nas declarações. A circularidade não é uma falha do argumento; é parte do caso. O artigo trata das condições sob as quais humanos e agentes coproduzem cognição. Escrever sobre essa condição com a ajuda de um agente não é uma refutação; é uma ilustração. A pergunta relevante é se o humano permanece responsável. O artigo argumenta que sim.

## 8. Testando a hipótese: uma epistemologia N-of-1

A alegação de que a prótese ajuda é uma hipótese empírica. Deve ser testada, não presumida. O caso é único, personalizado e heterogêneo; um ensaio randomizado tradicional não é viável nem ético. O desenho N-of-1 — ou experimento de caso único — permite testar hipóteses em uma pessoa, com medidas repetidas, condições alternadas e pré-registro (Nosek et al., 2018). Não produz generalização estatística, mas produz evidência local, útil para decisões informadas.

O protocolo é uma proposta. Não foi executado. Deve ser adaptado com profissionais de saúde, neuropsicólogos e revisão de ética em pesquisa. Os desfechos primários devem incluir tempo para retomar após uma interrupção, taxa de conclusão de tarefas, taxa de erros em tarefas rotineiras, carga cognitiva percebida e calibração da confiança. Desfechos secundários devem incluir senso de agência, sono e vida social, e sintomas de estresse. A matriz completa de desfechos está no material suplementar.

Um desenho possível é um **ABAB com blocos randomizados** ao longo de 12 semanas. Na fase A, o autor realiza tarefas comparáveis com suas ferramentas habituais, sem o sistema. Na fase B, usa o sistema com as mesmas tarefas. A e B alternam, com uma semana de washout. A ordem dos blocos é randomizada e registrada. A avaliação de alguns desfechos pode ser cega. Hipóteses, desfechos, análises e critérios de parada são registrados antes do início. A análise pode combinar inspeção visual de séries temporais com modelos mistos; tamanhos de efeito devem ser reportados com incerteza; a multiplicidade deve ser controlada ou explicitamente discutida; resultados negativos devem ser publicados. A análise não deve ser feita pelo mesmo agente que implementou a intervenção sem supervisão independente.

A ética do protocolo é tão importante quanto o desenho: consentimento informado, proteção de dados sensíveis, supervisão clínica, separação entre pesquisa e cuidado, revisão por comitê de ética quando aplicável e compromisso de não transformar o resultado em alegação de cura ou prevenção. O protocolo N-of-1 não é uma concessão ao empirismo. É uma expressão da mesma humildade epistêmica que o Core tenta institucionalizar: a disposição de tratar a própria prótese como hipótese.

## 9. Conclusão

Este artigo analisou o Core como uma prótese cognitiva autoral. O argumento procedeu em três passos. Primeiro, o sistema é um andaime robusto que carrega parte da carga cognitiva, transforma a tarefa e é normativamente integrado às práticas do autor. Não é parte literal da mente, mas é mais do que uma ferramenta neutra. Segundo, sua assinatura cognitiva é uma configuração situada de escolhas documentáveis — um estilo de responsabilidade, não uma impressão digital. Terceiro, o ideal de soberania epistêmica que motiva o sistema é necessariamente limitado: a prótese administra a dependência de agentes, modelos e registros, mas não pode eliminá-la.

O contexto de AH/SD e risco de Alzheimer dá urgência ao projeto. A AH/SD ajuda a explicar a intensidade, a complexidade e a exigência de rigor; o risco neurocognitivo ajuda a explicar a ênfase em memória, continuidade e retomada. Mas o artigo recusou a causalidade fácil: não há evidência de que a AH/SD cause Alzheimer, nem de que o Core previna a doença. O que existe é uma coerência de projeto: um sistema construído para sustentar a vida cognitiva de alguém que conhece a própria fragilidade.

A contribuição principal não é o sistema em si, mas a possibilidade de pensá-lo criticamente. Uma prótese cognitiva autoral deve ser avaliada pelo que preserva, não pelo que promete. Se o Core ajuda o autor a continuar pensando, trabalhando e ensinando, cumpre uma função; se o impede de dormir, de conviver ou de parar, falha. O critério não é a quantidade de agentes, especificações ou ciclos. É a qualidade de vida que a arquitetura torna possível.

O programa de pesquisa que se abre é claro: medir, com desenho N-of-1 e supervisão clínica, os efeitos do Core sobre retomada, carga cognitiva, erros, agência e bem-estar; comparar com alternativas mais simples; investigar os riscos de dependência e perda de habilidades; e desenvolver uma ética de próteses cognitivas que seja ao mesmo tempo rigorosa e humana.

A casa não substitui o arquiteto. Ela lhe devolve tempo e espaço para continuar a desenhar — e, quando for preciso, para sair.

---

## Declarações

**Conflitos de interesse.** O autor declara não ter conflitos de interesse financeiros ou não financeiros. O autor é o criador e principal usuário do sistema analisado; essa relação é declarada e tratada como possível fonte de viés na Seção 2.3.

**Financiamento.** Esta pesquisa não recebeu financiamento específico de agências públicas, comerciais ou sem fins lucrativos.

**Ética e consentimento.** Trata-se de um autoestudo baseado na análise documental do próprio projeto de software do autor e em seu autorrelato. Não envolve participantes além do autor, e não foram usados dados clínicos, biométricos ou de terceiros identificáveis. A aprovação ética não foi necessária. O autor consente com a publicação do autorrelato e da análise.

**Consentimento para publicação.** O autor é o único participante e consente com a publicação.

**Disponibilidade de dados e código.** O código, as especificações, os testes e os registros de evolução estão disponíveis em repositório público: https://github.com/MarceloClaro/opencode-ecosystem-core. O artigo não relata dados experimentais; o corpus documental é descrito na Seção 2.2 e no Apêndice A.

**Preprint.** Uma versão anterior em português deste artigo está disponível no repositório público do projeto. Ela não foi revisada por pares. A presente versão é uma versão revista e ampliada.

**Uso de IA.** O autor utilizou um assistente de IA (o orquestrador `marceloclaro`, baseado em DeepSeek V4.1 Flash, via OpenCode) para rascunho preliminar, edição estrutural e formatação de referências. O autor revisou, reescreveu e verificou o texto, conferiu as fontes e assume plena responsabilidade pelo conteúdo. A IA não é autora e não tomou decisões interpretativas ou éticas. Um relato detalhado da divisão de trabalho humano–IA está na versão de submissão em inglês.

**Contribuições do autor.** O autor concebeu o estudo, projetou o sistema, coletou a evidência documental, escreveu e revisou o manuscrito e aprovou a versão final.

**Agradecimentos.** O autor agradece às comunidades de código aberto cujas bibliotecas, modelos e ferramentas tornaram o Core possível. Agradece também aos revisores, cuja crítica aprimorará o argumento.

## Apêndice A — Indicadores do repositório

Contagens obtidas por inspeção direta do checkout em 10 de novembro de 2026; base Git `1ce6ae98`. Contagens de arquivos ou de configuração não medem qualidade, disponibilidade, autenticação, inferência ou validação externa. Arquivos não commitados podem alterar os totais.

| Indicador | Valor | Fonte | Limite de leitura |
|---|---:|---|---|
| Arquivos de especificação | 681 | `specs/SPEC-*.md` | Contagem de arquivos; não mede qualidade nem vigência |
| Arquivos de teste | 646 | `tests/test_*.py` | Contagem; não mede cobertura nem confiabilidade |
| Ciclos de evolução | 845 | `evolution/cycles.json` | Inclui entradas legadas; pontuações são autoavaliação |
| Agentes configurados | 374 | `opencode.json` | Configuração; não prova disponibilidade |
| Servidores MCP | 35 | `opencode.json` | Configuração; não prova autenticação |
| Comandos | 35 | `opencode.json` | Configuração |
| Verificações estruturais | 22 | `doctor.py` | Checks locais; não são certificação externa |
| Ciclo mais recente | R1131 | `evolution/cycles.json` | Registro local; sem hardware ou validação externa |

O bloco reconciliado do `README.md` registra 366 agentes e 35 MCPs. A diferença entre as contagens é documental e deve ser reconciliada antes de uma publicação.

## Apêndice B — Glossário de termos arquiteturais

- **MetaBus.** Barramento de eventos metacognitivos e camada de memória compartilhada. Armazena memória episódica e semântica, um livro de confiança e eventos que podem ser consultados antes de uma nova decisão.
- **Blackboard.** Quadro compartilhado no qual agentes se voluntariam para tarefas com base em Agent Cards, capacidades declaradas, confiança histórica e carga.
- **Agent Card.** Descrição das capacidades, do esquema de entrada e do status de um agente.
- **Trust Engine.** Componente que mantém pontuações históricas por ação, aplica um gate comportamental e registra resultados.
- **BehavioralGate.** Guarda de pré-execução que autoriza ou bloqueia uma ação com base em uma pontuação de confiança e um limiar.
- **TaskRuntime.** Runtime local e determinístico para grafos de tarefas nanogranulares, com estados, leases, orçamentos e recuperação.
- **SpecRegistry.** Registro de especificações formais com critérios de aceite.
- **SpecVerifier.** Componente que verifica se uma entrega satisfaz os critérios de aceite de uma especificação.
- **EvolutionRegistry.** Registro de ciclos de evolução com objetivo, mudanças, pontuação, lições, hashes e âncoras de estado.
- **Token Economy.** Camada de coordenação com stake, slashing e mercado de taxas. É um dispositivo de governança, não uma medida de verdade ou competência.

## Referências

As referências são mantidas na língua original; os títulos em português são preservados quando a obra é em português. Os DOIs foram conferidos na versão de submissão em inglês.

Adams, F., & Aizawa, K. (2001). The bounds of cognition. *Philosophical Psychology, 14*(1), 43–64. https://doi.org/10.1080/09515080120033571

Beck, K. (2002). *Test-driven development: By example*. Addison-Wesley.

Brasil. (1996). *Lei nº 9.394, de 20 de dezembro de 1996: Diretrizes e bases da educação nacional*. Presidência da República.

Brasil. (2008). *Política nacional de educação especial na perspectiva da educação inclusiva*. Ministério da Educação.

Bush, V. (1945). As we may think. *The Atlantic Monthly, 176*(1), 101–108.

Caliskan, A., Yamaguchi, F., Dauber, E., Harang, R., Rieck, K., Greenstadt, R., & Narayanan, A. (2018). When coding style survives compilation: De-anonymizing programmers from executable binaries. In *Proceedings of the Network and Distributed System Security Symposium (NDSS)*. https://doi.org/10.14722/ndss.2018.23304

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis, 58*(1), 7–19. https://doi.org/10.1093/analys/58.1.7

Core Project. (2026a). *Preface: The cognitive signature of an agentic ecosystem* [Design document]. In *the Core project*.

Core Project. (2026b). *The Core project* [Computer software]. GitHub. https://github.com/MarceloClaro/opencode-ecosystem-core

Core Project. (2026c). *AGENTS.md* [Project documentation]. In *the Core project*.

Core Project. (2026d). *MANUAL.md* [Project documentation]. In *the Core project*.

Core Project. (2026e). *CORRIGENDUM.md* [Project documentation]. In *the Core project*.

Core Project. (2026f). *Modules*: `mci/metabus.py`, `mci/blackboard.py`, `mci/task_runtime.py`, `mci/reflexion.py`, `mci/metacognitive_evaluator.py`, `mci/metacognitive_gate.py`, `sdd/spec_engine.py`, `sdd/tdd_runner.py`, `trust/trust_engine.py`, `economy/token_economy.py`, `evolution/cycles.py`, `orchestrator.py`, `doctor.py` [Source code]. In *the Core project*.

Engelbart, D. C. (1962). *Augmenting human intellect: A conceptual framework* (Summary Report AFOSR-3223). Stanford Research Institute.

Floridi, L. (2013). Distributed morality in an information society. *Science and Engineering Ethics, 19*(3), 727–743. https://doi.org/10.1007/s11948-012-9413-4

Floridi, L., & Sanders, J. W. (2004). On the morality of artificial agents. *Minds and Machines, 14*(3), 349–379. https://doi.org/10.1023/B:MIND.0000035461.63578.9d

Fricker, M. (2007). *Epistemic injustice: Power and the ethics of knowing*. Oxford University Press.

Gagné, F. (2004). Transforming gifts into talents: The DMGT as a developmental theory. *High Ability Studies, 15*(2), 119–147. https://doi.org/10.1080/1359813042000314682

Hardwig, J. (1985). Epistemic dependence. *The Journal of Philosophy, 82*(7), 335–349. https://doi.org/10.2307/2026523

Hollan, J., Hutchins, E., & Kirsh, D. (2000). Distributed cognition: Toward a new foundation for human-computer interaction research. *ACM Transactions on Computer-Human Interaction, 7*(2), 174–196. https://doi.org/10.1145/353485.353487

Hutchins, E. (1995). *Cognition in the wild*. MIT Press.

Insel, T., Cuthbert, B., Garvey, M., Heinssen, R., Pine, D. S., Quinn, K., Sanislow, C., & Wang, P. (2010). Research domain criteria (RDoC): Toward a new classification framework for research on mental disorders. *American Journal of Psychiatry, 167*(7), 748–751. https://doi.org/10.1176/appi.ajp.2010.09091379

Ioannidis, J. P. A. (2005). Why most published research findings are false. *PLoS Medicine, 2*(8), e124. https://doi.org/10.1371/journal.pmed.0020124

Jack, C. R., Bennett, D. A., Blennow, K., Carrillo, M. C., Dunn, B., Haeberlein, S. B., Holtzman, D. M., Jagust, W., Jessen, F., Karlawish, J., Liu, E., Molinuevo, J. L., Montine, T., Phelps, C., Rankin, K. P., Rowe, C. C., Scheltens, P., Siemers, E., Snyder, H. M., & Sperling, R. (2018). NIA-AA research framework: Toward a biological definition of Alzheimer's disease. *Alzheimer's & Dementia, 14*(4), 535–562. https://doi.org/10.1016/j.jalz.2018.02.018

Livingston, G., Huntley, J., Sommerlad, A., Ames, D., Ballard, C., Banerjee, S., Brayne, C., Burns, A., Cohen-Mansfield, J., Cooper, C., Costafreda, S. G., Dias, A., Fox, N., Gitlin, L. N., Howard, R., Kales, H. C., Kivimäki, M., Larson, E. B., Ogunniyi, A., … Mukadam, N. (2020). Dementia prevention, intervention, and care: 2020 report of the Lancet Commission. *The Lancet, 396*(10248), 413–446. https://doi.org/10.1016/S0140-6736(20)30367-6

MacCormack, A., Baldwin, C., & Rusnak, J. (2012). Exploring the duality between product and organizational architectures: A test of the mirroring hypothesis. *Research Policy, 41*(8), 1309–1324. https://doi.org/10.1016/j.respol.2012.04.011

Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology, 2*(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175

Nii, H. P. (1986). Blackboard systems: The blackboard model of problem solving and the evolution of blackboard architectures. *AI Magazine, 7*(2), 38–53.

Norman, D. A. (1991). Cognitive artifacts. In J. M. Carroll (Ed.), *Designing interaction: Psychology at the human-computer interface* (pp. 17–38). Cambridge University Press.

Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences, 115*(11), 2600–2606. https://doi.org/10.1073/pnas.1708274114

Poldrack, R. A. (2011). Inferring mental states from neuroimaging data: From reverse inference to large-scale decoding. *Neuron, 72*(5), 692–697. https://doi.org/10.1016/j.neuron.2011.11.001

Renzulli, J. S. (1978). What makes giftedness? Reexamining a definition. *Phi Delta Kappan, 60*(3), 180–184.

Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences, 20*(9), 676–688. https://doi.org/10.1016/j.tics.2016.07.002

Rupert, R. D. (2004). Challenges to the hypothesis of extended cognition. *Journal of Philosophy, 101*(8), 389–428. https://doi.org/10.5840/jphil2004101826

Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems (NeurIPS)*. arXiv:2303.11366

Sterelny, K. (2010). Minds: Extended or scaffolded? *Phenomenology and the Cognitive Sciences, 9*(4), 465–481. https://doi.org/10.1007/s11097-010-9174-y

Stern, Y. (2002). What is cognitive reserve? Theory and research application of the reserve concept. *Journal of the International Neuropsychological Society, 8*(3), 448–460. https://doi.org/10.1017/S1355617702813248

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science, 12*(2), 257–285. https://doi.org/10.1207/s15516709cog1202_4

Tronto, J. C. (1993). *Moral boundaries: A political argument for an ethic of care*. Routledge.

Verbeek, P.-P. (2006). Materializing morality: Design ethics and technological mediation. *Science, Technology, & Human Values, 31*(3), 361–380. https://doi.org/10.1177/0162243905285847

Wooldridge, M., & Jennings, N. R. (1995). Intelligent agents: Theory and practice. *The Knowledge Engineering Review, 10*(2), 115–152. https://doi.org/10.1017/S0269888900008122

Yarkoni, T. (2022). The generalizability crisis. *Behavioral and Brain Sciences, 45*, e1. https://doi.org/10.1017/S0140525X20001685

Yin, R. K. (2018). *Case study research and applications: Design and methods* (6th ed.). Sage.

---
