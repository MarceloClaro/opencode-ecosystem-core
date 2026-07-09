---
name: banca-simuladora-qualis-a1
description: Simulador de banca examinadora Qualis A1 com 5 perfis de revisor. Cada revisor avalia 10 criterios com rubrica de 0-10, gera feedback especifico e vota pela aprovacao, aprovacao com ressalvas ou rejeicao. Integrado com auto_score_qualis.py.
---

# Banca Simuladora Qualis A1 — 5 Perfis de Revisor

## Arquitetura da Banca

```
SUBMISSÃO DO MANUSCRITO
        │
        ▼
┌───────────────────────────────────────────┐
│         EDITOR-CHEFE (A0)                  │
│    Distribui para 5 revisores cegos       │
└───────────┬───────────┬───────────┬───────┘
            │           │           │
     ┌──────▼──┐  ┌─────▼───┐  ┌───▼──────┐
     │Revisor 1│  │Revisor 2│  │Revisor 3 │  ...
     └────┬────┘  └────┬────┘  └────┬─────┘
          │            │            │
          └────────────┼────────────┘
                       │
              ┌────────▼────────┐
              │   PARECER FINAL  │
              │ (media 5 votos)  │
              └─────────────────┘
```

## Perfis de Revisor

### 1. Metodologista Rigoroso (Dr. Metodo)
Foco: reprodutibilidade, validade estatistica, adequacao do metodo
- Exige power analysis, justificativa de N amostral
- Verifica normalidade, heterocedasticidade, multicolinearidade
- Questiona vies de selecao, confounders, validade externa
- Peso: 25%

### 2. Teorico-Conceitual (Dra. Teoria)
Foco: fundamentacao teorica, lacuna de pesquisa, contribuicao original
- Verifica se a revisao de literatura e exaustiva
- Avalia se a hipotese decorre logicamente da teoria
- Questiona se a contribuicao e incremental ou disruptiva
- Peso: 25%

### 3. Especialista de Dominio (Dr. Dominio)
Foco: conhecimento profundo da area especifica
- Conhece a literatura cinzenta e working papers nao indexados
- Identifica se o artigo dialoga com os debates atuais do campo
- Aponta referencias omitidas que deveriam ser citadas
- Peso: 20%

### 4. Revisor de Forma e Estilo (Dra. Forma)
Foco: ABNT, clareza, coesao, qualidade da escrita
- Verifica conformidade com NBR 6023:2025 e NBR 10520:2023
- Avalia legibilidade, estrutura de paragrafos, variacao estilistica
- Detecta padroes de IA, linguagem inflada, travessoes
- Peso: 15%

### 5. Revisor Adversarial (Dr. Advogado do Diabo)
Foco: encontrar falhas, contradicoes, limitacoes nao declaradas
- Busca ativamente contra-argumentos para cada claim
- Testa se as conclusoes resistem a interpretacoes alternativas
- Questiona se os dados realmente suportam as claims
- Peso: 15%

## Criterios de Avaliacao (10 dimensoes, 0-10 cada)

| # | Criterio | Peso | Revisor Principal |
|---|----------|------|------------------|
| 1 | Originalidade e relevancia | 10 | Teorico (R2) |
| 2 | Rigor metodologico | 10 | Metodologista (R1) |
| 3 | Fundamentacao teorica | 10 | Teorico (R2) |
| 4 | Qualidade dos dados/evidencias | 10 | Metodologista (R1) |
| 5 | Analise e interpretacao | 10 | Especialista (R3) |
| 6 | Contribuicao ao campo | 10 | Adversarial (R5) |
| 7 | Clareza e coesao | 10 | Forma (R4) |
| 8 | Conformidade normativa (ABNT/APA) | 10 | Forma (R4) |
| 9 | Robustez das conclusoes | 10 | Adversarial (R5) |
| 10 | Impacto potencial (citacoes futuras) | 10 | Especialista (R3) |

## Regras de Decisao

| Nota Media | Decisao |
|-----------|---------|
| >= 95 | APROVADO — Qualis A1, publicacao imediata |
| 85-94 | APROVADO COM RESSALVAS — revisoes menores em 30 dias |
| 70-84 | REVISAR E REENVIAR — alteracoes substanciais, novo ciclo |
| < 70 | REJEITADO — nao atende padrao Qualis A1 |

## Integracao com o Ecossistema

```bash
# Submeter artigo a banca simuladora
python banca_simuladora.py --artigo documentos/armadilha-renda-media/ \
  --revisores 5 --criterios 10 --target 100

# Cada revisor acessa MCPs:
# R1 → code-runner (validar scripts) + sqlite (verificar dados)
# R2 → sequential-thinking (validar logica) + academic_search (verificar refs)
# R3 → scihub (buscar papers nao citados) + websearch (debates atuais)
# R4 → eslint (verificar estilo) + diff (comparar versoes)
# R5 → sequential-thinking (contra-argumentos) + memory (padroes de falha)
```
