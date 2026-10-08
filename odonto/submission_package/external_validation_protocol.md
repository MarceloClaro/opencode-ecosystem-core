# Protocolo de Validação Externa — OdontoCA

**Versão** 1.0 · **Modelo-alvo** `odontoca_clinical_model.joblib` (SHA-256 no model card) · **Status** aguardando coorte externa

---

## 1. Objetivo

Validar, em coorte independente e prospectiva, o modelo de risco por dente
`clinical_minimal` travado no desenvolvimento. A validação externa é o único
caminho que converte o estudo de desenvolvimento em evidência de desempenho
clínico. Sem ela, o PROBAST+AI permanece `High/High` e nenhuma alegação de
utilidade clínica é sustentável.

Este protocolo **não** modifica o modelo. Qualquer alteração de variável,
coeficiente, hiperparâmetro ou limiar invalida a validação e exige um novo
modelo e nova validação.

## 2. Modelo travado

| Item | Valor |
|---|---|
| Modelo primário | `clinical_minimal` |
| Preditores | `tooth_position`, `age_months_t`, `host_dmfs_t`, `neighbor_caries_count` |
| Coeficientes one-hot | 23 |
| Grau de liberdade efetivo | 24 |
| `C` selecionado | 10.0 (CV agrupada, average precision) |
| Recalibração | intercepto + inclinação, `slope` > 0, ajustada em cross-fit |
| Desfecho | `H→C` na próxima consulta registrada (2–5 meses) |
| Coorte de desenvolvimento | 996 transições, 83 eventos, 81 crianças |

O `clinical_spatial` é candidato **secundário exploratório** (39 gl). Não deve
ser empregado até que seus preditores derivados sejam reconstruídos e
verificados quanto a disponibilidade prospectiva.

## 3. Dimensionamento da amostra (regra de Riley et al., BMJ 2020;368:m441)

Eventos necessários = `max(100, 10 × gl)`:

| Modelo | gl | Eventos necessários |
|---|---|---|
| `clinical_minimal` (primário) | 24 | **240** |
| `clinical_spatial` (secundário) | 39 | 390 |

Tamanho Required, nível de dente, para o modelo primário:

| Prevalência esperada do desfecho | Dentes | Crianças (~12 dentes) |
|---|---|---|
| 5% | 4.800 | ~400 |
| 8,33% (prevalência do desenvolvimento) | 2.882 | ~241 |
| 15% | 1.600 | ~134 |
| 20% | 1.200 | ~100 |

**Déficit da coorte de desenvolvimento:** 83 eventos para 24 gl = **3,5
eventos por parâmetro**, contra 10 recomendados. A coorte de desenvolvimento
é, portanto, subdimensionada para sustentar o modelo; este é o achado central
de PROBAST no domínio *Analysis* e a justificativa direta desta validação.

Dimensionar pela prevalência mais baixa plausível é conservador. Se a
prevalência externa for desconhecida, planejar por 5% e monitorar o
fracasso de eventos após 50% da coleta.

## 4. Desenho

- **Prospectivo, multicêntrico, enrolment consecutivo** — sem seleção de Conveniência.
- **Independência:** centros e equipe sem vínculo com o desenvolvimento; acesso ao código-fonte apenas após o lock (o código é público, o *fitting* não).
- **Unidade:** transição por dente, agrupada por criança em toda inferência.
- **Janela de predição:** consulta `t`; desfecho avaliado na consulta consecutiva seguinte, com intervalo registrado. Excluir intervalo ≤ 0.
- **Cegamento:** avaliador de desfecho cegado ao risco predito.

## 5. Desfechos pré-especificados

**Primários**
1. **Discriminação** — AUROC com IC 95% por bootstrap de crianças (1.000 reamostragens, agrupando todos os dentes da criança).
2. **Calibração** — inclinação da calibração e erro absoluto de calibração em subgrupos, com IC 95%. Declarações de tipo *slope>1* ou *slope<1* pré-especificadas.

**Secundários**
3. Brier score e perda logarítmica, comparados ao preditor de prevalência.
4. AUPRC e curva de propriedade diagnóstica, com aviso de dependência de prevalência.
5. Curva de decisão / benefício líquido em limiares **pré-especificados** (0,05; 0,10; 0,20) — esta é a primeira oportunidade legítima de propor limiar.
6. Subgrupos pré-especificados: faixa etária, sexo, faixa de dmfs, centro. Ausência de diferença estatisticamente significativa **não** será interpretada como igualdade.

**Decisão de sucesso (pré-especificada)**
- AUROC pontual ≥ 0,65 **e** IC 95% da inclinação da calibração contém 1 **e** erro absoluto de calibração ≤ 0,05.
- Falhar em qualquer critério implica declarar o modelo **não transportável** e reportar como tal.

## 6. Registro e reprodutibilidade

1. **Preregistrar** este protocolo (OSF ou equivalente) **antes** do início do recrutamento, incluindo a SHA-256 do artefato.
2. Pontuar exclusivamente com `manuscript_assets/predict_clinical_risk.py`, que carrega o mesmo bundle publicado.
3. Reportar contagens de coorte, perda de seguimento e desvio do protocolo.
4. Devolver o CSV bruto de entrada e o de saída como material suplementar.

## 7. Ética e consentimento

- Aprovação por CEP local antes do recrutamento; consentimento informado dos responsáveis.
- A determination de ética do estudo **secundário** sobre a coorte pública de origem deve ser confirmada pelos autores antes da submissão do manuscrito (pendente no manuscrito atual).
- Sem reidentificação; somente variáveis necessárias aos quatro preditores.

## 8. Riscos declarados

| Risco | Mitigação |
|---|---|
| Verificar a transportabilidade do modelo é o objetivo; resultado negativo é publicável | Nenhum resultado positivo é pré-assumido |
| Deriva entre centros | Análise por centro e por subgrupo |
| Deriva temporal | Recorte temporal definido no protocolo |
| Deriva de predição entre consulta e desfecho | Intervalo registrado e reportado como covariável |
| Mutação do código durante a coleta | SHA-256 travada; usar apenas o bundle publicado |
| Leitura otimista dos resultados | Desfechos e limiares pré-especificados; decisão de sucesso fixada |
