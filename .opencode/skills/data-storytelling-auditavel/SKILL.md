---
name: data-storytelling-auditavel
description: >-
  Transforma dados em figura e narrativa auditáveis: escolha de codificação,
  título-mensagem, legenda de quatro camadas, fonte rastreável e nota
  metodológica (n, período, filtros, definições e limitações), com gate
  determinístico para eixo truncado, duplo eixo, 3D, pizza sobrecarregada,
  causalidade indevida, incerteza ausente e unidade omitida. Renderiza SVG
  acessível e sela o dossiê com SHA-256 (SPEC-935-R1003). Use para relatórios,
  artigos, dashboards, slides e prestação de contas. Não promete qualidade
  estética, aceite editorial ou causalidade; exige revisão humana.
---

# Data Storytelling Auditável (SPEC-935-R1003)

## 1. Princípio operacional

**Uma figura, uma decisão.** Se o leitor não consegue enunciar a conclusão em
uma frase depois de 10 segundos, aquilo é um gráfico — não uma história.

A skill não pergunta "qual gráfico fica bonito?". Pergunta:

1. Que decisão esta figura deve sustentar?
2. Qual é a mensagem, com número e comparador?
3. Qual codificação torna a comparação honesta?
4. Que legenda, fonte e nota permitem reconstruir a leitura?
5. O que os dados **não** permitem concluir?

Sem resposta para as cinco, não há entrega.

## 2. Quando usar — e quando não usar

**Use quando:**

- houver dados reais (ou sintéticos claramente rotulados) e uma mensagem a
  comunicar;
- a figura for para artigo, relatório, slide, dashboard, parecer ou prestação
  de contas;
- for preciso auditar escala, cor, incerteza, denominador ou linguagem causal;
- a entrega exigir legenda, fonte e nota metodológica rastreáveis;
- for necessário reproduzir o artefato e provar integridade por hash.

**Não use quando:**

- o objetivo for inferência estatística, desenho causal ou meta-análise →
  `inferencia-quantitativa-avancada` / `pesquisa-artigo-qualis-a1`;
- a tarefa for identidade visual, tipografia ou direção de arte → skill de
  design;
- o alvo for mapa, rede, treemap complexo ou animação → a auditoria serve, mas
  o render embutido não cobre;
- não houver dados: produza protocolo e critérios de coleta. **Nunca invente
  número para preencher figura.**

## 3. Contrato de legenda e nota (quatro camadas)

No Brasil, "legenda" costuma designar o bloco sob (ou sobre) a figura; em
normas editoriais, o título fica acima e a fonte abaixo. Para eliminar a
ambiguidade, esta skill separa **quatro camadas obrigatórias**:

| Camada | Pergunta que responde | Obrigatória | Exemplo |
|---|---|---|---|
| **L1. Rótulo** | Qual é a figura? | Sim | `Gráfico 1 –` |
| **L2. Título-mensagem** | O que o leitor deve concluir? | Sim | `Cobertura passa de 41% para 83% em quatro anos` |
| **L3. Chave visual** | Como ler cor, tamanho e unidade? | Quando houver codificação | `Legenda: barras azuis = cobertura anual; unidade: %` |
| **L4. Fonte + Nota** | De onde veio e como foi produzido? | Sim | `Fonte: IBGE (2024). Nota: ... n = 120; período 2020–2024; ...` |

**Regras de composição:**

- Título sem ponto final, com no máximo 140 caracteres.
- Título nomeia o **achado**, não o tipo: "Cobertura dobra", não "Gráfico de
  barras".
- Título e nota não repetem a mesma frase; a nota aprofunda o método.
- Fonte com instituição, **ano de quatro dígitos** e URL/DOI quando existirem.
- Nota com **número** (n, período, medida) e **método**.
- Placeholders (`TODO`, `TBD`, `XXX`, `lorem`, `preencher`, `inserir`) são erro
  de entrega, não rascunho aceitável.
- Em ABNT, a estrutura usual é título acima, fonte abaixo; periódicos variam.
  **Confirme o manual do destino** — a skill não declara conformidade
  normativa automática.

### 3.1 Template de nota

```text
Nota: [o que a medida é, com numerador e denominador]. n = [n].
Período: [início–fim]. Filtros: [recorte]. Definições: [como o indicador foi
calculado, tratamento de ausentes]. Limitação: [o que o desenho não permite
concluir].
Fonte: [Instituição] ([ano]), [URL ou DOI]. [Elaboração própria com base em ...].
```

### 3.2 Contraste: nota fraca × nota auditável

| Nota fraca | Problema | Nota auditável |
|---|---|---|
| `Fonte: IBGE.` | sem ano nem identificador | ```Fonte: IBGE (2024), https://...``` |
| `Nota: dados tratados.` | não diz o quê, nem n, nem método | ```Nota: percentual de municípios com cobertura declarada; n = 120; período 2020–2024; sem imputação; não permite inferir causalidade.``` |
| `Nota: ver metodologia.` | terceiriza a explicação | ```Nota: média aritmética das 5 edições; n = 27 unidades; ausentes excluídos; comparável apenas dentro da série.``` |
| `Fonte: elaboração própria.` | sem base | ```Fonte: elaboração própria com base em IBGE (2024).``` |

## 4. Pipeline de sete etapas

### Etapa 0 — Enquadrar a decisão

Produza uma frase para cada item:

- **Público:** quem decide e o que já sabe.
- **Decisão:** o que muda se a mensagem for aceita.
- **Mensagem:** sujeito + resultado + comparador + período.
- **Contra-mensagem:** a leitura alternativa que os dados permitem.
- **Consequência de errar:** o custo de um gráfico enganoso.

Saída: `storyline` curta. Sem isso, não avance.

### Etapa 1 — Perfilar os dados

```python
from skills.data_storytelling import profile_dataset
profile = profile_dataset(rows)  # teto padrão: 50.000 linhas
```

Verifique:

- `n_rows`, tipos inferidos, `missing`, `ragged_rows`;
- se o campo numérico é realmente numérico (não código com máscara);
- se o campo temporal tem granularidade declarada;
- se `source_sha256` corresponde ao arquivo que será citado.

Limite: o perfil descreve os bytes recebidos; **não valida verdade,
representatividade ou causalidade**.

### Etapa 2 — Escolher a codificação

```python
from skills.data_storytelling import recommend_chart
rec = recommend_chart(profile, intent="comparison", emphasis="regiao")
```

Intenções aceitas: `trend`, `comparison`, `ranking`, `composition`,
`distribution`, `relationship`, `deviation`.

| Intenção | Primeira escolha | Condição | Nunca |
|---|---|---|---|
| Tendência | `line` | eixo X temporal ordenado | pizza, barras com base ≠ 0 |
| Comparação | `bar` | base zero, poucas categorias | pizza com muitas fatias |
| Ranking | `bar` horizontal ordenada | ordem por valor | ordem alfabética |
| Composição | `stacked_bar` | soma visível; 5–7 categorias | pizza > 4 fatias |
| Distribuição | `histogram` (n ≥ 30) / `dot` (n < 30) | bins declarados | pizza, média sem dispersão |
| Relação | `scatter` | controlar sobreposição > 500 pontos | inferir causalidade |
| Desvio | `diverging_bar` | zero explícito no centro | pizza, eixo truncado |

### Etapa 3 — Escrever o título-mensagem

Checklist:

- [ ] contém sujeito e resultado;
- [ ] contém número ou comparador;
- [ ] não começa com "Gráfico", "Figura" ou "Tabela";
- [ ] não usa hipérbole sem magnitude;
- [ ] não afirma causalidade sem desenho causal;
- [ ] cabe em 140 caracteres.

Exemplos:

- Fraco: `Gráfico de barras da cobertura`.
- Forte: `Cobertura passa de 41% para 83% em quatro anos`.
- Fraco: `Evolução dos casos`.
- Forte: `Casos caem 18% após a campanha, mas seguem acima de 2020`.

### Etapa 4 — Projetar a chave visual

- Rótulos diretos sempre que possível; legenda só quando necessário.
- Uma unidade por eixo; nada de "R$ / %" no mesmo eixo.
- Cor nunca é o único canal: use forma, padrão ou rótulo.
- Paleta segura para daltonismo (Okabe–Ito é a referência padrão).
- Máximo de 5 séries em linha e 12 categorias em barra.
- Sem 3D, sem sombra, sem gradiente que sugira magnitude inexistente.

### Etapa 5 — Escrever fonte e nota

A nota precisa responder, nesta ordem:

1. **O que é a medida?** (numerador, denominador, unidade)
2. **Qual recorte?** (n, período, filtros, território)
3. **Como foi calculada?** (média, mediana, percentual, missing)
4. **O que não permite concluir?** (limite explícito)
5. **Onde está a fonte?** (instituição, ano, URL/DOI)

Sem os cinco, a nota está incompleta.

### Etapa 6 — Auditar

```python
from skills.data_storytelling import audit_chart, audit_narrative
report = audit_chart(spec)
narrative = audit_narrative(claim, design="observational", base_declared=True)
```

Gate:

- `blocked` → corrija antes de renderizar;
- `revise` → corrija ou registre justificativa humana;
- `pass_with_notes` → entregue com as ressalvas;
- `approved` → passou nas regras desta versão, **não** é atestado de verdade.

### Etapa 7 — Selar

```python
from skills.data_storytelling import build_manifest, verify_manifest
manifest = build_manifest({
    "dossie.json": dossier_json,
    "auditoria.json": audit_json,
    "grafico.svg": svg,
    "legenda.md": caption_md,
})
assert verify_manifest(manifest, payloads)["ok"]
```

Guarde `spec`, dados, legenda, auditoria e manifesto. Sem isso, a entrega não
é reproduzível.

## 5. O que o gate bloqueia

### 5.1 Estrutura e leitura

| Código | Severidade | Correção |
|---|---|---|
| `MISSING_TITLE` | critical | escrever título-mensagem |
| `TITLE_NOT_MESSAGE` | medium | trocar nome do gráfico pelo achado |
| `NO_ALT_TEXT` | medium | descrever mensagem e valores principais |

### 5.2 Escala e eixo

| Código | Severidade | Correção |
|---|---|---|
| `TRUNCATED_AXIS` | critical | base zero em barra/área |
| `UNDECLARED_BASELINE` | high | declarar `y.zero=true` |
| `UNLABELED_AXIS_BREAK` | high | marcar e explicar a quebra |
| `DUAL_AXIS` | critical | separar painéis ou indexar |
| `THREE_D` | critical | projeção 2D |
| `LOG_SCALE_UNDECLARED` | high | rotular log e justificar |
| `MISSING_UNITS` | high | unidade ou `dimensionless` |
| `INCONSISTENT_PRECISION` | low | arredondar ou justificar |

### 5.3 Marca e cor

| Código | Severidade | Correção |
|---|---|---|
| `PIE_OVERLOAD` | critical/high | barra ordenada ou empilhada |
| `PIE_NOT_PART_TO_WHOLE` | high | pizza só com soma exata de 100% |
| `OVERPLOTTING` | high | alpha, binning, hexbin ou densidade |
| `CROWDED_SERIES` | medium | destacar poucas séries |
| `CROWDED_CATEGORIES` | medium | agrupar, filtrar ou barras horizontais |
| `COLOR_ONLY_ENCODING` | high | rótulo direto, forma ou padrão |
| `COLORBLIND_RISK` | high/medium | paleta segura + canal redundante |
| `NO_LEGEND` | medium | legenda ou rótulo direto |

### 5.4 Evidência e proveniência

| Código | Severidade | Correção |
|---|---|---|
| `MISSING_SAMPLE_SIZE` | high | declarar `n` |
| `MISSING_UNCERTAINTY` | high | IC, erro ou margem |
| `MISSING_SOURCE` | critical | instituição, ano, link/DOI |
| `SOURCE_NOT_TRACEABLE` | high | acrescentar ano/DOI/URL |
| `MISSING_NOTE` | high | nota metodológica |
| `NOTE_TOO_THIN` | high | n, período e método |
| `MISSING_MISSING_POLICY` | medium | exclusão, imputação ou "não informado" |

### 5.5 Alegação e narrativa

| Código | Severidade | Correção |
|---|---|---|
| `CAUSAL_CLAIM_OBSERVATIONAL` | critical | "associado a" ou desenho causal |
| `UNQUANTIFIED_SUPERLATIVE` | high | magnitude com número |
| `ABSOLUTE_CLAIM` | high | delimitar escopo |
| `UNSORTED_RANKING` | medium | ordenar por valor |
| `PERCENT_WITHOUT_BASE` | high | declarar denominador |
| `HYPE_WITHOUT_NUMBER` | high | trocar por dado |
| `NO_STATED_LIMIT` | medium | dizer o que não se conclui |

`score = max(0, 100 − 25·critical − 10·high − 3·medium − 1·low)` é
**prontidão heurística**, não nota de qualidade científica.

## 6. Anti-overclaim: reescritas obrigatórias

| Alegação | Problema | Reescreva |
|---|---|---|
| "O programa causou queda de 12 pontos." | desenho observacional | "A queda de 12 pontos coincide com o programa; o desenho não identifica causa." |
| "A arrecadação explodiu." | hipérbole sem número | "A arrecadação cresceu 30% (de R$ 1,2 mi para R$ 1,56 mi)." |
| "A maioria dos municípios aderiu." | sem denominador | "62% dos 120 municípios aderiram (n = 120)." |
| "Sempre foi assim." | absoluto sem escopo | "Em 2020–2024, o indicador ficou acima de X em todos os anos." |
| "Os dados provam que..." | prova inexistente | "Os dados são compatíveis com..." |
| "A média subiu." | média de quê? | "A média aritmética passou de 41 para 52 (n = 27)." |
| "Dobrou." | checar aritmética | "Passou de 41% para 83%." |
| "Sem precedentes." | hipérbole | "Maior valor da série 2020–2024." |
| "Correlação prova causalidade." | confusão | "Correlação de r = 0,72; não implica causalidade." |
| "Dados mostram..." | fonte vaga | "Segundo o IBGE (2024)..." |

Regra dura: **nenhuma frase causal sem desenho causal declarado**. O gate
`CAUSAL_CLAIM_OBSERVATIONAL` é `critical` e bloqueia a entrega.

## 7. Acessibilidade e leitura em P&B

- **Alt text:** mensagem + valores + período + fonte. Ex.: "Barras anuais de
  cobertura: 41% em 2020, 52% em 2021, 63% em 2022, 74% em 2023 e 83% em 2024."
- **Contraste:** texto ≥ 4,5:1; linhas ≥ 3:1.
- **Fonte mínima:** 11 pt em impresso; 16 px em slide.
- **Cor + redundância:** cor nunca sozinha; use rótulo direto ou padrão.
- **Sem 3D:** perspectiva altera área e ângulo.
- **Tabela de apoio:** figuras complexas exigem tabela com os valores.
- **Ordem de leitura:** título → eixo → marcas → fonte → nota.

## 8. Uso programático

### 8.1 Especificação mínima auditável

```json
{
  "chart": "bar",
  "title": "Cobertura passa de 41% para 83% em quatro anos",
  "claim": "A cobertura passou de 41% para 83% entre 2020 e 2024.",
  "source": "IBGE (2024)",
  "note": "Percentual de municípios com cobertura declarada; n = 120; período 2020–2024; sem imputação.",
  "legend": "Barras azuis: cobertura anual.",
  "alt_text": "Barras anuais de 41% em 2020 a 83% em 2024.",
  "sample_n": 120,
  "y": {"kind": "numeric", "zero": true, "unit": "%", "scale": "linear"},
  "x": {"kind": "temporal"},
  "category_count": 5,
  "series_count": 1,
  "design": "observational",
  "sorting": "ascending",
  "intent": "comparison",
  "decimals": 0,
  "data": [
    {"label": "2020", "value": 41},
    {"label": "2024", "value": 83}
  ]
}
```

Campos que o gate exige para não bloquear: `title`, `source`, `note`,
`sample_n`, `y.zero` (família de barras), `y.unit` (eixo numérico) e
`alt_text` (recomendado; ausência gera `medium`).

### 8.2 Fluxo completo

```python
from skills.data_storytelling import (
    profile_dataset, recommend_chart, audit_chart,
    caption_from_spec, render_svg, build_manifest, verify_manifest,
)

profile = profile_dataset(rows)
rec = recommend_chart(profile, intent="comparison")
report = audit_chart(spec)
if report["status"] in {"blocked", "revise"}:
    raise SystemExit(report["findings"])

caption = caption_from_spec(spec, number=1, kind="Gráfico")
svg = render_svg(spec)
manifest = build_manifest({
    "spec.json": spec_json,
    "auditoria.json": report_json,
    "grafico.svg": svg,
    "legenda.md": caption["markdown"],
})
```

### 8.3 CLI

```bash
# Dossiê sintético completo (prova física, manifesto verificável)
python3 -m skills.data_storytelling demo --out outputs/data-storytelling/demo

# Auditar uma especificação (exit 1 se blocked/revise)
python3 -m skills.data_storytelling audit spec.json

# Gerar a legenda de quatro camadas
python3 -m skills.data_storytelling caption spec.json --number 1 --kind Gráfico
```

Artefatos do `demo`: `dossie.json`, `grafico.svg`, `legenda.md`,
`auditoria.json`, `MANIFESTO.json`.

## 9. Reprodutibilidade e custódia

- `source_sha256`: hash canônico das linhas perfiladas.
- `spec_sha256`: hash da especificação auditada.
- `caption.sha256`: hash do texto plano da legenda.
- `manifest_sha256`: hash do manifesto sem o próprio campo.
- **Sem timestamps** por padrão: determinismo é propriedade de auditoria.
- Para verificar: `verify_manifest(manifest, {nome: bytes})`; detecta ausência
  e adulteração.
- Guarde, no mesmo diretório: dados, `spec.json`, `legenda.md`,
  `auditoria.json`, `grafico.svg`, `MANIFESTO.json`.

Escopo do selo: **os bytes e as regras desta versão**. Não certifica mérito
científico, aceite editorial nem revisão por pares.

## 10. Definição de pronto

- [ ] A decisão e o público estão escritos em uma frase.
- [ ] A mensagem tem sujeito, resultado, comparador e período.
- [ ] O perfil declara n, tipos, ausentes e `source_sha256`.
- [ ] A codificação segue o mapa de decisão; desvios têm justificativa.
- [ ] O título é mensagem, não nome de gráfico.
- [ ] A legenda cobre rótulo, título e chave visual.
- [ ] A fonte tem instituição, ano e URL/DOI quando existir.
- [ ] A nota tem n, período, método, filtros, definições e limitação.
- [ ] `audit_chart` não retorna `critical`/`high` sem justificativa humana.
- [ ] `validate_caption` retorna `ok: true` (sem placeholders).
- [ ] O SVG é XML válido, tem `<title>`/`<desc>` e não usa base ≠ 0 em barra.
- [ ] `verify_manifest` retorna `ok: true`.
- [ ] A limitação da conclusão está escrita na nota.
- [ ] Um humano revisou dados, alegação e adequação ao veículo.

## 11. Limites explícitos

- As regras são **heurísticas declaradas**; não substituem estatística,
  desenho causal, revisão por pares ou editor.
- O perfil não valida a veracidade dos dados; valida forma e completude.
- O gate não mede estética, legibilidade real em impresso ou adequação
  cultural.
- O render cobre `bar` e `line`; os demais tipos exigem renderizador externo,
  após a auditoria.
- A estrutura de legenda é editorial; normas ABNT, APA, IEEE e manuais de
  periódicos divergem. **Confirme o destino.**
- `approved` significa "passou nas regras desta versão", nunca "é verdadeiro",
  "é causal" ou "é Qualis A1".

## 12. Erros comuns e correção imediata

| Erro | Correção |
|---|---|
| `unsupported_chart` | usar um tipo do mapa de decisão |
| `bar_requires_zero_baseline` | fixar `y.zero=true` ou trocar para linha/ponto |
| `no_compatible_chart` | acrescentar campo numérico/temporal ou mudar a intenção |
| `missing_note` | escrever a nota de quatro perguntas |
| `SOURCE_NOT_TRACEABLE` | acrescentar ano, DOI ou URL |
| `NOTE_WITHOUT_NUMBER` | incluir n, período ou medida |
| `PLACEHOLDER_TEXT` | substituir `TODO`/`TBD` por conteúdo final |
| `TITLE_TOO_LONG` | reduzir para ≤ 140 caracteres |

## 13. Arquivos e testes

- Especificação: `specs/SPEC-935-R1003-data-storytelling-auditavel.md`
- Motor: `skills/data_storytelling/` (`profiling`, `rules`, `captions`,
  `render`, `manifest`, `util`, CLI)
- Testes: `tests/test_r1003_data_storytelling.py`
- Execução: `python3 -m pytest tests/test_r1003_data_storytelling.py -q`
