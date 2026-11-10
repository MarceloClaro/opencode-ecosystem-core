# Pesquisa para melhorar a camada de cognição (insumo para R1133–R1137)

**Data:** 2026-11-10
**Escopo:** literatura recente para mitigar as cinco limitações declaradas da
camada `core_cognition/` e otimizar a integração com o Core.
**Estatuto:** dossiê de pesquisa e desenho. Não é prova de eficácia, não é
revisão sistemática e não substitui validação clínica ou revisão externa.

## Resumo executivo

| Limitação | Artigo-chave | Técnica | Próximo módulo |
|---|---|---|---|
| 1. Heurística/estrutural | EMA as a Measure of Intervention Change (2025); Not all cognitive offloading is equal (2026) | Contrato de medição, EMA, teste de transferência | `measurement.py` (R1136) |
| 2. N-of-1 validador | SCRIBE 2016; SCED effect sizes (2021/2025) | Runner de execução, Tau-U/NAP/PEM, autocorrelação | `n_of_1_runner.py`, `sced.py` (R1137) |
| 3. Ledger não produz evidência | Fact or Fiction (2020); SciClaimHunt (2025) | Grafo claim–evidência, SUPPORT/CONTRADICT/INSUFFICIENT, PROV | `claims_graph.py` (R1134) |
| 4. Trust/stake não é verdade | Lee & See (2004); Adaptive Trust Calibration (2020); UQ survey (2025) | Coordination vs. warrant, Brier/ECE, abstenção | `trust_warrant.py` (R1135) |
| 5. Stop rules não ativas | Runtime Compliance Verification (2026); Agent Safety as Runtime Contract (2026) | Contrato de runtime, classes de ação, circuit breaker | `runtime_contract.py` (R1133) |

## 1. As cinco limitações

1. A camada é heurística e estrutural; não mede eficácia cognitiva nem valida
   clinicamente o sistema.
2. O protocolo N-of-1 é um validador de desenho, não um estudo executado.
3. O claims ledger organiza evidência; não a produz.
4. Trust score, stake e token economy são dispositivos de coordenação, não
   medidas de verdade.
5. As stop rules são um avaliador de política; a integração automática no loop
   do orquestrador ainda não foi ativada.

## 2. Limitação 1 — medir em vez de apenas descrever

### Artigos e técnicas

| Artigo | DOI | Técnica aproveitável |
|---|---|---|
| An Online Framework for Cognitive Load Assessment in Industrial Tasks (2022) | 10.1016/j.rcim.2022.102380 | Avaliação de carga cognitiva combinando medidas subjetivas, de desempenho e, quando disponíveis, fisiológicas; utilidade para um contrato de medição multi-modal. |
| Measurement and Management of Cognitive Load in Surgical Education (2023) | 10.1016/j.jsurg.2022.10.001 | Revisão de instrumentos de carga cognitiva e estratégias de manejo; lembra que medida sem contexto de tarefa é pouco interpretável. |
| Ecological Momentary Assessment as a Measure of Intervention Change (2025) | 10.2196/69297 | EMA como medida de mudança em intervenções digitais; exige avaliar confiabilidade, validade, burden e adesão antes de tratar EMA como desfecho. |
| Ecological Momentary Assessment in a Digital Health Intervention for Dementia and Caregivers (2020) | 10.2196/17120 | EMA em população com vulnerabilidade cognitiva; lições sobre burden, apoio do cuidador e dados faltantes. |
| Not all cognitive offloading is equal (2026) | 10.3389/fpsyg.2026.1878629 | Distinção entre offloading dependente e autônomo; mede se a pessoa consegue realizar a tarefa sem a ferramenta, não apenas se usa a ferramenta. |
| AI Tools in Society: Impacts on Cognitive Offloading and Critical Thinking (2025) | 10.3390/soc15010006 | Offloading como mediador entre uso de IA e pensamento crítico; sugere medir transferência e não só produtividade. |

### O que implementar

- **Contrato de medição** (`core_cognition/measurement.py`):
  - instrumento, construto, população validada, confiabilidade, burden, modo
    (auto-relato, log, desempenho, fisiológico opcional), frequência;
  - regra de dados faltantes e de adesão mínima;
  - separação entre **desfecho primário**, **secundário** e **exploratório**.
- **EMA local** com agenda, lembretes, janela de resposta e registro de
  compliance; sem rede por padrão.
- **Teste de transferência**: após washout, medir a tarefa sem a ferramenta.
  Isso diferencia offloading dependente de autônomo.
- **Metadados psicométricos** obrigatórios no protocolo N-of-1; sem eles, o
  desfecho é marcado como exploratório.

### O que isso mitiga

Move a camada de “heurística estrutural” para “infraestrutura de medição”.
Não produz eficácia por si: exige dados do usuário, instrumentos validados e
revisão clínica.

## 3. Limitação 2 — executar o N-of-1, não apenas validar o desenho

### Artigos e técnicas

| Artigo | DOI | Técnica aproveitável |
|---|---|---|
| Determining Optimal Therapy — Randomized Trials in Individual Patients (1986) | 10.1056/NEJM198604033141406 | Desenho N-of-1 com fases alternadas e randomização; base histórica. |
| SCRIBE 2016 (2016) | 10.1016/j.jclinepi.2016.04.006 | Relato de caso único: pré-registro, fases, medidas repetidas, cegamento, ética e limitações. |
| Autocorrelation and estimates of treatment effect size for SCED data (2021) | 10.1002/bin.1783 | Efeitos de SCED precisam considerar autocorrelação; não usar fórmulas de grupos independentes. |
| Standardized Effect Sizes for Autocorrelated SCED Data (2025) | 10.1007/s10864-025-09603-w | Simulação de tamanhos de efeito padronizados sob autocorrelação; escolha informada do estimador. |
| Visual Depictions of Rate of Improvement and Quantitative Effect Sizes (2022) | 10.1007/s10864-022-09500-6 | Análise visual e quantitativa devem ser combinadas, não substituídas uma pela outra. |
| EMA as a Measure of Intervention Change (2025) | 10.2196/69297 | EMA como medida repetida; exigências de validade e burden. |

### O que implementar

- **Runner N-of-1** (`core_cognition/n_of_1_runner.py`):
  - estados: `preregistered → recruiting → phase_A → washout → phase_B →
    analysis → report`;
  - agenda de randomização, lembretes, adesão, eventos adversos e parada;
  - lock do protocolo por hash; mudança exige emenda registrada.
- **Análise SCED** (`core_cognition/sced.py`):
  - Tau-U, NAP, PEM e Tau;
  - teste de randomização;
  - diagnóstico de autocorrelação (lag-1) e aviso quando o estimador não for
    adequado;
  - relatório com análise visual + quantitativa e limites.
- **Integração com `n_of_1.py`**: o validador atual passa a exigir instrumento,
  adesão mínima, eventos adversos e plano de dados faltantes.

### O que isso mitiga

Transforma o validador em **infraestrutura de execução e análise**. A execução
real ainda exige participante, consentimento, supervisão clínica e ética.

## 4. Limitação 3 — o ledger organiza, mas não vincula evidência

### Artigos e técnicas

| Artigo | DOI | Técnica aproveitável |
|---|---|---|
| Fact or Fiction: Verifying Scientific Claims (2020) | 10.18653/v1/2020.emnlp-main.609 | Formulação de verificação de claims científicos com evidência sentence-level; rótulos SUPPORT, CONTRADICT, INSUFFICIENT. |
| SciClaimHunt (2025) | 10.1109/ijcnn64981.2025.11227296 | Dataset e tarefa de verificação científica baseada em evidência; utilidade para esquema de anotação. |
| GraphRAG for Scientific Evidence Verification (2025) | sem DOI estável | Grafo claim–documento–entidade para recuperar evidência e rotular suporte. |
| MEVER (2026) | 10.48448/nz7j-bw62 | Verificação multimodal com recuperação de evidência em grafo e explicação. |
| W3C PROV (standard) | — | Modelo de proveniência: entidade, atividade, agente, uso e geração. |

### O que implementar

- **Grafo claim–evidência** (`core_cognition/claims_graph.py`):
  - nós: claim, fonte, trecho, teste, validação externa;
  - arestas: `supports`, `contradicts`, `insufficient`, `derived_from`;
  - cada aresta carrega fonte, hash, localizador e data.
- **Rótulos de suporte** no ledger: `supported`, `contradicted`,
  `insufficient`, `mixed`; nunca “verdadeiro” sem validação externa.
- **Detecção de contradições**: claims com evidência conflitante são marcados
  e enviados para revisão.
- **Proveniência PROV-like**: exportar JSON com `entity`, `activity`, `agent`,
  `used`, `generated`; integrar com `mci/evidence_graph.py`.
- **Recuperação, não produção**: o ledger pode buscar trechos em fontes já
  indexadas (arXiv, Crossref, RAG local), mas não inventa evidência.

### O que isso mitiga

O ledger deixa de ser apenas um registro e passa a **vincular, rotular e
contradizer** evidência. A produção de evidência continua sendo experimental
ou documental, não automática.

## 5. Limitação 4 — separar coordenação de warrant

### Artigos e técnicas

| Artigo | DOI | Técnica aproveitável |
|---|---|---|
| Trust in Automation: Designing for Appropriate Reliance (2004) | 10.1518/hfes.46.1.50_30392 | Confiança calibrada; reliance apropriada; distinguir confiança de verdade. |
| Adaptive Trust Calibration for Human-AI Collaboration (2020) | 10.1371/journal.pone.0229132 | Calibração adaptativa; detectar over-trust e under-trust. |
| Rapid Trust Calibration through Interpretable and Uncertainty-Aware AI (2020) | 10.1016/j.patter.2020.100049 | Explicações e incerteza para calibrar confiança rapidamente. |
| Effect of Confidence and Explanation on Accuracy and Trust Calibration (2020) | 10.1145/3351095.3372852 | Confiança declarada e explicação afetam calibração; medir separadamente. |
| Cognitive Transparency and Trust Calibration in XAI (2026) | 10.3389/fpsyg.2026.1924913 | Transparência cognitiva e reliance; modelo psicológico de dependência. |
| Uncertainty Quantification and Confidence Calibration in LLMs: A Survey (2025) | 10.1145/3711896.3736569 | UQ, selective prediction e abstenção. |
| LLM Uncertainty Proxies: Discrimination and Calibration (2024) | 10.1093/jamia/ocae254 | Proxies de incerteza para uso médico; discriminação e calibração. |
| Revisiting Uncertainty Estimation and Calibration of LLMs (2025) | 10.48550/arxiv.2505.23854 | Comparação ampla de métodos de incerteza; cuidado com calibração aparente. |

### O que implementar

- **Trust warrant** (`core_cognition/trust_warrant.py`):
  - `coordination_score`: trust/stake como sinal de alocação;
  - `calibration_score`: Brier, ECE e curva de confiabilidade, quando houver
    outcomes;
  - `evidence_status`: observação, inferência, testado, validado externamente;
  - `warrant`: `coordination_only` por padrão; `epistemic_warrant` só com
    validação externa.
- **Abstenção**: quando a evidência é insuficiente, o sistema recomenda
  `abstain` em vez de preencher a lacuna.
- **Explicação com incerteza**: relatar intervalo, evidência e limitação, não
  apenas um score.
- **Regra dura**: trust score e stake **nunca** promovem um claim a
  `externally_validated`.

### O que isso mitiga

Separa explicitamente **coordenação** de **warrant epistêmico**. A calibração
real exige histórico de acertos/erros; sem ele, o módulo reporta
`calibration_insufficient_data` em vez de inventar uma métrica.

## 6. Limitação 5 — ativar as stop rules no runtime

### Artigos e técnicas

| Artigo | DOI | Técnica aproveitável |
|---|---|---|
| Runtime Compliance Verification for AI Agents (2026) | 10.1007/978-3-032-41160-0_16 | Verificação de conformidade em runtime; contratos antes/depois de ações. |
| Policy-as-Prompt (2025) | 10.48550/arxiv.2509.23994 | Traduzir políticas em guardrails executáveis; política como código, não só prompt. |
| Action-Class Authority (2026) | 10.2139/ssrn.7095138 | Classificar ações por reversibilidade; verificação mais forte para ações irreversíveis. |
| Layered Translation Method for Runtime Guardrails (2026) | 10.48550/arxiv.2604.05229 | Tradução em camadas de normas para controles executáveis; auditoria por camada. |
| What Can Be Enforced? (2026) | 10.48550/arxiv.2607.22868 | Teoria de segurança certificada em runtime; limites do que um gate consegue observar. |
| Agent Safety Should Be a Runtime Contract (2026) | 10.48550/arxiv.2608.11274 | Segurança como contrato de runtime, não apenas treinamento. |
| Online Synthesis for Runtime Enforcement of Safety in Multiagent Systems (2021) | 10.1109/tcns.2021.3061900 | Síntese online de enforcement; modificar comportamento quando violação é detectada. |

### O que implementar

- **Contrato de runtime** (`core_cognition/runtime_contract.py`):
  - `ActionClass`: `read_only`, `reversible`, `irreversible`, `high_risk`;
  - `before_action()` e `after_action()`;
  - decisão `allow`, `ask`, `defer`, `block`;
  - circuit breaker por falhas, orçamento, violações repetidas e horário;
  - log auditável com decisão, regra, evidência e estado.
- **Integração no orquestrador**:
  - antes de `delegate`, `dispatch_ready` e execução de ferramenta;
  - depois de `report_completion`;
  - `block` impede o efeito colateral; `ask` escala para humano; `defer`
    preserva estado.
- **Classes de ação** no Agent Card / tool manifest:
  - ferramentas de leitura: `read_only`;
  - escrita reversível: `reversible`;
  - publicação, envio, exclusão, gasto: `irreversible` ou `high_risk`.
- **Auditoria**: todo `block`/`ask`/`defer` gera evento no MetaBus e registro
  no `cycles`/ledger.

### O que isso mitiga

Ativa as stop rules no loop real, com contrato, classes de ação e auditoria.
Não garante segurança completa: o artigo “What Can Be Enforced?” lembra que o
gate só aplica o que consegue observar e representar.

## 7. Roadmap priorizado

| Ordem | Spec proposta | Entrega | Dependência | Impacto |
|---|---|---|---|---|
| 1 | **R1133 — Runtime contract e stop rules ativas** | `runtime_contract.py` + hooks no orquestrador + classes de ação | Nenhuma | Alto: fecha a limitação 5 |
| 2 | **R1134 — Claims graph e proveniência** | `claims_graph.py`, links, contradições, PROV-like | `claims_ledger.py`, `mci/evidence_graph.py` | Alto: fecha a limitação 3 |
| 3 | **R1135 — Trust warrant e calibração** | `trust_warrant.py`, Brier/ECE, abstenção | Histórico de outcomes | Médio-alto: fecha a limitação 4 |
| 4 | **R1136 — Measurement contract e EMA** | `measurement.py`, instrumentos, EMA, transfer test | Dados do usuário | Médio: mitiga a limitação 1 |
| 5 | **R1137 — N-of-1 runner e SCED** | `n_of_1_runner.py`, `sced.py`, Tau-U/NAP/PEM | R1136, ética e supervisão | Médio: mitiga a limitação 2 |

**Recomendação:** começar por R1133 (runtime) e R1134 (claims graph). São os
dois avanços com menor dependência de dados clínicos e maior efeito imediato
sobre o Core. R1135 pode começar com dados sintéticos/auto-relatados, mas só
produz calibração útil com outcomes reais. R1136/R1137 exigem participante,
instrumentos validados e supervisão clínica; são pesquisa, não feature.

**Status R1133:** implementado em `core_cognition/runtime_contract.py` e
integrado ao orquestrador. Ver `SPEC-935-R1133-runtime-contract-stop-rules.md`
e `tests/test_r1133_runtime_contract.py`.

## 8. O que não pode ser resolvido só por software

- **Eficácia cognitiva:** exige instrumentos validados, dados do usuário,
  comparadores e revisão independente.
- **Validação clínica:** exige desenho aprovado por ética, supervisão e
  desfechos clínicos.
- **Generalização:** um caso único não sustenta afirmações populacionais.
- **Verdade:** um ledger, um grafo ou uma calibração não produzem verdade;
  organizam evidência e incerteza.
- **Segurança completa:** um gate só aplica o que consegue observar; ações
  irreversíveis exigem classes próprias e revisão humana.

## 9. Referências

As referências novas estão nas tabelas acima, com título e DOI. A lista abaixo
cobre as obras clássicas e os padrões usados no desenho.

ADAMS, F.; AIZAWA, K. The bounds of cognition. *Philosophical Psychology*,
v. 14, n. 1, p. 43–64, 2001. DOI: 10.1080/09515080120033571.

ALFRINK, K. et al. Contestable AI by design: towards a framework. *Minds and
Machines*, v. 32, 2022. DOI: 10.1007/s11023-022-09611-z.

CHEN, A. et al. Policy-as-Prompt: turning AI governance rules into guardrails
for AI agents. arXiv:2509.23994, 2025. DOI: 10.48550/arxiv.2509.23994.

FRIEDMAN, B. et al. Value-sensitive design and information systems. In:
*The Handbook of Information and Computer Ethics*, 2006.

GUYATT, G. et al. Determining optimal therapy — randomized trials in individual
patients. *New England Journal of Medicine*, v. 314, n. 14, p. 889–892, 1986.
DOI: 10.1056/NEJM198604033141406.

HARDWIG, J. Epistemic dependence. *The Journal of Philosophy*, v. 82, n. 7,
p. 335–349, 1985. DOI: 10.2307/2026523.

HORVITZ, E. Principles of mixed-initiative user interfaces. In: *CHI ’99*,
p. 159–166, 1999. DOI: 10.1145/302979.303030.

LEE, J. D.; SEE, K. A. Trust in automation: designing for appropriate reliance.
*Human Factors*, v. 46, n. 1, p. 50–80, 2004. DOI: 10.1518/hfes.46.1.50_30392.

MARK, G. et al. No task left behind? Examining the nature of fragmented work.
In: *CHI ’05*, p. 321–330, 2005. DOI: 10.1145/1054972.1055017.

NOSEK, B. A. et al. The preregistration revolution. *PNAS*, v. 115, n. 11,
p. 2600–2606, 2018. DOI: 10.1073/pnas.1708274114.

PARASURAMAN, R.; RILEY, V. Humans and automation: use, misuse, disuse, abuse.
*Human Factors*, v. 39, n. 2, p. 230–253, 1997. DOI:
10.1518/001872097778543886.

RISKO, E. F.; GILBERT, S. J. Cognitive offloading. *Trends in Cognitive
Sciences*, v. 20, n. 9, p. 676–688, 2016. DOI: 10.1016/j.tics.2016.07.002.

TATE, R. L. et al. The Single-Case Reporting Guideline In BEhavioural
Interventions (SCRIBE) 2016 statement. *Journal of Clinical Epidemiology*,
v. 73, p. 142–152, 2016. DOI: 10.1016/j.jclinepi.2016.04.006.

TRONTO, J. C. *Moral boundaries: a political argument for an ethic of care*.
Routledge, 1993.

WEISER, M.; BROWN, J. S. The coming age of calm technology. In: *Beyond
Calculation*, p. 75–85, 1997. DOI: 10.1007/978-1-4612-0685-9_6.
