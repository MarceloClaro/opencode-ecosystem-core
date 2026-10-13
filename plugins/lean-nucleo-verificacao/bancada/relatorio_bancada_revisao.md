# Relatório interno honesto — bancada + revisões (R756/R757)

Data: 2026-10-10. Ambiente: Core local, sem rede executada pelos revisores.
Revisores Task 28/31 falharam (free tier fora do OpenCode — registrado);
revisões independentes obtidas via executor codex com fallback (claude em
limite de conta). Não são revisão cega nem externa.

## 1. Bancada (bancada_routing.py, 200 decisões, 5 seeds)

| Estratégia | regret médio ± IC95 | hit rate ± IC95 |
|---|---|---|
| atenção (router real) | 0,0421 ± 0,0105 | 0,625 ± 0,067 |
| aleatório | 0,1882 ± 0,0219 | 0,200 ± 0,055 |
| menor-carga | 0,2167 ± 0,0250 | 0,215 ± 0,057 |
| maior-cobertura | 0,2118 ± 0,0215 | 0,165 ± 0,051 |

Latência média 2,17 ms (máx 31 ms); softmax soma 1 (desvio máx 1,1e-16).
Oráculo oculto: cobertura×(0,4+0,6q), q latente nunca vista pelo roteador.
IC95 = aproximação normal (média ± 1,96·dp/√n) — documentado aqui, pois foi
cobrado na revisão. Hit = escolha coincide com o máximo do oráculo.

## 2. Auditoria da bancada — veredito: evidência preliminar restrita

Falhas aceitas: (a) confiança observável correlacionada com q é proxy
privilegiada — risco de circularidade real; exigir ablação com confiança
independente/ruidosa/anticorrelacionada; (b) baselines fracos (maior-cobertura
ignora q por construção); faltam comparadores que combinem sinais + ablações
do próprio router; (c) 200 decisões ≠ 200 observações independentes; 5 seeds
limitam precisão; análise deve ser pareada por tarefa/seed; (d) sem tarefas
reais, sem LangGraph/CrewAI executados, sem métricas de custo/falha — nada
externo se sustenta. Condições de publicabilidade: eliminar proxies,
comparadores fortes, protocolo reproduzível (script + seeds já publicados
neste diretório).

## 3. Revisão dos teoremas — veredito: REVISÃO MAIOR

Objeções que ficam de pé: (a) "teorema de eficiência" excede 6 lemas de
normalização/existência — eficiência operacional não demonstrada; (b) analogia
Transformer é cosmética até haver correspondência Q/K/V ↔ escores do router;
(c) lacuna floats/top-k/gates ↔ objetos reais formalizados; (d) originalidade
dos lemas (fatos elementares) deve ser explicitada, não presumida.
Parcialmente já respondidas no artefato (revisor não viu os arquivos): T5 exige
`Nontrivial` (singleton excluído); hipóteses de finitude explicitadas;
`machine_checked` reproduzível via projeto pinado v4.34.1 + teste R755.
A fazer: auditoria `#print axioms`, correspondência Q/K/V formal, top-k,
erro numérico float vs Real, empates.

## 4. Conclusão

Nada aqui autoriza "inovador/disruptivo". Autoriza: "roteamento por atenção
com otimalidade relativa provada por máquina, calibração empírica interna
(regret 0,04 vs 0,19–0,22 dos baselines ingênuos, ICs sem sobreposição) e
trilha de reprodução publicada — evidência preliminar, sob revisão maior".

## 5. Cobertura das lacunas com prova e contraprova (R758)

Prova nova — **T7 `softmax_peso_total_singleton`**: candidato único recebe
peso 1, complementando T5 e fechando o singleton nos dois casos. A primeira
versão carregou `sorryAx` por erro de aplicação (`sum_eq_single_of_mem`
exige o elemento explícito); a auditoria `#print axioms` pegou, corrigido:
**7/7 só com `[propext, Classical.choice, Quot.sound]`** (`axiomas.txt`).

Contraprova numérica (`contraprova_float.py`, 20k vetores): 0 violações —
soma (pior 2,2e-16), limites, invariância a shift (0,00), argmax preservado,
singleton=[1.0], vazio=[]. Ponte float↔Real documentada.

ablações (`bancada_ablacao.py`, 200 decisões cada, pareado):

| qw | atenção | media_igual (diff) | sem_confianca (diff) | conf_anti (diff) |
|---|---|---|---|---|
| 0,3 | 0,0146 | 0,0319 (+0,017) | 0,1072 (+0,093) | 0,1802 (+0,166) |
| 0,6 | 0,0292 | 0,0638 (+0,035) | 0,2144 (+0,185) | 0,3604 (+0,331) |
| 0,9 | 0,0438 | 0,0957 (+0,052) | 0,3216 (+0,278) | 0,5406 (+0,497) |

Atenção vence nos 3 mundos; fusão ponderada supera pesos iguais sempre
(win 0,99). Achado desconfortável registrado: **sem a cabeça de confiança, o
roteador ≈ aleatório neste simulador** — a vantagem depende de reputação
calibrada, e o peso do oráculo em q comanda a magnitude. A sensibilidade
responde "pesos arbitrários": ranking estável em qw ∈ {0,3; 0,6; 0,9}.

Restante (fora do pacote eficiente): top-k formal, temperatura, Q/K/V
formal, erro numérico certificado, benchmark externo head-to-head.
