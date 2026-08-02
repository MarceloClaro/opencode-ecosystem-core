---
spec_id: SPEC-935-R369
title: Andaimes de raciocínio produtivo científico-literário + gates de honestidade
component: reasoning/production_scaffolds.py
status: verified
test_file: tests/test_r369_production_scaffolds.py
---

# SPEC-935-R369 — Andaimes de Raciocínio Produtivo

**Data:** 2026-08-02
**Motivação:** o ecossistema tem motores de raciocínio (SPEC-917: 11 motores;
ARCHE RLT/Peirce) e agentes de produção (acadêmicos 00–33, literários), mas
nenhuma ponte contratual entre raciocínio e produto final. "Artigos
cientificamente relevantes e inovadores" e "obras literárias disruptivas" não
podem ser prometidos por software (CORRIGENDUM); o que o software pode
garantir é que (a) os **movimentos de raciocínio** obrigatórios do gênero
estejam presentes e auditáveis, (b) alegações de novidade sejam
**argumentadas, não anunciadas**, e (c) a distintividade literária seja
**medida descritivamente**, nunca decretada.

## 1. Componentes

### 1.1 Andaime científico (`SCIENTIFIC_MOVES`)

Movimentos obrigatórios para artigo/tese/dissertação, cada um com marcadores
determinísticos pt/en e `engine_hint` mapeando para os motores existentes
(`reasoning/engines.py`) e os tipos de Peirce (ARCHE):

| move | engine_hint | exemplo de marcadores |
|---|---|---|
| problema | critical | problema, problem, questão de pesquisa |
| lacuna | abducao/critical | lacuna, gap, não há estudos, pouco explorado |
| hipotese | abducao/bayesian | hipótese, hypothesis, H1, conjectura |
| metodo | deducao/causal | método, methodology, procedimento, amostra |
| evidencia | inducao/bayesian | resultados, evidência, tabela, p <, IC |
| contra_argumento | counterfactual/critical | contra-argumento, alternativa, entretanto |
| limitacao | critical | limitação, limitations, ameaças à validade |
| contribuicao | analogical | contribuição, contribution, implicações |

### 1.2 `audit_scientific_manuscript(sections)`

- Entrada: mapeamento `{nome_da_secao: texto}` (fail-closed se vazio/inválido).
- Achado `MISSING_MOVE` (medium; high para `metodo`, `evidencia` e
  `limitacao`) quando nenhum marcador do movimento aparece em nenhuma seção.
- **Auditoria de novidade:** termos de novidade (`inédito`, `inovador`,
  `pioneiro`, `primeiro`, `novel`, `unprecedented`, `state-of-the-art`)
  exigem, na mesma frase, um ancoradouro de comparação ou citação
  (`\cite{}`, `[n]`, `(Autor, ano)`, "em comparação", "diferente de",
  "compared to", "unlike"). Sem ancoradouro → `UNSUPPORTED_NOVELTY_CLAIM`
  (high). Novidade se argumenta contra literatura, não se decreta.
- Saída: envelope determinístico com `findings[]`, `moves_presentes`,
  `human_gate` (`required` se houver high) e disclaimer (a presença de
  movimentos não atesta relevância científica).

### 1.3 Andaime literário (`LITERARY_PLAN_FIELDS` + validação)

Plano de obra contratual (`validate_literary_plan`): `voz` (descrição),
`conflito_central`, `simbolos` (lista não vazia), `estrategia_estranhamento`
(o que a obra faz de não óbvio) e `cliches_a_evitar` (lista, pode ser vazia).
Fail-closed. O plano força o raciocínio literário a ser explícito antes da
escrita — sem prometer que o resultado será "disruptivo".

### 1.4 `literary_distinctiveness_report(text)`

Relatório **medido e descritivo** (nunca veredito): razão type-token,
média e desvio do comprimento de frases, contagens de marcas rítmicas
(`?`, `!`, reticências, travessão), acertos num léxico curado de clichês
pt (≥ 20 expressões: "lágrimas amargas", "silêncio ensurdecedor", "frio na
espinha", "coração partido"...), e os símbolos recorrentes (tokens de
conteúdo mais repetidos). Campos `measured: true`,
`claim: internal-descriptive-measurement` e disclaimer explícito:
distintividade medida ≠ qualidade nem disrupção literária.

### 1.5 `select_scaffold(task_description)`

Ponte com a camada epistêmica (R363/R368): usa `infer_task_episteme` —
`empirico_analitico`/`formal_dedutivo` → `scientific`;
`hermeneutico_interpretativo` → `literary`; demais regimes ou episteme
indeterminada → `indeterminate` (fail-open: cabe a humano/orquestrador
escolher; nunca chuta).

## 2. Critérios de aceitação

1. Manuscrito completo (8 movimentos) → zero `MISSING_MOVE`.
2. Manuscrito sem método/limitação → achados high e `human_gate=required`.
3. "abordagem inédita" sem ancoradouro → `UNSUPPORTED_NOVELTY_CLAIM`;
   com `\cite{}` ou "em comparação com X" na mesma frase → sem achado.
4. Plano literário sem símbolos ou sem estranhamento → `ContractError`.
5. Relatório de distintividade: campos medidos, clichês detectados,
   determinismo bit a bit, disclaimer presente.
6. `select_scaffold`: tarefa estatística → scientific; tarefa de tradução
   literária → literary; texto sem sinais → indeterminate.
7. Todos os movimentos científicos têm `engine_hint` existente no pacote
   `reasoning` (coerência com SPEC-917).
