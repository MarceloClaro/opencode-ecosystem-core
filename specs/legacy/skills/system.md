# Specs: Skills — System

**Categoria:** system | **Total:** 10 skills | **Revisao:** 2026-05-27

---

## code-review (v2.1.0)
### Comportamento
Metodologia de revisao em 4 camadas com severidade e confianca >= 80%. References em 7 arquivos.
### Criterios
- [ ] Revisao cobre 4 camadas (corretude, seguranca, performance, manutencao)
- [ ] Severidade classificada (critical/high/medium/low)
- [ ] Confianca >= 80% para reportar
- [ ] Referencias file:line em todos os achados

## reasoning-orchestrator (v9.0.0)
### Comportamento
68 tipos de raciocinio (58 + 10 Teoria dos Jogos) em 4 niveis L1-L4. 3 niveis de publicacao (N1 Magnum, N2 Standard, N3 Express).
### Criterios
- [ ] Selecao de framework logico por tipo de tarefa
- [ ] 4 niveis de profundidade configuráveis
- [ ] TokenEconomy integrado
- [ ] DataOrchestrator integrado

## reasoning-orchestrator-v11 (v11.0.0)
### Comportamento
Evolucao do v9: 12 agentes especializados em pipeline de 7 fases. Integrado com Cora-Debate V1-V6.
### Criterios
- [ ] Pipeline 7 fases: Inductor → BaseCase → Contradiction → LemmaTracker → CrossRef → StressTest → ProofHealth
- [ ] Verificacao simbolica via Cora V1-V6
- [ ] Compatibilidade reversa com v9.0.0

## token-efficiency (v2.1.0)
### Comportamento
5 principios de otimizacao: chines para contexto interno (+40% densidade), PT-BR formal para saida, compressao de dados, tabelas vs paragrafos, evitar redundancia.
### Criterios
- [ ] Economia de 30-70% de tokens vs texto nao otimizado
- [ ] Nenhum caractere CJK vaza para saida do usuario
- [ ] Corretor ptbr_corrector.py executado antes de cada entrega

## self-heal (v1.0.0)
### Comportamento
Auto-cura do ecossistema: detecta falhas, diagnostica causa, aplica correcao, verifica.
### Criterios
- [ ] Deteccao de MCP offline
- [ ] Diagnostico automatico (log, dependencias, timeout)
- [ ] Correcao sem intervencao humana (restart, reinstall, fallback)

## skill-creator (v1.0.0)
### Comportamento
Criacao de novas skills seguindo template canonico e token budget.
### Criterios
- [ ] SKILL.md gerado conforme SKILL_TEMPLATE.md
- [ ] Token budget respeitado (<= 2500 tokens)
- [ ] Progressive disclosure aplicado

## plan-review (v2.1.0)
### Comportamento
Revisao de planos contra 3 criterios: Citation Quality, Completeness, Actionability.
### Criterios
- [ ] Plano revisado contra os 3 criterios
- [ ] Score por criterio
- [ ] Sugestoes de melhoria acionaveis

## philosophy-enforcement (v1.0.0)
### Comportamento
Aplica filosofia de codigo do ecossistema em todas as geracoes.
### Criterios
- [ ] Verifica aderencia a principios de design
- [ ] Reporta violacoes com severidade

## code-philosophy (v2.1.0)
### Comportamento
5 Leis da Defesa Elegante: principios de logica interna e fluxo de dados.
### Criterios
- [ ] Codigo gerado segue as 5 leis
- [ ] Violacoes detectadas e reportadas

## academic-audit (v1.0.0)
### Comportamento
Auditoria academica caixa branca: compatibilidade TSAC (87 palavras banidas), padroes Qualis A1.
### Criterios
- [ ] TSAC compliance verificado
- [ ] 87 palavras banidas detectadas
- [ ] Rastreamento minucioso de alteracoes
