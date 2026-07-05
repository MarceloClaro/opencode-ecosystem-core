# SPEC-060: Game Theory & Strategic Reasoning (Fase B)

## Status: PROPOSED
## Autor: Marcelo Claro (Orquestrador Supremo) & Antigravity pair programmer
## Data: 2026-06-29
## Ciclo: R30

---

## 1. Visão Geral

Esta especificação define o design e a implementação da **Fase B (Game Theory & Strategic Reasoning)** para o **OpenCode Ecosystem**. 

O objetivo é introduzir 10 modelos matemáticos clássicos de Teoria dos Jogos ao ecossistema, permitindo que agentes tomem decisões estratégicas em cenários de conflito, cooperação ou concorrência. Essas simulações serão integradas ao motor lógico **ARCHE RLT** (para deduzir equilíbrios de escolha) e ao **RUMI Causal Discovery** (para formular hipóteses causais baseadas nas dinâmicas de incentivos dos jogadores).

---

## 2. Objetivos e Requisitos

* **O1**: Implementar classes utilitárias para **10 modelos de jogos clássicos**:
  1. Dilema do Prisioneiro (*Prisoner's Dilemma*)
  2. Batalha dos Sexos (*Battle of the Sexes*)
  3. Caça ao Cervo (*Stag Hunt*)
  4. Jogo do Frango / Gavião-Pombo (*Chicken / Hawk-Dove*)
  5. Par ou Ímpar (*Matching Pennies*)
  6. Duopólio de Cournot (*Cournot Duopoly*)
  7. Liderança de Stackelberg (*Stackelberg Leader-Follower*)
  8. Jogo da Centopeia (*Centipede Game*)
  9. Jogo do Ultimato (*Ultimatum Game*)
  10. Jogo dos Bens Públicos (*Public Goods Game*)
* **O2**: Desenvolver resolvedores para calcular **Equilíbrios de Nash (Puros/Mistos)** e Equilíbrios Perfeitos em Subjogos (SPNE).
* **O3**: Integrar os resultados estratégicos como árvores lógicas do tipo **ARCHE RLT** (PeirceType.DEDUCTION_RULE).
* **O4**: Mapear as relações de incentivos $\to$ comportamento como hipóteses causais no **RUMI Causal Discovery**.
* **O5**: Registrar ferramentas MCP correspondentes no `ecosystem_capabilities_server.py`.
* **O6**: Desenvolver suíte de testes TDD (`specs/test_game_theory.py`) com pelo menos 12 casos de teste (CTs).

---

## 3. Os 10 Modelos e Formulação Matemática

### 3.1 Dilema do Prisioneiro
* Estratégias: Cooperar ($C$), Desertar ($D$).
* Payoffs típicos: R (Recompensa) = 3, T (Tentação) = 5, S (Otário) = 0, P (Punição) = 1.
* Equilíbrio: $(D, D)$ é o único equilíbrio em estratégias puras.

### 3.2 Batalha dos Sexos
* Estratégias: Atividade A (Opera), Atividade B (Futebol).
* Coordenação com preferências assimétricas.
* Equilíbrios: Dois equilíbrios puros $(A, A)$ e $(B, B)$, e um misto.

### 3.3 Caça ao Cervo
* Estratégias: Cervo ($S$), Lebre ($H$).
* Cooperação de alto risco vs. individualismo seguro.
* Equilíbrios: Dois equilíbrios puros $(S, S)$ (eficiente) e $(H, H)$ (seguro contra risco).

### 3.4 Jogo do Frango
* Estratégias: Desviar ($S$), Seguir reto ($D$).
* Equilíbrios: Dois equilíbrios puros $(S, D)$ e $(D, S)$ (anti-coordenação).

### 3.5 Par ou Ímpar
* Estratégias: Cara ($H$), Coroa ($T$).
* Jogo de soma zero puramente competitivo.
* Equilíbrio: Apenas equilíbrio misto com probabilidade $0.5$ para cada ação.

### 3.6 Duopólio de Cournot
* Jogo contínuo onde empresas escolhem quantidades $q_1, q_2$ simultaneamente.
* Preço de mercado: $P(Q) = a - b(q_1 + q_2)$.
* Custo: $C_i(q_i) = c \cdot q_i$.
* Equilíbrio: $q_1^* = q_2^* = \frac{a - c}{3b}$.

### 3.7 Liderança de Stackelberg
* Jogo sequencial de quantidade. Líder escolhe $q_1$, seguidor escolhe $q_2(q_1)$.
* Equilíbrio por indução retroativa (Backwards Induction): $q_1^* = \frac{a - c}{2b}$, $q_2^* = \frac{a - c}{4b}$.

### 3.8 Jogo da Centopeia
* Jogo sequencial onde jogadores alternam em cooperar ($C$) ou pegar o pote ($P$).
* Payoffs aumentam a cada rodada.
* Equilíbrio: Pegar o pote imediatamente na primeira rodada por indução retroativa.

### 3.9 Jogo do Ultimato
* Propositor oferece fração $x \in [0, 1]$ de uma soma. Respondente aceita ou rejeita.
* Equilíbrio: Propositor oferece a menor fração positiva $\epsilon$ e o respondente aceita.

### 3.10 Jogo dos Bens Públicos
* $N$ jogadores contribuem $c_i \in [0, m]$ para um pote comum.
* Pote é multiplicado por $r > 1$ e dividido igualmente por $N$ jogadores ($r < N$).
* Equilíbrio: Contribuição zero por parte de todos os jogadores (carona / *free-riding*).

---

## 4. Integração Lógica e Causal

### 4.1 Árvores Lógicas (ARCHE RLT)
O equilíbrio de Nash será traduzido em um nó de inferência deductiva (`RLTNode`) estruturado como:
* **Premissa**: A matriz de payoffs do jogo e as condições de racionalidade dos jogadores.
* **Conclusão**: O equilíbrio de Nash deduzido.
* **Tipo**: `PeirceType.DEDUCTION_RULE`.

### 4.2 Hipóteses Causais (RUMI)
As mudanças nos incentivos de payoffs ($P$) causam mudanças de equilíbrios de escolha ($E$). O mapeamento será:
* **Causa**: Alteração no payoff de cooperação.
* **Efeito**: Aumento na probabilidade de cooperação.
* **Mecanismo**: Teorema de estabilidade de equilíbrio de Nash.

---

## 5. Mapeamento de Novas Ferramentas MCP

As seguintes ferramentas MCP serão expostas no servidor capabilities:
1. `eco_game_theory_solve`: Resolve qualquer um dos 10 jogos com parâmetros personalizados.
2. `eco_game_theory_to_rlt`: Exporta a resolução de um jogo como árvore lógica ARCHE RLT.
3. `eco_game_theory_to_rumi`: Converte as dinâmicas de incentivos em hipóteses causais RUMI.
