# SPEC-921: Módulo de Raciocínio Jurídico Brasileiro

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-08
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Implementar um módulo de raciocínio jurídico especializado no sistema jurídico brasileiro, integrado ao ecossistema OpenCode Core. O módulo deve contemplar os métodos fundamentais de argumentação e decisão jurídica adotados no Brasil, com base na Constituição Federal de 1988, no Código de Processo Civil de 2015 (Lei 13.105/2015) e na jurisprudência dos tribunais superiores (STF, STJ, TST, TSE).

## 2. Diagnóstico — Estado Atual

O ecossistema possui 12 motores de raciocínio no pacote `reasoning/` (lógico, simbólico, probabilístico, causal, temporal, fuzzy, dialético, analógico, contrafactual, quântico, cadeia de pensamento), mas **nenhum motor especializado em raciocínio jurídico**.

O direito brasileiro exige formas específicas de raciocínio que não são capturadas adequadamente por motores genéricos:

| Necessidade Jurídica | Motor Existente | Lacuna |
|---|---|---|
| Subsunção fato-norma (silogismo legal) | Z3Engine (lógico) | Não modela hierarquia normativa, antinomias, ponderação |
| Ponderação de princípios (Alexy) | Nenhum | Método específico de sopesamento com fórmula de peso |
| Análise de precedentes vinculantes | AnalogicalEngine | Ratio decidendi, distinguishing, overruling exigem lógica própria |
| Interpretação constitucional | CriticalEngine | Métodos hermenêuticos específicos (gramatical, sistemático, teleológico) |
| Scoring de argumentação | ReasoningEvaluator | Critérios jurídicos: legalidade, jurisprudência, doutrina, persuasão |

## 3. Escopo

### 3.1 Componentes

| # | Módulo | Classe/Função Principal | Descrição |
|---|---|---|---|
| 1 | `legal/syllogism.py` | `LegalSyllogism` | Subsunção: norma (major premise) + fato (minor premise) → conclusão. Suporte a antinomias, hierarquia (CF > lei > decreto) e conflitos de competência. |
| 2 | `legal/balancing.py` | `PrincipleBalancing` | Ponderação de princípios (Robert Alexy). Fórmula do peso: `W = I · G · S`. Teste de proporcionalidade: adequação, necessidade, proporcionalidade em sentido estrito. |
| 3 | `legal/precedents.py` | `PrecedentAnalyzer` | Análise de precedentes: ratio decidendi, obiter dictum, distinguishing, overruling, súmulas vinculantes, IRDR, repercussão geral (RG). |
| 4 | `legal/constitutional.py` | `ConstitutionalInterpretation` | Métodos de interpretação constitucional: gramatical, histórico, sistemático, teleológico, a contrario, a simili, proporcionalidade. |
| 5 | `legal/argumentation.py` | `LegalArgumentScorer` | Scoring de argumentos jurídicos: validade legal, suporte jurisprudencial, suporte doutrinário, consistência interna, persuasão retórica. |

### 3.2 Integração

- `legal/__init__.py` exporta todos os símbolos
- Integração opcional com `MultiReasoningEngine` via método `LegalReasoningBridge`
- Integração com MCI (MetaBus) para logging e reflexão

### 3.3 Critérios de Aceitação (TDD)

1. `LegalSyllogism.subsume()` retorna conclusão válida para silogismo simples
2. `LegalSyllogism.subsume()` detecta antinomia entre normas de mesmo nível
3. `LegalSyllogism.subsume()` aplica hierarquia normativa (CF > lei > decreto)
4. `LegalSyllogism.subsume()` identifica conflito de competência (União vs. Estado)
5. `PrincipleBalancing.balance()` aplica a fórmula do peso de Alexy
6. `PrincipleBalancing.proportionality()` executa teste tripartite (adequação, necessidade, proporcionalidade stricto sensu)
7. `PrincipleBalancing.balance()` retorna grau de precedência condicionado
8. `PrecedentAnalyzer.extract_ratio()` identifica ratio decidendi de ementa
9. `PrecedentAnalyzer.identify_distinguishing()` detecta distinção de fatos
10. `PrecedentAnalyzer.identify_overruling()` detecta superação de precedente
11. `ConstitutionalInterpretation.interpret()` aplica método gramatical/textual
12. `ConstitutionalInterpretation.interpret()` aplica método sistemático
13. `ConstitutionalInterpretation.interpret()` aplica método teleológico
14. `LegalArgumentScorer.score()` retorna score 0–1 com justificativa
15. `LegalArgumentScorer.score()` pondera validade legal > jurisprudência > doutrina

## 4. Referências Jurídicas

- **Constituição Federal de 1988**
- **CPC/2015 (Lei 13.105/2015)** — arts. 926-928 (precedentes), arts. 489 §1º (fundamentação)
- **LINDB (Decreto-Lei 4.657/1942)** — arts. 20-30 (segurança jurídica)
- **ALEXY, Robert.** Teoria dos Direitos Fundamentais (2008) / Fórmula do Peso
- **ÁVILA, Humberto.** Teoria dos Princípios (2003)
- **STRECK, Lenio.** Hermenêutica Jurídica e(m) Crise (2011)
- **MARINONI, Luiz Guilherme.** Precedentes Obrigatórios (2016)
- **STF** — Súmulas Vinculantes, Repercussão Geral
- **STJ** — Súmulas, IRDR, Recursos Repetitivos
