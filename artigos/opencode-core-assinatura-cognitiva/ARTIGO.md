# A casa que ajuda a pensar: prótese cognitiva, orquestração agêntica e assinatura autoral no OpenCode Ecosystem Core

**Subtítulo:** Estudo de caso de uma ferramenta construída por seu próprio usuário, em um contexto de altas habilidades/superdotação e risco de Alzheimer

**Autor:** Marcelo Claro Laranjeira — ORCID [0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)

**Colaboração:** orquestrador `marceloclaro` (DeepSeek V4.1 Flash, via OpenCode), a partir de leitura documental do repositório. Revisão humana independente pendente.

**Data:** 10 de novembro de 2026.

**Versão:** rascunho 1.0, para revisão.

---

> “Uma casa conserva decisões de quem a concebeu: a disposição das portas, o caminho entre os ambientes e os espaços reservados ao encontro. Isso não faz da planta um retrato completo da vida mental do arquiteto.”
>
> — LARANJEIRA (2026a), prefácio R909.

---

> **Nota de cuidado.** O relato de saúde que motiva este artigo é do próprio autor. A AH/SD não é doença; risco de Alzheimer não é diagnóstico; este texto não é aconselhamento médico. Nenhuma parte do sistema foi validada como intervenção neuroprotetora. O artigo descreve uma arquitetura e propõe um programa de avaliação; não demonstra eficácia clínica, cognitiva ou pedagógica.

---

## Resumo

Este artigo analisa o **OpenCode Ecosystem Core** como uma prótese cognitiva concebida por seu próprio usuário. A pergunta que orienta o texto é: o que acontece com a arquitetura de um sistema quando ele é projetado para compensar vulnerabilidades cognitivas específicas do criador — altas habilidades/superdotação (AH/SD) e risco de Alzheimer, ambos relatados pelo autor — e, ao mesmo tempo, para produzir evidência pública e contestável? A partir de análise documental do repositório (código, especificações, testes, registros de evolução e documentação), o artigo descreve o ciclo **Perceber → Especificar → Delegar → Executar → Verificar → Refletir** e mostra como ele externaliza memória, função executiva, atenção e verificação. Propõe o conceito de **prótese cognitiva autoral** e defende que a assinatura cognitiva do sistema é uma configuração situada de escolhas documentáveis, não um biomarcador ou um retrato mental. O artigo discute potencialidades e riscos — sobrecarga, dependência, viés de automação, burocratização do cuidado — e propõe um protocolo de avaliação N-of-1, pré-registrado e com supervisão clínica. Conclui que o Core pode ajudar seu criador a sustentar continuidade, memória e verificação, mas não previne, trata ou diagnostica Alzheimer; seu valor depende de preservar agência, vínculo social e contestabilidade.

**Palavras-chave:** prótese cognitiva; orquestração multiagente; altas habilidades/superdotação; risco de Alzheimer; assinatura cognitiva; SDD/TDD; evidência.

## Abstract

This article examines the **OpenCode Ecosystem Core** as a cognitive prosthesis designed by its own user. It asks what happens to a system's architecture when it is built to compensate for the creator's specific cognitive vulnerabilities — giftedness (high ability) and a self-reported risk of Alzheimer's disease — while also being designed to produce public, contestable evidence. Drawing on a documentary analysis of the repository (code, specifications, tests, evolution records and documentation), the article describes the cycle **Perceive → Specify → Delegate → Execute → Verify → Reflect** and shows how it externalizes memory, executive function, attention and verification. It proposes the concept of **authored cognitive prosthesis** and argues that the system's cognitive signature is a situated configuration of documentable choices, not a biomarker or a mental portrait. The article discusses potentials and risks — overload, dependency, automation bias, bureaucratization of care — and proposes a pre-registered N-of-1 evaluation protocol with clinical oversight. It concludes that the Core may help its creator sustain continuity, memory and verification, but it does not prevent, treat or diagnose Alzheimer's disease; its value depends on preserving agency, social ties and contestability.

**Keywords:** cognitive prosthesis; multi-agent orchestration; giftedness; Alzheimer's risk; cognitive signature; SDD/TDD; evidence.

---

## 1. Introdução: a ferramenta que nasce de uma falta

Quase todo software é escrito para um usuário genérico. Este artigo examina um caso inverso: um sistema construído por alguém que é, ao mesmo tempo, arquiteto, operador e usuário principal — e que o desenhou em resposta a uma vulnerabilidade que conhece de perto. O **OpenCode Ecosystem Core** não nasceu de uma demanda de mercado. Nasceu de uma necessidade de continuidade: manter o pensamento em movimento quando memória, atenção e energia não são garantidas.

A ferramenta é um monorepo de orquestração, pesquisa e produção de artefatos. Reúne agentes, servidores MCP, especificações formais, testes, registros de evolução, um livro, um pipeline científico e uma camada de memória metacognitiva. A sua regra de ouro é incomum: **nenhuma entrega sem spec, teste e evidência**. A pergunta central do projeto não é “quantos agentes existem?”, mas “o que foi executado, com qual fonte, qual hash e qual limite?” (OPENCODE ECOSYSTEM CORE, 2026a).

Este artigo parte de uma hipótese interpretativa: esse desenho não é apenas técnico. Ele carrega a marca de uma forma de pensar e de uma condição de vida. O criador relata altas habilidades/superdotação (AH/SD) e risco elevado de Alzheimer. A AH/SD associa-se, com frequência, a pensamento sistêmico, hiperfoco, padrões rápidos e exigência intelectual alta; também pode vir acompanhada de sobrecarga executiva, perfeccionismo e dificuldade de parar. O risco de Alzheimer, por sua vez, torna saliente a finitude da memória e a importância de deixar rastros. A arquitetura responde a esse duplo contexto com memória externalizada, contratos, verificação e retomada.

A tese deste artigo é esta: o Core é uma **prótese cognitiva autoral**. “Prótese” não no sentido médico de substituição de tecido, mas no sentido de uma estrutura externa que carrega parte da carga cognitiva e devolve ao usuário tempo, ordem e possibilidade de continuar. “Autoral” porque foi concebida por quem a usa e porque materializa escolhas documentáveis de seu criador. A assinatura cognitiva, aqui, não é um biomarcador, um teste de personalidade ou uma prova de consciência artificial. É uma **configuração situada de escolhas** — perguntas consideradas importantes, formas de decompor problemas, critérios de aceite, regras de memória e limites declarados (LARANJEIRA, 2026a).

O artigo tem quatro contribuições. Primeiro, propõe uma definição operacional de prótese cognitiva autoral, distinta de metáforas totalizantes como “segundo cérebro”. Segundo, descreve a arquitetura do Core e mostra como cada mecanismo responde a uma função cognitiva. Terceiro, examina os riscos dessa forma de assistência — dependência, sobrecarga, viés de automação, burocratização do cuidado. Quarto, propõe um protocolo de avaliação N-of-1, pré-registrado e com supervisão clínica, para que a hipótese de benefício possa ser testada em vez de presumida.

O método é documental e interpretativo. Não houve avaliação clínica, neuropsicológica ou experimental do autor. A análise se apoia no código, nas especificações, nos testes, nos registros de evolução e na documentação do repositório, além de literatura sobre cognição estendida, carga cognitiva, AH/SD e reserva cognitiva. O artigo distingue, ao longo do texto, **observação** (o que o repositório contém), **interpretação** (o que essas escolhas sugerem) e **prescrição** (o que se propõe avaliar). Essa distinção é o que separa uma análise crítica de uma peça de autopromoção.

O percurso é o seguinte. A seção 2 apresenta o caso e o método, com as contagens e os limites. A seção 3 discute AH/SD e risco de Alzheimer como condições de projeto, não como diagnósticos. A seção 4 revisa a literatura sobre cognição estendida, artefatos, carga cognitiva e reserva. A seção 5 descreve a arquitetura do Core. A seção 6 propõe a leitura da assinatura cognitiva. A seção 7 distingue o que a prótese faz do que ela não faz. A seção 8 examina riscos e salvaguardas. A seção 9 apresenta o protocolo de avaliação. A seção 10 discute a casa, o arquiteto e o tempo. A seção 11 conclui.

## 2. O caso e o método

### 2.1 O objeto

O OpenCode Ecosystem Core é um monorepo público, mantido por Marcelo Claro Laranjeira, que se descreve como “pesquisa, agentes e evidência em um único core auditável”. A configuração local do checkout analisado em 10 de novembro de 2026 (commit `1ce6ae98`) registra 35 servidores MCP, 35 comandos e 374 entradas de agente no `opencode.json`. O bloco reconciliado do `README.md` registra 366 agentes; a divergência entre contagens é um lembrete de que inventário não é retrato único e de que a documentação também tem história.

A tabela 1 resume os indicadores usados neste artigo. Todos são contagens de arquivos ou de configuração. Nenhum deles mede qualidade, disponibilidade, autenticação, inferência ou validação externa.

**Tabela 1 — Indicadores do checkout analisado (10/11/2026)**

| Indicador | Valor | Fonte | Limite de leitura |
|---|---:|---|---|
| Arquivos de especificação | 681 | `specs/SPEC-*.md` | Contagem de arquivos; não mede qualidade nem vigência |
| Arquivos de teste | 646 | `tests/test_*.py` | Contagem; não mede cobertura nem confiabilidade |
| Ciclos registrados | 845 | `evolution/cycles.json` | Inclui entradas legadas; o score é autoavaliação |
| Agentes configurados | 374 | `opencode.json` | Configuração; não prova disponibilidade |
| Servidores MCP | 35 | `opencode.json` | Configuração; não prova autenticação |
| Comandos | 35 | `opencode.json` | Configuração |
| Verificações estruturais | 22 | `marceloclaro/doctor.py` | Checks locais; não são certificação externa |
| Ciclo mais recente | R1131 | `evolution/cycles.json` | Registro local, sem hardware ou validação externa |

Fonte: elaboração própria a partir do repositório (OPENCODE ECOSYSTEM CORE, 2026g). As contagens foram obtidas por inspeção direta do checkout de 10/11/2026; a base Git é `1ce6ae98`, e arquivos não commitados podem alterar os totais. O `README.md` adverte que “contagens de configuração e checks não comprovam disponibilidade, autenticação, inferência ou validação externa” (OPENCODE ECOSYSTEM CORE, 2026a).

### 2.2 Método

O artigo adota o estudo de caso instrumental (YIN, 2018): o Core interessa menos por si do que pelo fenômeno que ilumina — a construção de uma prótese cognitiva por seu próprio usuário. O corpus inclui:

- documentos de arquitetura e operação (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md`, `CORRIGENDUM.md`);
- o prefácio R909 sobre assinatura cognitiva e sua especificação;
- módulos de memória, orquestração, verificação, confiança, economia e evolução;
- registros de ciclos e contagens de specs e testes;
- literatura externa sobre cognição, aprendizagem, AH/SD e demência.

A análise é documental, não experimental. Não houve execução do sistema para medir desempenho, aplicação de testes cognitivos no autor ou acesso a prontuário, biomarcadores ou avaliação neuropsicológica. As afirmações sobre o código são verificáveis nos arquivos citados. As afirmações sobre a cognição do autor são interpretações baseadas em seu relato e em sua produção textual, não diagnósticos.

### 2.3 Posição e viés

O criador é também o usuário principal do sistema. Isso produz uma vantagem — acesso ao processo de projeto — e um risco: o viés de confirmação, a tendência a procurar e interpretar informação de modo a sustentar crenças prévias (NICKERSON, 1998). O próprio Core incorpora uma resposta a esse risco: o `CORRIGENDUM.md`, documento público de autocorreção de alegações; o gate metacognitivo, que não retorna “verificado” sem validação externa explícita; e a exigência de spec, teste e recibo. Esses mecanismos não eliminam o viés. Eles o tornam visível e contestável — que é o máximo que uma arquitetura pode prometer.

O artigo foi elaborado com auxílio do orquestrador `marceloclaro` (DeepSeek V4.1 Flash) a partir de leitura documental. A seleção de fontes, a redação e as interpretações são de responsabilidade do autor humano. Não houve revisão independente, revisão por pares ou validação externa. O texto é um rascunho para crítica, não um resultado certificado.

### 2.4 Limites

Os limites são explícitos:

1. **Caso único.** Não é possível generalizar para outras pessoas com AH/SD, outros criadores ou outras formas de risco neurocognitivo.
2. **Ausência de dados clínicos.** O risco de Alzheimer é relatado, não diagnosticado; não há biomarcadores, neuroimagem ou avaliação longitudinal.
3. **Contagens que envelhecem.** Specs, testes e ciclos mudam a cada commit. Os números valem para o checkout datado.
4. **Autoavaliação.** Os scores dos ciclos são atribuídos pelo próprio processo; não são benchmark externo (OPENCODE ECOSYSTEM CORE, 2026e).
5. **Ausência de teste de eficácia.** Nenhum desfecho cognitivo, funcional ou clínico foi medido.
6. **Metáfora não é mecanismo.** Chamar módulos de “memória”, “atenção” ou “metacognição” não os torna medidas da mente humana (POLDRACK, 2011). A fronteira entre descrição e diagnóstico exige cautela; o RDoC, por exemplo, é um quadro de pesquisa, não um instrumento clínico (INSEL et al., 2010).

## 3. O usuário-criador: alta capacidade, assincronia e risco

### 3.1 Altas habilidades/superdotação não é doença

Altas habilidades/superdotação (AH/SD) designa um perfil de potencial elevado, com manifestações heterogêneas em áreas específicas, combinado a criatividade e envolvimento com a tarefa (RENZULLI, 1978). Modelos desenvolvimentais acrescentam que o talento se constrói ao longo do tempo, em condições de aprendizagem, apoio e reconhecimento (GAGNÉ, 2004). No Brasil, a legislação educacional reconhece a AH/SD como categoria atendida pela educação especial (BRASIL, 1996; BRASIL, 2008), o que não resolve o problema da identificação, mas confirma que se trata de uma questão educacional e de desenvolvimento, não de uma patologia.

A expressão “sofre de superdotação”, usada no relato que originou este artigo, não corresponde a uma categoria nosológica. Ela captura algo real: o sofrimento que pode acompanhar a assincronia entre capacidade e ambiente — a distância entre o que a pessoa consegue pensar e o que o contexto lhe permite realizar. Esse sofrimento não é a superdotação em si; é o desencontro. O artigo preserva o relato e adota a formulação tecnicamente mais precisa: o autor **relata AH/SD**.

A literatura sobre AH/SD alerta contra dois reducionismos. O primeiro é o do QI único: reduzir a superdotação a uma medida de inteligência deixa de fora criatividade, motivação, áreas específicas e trajetória. O segundo é o do rótulo: tratar a identificação como destino, e não como ponto de partida para apoio. A heterogeneidade é a regra. Duas pessoas com AH/SD podem ter perfis cognitivos, emocionais e sociais muito diferentes. A produção recente do autor sobre dupla excepcionalidade (LARANJEIRA, 2026b) mostra que a identificação de AH/SD no Brasil é desigual e frequentemente unilateral, o que reforça a cautela deste artigo.

### 3.2 Forças e custos

No relato do autor, o perfil associa-se a pensamento sistêmico, reconhecimento rápido de padrões, hiperfoco e exigência alta. Essas características são recursos: permitem atravessar domínios, construir arquiteturas complexas e sustentar projetos longos. Também têm custos. O hiperfoco pode apagar a percepção do tempo e das necessidades básicas. A exigência alta pode transformar cada entrega em dívida. A rapidez associativa pode produzir uma sensação de evidência que os dados ainda não sustentam. A sensibilidade a inconsistências pode dificultar a convivência com sistemas imperfeitos — inclusive com o próprio corpo.

Esses custos não são universais nem diagnósticos. São hipóteses de trabalho, úteis porque explicam por que certas escolhas arquiteturais aparecem no Core: orçamentos, timeouts, checkpoints, especificações, testes, recibos. O sistema foi desenhado como se a atenção pudesse falhar, a memória pudesse se perder e a convicção pudesse enganar. Essa é uma forma de humildade operacional.

### 3.3 Risco de Alzheimer: risco não é diagnóstico

O autor relata risco elevado de Alzheimer. É importante distinguir três planos. A **doença de Alzheimer** é, na pesquisa contemporânea, definida por um continuum biológico, com marcadores que podem preceder décadas de sintomas (JACK et al., 2018). A **demência** é uma síndrome clínica, com impacto funcional. O **risco** é uma estimativa probabilística, que combina genética, fatores vasculares e metabólicos, escolaridade, atividade física, audição, vida social, depressão e outros fatores (LIVINGSTON et al., 2020). Risco não é destino; diagnóstico não é prognóstico; prognóstico não é sentença.

A noção de **reserva cognitiva** ajuda a pensar o problema sem prometer milagres. A hipótese é que experiências de vida — educação, trabalho intelectual, engajamento social, atividades complexas — podem permitir que uma pessoa lide melhor com a patologia antes que os sintomas se tornem incapacitantes (STERN, 2002). Isso não significa que uma atividade específica previna a doença. A literatura é observacional, heterogênea e sujeita a causalidade reversa: quem tem mais reserva pode ser justamente quem teve mais oportunidades, saúde e recursos ao longo da vida.

Nenhum software foi validado como intervenção neuroprotetora. Um sistema como o Core pode, no máximo, reduzir demandas ambientais, apoiar rotinas, externalizar memória e preservar continuidade. Esses efeitos são plausíveis, mas precisam ser medidos. O artigo os trata como hipóteses de pesquisa, não como resultados.

### 3.4 A dupla vulnerabilidade como coação de projeto

O que interessa a este artigo não é especular sobre uma relação causal entre AH/SD e Alzheimer — não há base para isso —, mas entender a **coação de projeto** que surge quando alguém com alta demanda cognitiva e medo de perda constrói um sistema para não se perder. A tabela 2 resume essa tradução.

**Tabela 2 — Da vulnerabilidade relatada à hipótese arquitetural**

| Vulnerabilidade relatada | Hipótese de projeto | Mecanismo no Core | Limite |
|---|---|---|---|
| Esquecimento de contexto entre sessões | Memória externalizada e recuperável | MetaBus, `shared_memory.json`, confidence ledger | Memória seletiva; não é backup total |
| Dificuldade de iniciar e sequenciar tarefas longas | Contratos e decomposição | Specs, critérios de aceite, DAGs, leases | Exige intenção humana |
| Risco de confundir convicção com evidência | Verificação independente | TDD, SpecVerifier, gate anti-overclaim | Teste não é verdade científica |
| Hiperfoco e dificuldade de parar | Orçamentos e limites | Timeouts, stop rules, doctor, helpdesk | O sistema não controla o usuário |
| Medo de perder continuidade | Estado durável e retomada | TaskRuntime, checkpoints, EvolutionRegistry | Não preserva a pessoa; preserva traços |
| Necessidade de sentido e legado | Documentação e ensino | Livro, manual, MIRA, pipeline didático | Não mede eficácia pedagógica |

Fonte: elaboração própria. As linhas são hipóteses interpretativas, não relações causais demonstradas.

A tabela não diz que o sistema “resolve” essas vulnerabilidades. Diz que ele foi desenhado **como se** elas existissem. Essa distinção é decisiva: uma arquitetura pode ser epistemicamente útil sem ser terapeuticamente eficaz.

## 4. De andaimes a próteses: o que significa externalizar a cognição

### 4.1 A mente estendida e seus críticos

Clark e Chalmers (1998) propuseram que processos cognitivos podem se estender para além do crânio. O exemplo clássico é o caderno de Otto, que funciona como uma memória externa confiável e acessível. O “princípio de paridade” sugere que, se um processo externo desempenha a mesma função que um processo interno, ele merece o mesmo status cognitivo. A tese é filosófica, não clínica: ela desloca a unidade de análise do cérebro para o sistema pessoa-ambiente.

A tese tem críticos. Rupert (2004) argumenta que a cognição estendida não explica adequadamente a integração e a persistência dos processos internos. Sterelny (2010) propõe uma alternativa mais modesta: a mente é **andaimeada** por estruturas externas, mas nem todo andaime se torna parte do sistema cognitivo. Essa distinção é útil para este artigo. O Core não é apresentado como parte literal da mente do autor. É um **andaime robusto**, uma estrutura que carrega parte da carga e altera a forma como a tarefa é realizada.

### 4.2 Artefatos cognitivos

Norman (1991) mostrou que artefatos cognitivos não apenas armazenam informação: eles transformam a tarefa. Uma lista de verificação não é um lembrete passivo; ela reorganiza a sequência, reduz a dependência da memória de trabalho e torna o erro mais visível. O mesmo vale para uma especificação, um teste automatizado ou um recibo com hash. Esses artefatos não “pensam” pelo usuário; eles mudam a economia da atenção.

No Core, as specs, os critérios de aceite e os recibos são artefatos cognitivos de segunda ordem: não apenas representam o que deve ser feito, mas definem **quando** algo pode ser considerado feito. Eles externalizam uma função executiva — a de manter o critério estável ao longo do tempo — e reduzem a chance de que o entusiasmo ou o cansaço redefinam o sucesso no meio do caminho.

### 4.3 Carga cognitiva e descarga

A teoria da carga cognitiva (SWELLER, 1988) explica por que a mente tem limites: a memória de trabalho processa poucos elementos novos ao mesmo tempo, e a sobrecarga prejudica a aprendizagem. A descarga cognitiva — usar o ambiente para reduzir a demanda interna — é uma resposta adaptativa (RISKO; GILBERT, 2016). Mas a descarga tem custos. Se o usuário terceiriza a lembrança, pode lembrar menos; se terceiriza o cálculo, pode calcular menos; se terceiriza a verificação, pode confiar mais do que deveria.

O Core é, em grande parte, uma máquina de descarga cognitiva. Ele guarda o contexto, a spec, o teste, o resultado e a lição. Isso libera memória de trabalho para o que o sistema não pode fazer: escolher o problema, julgar o que importa, decidir quando parar. A questão não é se a descarga é boa ou ruim em abstrato; é se ela preserva as funções que o usuário quer manter exercitadas e se ela não transfere para o sistema decisões que exigem julgamento humano.

### 4.4 Cognição distribuída

Hutchins (1995) mostrou que a cognição de uma cabine de avião não está apenas na cabeça dos pilotos: está distribuída entre pessoas, instrumentos, procedimentos e representações. Hollan, Hutchins e Kirsh (2000) estenderam essa abordagem para a interação humano-computador. A unidade de análise é o sistema coordenado, não o indivíduo isolado.

O Core é um sistema distribuído de cognição: o autor, os agentes, os MCPs, as specs, os testes e os registros formam uma rede que produz decisões. Mas há uma assimetria ética: apenas o autor responde pelo que o sistema faz. A distribuição da cognição não distribui a responsabilidade. Essa assimetria é o fundamento da seção 7.

### 4.5 Reserva cognitiva: hipótese, não promessa

A reserva cognitiva é uma das hipóteses mais citadas e mais mal compreendidas. Ela sugere que a relação entre patologia e sintoma não é fixa: pessoas com mais recursos cognitivos podem tolerar mais patologia antes de manifestar sintomas (STERN, 2002). A implicação prática costuma ser simplificada como “use ou perca”. A literatura é mais cautelosa. Atividade intelectual, vida social, exercício físico, controle de fatores vasculares e educação aparecem associados a menor risco de demência em estudos observacionais (LIVINGSTON et al., 2020), mas os tamanhos de efeito variam, as populações são heterogêneas e a causalidade é difícil de estabelecer.

Para este artigo, a reserva cognitiva é relevante por duas razões. Primeiro, ela oferece uma linguagem para pensar o valor de um ambiente cognitivamente rico — sem transformar essa linguagem em promessa. Segundo, ela impõe um limite: se o Core ajuda o autor a manter engajamento, rotina e vínculo, ele pode contribuir para o que a literatura chama de reserva; mas isso precisa ser testado, não presumido.

### 4.6 Definição: prótese cognitiva autoral

Com base nessas tradições, o artigo define **prótese cognitiva autoral** como:

> um sistema técnico-artefactual, concebido por seu próprio usuário, que externaliza funções mnemônicas, executivas e epistêmicas, e que materializa um estilo de decisão; sua avaliação depende da capacidade de preservar a agência do usuário, e não da capacidade de substituí-lo.

A definição tem três consequências. Primeiro, ela é funcional, não médica: uma prótese cognitiva não precisa ser implantada nem prescrita para ser útil. Segundo, ela é autoral: o sistema carrega escolhas de quem o construiu, e essas escolhas podem ser examinadas. Terceiro, ela é normativa: o critério de sucesso não é “fazer mais rápido”, mas “preservar a possibilidade de o usuário continuar sendo o autor de suas decisões”.

## 5. A arquitetura do Core: o ciclo em seis movimentos

### 5.1 Visão geral

O Core organiza a operação em um ciclo de seis movimentos:

```text
Perceber → Especificar → Delegar → Executar → Verificar → Refletir
```

O ciclo não é uma sequência rígida; é uma gramática de governança (OPENCODE ECOSYSTEM CORE, 2026b, 2026c). Cada movimento tem mecanismos, artefatos e limites. A tabela 3 resume a tradução entre função cognitiva e arquitetura.

**Tabela 3 — Funções cognitivas e mecanismos do Core**

| Movimento | Função externalizada | Mecanismo | Evidência | Limite |
|---|---|---|---|---|
| Perceber | Contexto e memória | MetaBus, memória compartilhada, confidence ledger | `mci/metabus.py` | Memória seletiva; últimos 1000 eventos |
| Especificar | Intenção e critério | SpecRegistry, SpecVerifier, critérios de aceite | `sdd/spec_engine.py`, `specs/` | Spec não garante execução |
| Delegar | Divisão do trabalho e atenção | Blackboard A2A, Agent Cards, Trust Engine | `mci/blackboard.py`, `trust/` | Agentes não são pessoas |
| Executar | Sequenciamento e persistência | TaskRuntime, DAG, leases, orçamento | `mci/task_runtime.py` | Não decide o que importa |
| Verificar | Teste de realidade | TDD, SpecVerifier, BehavioralGate, anti-overclaim | `sdd/tdd_runner.py`, `mci/metacognitive_gate.py` | Teste não é verdade científica |
| Refletir | Consolidação e aprendizagem | Reflexion, EvolutionRegistry, lições | `mci/reflexion.py`, `evolution/cycles.py` | Autoavaliação não é validação externa |

Fonte: elaboração própria a partir de `marceloclaro/orchestrator.py` e dos módulos citados (OPENCODE ECOSYSTEM CORE, 2026f).

### 5.2 Perceber: a memória como espaço de trabalho

O MetaBus é descrito como um “barramento de eventos metacognitivos unificado” e uma “memória compartilhada” entre agentes. Ele mantém memória episódica, memória semântica e um **confidence ledger** — um registro de confiança por agente ou tópico. A inspiração declarada é a Global Workspace Theory, o framework Reflexion e a memória colaborativa em sistemas multiagente (OPENCODE ECOSYSTEM CORE, 2026f).

Na prática, o MetaBus faz três coisas. Primeiro, publica eventos: pedidos de tarefa, conclusões, reflexões, falhas. Segundo, permite que agentes se inscrevam em eventos. Terceiro, persiste um estado que pode ser consultado antes de uma nova decisão. A memória é seletiva: o código mantém os últimos 1000 eventos episódicos. Isso é uma escolha de projeto, não um detalhe. Um sistema que tentasse lembrar tudo teria custo, ruído e risco de contaminação. A seletividade é uma forma de esquecimento produtivo.

A função cognitiva externalizada é o **contexto**. O autor não precisa reconstruir de memória o que já foi decidido, testado ou descartado. Mas o MetaBus não é um backup da mente. Ele registra traces, não vive a experiência. A diferença é importante: um trace pode ser consultado; uma experiência precisa ser interpretada.

### 5.3 Especificar: o contrato antes do impulso

O SpecRegistry carrega especificações formais; o SpecVerifier verifica critérios de aceite; o TDDRunner produz evidência de teste. A regra é explícita: nenhuma entrega sem spec, teste e evidência. A prática de escrever o teste antes da implementação é a base do TDD (BECK, 2002). No checkout analisado, há 681 arquivos de spec no padrão `SPEC-*.md`. A spec não é um documento burocrático: é o lugar onde a intenção se torna critério.

A função cognitiva externalizada é a **função executiva**: manter o objetivo estável, decompor em passos, definir o que conta como feito. Para alguém com hiperfoco, a spec funciona como um trilho. Para alguém com risco de sobrecarga, ela funciona como um limitador: não é preciso decidir tudo de novo a cada sessão. Para alguém com tendência a confundir convicção e evidência, ela funciona como um contrato contra a própria volatilidade.

O limite é claro: uma spec pode se tornar um fim em si mesma. O Core tem 681 specs; isso é uma riqueza e um risco. A riqueza está na rastreabilidade; o risco está na burocratização. Um sistema que exige uma spec para cada gesto pode paralisar o gesto. A seção 8 volta a esse ponto.

### 5.4 Delegar: o Blackboard e a economia da confiança

O Blackboard implementa um quadro compartilhado no qual agentes se voluntariam para tarefas com base em **Agent Cards** — descrições de capacidades, esquema de entrada e status. O padrão blackboard é clássico em sistemas de IA (NII, 1986), e a noção de agente como sistema autônomo que percebe e age em um ambiente vem da literatura de agentes (WOOLDRIDGE; JENNINGS, 1995). A seleção pondera capacidades declaradas, confiança histórica e carga. O Trust Engine mantém scores por ação, aplica um gate comportamental e registra resultados. A Token Economy adiciona stake, slashing e um mercado de taxas (OPENCODE ECOSYSTEM CORE, 2026f).

A função cognitiva externalizada é a **divisão do trabalho**. O autor não precisa executar tudo; ele publica uma tarefa, recebe voluntários e escolhe. A metáfora é de mercado, mas o mecanismo é de governança: a confiança é histórica, a carga é um limite e o stake é um compromisso. Um agente com histórico ruim perde prioridade; um agente sobrecarregado é preterido; um agente que falha pode sofrer slashing.

Há dois riscos. O primeiro é o **falso objetivismo**: um score de confiança não é uma medida de verdade. Um agente pode ter alto trust e produzir uma resposta errada com confiança. O segundo é o **falso mérito**: o stake mede compromisso, não competência. A economia de tokens é um dispositivo de coordenação, não uma epistemologia. O artigo insiste nessa distinção porque a arquitetura, por si só, não a garante.

### 5.5 Executar: a arquitetura da interrupção

O TaskRuntime implementa grafos de tarefas nanogranulares, com estados, leases, orçamentos e recuperação. A inspiração é um runtime local e determinístico, sem depender de rede ou de serviços globais. O detalhe importante para este artigo é que o runtime **assume a interrupção**. Ele foi desenhado para que uma tarefa possa ser retomada, não para que o usuário nunca pare.

A função cognitiva externalizada é o **sequenciamento e a persistência**. O sistema mantém o estado, concede leases, expira tentativas e registra resultados. O autor pode sair, voltar e continuar. Para uma pessoa com risco de fadiga ou perda de contexto, isso é mais do que conveniência: é uma forma de preservar a continuidade do trabalho sem exigir que o corpo e a atenção sejam constantes.

O limite é que o runtime não decide o que importa. Ele pode executar muito bem uma tarefa que não deveria ser feita. A priorização continua humana. A arquitetura da interrupção não substitui a arquitetura do desejo.

### 5.6 Verificar: o teste de realidade

A verificação é o coração epistêmico do Core. O TDDRunner produz evidência de teste; o SpecVerifier confere critérios; o BehavioralGate autoriza ou bloqueia ações com base em confiança; o gate metacognitivo classifica o grau de uma alegação e **não retorna “verificado” sem validação externa explícita**. O `CORRIGENDUM.md` registra alegações que soaram mais fortes do que a evidência disponível e propõe a leitura correta.

A função cognitiva externalizada é o **teste de realidade**. O sistema não impede o autor de acreditar em algo; ele torna mais difícil declarar que algo foi provado quando não foi. Para alguém com alta capacidade de construir narrativas coerentes, esse é um contrapeso necessário. A coerência interna de uma explicação não é prova de sua verdade; um teste que passa não é prova de que o teste mede o que deveria medir; um score alto não é prova de mérito.

O limite é o mesmo de qualquer sistema de verificação: ele só verifica o que foi especificado. Um teste pode confirmar uma hipótese errada, uma spec pode formalizar um critério inadequado, um gate pode bloquear uma ação correta. A verificação é uma prática, não uma máquina de certeza. A literatura sobre reprodutibilidade mostra que resultados aparentes podem não se sustentar (IOANNIDIS, 2005).

### 5.7 Refletir: a consolidação e o registro

O ReflexionEngine, inspirado em Shinn et al. (2023), gera reflexões pós-tarefa e as publica no MetaBus; o EvolutionRegistry registra ciclos com objetivo, mudanças, score, lições, hashes e âncoras de estado. O `cycles.json` analisado tem 845 entradas. A função cognitiva externalizada é a **consolidação**: transformar uma execução em lição, e uma lição em memória que pode ser recuperada.

A reflexão tem dois efeitos. O primeiro é técnico: o sistema aprende com falhas e ajusta rotas. O segundo é existencial: o autor deixa um rastro de seu percurso. Em um contexto de risco de perda de memória, esse rastro tem valor próprio. Ele não preserva a pessoa, mas preserva decisões, justificativas e aprendizados. É uma forma de continuidade indireta.

O limite é que a autoavaliação não é validação externa. Os scores dos ciclos são atribuídos pelo próprio processo; o `CORRIGENDUM.md` reconhece que a média de 9,4/10 não é benchmark. A reflexão pode se tornar autojustificação se não houver contraprova. O Core tem mecanismos de contraprova — testes, revisão adversarial, gate externo —, mas eles não eliminam o risco.

### 5.8 A camada humana: orientação e ensino

Além do núcleo de orquestração, o Core inclui uma camada de orientação e ensino: o `doctor` (diagnóstico), o `helpdesk` (ajuda guiada), o manual (OPENCODE ECOSYSTEM CORE, 2026d), o livro, o pipeline MIRA de apresentações e o Book Studio. Essa camada dialoga com princípios de desenho multimídia (MAYER; MORENO, 2003), sem que isso prove eficácia pedagógica; a aproximação com a neurociência exige cautela contra neuromitos (HOWARD-JONES, 2014). Essa camada não é acessória. Ela externaliza a **orientação** — a capacidade de saber onde se está e o que fazer a seguir — e a **vocação didática** — a vontade de transformar o próprio percurso em material para outros.

Para o autor, essa camada tem um duplo valor. Ela o ajuda a se orientar quando o contexto se dispersa; e ela transforma o conhecimento construído em legado. Para o leitor, ela é uma porta de entrada. Para o crítico, ela é um risco: documentação em excesso pode criar a ilusão de que o sistema é mais compreendido do que é. A seção 8 retoma esse ponto.

## 6. A assinatura cognitiva: cinco marcas documentáveis

### 6.1 O que é — e o que não é

O prefácio R909 define **assinatura cognitiva autoral** como “essa configuração situada de escolhas documentáveis”. A definição é deliberadamente modesta. Ela não afirma que o código revela a mente do autor; afirma que o código conserva marcas de suas perguntas, critérios, representações e decisões. A versão forte — todo ecossistema revelaria, de maneira única e recuperável, a cognição de um único criador — ultrapassa a evidência disponível (LARANJEIRA, 2026a). A atribuição estilística a partir de artefatos técnicos tem limites; ela pode conservar regularidades, mas não mede personalidade ou cognição (CALISKAN et al., 2018).

Essa modéstia é necessária por três razões. Primeiro, porque a autoria é composta: o Core usa bibliotecas, modelos, dados, práticas herdadas e contribuições de agentes. Segundo, porque a relação entre código e cognição não é transparente: um mesmo estilo pode ser produzido por motivações diferentes. Terceiro, porque a interpretação pode se tornar mitologia: o autor pode confundir a própria narrativa com uma prova.

### 6.2 As cinco marcas

Ainda assim, cinco marcas são documentáveis. Elas não esgotam a assinatura; são um recorte interpretativo.

**1. A memória tratada como frágil.** O sistema é construído como se a memória pudesse falhar. Há memória compartilhada, confidence ledger, specs, recibos, hashes, âncoras de estado. Essa escolha não é apenas técnica: é uma postura existencial. O autor não confia na lembrança; confia no registro. A frase “o que foi executado, com qual fonte, qual hash e qual limite?” é uma resposta à possibilidade de esquecimento.

**2. O contrato antes do impulso.** A regra “nenhuma entrega sem spec” subordina a inspiração a uma forma. Para um criador com alta fluência e hiperfoco, isso é contraintuitivo: a vontade de fazer vem antes do contrato. A arquitetura inverte a ordem. O contrato não nega o impulso; ele o protege de si mesmo, impedindo que o entusiasmo redefina o critério de sucesso no meio do caminho.

**3. A verificação contra a própria convicção.** O gate anti-overclaim, o `CORRIGENDUM.md` e a exigência de validação externa são uma resposta à tendência de confundir coerência com verdade. Essa é talvez a marca mais distintiva do Core. Não se trata de desconfiar dos outros; trata-se de desconfiar da própria capacidade de construir uma narrativa convincente. A arquitetura transforma essa desconfiança em procedimento.

**4. A arquitetura da interrupção.** O runtime assume que a tarefa pode ser interrompida; o MetaBus assume que o contexto pode se perder; o `doctor` assume que o ambiente pode estar quebrado. O sistema é feito para retomar, não para exigir presença contínua. Essa marca é especialmente significativa em um contexto de risco neurocognitivo: a arquitetura não promete memória perfeita, mas promete um caminho de volta.

**5. A vocação didática.** O livro, o manual, o MIRA, os explicadores e a preocupação com a “democratização do conhecimento” mostram que a assinatura não está apenas no código. Está na vontade de ensinar o que foi aprendido. Essa marca tem uma dimensão ética: o conhecimento não é tratado como propriedade, mas como algo que deve ser tornado acessível — com limites, fontes e avisos.

### 6.3 A assinatura é composta

A hipótese da “mirroring” entre organização e arquitetura sugere que a modularidade de um sistema pode refletir a forma de coordenação de quem o produz (MACCORMACK; BALDWIN; RUSNAK, 2012). A cognição distribuída sugere que a unidade relevante é o sistema pessoa-instrumento-procedimento, não o indivíduo isolado (HUTCHINS, 1995). Ambas as tradições convergem para uma leitura composta: a assinatura do Core não é um retrato do autor, mas o resultado de uma interação entre autor, ferramentas, modelos, comunidade e história.

Isso não dissolve a autoria. O autor escolheu as perguntas, os critérios, as prioridades e os limites. Ele também escolheu usar agentes e modelos, e escolheu registrar essa escolha. A assinatura está menos nos detalhes do código do que na **forma de responder à incerteza**: documentar, testar, corrigir, pedir revisão. É uma assinatura de responsabilidade. A mediação tecnológica materializa valores e escolhas, mas não garante que eles sejam virtuosos (VERBEEK, 2006).

### 6.4 O risco de mito

Toda interpretação de autoria corre o risco de se tornar mito. O mito tem três formas. A primeira é a **celebração**: transformar a arquitetura em prova de genialidade. A segunda é a **justificação**: usar a assinatura para explicar ou desculpar falhas. A terceira é a **prisão**: acreditar que o autor só pode criar de uma maneira, e que a assinatura é um destino.

O artigo recusa as três. A assinatura é uma hipótese interpretativa, não uma essência. A generalização de um caso único exige cautela (YARKONI, 2022). Ela pode ser contestada por contraexemplos: escolhas que contrariam o padrão, contribuições que vêm de outros, momentos em que o sistema falha. A própria existência do `CORRIGENDUM.md` é uma contraprova à tentação de celebrar. Um sistema que se corrige publicamente não é um monumento; é uma obra em andamento.

## 7. O que a prótese faz — e o que ela não faz

### 7.1 O que ela faz

O Core pode ajudar o autor de várias maneiras concretas:

- **Reduz o custo de troca.** O contexto fica registrado; o autor não precisa reconstruí-lo a cada sessão.
- **Externaliza a função executiva.** Specs, critérios e DAGs transformam intenção em sequência.
- **Amplia a capacidade de verificação.** Testes, gates e recibos tornam o erro mais visível.
- **Preserva a continuidade.** O estado durável permite retomar depois de uma interrupção.
- **Distribui o trabalho.** Agentes e MCPs assumem tarefas repetitivas ou especializadas.
- **Documenta o percurso.** O registro de ciclos e lições cria uma memória indireta.
- **Apoia o ensino.** O livro, o manual e o MIRA transformam o percurso em material para outros.
- **Cria um espaço de contestação.** O `CORRIGENDUM.md` e o gate anti-overclaim tornam o sistema aberto à crítica.

Esses benefícios são plausíveis, mas não medidos. A seção 9 propõe como medi-los.

### 7.2 O que ela não faz

O Core **não** previne Alzheimer. **Não** trata demência. **Não** diagnostica. **Não** substitui sono, exercício, alimentação, vida social, acompanhamento médico ou psicológico. **Não** garante decisões corretas. **Não** elimina vieses. **Não** preserva a pessoa; preserva traços. **Não** torna o autor imortal.

Essa lista pode parecer óbvia, mas é necessária. A linguagem de “segundo cérebro”, “memória aumentada” e “agente pessoal” pode facilmente deslizar para a promessa de que o sistema compensa o que a biologia não compensa. A arquitetura do Core, com sua ênfase em evidência e limites, oferece recursos para resistir a essa tentação. Mas a tentação não desaparece porque o sistema tem um `CORRIGENDUM.md`.

### 7.3 Os paradoxos da prótese

Toda prótese cognitiva carrega paradoxos.

**O paradoxo da descarga.** Quanto mais o sistema carrega a memória, menos o usuário exercita a memória. Isso pode ser bom (liberar recursos para tarefas de alto nível) ou ruim (perder prática). A resposta não é abandonar a descarga; é criar momentos deliberados de prática sem rede.

**O paradoxo do registro.** Quanto mais o sistema registra, mais o usuário precisa navegar por registros. O excesso de documentação pode se tornar uma segunda sobrecarga. A resposta é podar, hierarquizar e criar critérios de relevância.

**O paradoxo da verificação.** Quanto mais o sistema verifica, mais o usuário pode confiar no sistema e menos verifica por conta própria. A resposta é manter a verificação humana em pontos críticos e treinar o julgamento, não apenas o uso da ferramenta.

**O paradoxo da personalização.** Quanto mais o sistema se adapta ao usuário, mais difícil é para outros usá-lo e mais difícil é para o usuário sair. A resposta é documentar, exportar e manter padrões abertos.

### 7.4 A questão ética

Se a ferramenta foi feita para um usuário, o que acontece com os outros? O Core é, ao mesmo tempo, idiossincrático e universal. Nasceu de uma necessidade singular, mas seus padrões — memória externalizada, contratos, verificação, retomada — são generalizáveis. A questão ética é evitar que a prótese se torne um privilégio: acesso a hardware, energia, tempo e conhecimento técnico não são distribuídos igualmente.

A resposta do projeto é parcial: licença MIT, ênfase local-first, documentação aberta. Isso não resolve a desigualdade, mas cria condições para que outros possam adaptar. A prótese autoral só se justifica se puder ser contestada, reproduzida e modificada por outros. Caso contrário, ela é apenas uma extensão privada de privilégio.

## 8. Riscos, efeitos adversos e salvaguardas

A tabela 4 resume os principais riscos e as salvaguardas existentes ou propostas. Nenhuma salvaguarda elimina o risco; elas o tornam gerenciável.

**Tabela 4 — Riscos e salvaguardas**

| Risco | Como aparece | Salvaguarda no Core | Salvaguarda adicional necessária | Risco residual |
|---|---|---|---|---|
| Dependência | O autor deixa de agir sem o sistema | Estado durável, documentação | Sessões sem ferramenta; prática deliberada | Médio |
| Viés de automação | Aceitar sugestões de agentes sem verificar | Gates, testes, revisão adversarial | Red team independente; amostragem manual | Médio |
| Desskilling | Perda de habilidades por descarga | Specs e testes explícitos | Exercícios manuais regulares | Médio |
| Hiperfoco | Trabalho sem pausa; exaustão | Timeouts, orçamentos | Limites de tempo; apoio social; sono | Alto |
| Perfeccionismo | Specs e testes infinitos | Critérios de aceite, stop rules | Revisão de escopo; “bom o suficiente” | Alto |
| Complexidade | 681 specs, 646 testes, 845 ciclos | Modularidade, documentação | Poda, dívida técnica, priorização | Alto |
| Privacidade | Memória registra contexto sensível | Local-first, allowlists | Redação, retenção, consentimento | Médio |
| Falsa segurança | Linguagem de “verificado” | Gate anti-overclaim | Formação do usuário; auditoria externa | Médio |
| Isolamento | Trabalho mediado por agentes | Colaboração via Blackboard | Vínculo humano; comunidade | Alto |
| Sobrecarga de cuidado | O sistema exige mais do que devolve | Doctor, helpdesk | Métrica de custo/benefício; pausas | Alto |

Fonte: elaboração própria.

### 8.1 A segunda doença

Há um risco que merece nome próprio: a prótese pode se tornar uma **segunda doença**. Um sistema que exige specs, testes, revisões, atualizações e manutenção pode consumir a vida que deveria proteger. O autor pode passar mais tempo cuidando da arquitetura do que vivendo o que a arquitetura deveria possibilitar. O hiperfoco, que é uma força, pode se aliar ao perfeccionismo e transformar o Core em um labirinto.

Esse risco não é hipotético. O repositório tem 681 specs, 646 testes e 845 ciclos. A riqueza é real; o custo também. A arquitetura precisa de **stop rules** — critérios explícitos para parar, publicar, descansar e deixar algo imperfeito. Sem isso, a prótese se volta contra o usuário.

### 8.2 Defaults humanos

O Core é, em muitos lugares, **fail-closed**: na dúvida, bloqueia. Isso é adequado para segurança, mas pode ser desumano. Um sistema que bloqueia demais pode paralisar; um que exige demais pode excluir. A proposta de “defaults humanos” é que o sistema, ao falhar, ofereça um caminho de saída: uma explicação, uma alternativa, um contato humano, uma forma de continuar.

Isso vale especialmente para um usuário com risco neurocognitivo. Se o sistema não entender o contexto, ele deve dizer “não sei” e oferecer ajuda, não insistir em uma rota. Se o usuário estiver cansado, o sistema deve sugerir pausa, não mais uma spec. A arquitetura da verificação precisa ser acompanhada de uma arquitetura do cuidado.

## 9. Como saber se funciona: um protocolo de avaliação N-of-1

### 9.1 Por que N-of-1

O caso é único, personalizado e heterogêneo. Um ensaio randomizado tradicional não é viável nem ético para uma intervenção tão pessoal. O desenho N-of-1 — ou experimento de caso único — permite testar hipóteses em uma pessoa, com medidas repetidas, condições alternadas e pré-registro (NOSEK et al., 2018). Ele não produz generalização estatística, mas produz evidência local, útil para decisões informadas.

O protocolo abaixo é uma proposta. Não foi executado. Deve ser adaptado com profissionais de saúde, neuropsicologia e ética em pesquisa.

### 9.2 Desfechos

**Tabela 5 — Desfechos propostos**

| Desfecho | Instrumento | Frequência | Hipótese | Risco de distorção |
|---|---|---|---|---|
| Tempo para retomar após interrupção | Registro automático + diário | Diário | O Core reduz o custo de retomada | Medida depende do contexto |
| Taxa de conclusão de tarefas | Log do sistema | Semanal | O Core aumenta a conclusão | Pode incentivar tarefas fáceis |
| Erros em tarefas rotineiras | Checklist cego | Semanal | O Core reduz erros | Pode não capturar erros raros |
| Carga cognitiva percebida | NASA-TLX adaptado | Semanal | O Core reduz a carga | Auto-relato sujeito a viés |
| Calibração da confiança | Confiança declarada vs. acerto | Semanal | O Core melhora a calibração | Pode medir confiança no sistema, não no julgamento |
| Senso de agência | Escala breve + entrevista | Quinzenal | O Core preserva a agência | Conceito multidimensional |
| Sono e vida social | Diário de hábitos | Semanal | O Core não piora esses domínios | Auto-relato |
| Sintomas de estresse | Escala validada | Quinzenal | O Core não aumenta o estresse | Requer interpretação clínica |

Fonte: elaboração própria. A seleção final deve ser feita com um profissional.

### 9.3 Desenho

Um desenho possível é o **ABAB com blocos randomizados** ao longo de 12 semanas:

- **Fase A (sem Core):** o autor realiza tarefas comparáveis com suas ferramentas habituais, sem o sistema.
- **Fase B (com Core):** o autor usa o sistema com as mesmas tarefas.
- **Repetição:** A e B alternam, com washout de uma semana.
- **Randomização:** a ordem dos blocos é sorteada e registrada.
- **Cegamento:** a avaliação de alguns desfechos (por exemplo, qualidade de um artefato) pode ser feita por um terceiro que não sabe em qual fase o artefato foi produzido.
- **Pré-registro:** hipóteses, desfechos, análises e critérios de parada são registrados antes do início.

### 9.4 Análise

A análise pode combinar inspeção visual de séries temporais com modelos mistos para medir mudança de nível e tendência. O tamanho do efeito deve ser reportado com incerteza. A multiplicidade de desfechos deve ser controlada ou explicitamente discutida. Resultados negativos devem ser publicados. A análise não deve ser feita pelo mesmo agente que implementou a intervenção sem supervisão independente.

### 9.5 Ética

O protocolo exige:

- consentimento informado e possibilidade de retirada;
- proteção de dados sensíveis;
- supervisão clínica para interpretar sinais de declínio cognitivo;
- separação entre dados de pesquisa e dados de cuidado;
- revisão por um comitê de ética, quando aplicável;
- compromisso de não transformar o resultado em alegação de cura ou prevenção.

## 10. Discussão: a casa, o arquiteto e o tempo

A metáfora da casa, proposta no prefácio R909, organiza a conclusão. Uma casa conserva decisões de quem a concebeu; mas não é a pessoa. Ela pode ser reformada, habitada por outros, abandonada. O Core é uma casa com vários cômodos: a memória (MetaBus), a oficina (TaskRuntime), a biblioteca (specs, docs, livro), o tribunal (verificação, `CORRIGENDUM`), o arquivo (EvolutionRegistry) e a sala de aula (manual, MIRA, explicadores). Cada cômodo tem uma função; nenhum deles é a mente do arquiteto.

A dimensão temporal é central. O risco de Alzheimer torna saliente a finitude da memória. O sistema é uma aposta contra o esquecimento, mas não pode vencer a mortalidade. Ele pode preservar traços, não presença. Pode permitir que o autor retome um projeto depois de uma pausa, mas não pode garantir que ele se lembre por que começou. A casa ajuda a pensar, mas não pensa por ele.

A dimensão coletiva também é central. O Core é uma obra composta: autor, agentes, bibliotecas, modelos, comunidade. A assinatura é do autor, mas não é só dele. Essa composição é uma riqueza e uma responsabilidade. A riqueza está na possibilidade de fazer mais do que uma pessoa faria sozinha; a responsabilidade está em não apagar as contribuições dos outros nem atribuir ao autor o que é coletivo.

A dimensão política é inescapável. Próteses cognitivas não são neutras. Elas exigem infraestrutura, energia, tempo e conhecimento. Se forem tratadas como luxo, aumentarão a desigualdade; se forem tratadas como direito, precisarão de políticas de acesso, formação e cuidado. O Core, com sua licença aberta e ênfase local-first, é uma contribuição, não uma solução.

A dimensão epistemológica é a mais delicada. O Core é uma máquina de humildade: ele exige spec, teste, recibo e correção. Mas a humildade pode se tornar uma nova forma de orgulho — “meu sistema é mais rigoroso do que os outros”. O `CORRIGENDUM.md` é a vacina contra isso. Ele lembra que o rigor é uma prática, não uma identidade. Um sistema que se corrige não é infalível; é apenas mais honesto sobre suas falhas.

## 11. Conclusão

Este artigo analisou o OpenCode Ecosystem Core como uma prótese cognitiva autoral. A tese foi defendida em três passos. Primeiro, o sistema externaliza funções cognitivas concretas: memória, função executiva, atenção, verificação e reflexão. Segundo, essa externalização carrega uma assinatura: desconfiança produtiva da própria memória, primazia do contrato, verificação contra a própria convicção, arquitetura da interrupção e vocação didática. Terceiro, essa assinatura é uma interpretação situada, não um biomarcador; ela precisa ser contestada, não celebrada.

O contexto de AH/SD e risco de Alzheimer é o que dá urgência ao projeto. A AH/SD ajuda a explicar a intensidade, a complexidade e a exigência de rigor; o risco neurocognitivo ajuda a explicar a ênfase em memória, continuidade e retomada. Mas o artigo recusou a causalidade fácil: não há evidência de que AH/SD cause Alzheimer, nem de que o Core previna a doença. O que há é uma coerência de projeto: um sistema construído para sustentar a vida cognitiva de alguém que conhece a própria fragilidade.

A contribuição principal não é o sistema em si, mas a possibilidade de pensá-lo criticamente. Uma prótese cognitiva autoral deve ser avaliada pelo que preserva, não pelo que promete. Se o Core ajuda o autor a continuar pensando, trabalhando e ensinando, ele cumpre uma função; se o impede de dormir, de conviver ou de parar, ele falha. O critério não é a quantidade de agentes, specs ou ciclos. É a qualidade da vida que a arquitetura torna possível.

O programa de pesquisa que se abre é claro: medir, com desenho N-of-1 e supervisão clínica, os efeitos do Core sobre retomada, carga cognitiva, erros, agência e bem-estar; comparar com alternativas mais simples; investigar os riscos de dependência e desskilling; e desenvolver uma ética de próteses cognitivas que seja ao mesmo tempo rigorosa e humana.

A casa não substitui o arquiteto. Ela lhe devolve tempo e espaço para continuar a desenhar — e, quando for preciso, para sair.

---

## Referências

### Fontes primárias do repositório

OPENCODE ECOSYSTEM CORE. **README.md**. Commit `1ce6ae98`, 2026a. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **ARCHITECTURE.md**. Commit `1ce6ae98`, 2026b. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **AGENTS.md**. Commit `1ce6ae98`, 2026c. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **MANUAL.md**. Commit `1ce6ae98`, 2026d. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **CORRIGENDUM.md**. Commit `1ce6ae98`, 2026e. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **Módulos**: `mci/metabus.py`, `mci/blackboard.py`, `mci/task_runtime.py`, `mci/reflexion.py`, `mci/metacognitive_evaluator.py`, `mci/metacognitive_gate.py`, `sdd/spec_engine.py`, `sdd/tdd_runner.py`, `trust/trust_engine.py`, `economy/token_economy.py`, `evolution/cycles.py`, `marceloclaro/orchestrator.py`, `marceloclaro/doctor.py`. Commit `1ce6ae98`, 2026f. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

OPENCODE ECOSYSTEM CORE. **opencode.json** e **evolution/cycles.json**. Commit `1ce6ae98`, 2026g. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core. Acesso em: 10 nov. 2026.

LARANJEIRA, M. C. **A assinatura cognitiva de um ecossistema agêntico**: prefácio R909. In: OPENCODE ECOSYSTEM CORE. *livro-core/mod-00-capa.tex*. 2026a. Disponível em: https://github.com/MarceloClaro/opencode-ecosystem-core/blob/main/docs/PREFACIO_ASSINATURA_COGNITIVA_R909.md. Acesso em: 10 nov. 2026.

LARANJEIRA, M. C. **Dupla excepcionalidade no Brasil**: autismo, altas habilidades/superdotação e desafios de identificação a partir do Censo Escolar (2021–2024). 2026b. Trabalho de Conclusão de Curso (Pós-graduação Lato Sensu em Educação Especial e Inclusiva, Neuropsicopedagogia Institucional e Clínica) — FACUMINAS, Brasília, 2026.

### Literatura

BECK, K. **Test-Driven Development**: by example. Boston: Addison-Wesley, 2002.

BRASIL. **Lei nº 9.394, de 20 de dezembro de 1996**. Estabelece as diretrizes e bases da educação nacional. Brasília, DF: Presidência da República, 1996.

BRASIL. **Política Nacional de Educação Especial na Perspectiva da Educação Inclusiva**. Brasília, DF: Ministério da Educação, 2008.

CALISKAN, A. et al. When coding style survives compilation: de-anonymizing programmers from executable binaries. In: **Network and Distributed System Security Symposium (NDSS)**, 2018. DOI: 10.14722/ndss.2018.23304.

CLARK, A.; CHALMERS, D. The extended mind. **Analysis**, v. 58, n. 1, p. 7–19, 1998. DOI: 10.1093/analys/58.1.7.

GAGNÉ, F. Transforming gifts into talents: the DMGT as a developmental theory. **High Ability Studies**, v. 15, n. 2, p. 119–147, 2004. DOI: 10.1080/1359813042000314682.

HOLLAN, J.; HUTCHINS, E.; KIRSH, D. Distributed cognition: toward a new foundation for human-computer interaction research. **ACM Transactions on Computer-Human Interaction**, v. 7, n. 2, p. 174–196, 2000. DOI: 10.1145/353485.353487.

HOWARD-JONES, P. A. Neuroscience and education: myths and messages. **Nature Reviews Neuroscience**, v. 15, p. 817–824, 2014. DOI: 10.1038/nrn3817.

HUTCHINS, E. **Cognition in the Wild**. Cambridge, MA: MIT Press, 1995.

INSEL, T. et al. Research domain criteria (RDoC): toward a new classification framework for research on mental disorders. **American Journal of Psychiatry**, v. 167, n. 7, p. 748–751, 2010. DOI: 10.1176/appi.ajp.2010.09091379.

IOANNIDIS, J. P. A. Why most published research findings are false. **PLoS Medicine**, v. 2, n. 8, e124, 2005. DOI: 10.1371/journal.pmed.0020124.

JACK, C. R. et al. NIA-AA research framework: toward a biological definition of Alzheimer's disease. **Alzheimer's & Dementia**, v. 14, n. 4, p. 535–562, 2018. DOI: 10.1016/j.jalz.2018.02.018.

LIVINGSTON, G. et al. Dementia prevention, intervention, and care: 2020 report of the Lancet Commission. **The Lancet**, v. 396, n. 10248, p. 413–446, 2020. DOI: 10.1016/S0140-6736(20)30367-6.

MACCORMACK, A.; BALDWIN, C.; RUSNAK, J. Exploring the duality between product and organizational architectures: a test of the mirroring hypothesis. **Research Policy**, v. 41, n. 8, p. 1309–1324, 2012. DOI: 10.1016/j.respol.2012.04.011.

MAYER, R. E.; MORENO, R. Nine ways to reduce cognitive load in multimedia learning. **Educational Psychologist**, v. 38, n. 1, p. 43–52, 2003. DOI: 10.1207/S15326985EP3801_6.

NICKERSON, R. S. Confirmation bias: a ubiquitous phenomenon in many guises. **Review of General Psychology**, v. 2, n. 2, p. 175–220, 1998. DOI: 10.1037/1089-2680.2.2.175.

NII, H. P. Blackboard systems: the blackboard model of problem solving and the evolution of blackboard architectures. **AI Magazine**, v. 7, n. 2, p. 38–53, 1986.

NORMAN, D. A. Cognitive artifacts. In: CARROLL, J. M. (ed.). **Designing Interaction**: psychology at the human-computer interface. Cambridge: Cambridge University Press, 1991. p. 17–38.

NOSEK, B. A. et al. The preregistration revolution. **Proceedings of the National Academy of Sciences**, v. 115, n. 11, p. 2600–2606, 2018. DOI: 10.1073/pnas.1708274114.

POLDRACK, R. A. Inferring mental states from neuroimaging data: from reverse inference to large-scale decoding. **Neuron**, v. 72, n. 5, p. 692–697, 2011. DOI: 10.1016/j.neuron.2011.11.001.

RENZULLI, J. S. What makes giftedness? Reexamining a definition. **Phi Delta Kappan**, v. 60, n. 3, p. 180–184, 1978.

RISKO, E. F.; GILBERT, S. J. Cognitive offloading. **Trends in Cognitive Sciences**, v. 20, n. 9, p. 676–688, 2016. DOI: 10.1016/j.tics.2016.07.002.

RUPERT, R. D. Challenges to the hypothesis of extended cognition. **Journal of Philosophy**, v. 101, n. 8, p. 389–428, 2004. DOI: 10.5840/jphil2004101826.

SHINN, N. et al. Reflexion: language agents with verbal reinforcement learning. In: **Advances in Neural Information Processing Systems (NeurIPS)**, 2023. arXiv:2303.11366.

STERELNY, K. Minds: extended or scaffolded? **Phenomenology and the Cognitive Sciences**, v. 9, n. 4, p. 465–481, 2010. DOI: 10.1007/s11097-010-9174-y.

STERN, Y. What is cognitive reserve? Theory and research application of the reserve concept. **Journal of the International Neuropsychological Society**, v. 8, n. 3, p. 448–460, 2002. DOI: 10.1017/S1355617702813248.

SWELLER, J. Cognitive load during problem solving: effects on learning. **Cognitive Science**, v. 12, n. 2, p. 257–285, 1988. DOI: 10.1207/s15516709cog1202_4.

VERBEEK, P.-P. Materializing morality: design ethics and technological mediation. **Science, Technology, & Human Values**, v. 31, n. 3, p. 361–380, 2006. DOI: 10.1177/0162243905285847.

WOOLDRIDGE, M.; JENNINGS, N. R. Intelligent agents: theory and practice. **The Knowledge Engineering Review**, v. 10, n. 2, p. 115–152, 1995. DOI: 10.1017/S0269888900008122.

YARKONI, T. The generalizability crisis. **Behavioral and Brain Sciences**, v. 45, e1, 2022. DOI: 10.1017/S0140525X20001685.

YIN, R. K. **Case Study Research and Applications**: design and methods. 6. ed. Thousand Oaks: Sage, 2018.

---

## Apêndice A — Evidências e contagens

As contagens abaixo foram obtidas por inspeção do checkout em 10 de novembro de 2026. Elas não constituem certificação de qualidade, cobertura, disponibilidade ou validação externa.

| Evidência | Caminho | O que mostra | O que não mostra |
|---|---|---|---|
| Ciclo de orquestração | `marceloclaro/orchestrator.py` | Perceber, delegar, refletir; integração com MCI, SDD/TDD, trust e economia | Não mostra eficácia cognitiva |
| Memória compartilhada | `mci/metabus.py` | Memória episódica/semântica, eventos, confidence ledger | Não é backup total da mente |
| Blackboard A2A | `mci/blackboard.py` | Agent Cards, tarefas, voluntários, seleção | Não é um mercado de verdade |
| Runtime de tarefas | `mci/task_runtime.py` | DAGs, leases, orçamento, retomada | Não decide prioridades |
| Especificações | `sdd/spec_engine.py`, `specs/` | Critérios de aceite, verificação | Spec não garante execução |
| TDD | `sdd/tdd_runner.py`, `sdd/tdd_history.py` | Evidência de teste, histórico RED/GREEN | Teste não é verdade científica |
| Confiança | `trust/trust_engine.py`, `trust/behavioral_gate.py` | Score histórico, gate, goal drift | Trust não é mérito |
| Economia | `economy/token_economy.py` | Stake, slashing, fee market | Stake não é competência |
| Evolução | `evolution/cycles.py`, `evolution/cycles.json` | Ciclos, lições, hashes, scores | Score é autoavaliação |
| Prefácio R909 | `docs/PREFACIO_ASSINATURA_COGNITIVA_R909.md` | Definição de assinatura cognitiva | Não é prova de mente |
| Corrigendum | `CORRIGENDUM.md` | Autocorreção pública de overclaims | Não elimina vieses |

## Apêndice B — Checklist de verificação editorial

- [ ] O texto distingue relato, risco, diagnóstico e prevenção.
- [ ] O texto não afirma que o Core previne, trata ou diagnostica Alzheimer.
- [ ] O texto não afirma que AH/SD causa Alzheimer.
- [ ] O texto não afirma validação externa, revisão por pares ou aceite editorial.
- [ ] Cada afirmação sobre o código tem arquivo de referência.
- [ ] As contagens estão datadas e acompanhadas de ressalva.
- [ ] As referências externas têm DOI ou identificador verificável.
- [ ] O texto inclui riscos e efeitos adversos.
- [ ] O texto inclui protocolo de avaliação e limites.
- [ ] O texto inclui nota de uso de IA e revisão humana pendente.
- [ ] O texto não transforma a assinatura cognitiva em biomarcador ou prova de consciência.
- [ ] O texto preserva a privacidade do autor e não especula sobre dados clínicos não fornecidos.

---

**Nota final.** Este artigo é um rascunho de trabalho. Ele foi escrito a partir de leitura documental do repositório e de literatura externa, com auxílio de IA. Não passou por revisão por pares, revisão clínica ou validação independente. A hipótese central — a de que o Core funciona como prótese cognitiva autoral — é uma interpretação a ser testada, não um resultado. O autor e eventuais revisores devem tratar o texto como ponto de partida para crítica, não como conclusão.
