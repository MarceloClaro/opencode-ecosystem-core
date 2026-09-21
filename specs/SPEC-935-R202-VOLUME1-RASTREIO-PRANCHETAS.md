# SPEC-935-R202: Rastreio Durante as Atividades das Pranchetas

**Versão:** 1.00
**Data:** Setembro 2026
**Status:** EM EXECUÇÃO
**Autor:** MarceloClaro (Orquestrador)
**Base:** Volume 1 v4.4 (514 páginas; Parte 6 com fichas D1–D6 de observação em contexto amplo)

---

## 1. CONTEXTO E PROBLEMA

A v4.4 entregou um Guia de Observação (Parte 6) com fichas estruturadas
D1–D6 de **contexto amplo** (4 semanas, sala/pátio/atividade livre) e encaminhamento.
Porém **não existe instrumento de rastreio durante a atividade da prancheta**:
o professor que aplica uma folha de prática (162 planchetas reproduzíveis) não tem
um local padronizado para registrar, **na hora**, comportamentos observáveis da criança
— autonomia para iniciar, precisão, sinais de alerta por domínio (D1–D6).

Sem esse elo temporal, o registro da Parte 6 depende da memória e de múltiplas
ferramentas; sinais isolados que só aparecem em atividade dirigida escrita podem se perder.

**Objetivo:** adicionar um rastreio rápido, ético e padronizado **dentro de cada
plancheta** (faixa de rodapé), mais um protocolo de uso (Parte 6) e uma ficha semanal
de consolidação por aluno, alimentando o fluxo de encaminhamento já existente.

---

## 2. REQUISITOS FUNCIONAIS (RF)

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| RF-01 | Faixa de rastreio automática em TODA plancheta | `grep -c "\\plancheta{"` = nº de `\thispagestyle{planchetarastreio}` correspondente; faixa presente no rodapé da página da plancheta |
| RF-02 | Indicadores observáveis rápidos (não escore) | Faixa contém: início (sozinho/ajuda/dirigido), conclusão (completa/parcial/não), precisão (acertos/itens), tempo (informativo), domínios D1–D6 para marcar apenas sinais que DESTOAM |
| RF-03 | Ética: observação ≠ diagnóstico | Texto da faixa e do protocolo: nunca rotula, nunca gera nota; sinais → ficha semanal → encaminhamento (fluxo D1–D6 existente) |
| RF-04 | Ficha semanal de consolidação por aluno | Página reproduzível na Parte 6 com tabela: semana, planchetas realizadas, sinais por domínio, fatos observados (sem hipóteses), próxima ação (acomodar/revisar/encaminhar) |
| RF-05 | Integração com fluxo existente | Protocolo explicita: faixa da prancheta alimenta D1–D6 somente após persistência (≥ 3 ocorrências na mesma prancheta ou em 2 pranchetas seguidas); velocidade não é critério |
| RF-06 | Compatível com 162 planchetas sem edição individual | Implementação via `\fancypagestyle{planchetarastreio}` + `\thispagestyle` dentro do comando `\plancheta` — zero edição manual em cada folha |
| RF-07 | Acessibilidade visual | Fonte ≥ small; contraste WCAG AA; símbolos S/F/R/N ou checkbox; caixa discreta para não confundir o aluno |

---

## 3. REQUISITOS NÃO-FUNCIONAIS (RNF)

| ID | Requisito | Métrica |
|---|---|---|
| RNF-01 | Compilação LaTeX | `pdflatex` ×2 sem erros; exit 0 |
| RNF-02 | Sem new overfulls nos rodapés | Faixa cabe dentro da margem inferior (3cm); usar `resizebox` se necessário |
| RNF-03 | Tamanho do PDF | Não ultrapassar ~530 páginas (faixa usa espaço de rodapé já existente, sem inflar páginas) |
| RNF-04 | Entrega | `Volume_1_1ano_v4.5.pdf` em `C:\Users\marce\Downloads\Alfabetizar_Bem\` |
| RNF-05 | Anti-overclaim | Nenhum texto diz "triagem psicométrica", "ponto de corte" ou "diagnóstico"; apenas "sinais de alerta" e "encaminhamento" |

---

## 4. ARQUITETURA DE MUDANÇAS

### 4.1 Arquivos

| Arquivo | Mudança |
|---|---|
| `alfabetizar.cls` | Definir `\fancypagestyle{planchetarastreio}` (rodapé com faixa compacta); no comando `\plancheta`, adicionar `\thispagestyle{planchetarastreio}` após `\clearpage`; comandos auxiliares `\caixarastreio`, `\quadrodominioprancheta` |
| `parte6-guia-triagem.tex` | Nova seção "Rastreio Durante as Atividades das Pranchetas": como usar a faixa, legenda, regra de persistência, limites éticos; nova subseção com ficha semanal reproduzível (`\fichasemanalprancheta`) |
| `parte5-guia-professor.tex` | Breve menção na rotina do professor (1 parágrafo) sobre preencher a faixa ao final da aplicação da plancheta |
| `main.tex` | Versão 4.5 na capa e créditos |

### 4.2 Modelo da faixa de rastreio (rodapé da plancheta)

```
┌──────────────────────────────────────────────────────────────┐
│ Rastreio rápido (professor) — marque só o que DESTOAR:       │
│ Início: □ sozinho □ com ajuda □ dirigido   Conclusão: □ completa □ parcial □ não │
│ Precisão: __ de __ itens   Tempo: __ min (informativo)       │
│ Sinais de alerta: D1□ D2□ D3□ D4□ D5□ D6□  Obs.: ___________ │
│ Legenda → Parte 6. Observação escolar, NUNCA diagnóstico.    │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Ficha semanal (Parte 6, página reproduzível)

Tabela por aluno (iniciais): semana, planchetas feitas, sinais por domínio,
fatos em linguagem observável, decisão (manter acomodação / revisar rota /
registrar e encaminhar). Sem nota, sem ponto de corte.

---

## 5. CRITÉRIOS DE ACEITAÇÃO (Definition of Done)

| Critério | Como Verificar | Status |
|---|---|---|
| **CA-01** Faixa presente no rodapé de toda plancheta | Compilar e inspecionar 3 páginas de plancheta (ex.: A-01, B-01, C-05) | ☐ |
| **CA-02** RF-02 (indicadores rápidos, sem escore) | Inspeção visual + texto da faixa | ☐ |
| **CA-03** Ética (RF-03): "NUNCA diagnóstico" presente | `grep -ci "nunca diagnóstico"` parte6 ≥ 1 | ☐ |
| **CA-04** Ficha semanal reproduzível (RF-04) | Seção presente na Parte 6 com `\plancheta` ou `\fichasemanalprancheta` | ☐ |
| **CA-05** Zero edição manual nas 162 planchetas (RF-06) | `grep -c "\\thispagestyle{planchetarastreio}"` em `parte2`+`parte3` = 0; definido só no comando `\plancheta` | ☐ |
| **CA-06** Compila sem erros (RNF-01) | `pdflatex` ×2 → exit 0 | ☐ |
| **CA-07** Sem overfull novo em rodapés (RNF-02) | Log sem `Overfull` > 3pt na faixa | ☐ |
| **CA-08** PDF v4.5 entregue (RNF-04) | `Volume_1_1ano_v4.5.pdf` presente, páginas ≤ 530 | ☐ |

---

## 6. PLANO DE EXECUÇÃO (TDD)

| Fase | Ação | Teste (RED) | Implementação (GREEN) | Refatoração |
|---|---|---|---|---|
| 1 | `alfabetizar.cls`: estilo de página + faixa | Compilar com 1 plancheta fake e ver rodapé | Adicionar `\fancypagestyle{planchetarastreio}` + `\thispagestyle` no `\plancheta` | Ajustar altura/queda de linha |
| 2 | `parte6`: seção + ficha semanal | Inspeção de conteúdo | Escrever seção e ficha | Revisão ética de linguagem |
| 3 | `parte5`: menção no guia | grep de texto | 1 parágrafo | — |
| 4 | `main.tex` v4.5 | grep versão | Atualizar capa/créditos | — |
| 5 | Build completo | `pdflatex` ×2 exit 0 | Corrigir overfulls | Limpeza log |

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Rodapé com 3 linhas colide com conteúdo da plancheta | Média | Médio | `bottom=3cm` já reserva espaço; faixa compacta `\footnotesize`; usar `\thispagestyle` (só na página da plancheta) |
| Professor interpreta como "teste" e dá nota | Média | Alto | Texto explícito na faixa: "NUNCA gera nota"; protocolo da Parte 6 esclarece |
| Overclaim de rastreio psicométrico | Baixa | Crítico | Vocabulário restrito: "sinais de alerta", "persistência", "encaminhamento"; sem ponto de corte |
| Memória/metodologia mal compreendida | Média | Médio | Legenda curta na faixa aponta para a Parte 6; 4 semanas de persistência permanece regra |

---

## 8. ENTREGÁVEIS

1. **SPEC-935-R202.md** (este documento) — `specs/`
2. **alfabetizar.cls** com faixa de rastreio automática
3. **parte6** com protocolo + ficha semanal
4. **Volume 1 v4.5 PDF** — `C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_1_1ano_v4.5.pdf`
5. **Relatório de conformidade** — CA-01 a CA-08

---

## 9. APROVAÇÃO

| Papel | Nome | Status | Data |
|---|---|---|---|
| Orquestrador | MarceloClaro | ☐ | 2026-09-12 |
| Revisor Pedagógico | [AGUARDANDO] | ☐ | |

---

**Próxima ação:** implementar `\fancypagestyle{planchetarastreio}` na classe (Fase 1).