# PLANO DE REVISÃO M8 — R522 (baseado na banca editorial simulada)

**Manuscrito:** `manuscrito_porescrito799_brasil_comparado_R522_v49_CORRECOES_FINAIS_M7`
**Status atual:** v49 (M7 aplicado) — antes da submissão final ao periódico Educação Por Escrito
**Ferramenta:** `banca_simulate` (SPEC-976 R-976.11–14), seed 42, 12 revisores simulados
**Data:** 2026-09-23

> ⚠️ **Anti-overclaim (R110):** a banca é uma **simulação determinística** com
> rótulos de periódicos Qualis A1/Q1 apenas para calibração de perfil. NÃO é
> revisão por pares real, NÃO constitui validação externa e NÃO é promessa
> editorial. A revista-alvo real (Educação Por Escrito) é Qualis A4 — qualquer
> menção a "A1" permanece meta interna de rigor. Este plano organiza a
> revisão; a decisão final de submissão depende das pendências reais do
> `README_R522.md`, depósito OSF/Zenodo e conferência editorial humana.

---

## 1. Diagnóstico da banca simulada (12 revisores, 12 critérios)

Veredito global: **REVISÕES MAIORES** · Score ponderado: **56.9/100**

| Critério | Sinal textual (0..1) | Média banca (−1..1) | Status |
|---|---|---|---|
| redação | 0.111 | −0.389 | 🔴 **CRÍTICO** |
| originalidade | 0.636 | −0.364 | 🔴 **ALTO** |
| reprodutibilidade | 0.727 | −0.273 | 🟠 atenção |
| clareza | 0.700 | −0.050 | 🟡 ok |
| impacto | 1.000 | +0.000 | 🟡 ok |
| metodologia | 0.833 | +0.083 | 🟢 forte |
| estatística | 0.583 | +0.083 | 🟢 forte |
| relevância | 0.600 | +0.100 | 🟢 forte |
| evidências | 1.000 | +0.250 | 🟢 forte |
| teoria | 0.625 | +0.625 | 🟢 fortalezas |
| ética | 0.727 | +0.727 | 🟢 fortalezas |
| coerência | 0.750 | +0.750 | 🟢 fortalezas |

**Leitura honesta:** o manuscrito já é fortíssimo em método, ética, evidência,
teoria e coerência (dimensões D1/E1/E4 altas, concordância κ=1,000 com
RH1/RH2 humanos, errata formalizada). As fragilidades são **de apresentação**:
a redação não declara/concretiza a conformidade formal esperada (ABNT/NBR,
apêndice, declaração de IA no corpo), a originalidade é enunciada mas pouco
densificada contra a literatura, e a reprodutibilidade depende do depósito
que está **exatamente na pendência #1 do README** (OSF/Zenodo + DOI).

---

## 2. Plano M8 — ações por fragilidade

### 2.1 Redação (crítico — 0.111 de sinal textual)

**Por que está baixo:** o texto não contém os marcadores formais que revisores
esperam ver: 0 menções a `ABNT`/`NBR 6023` (embora o PDF se chame
"FORMATACAO_ABNT"), 1 menção a citação, 0 a apêndice, 0 a uso explícito de
IAGen na autoria/redação.

| # | Ação | Prioridade | Critério de aceitação |
|---|---|---|---|
| M8-R1 | Inserir nota de **conformidade formal** (ABNT NBR 6023 para referências, citação (Autor, data), seções numeradas) em nota inicial ou seção "Aspectos formais" | Alta | O texto passa a conter "ABNT" e "NBR 6023" de forma explícita |
| M8-R2 | Transformar o `SUPLEMENTO_PRISMA_ScR_R522_v49` em **Apêndice A** referenciado no texto (atualmente é anexado separadamente) | Alta | Aparece "Apêndice" + referência explícita no corpo |
| M8-R3 | Registrar no manuscrito a **declaração de uso de tecnologias** (a declaração já existe em `SUBMISSAO_DECLARACAO_IA`/`DECLARACAO_IA_TECNOLOGIAS`), conforme a política editorial: descrever o papel da IAGen, se usado como apoio de redação/busca, com supervisão humana integral | Alta | Frase explícita no manuscrito + declaração assinada datada (pendência #2 do README) |
| M8-R4 | Conferência final de redação: gramática, ortografia, citações corretas (todas as refs usadas e vice-versa) | Média | Relatório de conferência bibliográfica (base: `BIBLIOGRAFIA_CONFERIDA_CORPUS_21`) sem pendências |
| M8-R5 | Confirmar abstract/keywords bilíngues alinhados ao resumo (PT/EN) e dentro dos limites do periódico | Média | Resumo↔abstract semânticamente idênticos, sem informações novas |

### 2.2 Originalidade (alto — média −0.364 apesar de sinal 0.636)

**Por que está baixo:** a lacuna é **enunciada** (PICo + contribuição tripla)
mas não **densificada**: a contribuição tripla não é retomada na discussão com
ancoragem medida, nem posicionada contra a literatura internacional incluída.

| # | Ação | Prioridade | Critério de aceitação |
|---|---|---|---|
| M8-O1 | Em "Discussão", criar subseção **"Contribuição e originalidade"** que retoma a tripla contribuição (gap mensurável, matriz comparativa, agenda) e a sustenta com os dados D1–D6/E1–E4 | Alta | Cada uma das 3 contribuições declaradas na introdução é explicitamente respondida na discussão |
| M8-O2 | Incluir **tabela comparativa** posicionando o estudo frente aos estudos internacionais do corpus (UE, Portugal, Alemanha, EUA, UNESCO): o que os outros mediram, o que este estudo adiciona (perspectiva brasileira + equidade algorítmica) | Alta | Tabela com ≥3 países/regiões comparadas e coluna "contribuição deste estudo" |
| M8-O3 | Explicitar na conclusão a **novidade específica** (primeira scoping review com corpora RH1/RH2 humanos e κ=1,000 sobre IAGen na educação jurídica BR comparada) sem overclaim | Alta | Frase de novidade presente, proporcional e sem "primeiro da história" não verificável |
| M8-O4 | Adicionar seção **"Limitações"** densa (8 menções já existem; consolidar em parágrafo único) — revisores rigorosos valorizam limites explícitos | Média | Seção única de limitações com implicações para generalização |

### 2.3 Reprodutibilidade (atenção — média −0.273 apesar de sinal 0.727)

**Por que está baixo:** os sinais existem (OSF, OpenAlex, DOAJ, DOI, κ,
RH1/RH2) mas a média negativa reflete revisores rigorosos exigindo o
**depósito efetivo** — que é precisamente a pendência #1 do README.

✅ **BLOCO A EXECUTADO (23/09/2026)** — depósito REAL confirmado:
| # | Ação | Status | Evidência |
|---|---|---|---|
| M8-P1 | **Depositar em OSF/Zenodo**: protocolo, matriz, log, errata, suplemento PRISMA-ScR, instrumentos RH1/RH2 | ✅ FEITO | Zenodo DOI real `10.5281/zenodo.22870968` (estado `done`, CC-BY-4.0, v49.2, 21/09); OSF público `https://osf.io/t7env/` com DOCX+PDF+Bibliografia+Pacote zip (48 KB) |
| M8-P2 | Inserir no manuscrito seção **"Disponibilidade de dados"** apontando o DOI/URL real (não placeholder) | ✅ FEITO (v50) | Parágrafo "Disponibilidade de dados" reescrito com DOI `10.5281/zenodo.22870968` + OSF `t7env`, acessados 23/09/2026 |
| M8-P3 | Se aplicável, disponibilizar **scripts de análise** (Python/R) + seed em repositório, e citá-los | 🔲 Opcional | `PACOTE_PUBLICO_DEPOSITAVEL_R522_v49.zip` já no OSF — conferir se contém scripts |
| M8-P4 | Referenciar o protocolo OSF no método (registro/versão/Data de acesso) | ✅ FEITO (v50) | Citação de acesso 23/09/2026 na seção de reprodutibilidade |

**Rascunho para M8-P2 (seção "Disponibilidade de dados" no manuscrito):**

> Disponibilidade de dados: o preprint da revisão de escopo, a bibliografia
> conferida do corpus (n=21), a errata da concordância RH1/RH2 (κ=1,000),
> o suplemento PRISMA-ScR e os instrumentos de triagem estão depositados
> em acesso aberto no OSF (https://osf.io/t7env/) com versão de preprint
> arquivada sob DOI 10.5281/zenodo.22870968 (CC-BY-4.0). Consultados em
> 23/09/2026.

### 2.4 Manutenção das fortalezas (não regredir)

| # | Ação | Prioridade |
|---|---|---|
| M8-K1 | Preservar a linguagem anti-overclaim M7 (proporcionalidade) na nova redação de originalidade/limitações | Alta |
| M8-K2 | Manter a errata RH2/κ e a série humana RH1/RH2 como vigentes (não reintroduzir RH2-IA) | Alta |
| M8-K3 | Reaplicar checklist PRISMA-ScR no texto final pós-M8 | Média |

---

## 3. Ordem de execução sugerida

1. ~~**Bloco A (reprodutibilidade — bloqueia):** M8-P1 → M8-P2 → M8-P4~~ → **BLOCO A EXECUTADO (23/09)**: depósito Zenodo (DOI real) + OSF público confirmados; **M8-P2 (DOI inserido na v50)** e **M8-P4 (protocolo citado com acesso 23/09/2026)** feitos — ✅.
2. ~~**Bloco B (redação — crítico):** M8-R1 → M8-R2 → M8-R3 → M8-R4 → M8-R5~~ → **BLOCO B APLICADO (23/09)**: R1 (ABNT/NBR) ✅, R2 (Apêndice A anexado + remissão) ✅, R3 (declaração IA já existente — mantida) ✅; R4/R5 passam à conferência editorial final.
3. ~~**Bloco C (originalidade — alto):** M8-O1 → M8-O2 → M8-O3 → M8-O4~~ → **BLOCO C APLICADO (23/09)**: subseção 5.4 + Tabela 1 ✅, 5.5 Limitações ✅, novidade proporcional na Conclusão ✅.
4. **Bloco D (manutenção):** M8-K1 → M8-K2 → M8-K3 — conferência RH1/RH2 **concluída** (23/09) aprovando sem alterações; K3 (PRISMA-ScR no texto final) permanece como passo da conferência editorial.
5. Re-rodar a banca simulada (seed 42) para comparar `score` e médias
6. Executar as pendências finais do README (Turnitin, conferência editorial)

---

## 4. Métrica de verificação (pós-M8)

**Status 23/09/2026 — Blocos A/B/C aplicados e CONFERIDOS RH1/RH2; v50 oficial promovida:**

| Métrica | Meta | v49 (base) | v50 (conferido) | Status |
|---|---|---|---|---|
| Score | ≥ 65 | 56.9 | **59.5** | 🟡 avançou +2.6 |
| redação — sinal | ≥ 0.4 | 0.111 | **0.556** | ✅ |
| redação — média | ≥ −0.1 | −0.389 | **+0.056** | ✅ saiu das fragilidades |
| reprodutibilidade — média | ≥ +0.1 | −0.273 | −0.182 | 🟡 melhorou |
| originalidade — média | ≥ +0.1 | −0.364 | −0.364 | 🔴 limitação do modelo |
| Fragilidades | só OK | redação+original | **só original** | 🟡 1/2 resolvida |

**Leitura honesta do delta:** o ganho de +2.6 vem de marcadores reais inseridos
(ABNT/NBR explícitas, remissão ao Apêndice A, DOI real na Disponibilidade de
dados, subseções 5.4/5.5 e novidade proporcional na Conclusão). A originalidade
não se move porque o sinal regex já era 0.636 — a melhoria da **densidade
argumentativa** (M8-O1..O4 aplicados) precisa de validação por revisores
humanos, fora do escopo da simulação.

**Arquivos gerados (v50):**
- `manuscrito_porescrito799_brasil_comparado_R522_v50_OFICIAL_M8_CONFERIDO.docx` (61.746 chars; v49 = 48.696)
- `manuscrito_porescrito799_brasil_comparado_R522_v50_OFICIAL_M8_CONFERIDO.pdf` (PDF de conferência LibreOffice)
- Manifemplos SHA-256 em `MANIFESTO_SHA256_v50_OFICIAL_M8_CONFERIDO.*.json`

✅ **Conferência humana RH1/RH2 CONCLUÍDA em 23/09/2026** — v50 aprovada sem alterações
posteriores ao arquivo; promovida a oficial. Restam apenas as pendências editoriais
do `README_R522.md` (Turnitin, assinatura da declaração de IA, instruções do periódico).

Alvo razoável (sem garantir aprovação real): elevar **score ≥ 65** e sair de
"REVISÕES MAIORES" para "REVISÕES MENORES" na simulação, com:
- `redação` com sinal textual ≥ 0.4 (média ≥ −0.1) — ✅ atingido
- `originalidade` com média ≥ +0.1 — depende de validação humana
- `reprodutibilidade` com média ≥ +0.1 — após reforço de scripts/citação do protocolo

Comando de verificação:

```bash
python3 - <<'PY'
from marceloclaro.orchestrator import MarceloClaroOrchestrator
r = MarceloClaroOrchestrator().banca_simulate(
    open("ARTIGO_M8.txt", encoding="utf-8").read(),
    n_members=12, rounds=12, seed=42,
    requirement="verificação pós-M8 R522")
print(r["verdict"], r["weighted_score"])
print(r["by_criterion"]["redação"], r["by_criterion"]["originalidade"], r["by_criterion"]["reprodutibilidade"])
PY
```

---

## 5. Rastreabilidade

- Origem do diagnóstico: simulação seed 42 (2026-09-23), `banca_42_12_*`,
  texto extraído do PDF `R522_ARTIGO_PREPRINT_v49_2_FORMATACAO_ABNT.pdf`
  (48.696 chars, `pdftotext -layout`).
- Perfis editoriais usados para calibração: `mirofish/social/editorial_profiles.py`
  (11 revistas A1/Q1, normas públicas).
- Especificação: `specs/SPEC-976-mirofish-offline-social-simulation.md` R-976.11–14.

> Este plano é um **instrumento de revisão orientada**. A decisão de submissão
> e o galardão editorial cabem exclusivamente aos periódicos reais e à
> conferência humana; a simulação jamais decide por eles.