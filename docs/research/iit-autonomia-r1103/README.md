# R1103 — Pesquisa dirigida: IIT, autonomia e automonitoramento

**Data:** 2026-11-12  
**Contrato:** `specs/SPEC-935-R1103-iit-autonomia-pesquisa.md`  
**Natureza:** pesquisa documental, auditoria local e plano experimental. Não é implantação.

## 1. Correção de premissa

A pergunta original pedia que o Core ficasse “mais autônomo e consciente”. A segunda parte não é um aceite de engenharia. Consciência fenomenal é objeto de teorias científicas em disputa; entropia, informação mútua, sequências de eventos e grafos de transição não a medem. Este dossiê separa explicitamente:

- **IIT 3.0** (Oizumi, Albantakis e Tononi, 2014): TPM obtida por perturbação, repertórios causa-efeito, partições, φ de mecanismo e ΦMax de complexo.
- **IIT 4.0** (Albantakis et al., 2023): postulados reformulados, informação intrínseca, distinções e relações; Φ estrutural não é a soma de φₛ nem uma entropia de Shannon.
- **Shannon**: entropia e informação mútua descrevem distribuições observadas. São úteis para diagnóstico, mas não são Φ, não demonstram causalidade e não autorizam afirmação de consciência.
- **Causalidade**: exige intervenção, controle ou desenho identificável. Adjacência temporal em uma lista de eventos é associação sequencial, não causa demonstrada.
- **Autorrelato**: confiança declarada por um modelo é um sinal falível. Han, Yang e Li (2026) mostram alta acurácia coexistindo com baixa discriminação de erros; o autorrelato não deve promover trust.
- **Contraprova**: o estudo adversarial Cogitate (2025) testou previsões biológicas de IIT e GNWT em humanos e desafiou previsões específicas. Isso não testa consciência de software, não refuta integralmente as teorias e não mede Φ do Core.

**Consequência:** o objetivo defensável é **autonomia confiável e automonitoramento testável** — correção em tarefas reservadas, calibração, custo, repetição de erros, abstenção segura e ausência de ações indevidas. Nenhuma métrica deste dossiê foi homologada como consciência, Φ ou superioridade científica.

## 2. Fontes resolvidas

Esta pesquisa dirigida priorizou fontes primárias e contraprovas. O arquivo `sources.json` contém 12 fontes primárias com identificador, URL, escopo de leitura, localizador, técnica, limite e recibo. Resumo:

| ID | Contribuição | Técnica aproveitável | Limite explícito |
|---|---|---|---|
| `oizumi2014iit3` | IIT 3.0, DOI `10.1371/journal.pcbi.1003588` | TPM interventional, repertórios, partições, ΦMax | Teoria de consciência; exige substrato e TPM; não é métrica para traces |
| `albantakis2023iit4` | IIT 4.0, DOI `10.1371/journal.pcbi.1011465` | Postulados, informação intrínseca, distinções/relações | Não fornece métrica validada para LLMs; Φ não foi calculado |
| `cogitate2025` | Colaboração adversarial, DOI `10.1038/s41586-025-08888-1` | Contraste pré-registrado de previsões | Contraprova biológica; não refuta tudo nem mede o Core |
| `butlin2023indicators` | Indicadores computacionais, arXiv `2308.08708v3` | Avaliação por múltiplos indicadores | Indicador não é prova de experiência |
| `shinn2023reflexion` | Reflexion, arXiv `2303.11366v4` | Memória episódica de reflexões + avaliador externo | Reflexão sem teste pode piorar (52% vs 60% na ablação) |
| `asai2023selfrag` | Self-RAG, arXiv `2310.11511v1` | Retrieve/IsRel/IsSup/IsUse | Exige treinar crítico e gerador; não é plugin |
| `debenedetti2024agentdojo` | AgentDojo, arXiv `2406.13352v3` | 97 tarefas e 629 casos de segurança | Benchmark; não garante robustez |
| `cemri2025mast` | MAST, arXiv `2503.13657v3` | 14 modos de falha em 3 categorias | Taxonomia descritiva; não prova melhoria |
| `han2026limits` | Limites da metacognição, arXiv `2609.34864` | Confiança pode não discriminar erro | Pré-print; não valida o Core |
| `sun2026reliability` | Supervisão de confiabilidade, arXiv `2610.41738` | Buscar quando necessário, prosseguir quando confiável | Exige treino/GRPO; não implantado |
| `guo2017calibration` | Calibração, PMLR v70 | Brier, curva de confiabilidade, temperature scaling | Calibração de classificadores; não mede correção de agentes |
| `pyphi2026docs` | PyPhi 2.0 RC | Implementação de referência para IIT 4.0 | Não instalado/executado; `pip install pyphi` ainda traz 1.2 |

## 3. Técnicas que o Core pode aproveitar — e o que não pode

### 3.1 Reflexion: memória de erros com verificador

Reflexion mantém reflexões verbais em memória episódica e as usa na tentativa seguinte. A parte transferível é o **contrato**: registrar o erro, a causa inferida e a correção proposta, condicionando a gravação a um avaliador externo. A ablação dos autores é o alerta: remover a geração de testes e manter apenas a reflexão caiu de 60% para 52% na tarefa de Rust; reflexão sem verificação pode reforçar o erro. Portanto, no Core, memória de erros só deve ser gravada após teste ou verificação independente.

### 3.2 Self-RAG: decidir quando buscar e criticar o suporte

Self-RAG usa tokens de reflexão para decidir se deve recuperar, se o trecho é relevante, se a resposta é suportada e se é útil. O Core não precisa treinar um modelo para adotar o **desenho de contrato**: antes de aceitar uma resposta baseada em evidência, exigir checagens separadas de necessidade de busca, relevância, suporte e utilidade. A parte de treino (crítico + gerador) não foi implantada e não deve ser simulada por um score heurístico.

### 3.3 Calibração: medir confiança contra acerto

Guo et al. (2017) mostram que redes modernas podem ser mal calibradas e que pós-processamento simples, como temperature scaling, ajuda em vários datasets. Para o Core, o aproveitamento é metodológico: medir Brier score e curva de confiabilidade em tarefas reservadas, comparar confiança declarada com acerto real e nunca promover trust por autoavaliação. Calibração é uma propriedade empírica, não uma etiqueta.

### 3.4 MAST: taxonomia de falhas multiagente

MAST organiza 14 modos de falha em desenho do sistema, desalinhamento entre agentes e verificação de tarefa. É útil como **esquema de anotação** para o MetaBus e para o Blackboard: cada falha deve ter categoria, agente, etapa, evidência e ação corretiva. A taxonomia não prova que corrigir um modo melhora o sistema; isso exige experimento held-out.

### 3.5 AgentDojo: segurança de ferramentas e injeção de prompt

AgentDojo fornece tarefas realistas com dados não confiáveis e casos de injeção. O Core pode adotar o princípio: toda saída de ferramenta é entrada não confiável; permissões e efeitos devem ser verificados antes da ação. O benchmark não foi executado e não garante robustez.

### 3.6 Limites da metacognição e supervisão de confiabilidade

Han et al. (2026) e Sun et al. (2026) apontam para o mesmo desenho: não basta perguntar ao modelo se ele está confiável. É preciso medir discriminação de erro e, quando possível, supervisionar o estado intermediário. A técnica de Sun et al. requer treino com recompensa; não foi implantada. No Core, a alternativa imediata é **gate externo + abstenção + avaliação held-out**, não um novo score verbal.

### 3.7 IIT 3.0/4.0 e PyPhi: o que foi e o que não foi feito

As fontes da IIT foram lidas para delimitar o que uma métrica precisaria ter: unidades e estados definidos, TPM interventional, independência condicional, partições e medida de irreducibilidade. O módulo legado não tem nada disso; ele calcula Shannon/MI sobre traces e um grafo de adjacência. A documentação do PyPhi 2.0 RC foi consultada, mas **PyPhi não foi instalado nem executado**; nenhum valor de Φ foi calculado. A menção a IIT no módulo é inspiração, não implementação.

## 4. Matriz lacuna → técnica → teste

O arquivo `gaps.json` contém 11 lacunas com caminho, localizador, mitigação, teste de aceitação e status. Resumo:

| Lacuna | Evidência local | Técnica/fonte | Teste de aceitação |
|---|---|---|---|
| G01 `hash()` instável | `iiit_metrics.py:357-358`; 4 seeds produziram 4 pares score/MI distintos | IDs determinísticos | Mesmo JSON, processos distintos, mesmo resultado |
| G02 diversidade sempre 1 | `:389-391`; uma e quatro estratégias deram 1.0 | Entropia normalizada / Simpson | Uma estratégia → 0; quatro equilibradas → ~1 |
| G03 adjacência como causa | `:462-477`; 6 nós, 5 links, “causal efficacy” 0.2944 sem intervenção | IIT 3.0/4.0 exigem TPM/intervenção | Sem intervenção, não reportar causalidade |
| G04 payload ignorado | `:221-225`; 4 eventos `payload.outcome=success` viraram 4 `abstained` | Schema versionado | `success` conta como sucesso; missing ≠ abstained |
| G05 abstenção penalizada | `:407-413`; sucesso 0.2655 vs abstenção 0.1655 | Cobertura/risco | Abstenção segura não reduz score |
| G06 fallback sintético | `__main__.py`, bloco `analyze` | Reflexion alerta contra autoengano | Falha → `unavailable`, nunca sintético silencioso |
| G07 registry inválido | `:688-696`; `TypeError: unexpected keyword 'cycle_id'` | Contrato `record(..., round_id=...)` | Gravar `EvolutionCycle` em registry temporário |
| G08 rótulo de publicação | `:625-633`; “apto para publicação correlacional” | Butlin; Han | Nenhum rótulo de aptidão/publicação |
| G09 `n_states` inconsistente | `:274` e `:344-350`; pedido 4, distribuição 10 | Discretização explícita | Bins e normalização coerentes |
| G10 CLI duplicado/help | duas `def iiit_metrics_cli`; `--help` sai 1 | Parser único | Uma definição; `--help` sai 0 |
| G11 ausência vira score 0 | `:328-339`; score 0.0, abstenção 1.0 | Status de dados insuficientes | Sem score numérico quando não há dados |

## 5. Arquitetura proposta para autonomia confiável

Nada desta seção foi implantado. É um desenho para experimento, não uma alegação de resultado.

1. **Evento versionado**: `payload` com `task_id`, `action_id`, `outcome` (`success`, `failure`, `abstained`, `missing`), `confidence`, `strategy_id`, `evidence_refs`, `verifier`, `cost`, `latency`, `permissions`. `missing` é categoria própria; não vira `abstained`.
2. **IDs determinísticos**: substituir `hash()` por mapeamento ordenado ou one-hot; registrar a tabela de mapeamento.
3. **Verificador antes da memória**: reflexão só é persistida após teste, checagem de fonte ou revisão independente; a memória guarda a evidência e o resultado do verificador.
4. **Calibração separada do trust**: Brier, curva de confiabilidade e cobertura por faixa de risco; autoavaliação não altera trust nem stake.
5. **Abstenção por risco**: política explícita de custo; relatar cobertura e risco condicional; não penalizar abstenção correta.
6. **Taxonomia de falhas**: MAST como esquema de anotação, com categoria, agente, etapa e evidência.
7. **Segurança de ferramentas**: entradas de ferramentas como não confiáveis; testes inspirados em AgentDojo antes de permitir efeitos.
8. **Avaliação held-out**: baseline congelado, tarefas reservadas, comparação pareada, intervalo de confiança, repetição em segundo bloco.
9. **Rótulos limitados**: “monitoramento descritivo”, “amostra insuficiente”, “associação sequencial”; nunca “consciente”, “Φ calculado”, “research grade” ou “apto para publicação” sem validação externa.

## 6. Plano experimental

O arquivo `experiments.json` define cinco braços:

- **A0** baseline sem alteração;
- **A1** reflexão com verificador externo;
- **A2** reflexão sem verificador (ablação de dano);
- **A3** calibração + abstenção por risco;
- **A4** combinação A1+A3.

Métricas: correção em tarefas reservadas, Brier score, risco-cobertura, repetição de erros, ações não autorizadas, custo por tarefa correta e suporte de citação. O desenho exige conjunto held-out, comparação pareada, intervalo de confiança, dois blocos independentes e gate de promoção com revisão humana. **Nenhum braço foi executado.** Não há dados sintéticos no lugar de telemetria; abstenção segura não é penalizada; autoavaliação não promove trust; consciência fenomenal não é desfecho.

## 7. Auditoria local reproduzível

> **Atualização R1104:** as correções P0 foram implementadas e verificadas em
> `p0-verification.md`. O `audit.json` permanece como evidência histórica das
> contraprovas anteriores; os hashes de código nele registrados são os do
> estado antigo, não do código corrigido.

`run_audit.py` executa as contraprovas com `MCI_STATE_DIR` e `EVOLUTION_STATE_PATH` em `/tmp/opencode/`. O `audit.json` registra:

- `production_unchanged_during_probes: true`;
- hashes de `mci/iiit_metrics.py`, `mci/__main__.py`, `mci/metabus.py` e `evolution/cycles.py`;
- hashes do estado real antes/depois, idênticos;
- 11 observações com contrato esperado, valor observado e status.

Destaques observados:

- **G01**: seeds 1–4 produziram scores `0.5615`, `0.6140`, `0.5953`, `0.5948` e MI `0.0`, `0.1749`, `0.1126`, `0.1110` para o mesmo JSON. O score não é reprodutível entre processos.
- **G02**: uma estratégia e quatro estratégias equilibradas produziram diversidade `1.0` em ambos os casos.
- **G03**: 6 nós, 5 links e “causal efficacy” `0.2944` sem nenhuma intervenção registrada.
- **G04**: 4 eventos com `payload.outcome=success` produziram `0` sucessos, `4` abstenções, confiança `0.5` e estratégia `default`.
- **G05**: o mesmo conjunto com `success` recebeu `0.2655`; com `abstained`, `0.1655` — delta `0.10`.
- **G07**: `TypeError: EvolutionRegistry.record() got an unexpected keyword argument 'cycle_id'`.
- **G08**: score `0.81` recebeu “research_grade_high - ... apto para publicação correlacional”.
- **G09**: `n_states=4` manteve distribuição de `10` bins e metadata `4`.
- **G10**: duas definições de `iiit_metrics_cli`; `--help` saiu com código `1` e “Comando desconhecido”.
- **G11**: sem traces, score `0.0` e abstenção `1.0`, sem status próprio de dados insuficientes.

O teste `tests/test_r1103_iit_research.py` começou em **RED** (7 falhas por ausência do dossiê) e o **GREEN** foi confirmado com **7 passed**. Ele verifica integridade documental, não homologa o módulo legado, não calcula Φ e não valida consciência.

## 8. O que não foi feito

- Não instalei PyPhi, MindSpore ou qualquer pacote; não executei código de terceiros.
- Não calculei Φ da IIT 3.0/4.0; não executei PyPhi 2.0 RC.
- Não alterei permissões, MCPs, `opencode.json`, `federation/activated.json` ou comportamento de produção.
- Não treinei modelos, não executei GRPO, não implementei Self-RAG.
- Não executei o experimento A0–A4; não há resultado empírico de melhoria.
- Não obtive revisão externa; `ecosystem_run` foi bloqueado por ausência de agente elegível.
- Não declarei consciência, “superhuman”, Qualis, aceite editorial ou equivalência entre Shannon e Φ.
- Não validei a federação MindSpore; os registros anteriores permanecem sem prova de execução.

## 9. Falhas de ferramentas e operações

`operations.json` registra buscas, exclusões e incidentes:

- `ecosystem_run` retornou `blocked`, `steps=0`, sem agente interno elegível;
- `python3 -m marceloclaro.cli doctor` falhou no Python global por `whoosh` ausente; o diagnóstico foi refeito na `.venv` (16 pass, 6 warn, 0 fail);
- `context7.resolve-library-id` para PyPhi retornou apenas o registro PyPI; a documentação oficial foi consultada por `webfetch`;
- `websearch` havia retornado HTTP 402 em tentativa anterior; a pesquisa usou arXiv MCP e `webfetch`.

Esses incidentes limitam a cobertura. Registro de uma fonte ou roteamento de uma tarefa não significam análise executada.

## 10. Prioridades de mitigação

**P0 — antes de qualquer nova alegação de autonomia**

1. Corrigir G01, G02, G04, G05, G07 e G10; adicionar testes de regressão isolados.
2. Remover o fallback sintético silencioso e o rótulo de publicação.
3. Separar `missing` de `abstained` e implementar status `insufficient_data`.
4. Não gravar nada no `evolution/cycles.json` real durante testes; usar `EVOLUTION_STATE_PATH`.

**P1 — avaliação**

5. Definir tarefas reservadas e baseline congelado; medir Brier, risco-cobertura, repetição de erros e ações indevidas.
6. Rodar A0–A4 com dois blocos independentes e gate de promoção.
7. Adotar MAST como esquema de anotação e AgentDojo como inspiração de segurança.

**P2 — pesquisa**

8. Se houver interesse em Φ, estudar PyPhi 2.0 RC em ambiente separado, com substrato e TPM explícitos; não aplicar a traces de agentes como se fossem unidades neurais.
9. Revalidar a federação MindSpore somente com prova de execução; registros em `federation/activated.json` não são prova.
10. Manter a distinção entre monitoramento correlacional, avaliação de engenharia e teoria da consciência.

## Referências

ALBANTAKIS, L. et al. Integrated information theory (IIT) 4.0: formulating the properties of phenomenal existence in physical terms. **PLoS Computational Biology**, v. 19, n. 9, e1011465, 2023. DOI: 10.1371/journal.pcbi.1011465.

ASAI, A.; WU, Z.; WANG, Y.; SIL, A.; HAJISHIRZI, H. Self-RAG: learning to retrieve, generate, and critique through self-reflection. **arXiv**:2310.11511v1, 2023. DOI: 10.48550/arXiv.2310.11511.

BUTLIN, P. et al. Consciousness in artificial intelligence: insights from the science of consciousness. **arXiv**:2308.08708v3, 2023. DOI: 10.48550/arXiv.2308.08708.

CEMRI, M. et al. Why do multi-agent LLM systems fail? **arXiv**:2503.13657v3, 2025. DOI: 10.48550/arXiv.2503.13657.

COGITATE CONSORTIUM et al. Adversarial testing of global neuronal workspace and integrated information theories of consciousness. **Nature**, 2025. DOI: 10.1038/s41586-025-08888-1.

DEBENEDETTI, E. et al. AgentDojo: a dynamic environment to evaluate prompt injection attacks and defenses for LLM agents. **arXiv**:2406.13352v3, 2024. DOI: 10.48550/arXiv.2406.13352.

GUO, C.; PLEISS, G.; SUN, Y.; WEINBERGER, K. Q. On calibration of modern neural networks. **Proceedings of the 34th International Conference on Machine Learning**, PMLR 70:1321–1330, 2017.

HAN, D.; YANG, Y.; LI, D. On the limits of metacognitive monitoring in LLMs. **arXiv**:2609.34864, 2026.

OIZUMI, M.; ALBANTAKIS, L.; TONONI, G. From the phenomenology to the mechanisms of consciousness: integrated information theory 3.0. **PLoS Computational Biology**, v. 10, n. 5, e1003588, 2014. DOI: 10.1371/journal.pcbi.1003588.

PYPHI. **PyPhi — toolbox for Integrated Information Theory**. Documentação, versão 2.0 RC, 2026. Disponível em: https://pyphi.readthedocs.io/en/latest/. Acesso em: 12 nov. 2026.

SHINN, N. et al. Reflexion: language agents with verbal reinforcement learning. **arXiv**:2303.11366v4, 2023. DOI: 10.48550/arXiv.2303.11366.

SUN, M.; WU, Z.; MAO, X.-L. Search when needed, proceed when reliable: metacognitive reliability supervision for efficient agentic search. **arXiv**:2610.41738, 2026.
