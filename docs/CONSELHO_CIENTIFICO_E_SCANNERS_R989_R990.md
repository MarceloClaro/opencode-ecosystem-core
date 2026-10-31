# Conselho científico e evolução delimitada dos scanners — R989/R990

## Implementado e limites de autoridade

São **13 agentes computacionais**, sob MarceloClaro, com perfis gerenciados no
catálogo e contrato SDD/TDD. Não são pesquisadores humanos nem 13 validações
independentes: podem compartilhar modelo e fontes. A autonomia é sequencial,
delimitada e interrompida quando falta evidência ou execução confirmada.

| # | Perfil | Função |
|---|---|---|
| 1 | `scientist-problem` | Pergunta, hipóteses e critérios de refutação |
| 2 | `scientist-search` | Estratégia de busca reproduzível e lacunas |
| 3 | `scientist-curation` | Triagem, duplicatas e decisões de inclusão |
| 4 | `scientist-references` | Referências e correspondência de recortes |
| 5 | `scientist-methodology` | Desenho, paradigma e instrumentos |
| 6 | `scientist-statistics` | Análise quantitativa e incerteza |
| 7 | `scientist-qualitative` | Interpretação, reflexividade e casos negativos |
| 8 | `scientist-reproduction` | Dados, ambiente, código e recibos de reprodução |
| 9 | `scientist-feynman` | Explicação clara, lacunas e teste de transferência |
| 10 | `scientist-falsification` | Contraexemplos e hipóteses rivais |
| 11 | `scientist-game-theory` | Decisão de investigação sob utilidades declaradas |
| 12 | `scientist-ethics` | Consentimento, privacidade, licença e proveniência |
| 13 | `scientist-audit` | Síntese crítica, conflitos e revisão humana |

O primário criou os perfis por `agent_profile_action`, com `allow_edit=false`.
Leitura é permitida; edição, rede direta e delegação fora do primário são negadas.
Os dois comandos Bash permitidos em cada cartão são o doctor estrutural e o
teste vinculado à spec. Não existe um novo armazenamento de notas ou confiança.
**Reinicie o OpenCode** para carregar os novos perfis na interface.

## O que a lógica Feynman faz

Cada parecer contém `status`, `findings`, `evidence`, `limitations` e `feynman`.
O bloco Feynman explicita mecanismo, observações, inferências, refutador e menor
experimento. `FeynmanGates` é reutilizado somente para checklist declarativo
FEG-01..06. Não invocamos `teachback` nem produzimos selo de validação humana.
Uma explicação fluente ou pontuação alta não comprova entendimento ou verdade.

Os recortes devem aparecer literalmente em uma fonte identificada do corpus.
O hash confirma correspondência aos bytes fornecidos; **não** confirma autoria,
autenticidade, adequação da citação ao argumento ou qualidade do estudo.

## Teoria dos jogos sem transferir regras clínicas

O motor clínico existente contém `ClinicalGameTheoryEngine.compute_minimax_regret`.
Reaproveita-se o **critério matemático**, não seus parâmetros, diagnósticos,
sensibilidades, priors ou custos clínicos:

`R(s,a) = max_b U(s,b) - U(s,a)`; escolher ações que minimizem `max_s R(s,a)`.

`scientific_lab.council.minimax_regret` recebe uma matriz explícita estado→ação→
utilidade, exige valores finitos e todas as ações em cada estado, e retorna os
empates sem desempate oculto. É um auxílio à priorização de investigação. Não é
equilíbrio de Nash, consenso científico, estimativa causal nem recomendação clínica.

```python
from scientific_lab.council import minimax_regret
result = minimax_regret({
    "hipotese_1": {"replicar": 10, "nova_busca": 6},
    "hipotese_2": {"replicar": 0, "nova_busca": 6},
})
# Exemplo de utilidades declaradas, não dados empíricos:
# arrependimentos máximos replicar=6, nova_busca=4.
```

## Uso

Sem inferência ou rede:

```bash
python3 -m marceloclaro.scientific_lab council list
python3 -m marceloclaro.scientific_lab council plan --question "Como refutar esta hipótese?"
```

Execução real opt-in, com **texto não sensível** e executor autenticado:

```bash
python3 -m marceloclaro.scientific_lab council run \
  --question "Que evidência falta para avaliar este protocolo?" \
  --sources-json '[{"id":"p1","text":"Protocolo de demonstração sem resultados.","provenance":"Exemplo didático, não estudo empírico"}]' \
  --executor codex --confirm --timeout 120 --max-agents 1
```

`--confirm` autoriza enviar esse corpus ao executor configurado, sujeito à conta
e aos custos desse serviço. Sem confirmação, não há chamada. Máximo: 13 papéis,
uma tentativa por papel, 600s no total. `--max-agents 1` é um smoke test, não o
conselho completo. `queued`, ausência de tentativa, agente diferente, JSON inválido,
recorte inexistente, prazo expirado ou parecer parcial interrompem o fluxo.

`completed_review` significa apenas que os 13 pareceres estruturados foram
entregues no orçamento. Sempre `external_validation=false` e revisão humana.
Relatórios brutos são devolvidos; os próximos agentes recebem resumos delimitados,
explicitamente não exaustivos. Conflitos sem resolução não podem ser apagados por
votação. Nenhuma busca externa ou reprodução computacional é inferida de texto.

A busca neste ciclo é estratégia e análise do corpus fornecido. Coleta real deve
passar pelos conectores autorizados de MarceloClaro e trazer recibos. A execução
não tem uma nova barreira de sandbox: OpenShell continua separado e pendente.

## Scanners: o que mudou

O `ScientificReasoningScanner` existente agora retorna `triage` com hash, alertas,
offsets **do texto normalizado**, estado afirmativo/negado/citado/título e abstenção.
Aspas duplas em uma linha recebem contexto de citação; isso é heurístico e não
resolve endosso, ironia, aspas multilinha ou negação distante. Alertas não são
apagados: citações passam a pedir revisão contextual. Até 200 recortes são
retornados, com contagem total e indicação de truncamento. Entrada: até 1 milhão
de caracteres também na API Python direta.

Scores e rótulos antigos permanecem por compatibilidade. No scanner e no
`SuperRigorPipeline`, `authority` torna explícito que a triagem **não** certifica
ciência, autoriza publicação, promove confiança ou muda políticas. Um `passed`
legado é um limiar heurístico, não aceite editorial.

`scanners.scientific_evolution.evaluate_candidates` executa uma avaliação local
de dois candidatos fixos (`legacy`, `contextual`), sem código/regex arbitrário:

1. Exige 8–200 casos rotulados e corpus até 256 KB; pelo menos quatro casos e
   ambas as classes por partição (`dev`, `holdout`).
2. Recusa IDs/textos repetidos e grupos compartilhados entre as partições.
3. Escolhe pelo desenvolvimento; não troca o candidato em função do holdout.
4. Computa TP/FP/TN/FN, precisão, recall e acurácia balanceada. Zero no
   denominador resulta em `null`, nunca em pontuação perfeita.
5. Bloqueia recomendação se FP ou FN aumentarem no holdout. Informa o delta e
   `holdout_improvement`: uma recomendação não regressiva pode ter empate no holdout.
6. Produz tarefas propostas para refutação, estatística e auditoria. Não aciona
   esses agentes, modifica código, atualiza trust ou se autopromove.

Formato de caso: `{"id":"c1","group":"documento1","split":"dev","text":"...","label":true}`.
O rótulo indica um **gatilho categórico afirmado pelo autor**, não verdade ou
falsidade científica. Grupos/rótulos são declarados pelo fornecedor. O teste de
software usa exemplos sintéticos; não há calibração externa. Não reutilizar o
holdout como feedback para otimização sucessiva sem um novo conjunto congelado.

```bash
python3 -m marceloclaro.scientific_lab scanner-evolve --corpus-json '<lista de casos>'
```

Esta entrega melhora o scanner científico e seu resultado combinado. Não afirma
que os scanners noológico, literário, social ou jurídico foram todos recalibrados.

## Decisões de curadoria preservadas

- [Feynman Tutor, revisão 9e9ec6f](https://github.com/koukekoukej-glitch/feynman-tutor/tree/9e9ec6fa08bd2242b7aea1cf3419e28ea2e70664):
  MIT; inspiração para explicação e crítica. Launcher/extratores e memória paralela
  não foram incorporados. Adaptação de protocolo, não execução upstream.
- [OpenTwins, revisão f0317fe](https://github.com/ertis-research/opentwins/tree/f0317fef7fb3b841ad707ea51056101be39e1569):
  Apache-2.0 declarado; referência de gêmeos digitais para estudo específico,
  não novo stack do Core. O README consultado desaconselha produção.
- [OpenShell, revisão 42671c2](https://github.com/NVIDIA/OpenShell/tree/42671c2dd2c02b744850e0bda72b99d5509969c1):
  Apache-2.0 declarado; sandbox opcional. CLI/SDK ausentes na sondagem anterior;
  Podman presente não comprova disponibilidade. Nenhuma instalação foi feita.
  Piloto futuro exige release/imagem pinados, autorização e ensaios reais de
  egress, filesystem, telemetria, limpeza e recuperação. SDK PyPI não instala CLI.

Fontes históricas: `docs/AVALIACAO_REPOS_R888_B.md`,
`docs/AVALIACAO_REPOS_R888_A.md`, `docs/AVALIACAO_REPOS_METACOGNICA_R886.md`.
Revisão textual delegada de trechos não equivale a revisão por pares, execução do
conselho completo ou validação de segurança de runtime.
