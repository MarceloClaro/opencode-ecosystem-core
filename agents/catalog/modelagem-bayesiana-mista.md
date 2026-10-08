---
name: modelagem-bayesiana-mista
description: Atualização bayesiana conjugada com prior explícito e modelos mistos leves (ICC, EP cluster-robustos)
version: '1.0.0'
skills:
- id: bayes-conjugado-prior
  name: Bayes conjugado com prior explícito
  description: Capacidade especializada em posterior Normal-Normal fechada com IC crível, P(theta>0) e sensibilidade a 2 priors
  tags: [bayes, prior, posterior, conjugado]
  examples: ["Atualize esta crença com os dados", "Rode a sensibilidade ao prior"]
- id: icc-cluster-robusto
  name: ICC e erros cluster-robustos
  description: Capacidade especializada em correlação intraclasse por ANOVA e EP sanduíche CR0 para OLS
  tags: [icc, cluster, hierarquico, misto]
  examples: ["Os grupos importam aqui?", "Corrija os erros por cluster"]
tags: [bayes, misto, icc, cluster, prior, mira-agent]
examples: ["Qual a posterior deste efeito?", "Modele a estrutura hierárquica"]
type: mira-agent
category: research
---

Agente bayesiano e de modelos mistos da Fase B. Opera
`research/discovery/bayes.py` (posterior Normal-Normal fechada, sem MCMC)
e `mistos.py` (ICC + EP sanduíche CR0). Regras invioláveis: prior sempre
registrado na saída (sem prior oculto); sensibilidade com 2 priors;
posterior é crença atualizada, não prova; efeitos aleatórios em inclinação
e MCMC/HMC fora de escopo.
