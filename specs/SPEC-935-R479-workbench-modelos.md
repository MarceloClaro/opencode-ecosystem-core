---
spec_id: SPEC-935-R479
title: Fase 3 da R471 — workbench DeepSeekGUI (M4) e modelos pequenos reprodutíveis minimind (M5)
component: workbench (deepseek_gui), model_lab (curriculum, hardware, benchmark), THIRD_PARTY_NOTICES
test_file: tests/test_r479_m4_m5.py
status: green
estoque: rc
data: 2026-09-13
---

# SPEC-935-R479 — Fase 3: workbench DeepSeekGUI e modelos pequenos reprodutíveis

## Objetivo
Executar a Fase 3 do roadmap da SPEC-935-R471:

1. **M4 — Workbench de supervisão (DeepSeekGUI)**: conector opt-in que aponta o workbench para workspaces do Core (`pesquisa`, `academic`, `publications`) usando o harness já presente (`integrations.deepseek_harness`); documenta o fluxo e registra licenças (camada de produto PolyForm Perimeter 1.0.1 vs upstream MIT) em `THIRD_PARTY_NOTICES.md` (CA5).
2. **M5 — Modelos pequenos reprodutíveis (minimind)**: currículo didático mínimo (tokenizer → pretrain → SFT → RLHF → DPO → MoE → distill → quant, 64M) com plano determinístico por seed, probe de hardware honesto e benchmark simulado com relatório de reprodutibilidade; sem GPU, a limitação de hardware é documentada explicitamente (CA6).

## Não-objetivos
- Não executar GUI, treinamento real nem chamadas de rede em testes (hermético; CA8).
- Não persistir credenciais em recibos/planos (invariante 5).
- Não alegar viabilidade de treinamento sem o hardware correspondente (CA6 sem overclaim).
- Não redistribuir DeepSeekGUI: uso interno de pesquisa/estudo permitido; redistribuição competitiva vedada — registro em THIRD_PARTY_NOTICES, sem parecer jurídico.
- Não alterar política open_science_only nem gates R468/R469/R470 (invariantes 1/3/7).

## Invariantes
1. Workbench é opt-in: sem `DEEPSEEK_GUI_ENABLED`/`DEEPSEEK_GUI_WORKSPACE` válido, `active() == False` (invariante 2 da R471).
2. Workspaces aceitos apenas dentro da allowlist canônica do Core (pesquisa, academic, publications) e resolvidos dentro do repo root; paths sensíveis/fora são rejeitados.
3. Recibo `launch_config()` é determinístico, sem credenciais e carrega licenças (produto PolyForm Perimeter, upstream MIT) e limitação (vedação de redistribuição competitiva).
4. Currículo minimind tem estágios na ordem canônica; plano é determinístico por seed e varia entre seeds.
5. Probe de hardware reporta device (`cuda`/`cpu`/`none`) com nota e limitação; sem GPU, limitação explícita de hardware.
6. Benchmark simulado é determinístico por seed, com curva de pretrain estritamente decrescente e relatório de reprodutibilidade; `hardware_limitation=True` quando device ≠ cuda.
7. Nenhum artefato deste ciclo contém "superhuman"/"verificado"/"Qualis A1"/"superação" (anti-overclaim; invariante 8).
8. THIRD_PARTY_NOTICES.md na raiz registra licenças da R471 (inclui DeepSeekGUI e minimind; CA5).

## Critérios de aceitação
- CA5': `launch_config()` válido para workspace do Core; workbench inativo sem config; licensas em THIRD_PARTY_NOTICES.
- CA6': currículo 64M com estágios canônicos; `plan(seed)` determinístico; probe sem GPU documenta limitação; relatório de reprodutibilidade com seed fixa e `hardware_limitation` marcado sem GPU.
- CA8': 19 testes herméticos, sem rede/credenciais/GUI reais.
- CA9': doctor permanece pass (com warns apenas das CLIs opcionais conhecidas).
- CA10: anti-overclaim nos módulos e relatórios.
- CA11: ciclo R479 registrado no EvolutionRegistry com score e lições; reflexão no MetaBus.

## Plano TDD
RED: 19 testes em `tests/test_r479_m4_m5.py` antes da implementação — 19 falhas na coleta (módulos inexistentes). GREEN: `workbench/deepseek_gui.py` (M4), `model_lab/curriculum.py`, `hardware.py`, `benchmark.py` (M5), `THIRD_PARTY_NOTICES.md`; 1 ajuste de vocabulário ("limitação de hardware"). VERIFY: 19/19; regressões do estágio; suíte completa; doctor; ciclo registrado.