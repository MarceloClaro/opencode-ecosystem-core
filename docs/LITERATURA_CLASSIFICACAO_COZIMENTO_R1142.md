# Literatura — classificação quântica e “cozimento quântico”

**Data:** 2026-11-10
**Pergunta:** que técnicas reais de artigos avançados podem ser incorporadas ao
Core/GJQ para investigar classificação quântica e otimização de processos
culinários, e quais gaps precisam ser mitigados?

## 1. Achado sobre “cozimento quântico”

A busca Crossref por `quantum cooking food optimization` **não retornou artigo
estabelecido de cozimento quântico**. O resultado relevante foi um trabalho de
**machine learning clássico** para otimização de cozimento de grãos e legumes:

- *Smart cooking optimization: Machine learning modeling of soaking and cooking
  dynamics in rice and legumes*, Food Science and Preservation (2026),
  DOI `10.11002/fsp.2026.33.4.586`.

Portanto, o Core trata “cozimento quântico” como **otimização híbrida de
decisões de processo** (temperatura, tempo, cobertura, pré-aquecimento), não
como campo científico consolidado. O baseline é clássico; QAOA/VQE são
avaliados em QUBO sintético, sem dados sensoriais reais.

## 2. Classificação quântica — fontes e técnicas

| Fonte | DOI | Técnica | Gap que o Core deve testar |
|---|---|---|---|
| Havlíček et al., *Supervised learning with quantum-enhanced feature spaces*, Nature 567, 209 (2019) | `10.1038/s41586-019-0980-2` | feature map quântico e kernel por superposição; classifier em espaço de feature | escolha do feature map, custo do kernel, concorrência clássica, ruído |
| Schuld & Killoran, *Quantum machine learning in feature Hilbert spaces*, PRL 122, 040504 (2019) | `10.1103/PhysRevLett.122.040504` | feature Hilbert spaces e kernels | concentração do kernel, dimensão efetiva, dados clássicos |
| Huang et al., *Power of data in quantum machine learning*, Nat. Commun. 12, 2631 (2021) | `10.1038/s41467-021-22539-9` | projected quantum model; limites de vantagem com dados | vantagem só em regimes/estruturas específicas; baselines clássicos fortes |
| Caro et al., *Generalization in quantum machine learning from few training data*, Nat. Commun. 13, 4919 (2022) | `10.1038/s41467-022-32550-3` | erro de generalização `sqrt(T/N)`/`sqrt(K/N)` | poucos dados, número de gates treináveis, overfitting |
| Cerezo et al., *Variational quantum algorithms*, Nat. Rev. Phys. 3, 625 (2021) | `10.1038/s42254-021-00348-9` | VQA, ansatz, trainability | barren plateaus, custo de medição, ruído |

## 3. Técnicas extraídas

1. **Kernel quântico por fidelidade** e kernel ridge clássico como baseline.
2. **Feature map ZZ** com repetições; medir concentração e sensibilidade.
3. **Split sem vazamento**, curva de aprendizado e matriz de confusão.
4. **Baseline clássico forte** (RBF/kernel ridge) antes de qualquer alegação
   quântica.
5. **Modelo projetado / dados estruturados** para investigar quando há sinal
   além do clássico (Huang 2021).
6. **Generalização** como função de `N`, `T` e `K` (Caro 2022).
7. **QAOA/VQE** para QUBO de processo, com brute force e baseline aleatório.

## 4. Gaps e mitigações no Core

| Gap | Mitigação implementada/planejada |
|---|---|
| dataset pequeno e sintético | split explícito, leakage audit, curva de aprendizado |
| feature map arbitrário | kernel ZZ declarado; comparação com RBF |
| kernel concentration | auditoria de posto/autovalores planejada |
| ruído e shots | simulação sem ruído no piloto; ruído só com gate explícito |
| barren plateaus | QAOA p=1 e ansatz raso; sem alegação de escala |
| concorrência clássica | kernel ridge e RBF no mesmo split |
| cozimento sem literatura quântica | QUBO sintético, baseline clássico e validação sensorial obrigatória |
| generalização | relatório de acurácia treino/teste e tamanho amostral |

## 5. O que o framework entrega

- `quantum_research.classification`: dataset, feature map, kernel quântico,
  kernel ridge, RBF, leakage e auditoria.
- `quantum_research.cooking`: QUBO de 4 decisões, brute force, QAOA e baseline
  aleatório.
- `gjq_research_framework.plan(domain="classification"|"cooking")`: fases,
  gates e agentes específicos.

## 6. Limites

- Nenhum resultado desta rodada demonstra vantagem quântica.
- O dataset é sintético; o QUBO é sintético; não há dados sensoriais.
- O artigo de cozimento é clássico; não foi executado.
- A classificação quântica foi simulada por statevector, sem ruído.
- Um resultado favorável exigiria dados reais, baselines fortes, validação
  externa e revisão humana.
