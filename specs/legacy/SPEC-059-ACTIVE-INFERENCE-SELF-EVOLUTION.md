# SPEC-059: Active Inference & Self-Evolution Loop (Fase A)

## Status: PROPOSED
## Autor: Marcelo Claro (Orquestrador Supremo) & Antigravity pair programmer
## Data: 2026-06-29
## Ciclo: R30

---

## 1. Visão Geral

Esta especificação define o design e a implementação da **Fase A (Active Inference & Self-Evolution)** para o **OpenCode Ecosystem**. 

O objetivo é equipar o ecossistema com um mecanismo cibernético de tomada de decisão baseado no princípio de **Minimização de Energia Livre Variacional (Variational Free Energy Minimization - FEP)** de Karl Friston. Em vez de simplesmente reagir a erros, o ecossistema ativamente ajusta suas ações ou seus modelos internos (crenças) para minimizar a divergência entre o estado observado do ecossistema e suas expectativas de qualidade operacional (priors).

---

## 2. Objetivos e Requisitos

* **O1**: Implementar o **Active Inference Controller (AIC)** que calcula a Energia Livre Variacional ($F$) do ecossistema.
* **O2**: Implementar o loop de auto-evolução cibernética **Plan-Act-Reflect-Evolve** orientado por políticas ($\pi$) que minimizam a Energia Livre Esperada (EFE).
* **O3**: Integrar com a infraestrutura de cura/evolução existente (`evolution_loop.py` e `mcp_self_healer.py`).
* **O4**: Expor as capacidades do novo módulo através de ferramentas MCP nativas no `ecosystem_capabilities_server.py` para acesso via Antigravity e OpenCode CLI.
* **O5**: Desenvolver uma suíte de testes TDD com pelo menos 12 casos de teste (CTs) validando a convergência matemática do controlador.

---

## 3. Formulação Matemática

### 3.1 Estados e Variáveis

* **Estados Internos / Crenças ($s$)**: A representação que o controlador tem dos parâmetros operacionais ideais (metas de cobertura de testes, latência máxima, custos de token, acurácia).
* **Estados Externos ($x$)**: Os estados reais do ambiente (a base de código, status de compilação, etc.).
* **Observações / Inputs Sensoriais ($o$)**: As métricas reais extraídas do ecossistema pelos scanners.
* **Ações / Políticas ($\pi$)**: Ações corretivas ou evolutivas (geração de novas skills, refatoração de código, recalibração de pesos de auditoria).

### 3.2 Energia Livre Variacional ($F$)

A Energia Livre Variacional é uma medida de surpresa (incompatibilidade) entre o que o agente observa ($o$) e o que ele espera observar de acordo com seu modelo generativo interno $p(o, s)$. Ela é definida como:

$$F = D_{KL}(q(s) \parallel p(s|o)) - \ln p(o)$$

Onde $q(s)$ é a distribuição variacional (a crença atual) e $p(s|o)$ é a distribuição real posterior do estado dado a observação. 

Na prática de engenharia de software, aproximamos $F$ através de uma soma ponderada de erros quadráticos normalizados entre a expectativa de uma métrica $m$ e sua observação real:

$$F = \sum_{m \in M} w_m \cdot \left(\frac{\text{Prior}_m - \text{Observed}_m}{\sigma_m}\right)^2$$

Onde:
* $w_m$ é o peso (precisão ou *precision* $\gamma$) associado à importância da métrica.
* $\sigma_m$ é a variância esperada (tolerância a desvios).

### 3.3 Minimização de Energia Livre

O agente reduz a Energia Livre de duas maneiras:
1. **Inferência Perceptual (Ajuste de Crenças)**: Modifica as expectativas internas ($\text{Prior}_m$) para acomodar a nova realidade (aprendizado/recalibração de thresholds).
2. **Inferência Ativa (Ação)**: Seleciona e executa uma política $\pi$ para atuar sobre o ambiente e alterar as observações futuras de modo a aproximá-las dos priors originais.

---

## 4. Arquitetura do Componente

O módulo será implementado no arquivo `nexus/scripts/active_inference_controller.py` e conterá os seguintes componentes principais:

```
                  ┌──────────────────────────────┐
                  │   Ecosystem Observations     │
                  └──────────────┬───────────────┘
                                 │ (Métricas reais dos scanners)
                                 ▼
                  ┌──────────────────────────────┐
                  │  Active Inference Controller │
                  │                              │
                  │   - Generative Model (Priors)│
                  │   - Free Energy Calculator   │
                  │   - Policy Selector          │
                  └──────────────┬───────────────┘
                                 │
                    Se F > Limiar│ (Seleciona a política π que minimiza EFE)
                                 ▼
                  ┌──────────────────────────────┐
                  │      Self-Evolution Loop     │
                  │     (Plan-Act-Reflect)       │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Ecosystem Evolution       │
                  │ (Heal, Evolve Skill, Re-test)│
                  └──────────────────────────────┘
```

### 4.1 Dataclasses

```python
@dataclass
class CognitivePrior:
    metric_name: str
    target_value: float
    tolerance: float  # sigma
    precision: float  # weight (gamma)

@dataclass
class PolicyProposal:
    policy_id: str
    action_type: str  # 'heal', 'evolve_skill', 'recalibrate', 'optimize_prompts'
    target_component: str
    expected_free_energy: float
    parameters: dict = field(default_factory=dict)
```

---

## 5. Integração com Servidor MCP e Deploy

Registraremos as seguintes ferramentas no `ecosystem_capabilities_server.py`:

* `eco_active_inference_step`: Processa observações atuais, calcula a energia livre, propõe e executa uma política de minimização.
* `eco_active_inference_status`: Retorna o estado atual dos priors cognitivos, o histórico de energia livre calculada e as políticas executadas.
* `eco_run_self_evolution_cycle`: Inicia um ciclo completo de Plan-Act-Reflect-Evolve sobre um componente ou skill específica.

---

## 6. Casos de Teste TDD (12+ CTs)

A suíte de testes em `specs/test_active_inference.py` cobrirá:

1. **CT-059-001**: Inicialização do controlador com priors cognitivos válidos.
2. **CT-059-002**: Cálculo de Energia Livre com observações idênticas aos priors (deve ser próximo de 0).
3. **CT-059-003**: Cálculo de Energia Livre com alta divergência em métrica crítica (alta energia livre).
4. **CT-059-004**: Sensibilidade do cálculo de $F$ em relação ao peso de precisão ($\gamma$).
5. **CT-059-005**: Geração de propostas de política de ação quando $F$ ultrapassa o limiar tolerado.
6. **CT-059-006**: Estimativa de Energia Livre Esperada (EFE) para diferentes políticas.
7. **CT-059-007**: Execução da política de *Perceptual Inference* (atualização de crenças/recalibração).
8. **CT-059-008**: Execução da política de *Active Inference* (disparo de auto-cura/self-healer).
9. **CT-059-009**: Loop completo Plan-Act-Reflect reduzindo a Energia Livre em ciclos sucessivos.
10. **CT-059-010**: Persistência do histórico de estados cognitivos.
11. **CT-059-011**: Resiliência a observações corrompidas ou nulas.
12. **CT-059-012**: Integração fim-a-fim através da API de mock de estado do ecossistema.
