# SPEC-935-R1132 — Camada de cognição do Core (prótese cognitiva auditável)

**Status:** implementação local, sem rede, sem hardware, sem validação clínica
**Data:** 2026-11-10
**Depende de:** R909 (assinatura cognitiva), R110 (doctor), R212 (TaskRuntime), R1050 (gate metacognitivo)
**Origem:** estudo “A casa que ajuda a pensar” (versão PT/EN) e literatura sobre
calibração de confiança, viés de automação, N-of-1, contestabilidade e ética do cuidado.

## 1. Objetivo

Transformar os achados documentais e conceituais do estudo em uma camada
operacional do Core:

1. **Mapa explícito de funções cognitivas** — cada módulo declara qual função
   externaliza, qual falha endereça, qual evidência oferece e qual limite possui.
2. **Auditoria de risco epistêmico** — detecta overclaim, falsa objetividade,
   viés de automação, perda de habilidades e sobrecarga de manutenção.
3. **Regras de parada e padrões humanos** — orçamento de sessão, falhas
   consecutivas, razão manutenção/benefício, horário de silêncio e caminhos de
   saída.
4. **Claims ledger estruturado** — claims com status, evidência, falsificador,
   validação externa e histórico; promoção a “externamente validado” só com
   validação independente.
5. **Contestabilidade e saída** — relatório estrutural de exportação, segunda
   pessoa, documentação, apelação e saída.
6. **Protocolo N-of-1** — validação de pré-registro, desenho ABAB, desfechos,
   cegamento, ética e regras de parada; resumo descritivo, sem inferência causal.
7. **Checks no doctor** — três checks novos: mapa cognitivo, risco epistêmico e
   contestabilidade.

## 2. Não objetivos

- Demonstrar eficácia cognitiva, clínica ou neuroprotetora.
- Executar o protocolo N-of-1 ou recrutar participantes.
- Substituir avaliação médica, neuropsicológica ou ética.
- Generalizar o caso único.
- Declarar que trust score, stake ou token economy são medidas de verdade.
- Adicionar rede, hardware, credenciais ou chamadas externas.

## 3. Requisitos

- **R1.** `core_cognition/cognitive_function_map.py` carrega e valida
  `core_cognition/data/cognitive_function_map.json`.
- **R2.** O mapa cobre as funções obrigatórias: memória, função executiva,
  atenção, verificação, interrupção, reflexão, confiança e orientação.
- **R3.** Cada entrada do mapa tem módulo, mecanismo, falha endereçada,
  evidência e limite; módulos inexistentes ou limites vazios geram achado.
- **R4.** `core_cognition/epistemic_risk.py` detecta, no mínimo: overclaim,
  falsa objetividade, viés de automação, perda de habilidades e sobrecarga de
  manutenção.
- **R5.** `core_cognition/stop_rules.py` decide entre continuar, perguntar,
  adiar e parar; toda decisão inclui explicação, alternativa, contato humano e
  saída.
- **R6.** `core_cognition/claims_ledger.py` valida status, falsificador,
  evidência e validação externa independente; promove um claim a
  `externally_validated` somente com verificador independente e hash.
- **R7.** `core_cognition/contestability.py` audita exportação, segunda pessoa,
  documentação, apelação e saída; retorna score e lacunas.
- **R8.** `core_cognition/n_of_1.py` valida protocolo com pré-registro, ABAB,
  washout, desfechos mínimos, cegamento, ética e regras de parada; resume dados
  descritivamente.
- **R9.** `core_cognition/doctor_checks.py` expõe três checks compatíveis com o
  `doctor`: mapa cognitivo, risco epistêmico e contestabilidade.
- **R10.** `core_cognition/cli.py` oferece comandos `map`, `audit`, `risk`,
  `stop`, `ledger`, `contest` e `n-of-1`.
- **R11.** Nenhum módulo faz rede, subprocesso, hardware ou chamada a LLM.

## 4. Critérios de aceitação

- **CA01.** Mapa com pelo menos 8 funções obrigatórias e 12 entradas totais.
- **CA02.** `audit()` do mapa retorna `pass` no checkout atual.
- **CA03.** Overclaim é detectado quando `status=externally_validated` sem
  validação externa.
- **CA04.** Falsa objetividade é detectada quando trust score alto coexiste com
  zero evidência.
- **CA05.** Viés de automação é detectado quando a saída do agente é aceita sem
  julgamento independente.
- **CA06.** Perda de habilidades é detectada após 5 sessões sem verificação
  manual.
- **CA07.** Regras de parada retornam `stop` para orçamento de sessão excedido e
  `ask` para falhas consecutivas ou razão de manutenção alta.
- **CA08.** Toda decisão de parada contém explicação, alternativa, contato
  humano e saída.
- **CA09.** Claims ledger rejeita status inválido e promoção sem validação
  independente.
- **CA10.** Contestabilidade retorna `pass` no checkout atual e `warn` quando
  `uninstall.sh` ou `LICENSE` estão ausentes.
- **CA11.** Protocolo N-of-1 rejeita ausência de pré-registro, ética ou desenho
  ABAB.
- **CA12.** `tests/test_r1132_core_cognition.py` passa sem rede ou hardware.
- **CA13.** `doctor` inclui os três checks novos e permanece executável em
  menos de 5 segundos no modo estrutural.

## 5. Técnicas adaptadas

| Técnica | Fonte | Onde entra |
|---|---|---|
| Calibração de confiança / reliance apropriada | Lee & See (2004), DOI 10.1518/hfes.46.1.50_30392 | `epistemic_risk.py` |
| Uso, mau uso, desuso e abuso de automação | Parasuraman & Riley (1997), DOI 10.1518/001872097778543886 | `epistemic_risk.py` |
| Interfaces mistas / mixed-initiative | Horvitz (1999), DOI 10.1145/302979.303030 | `stop_rules.py` |
| Custo da interrupção e retomada | Mark et al. (2005), DOI 10.1145/1054972.1055017 | `n_of_1.py`, `stop_rules.py` |
| Tecnologia calma | Weiser & Brown (1997), DOI 10.1007/978-1-4612-0685-9_6 | `stop_rules.py` |
| N-of-1 / ensaio em paciente único | Guyatt et al. (1986), DOI 10.1056/NEJM198604033141406 | `n_of_1.py` |
| SCRIBE 2016 (relato de caso único) | Tate et al. (2016), DOI 10.1016/j.jclinepi.2016.04.006 | `n_of_1.py` |
| Pré-registro | Nosek et al. (2018), DOI 10.1073/pnas.1708274114 | `n_of_1.py` |
| Descarga cognitiva e seus custos | Risko & Gilbert (2016), DOI 10.1016/j.tics.2016.07.002 | `epistemic_risk.py` |
| Contestable AI by design | Alfrink et al. (2022), DOI 10.1007/s11023-022-09611-z | `contestability.py` |
| Supressão de IA para mitigar viés de automação | JAMIA (2023), DOI 10.1093/jamia/ocad118 | `epistemic_risk.py` |
| Humildade epistêmica em IA | 2025, DOI 10.1007/s11019-025-10264-9 | `claims_ledger.py` |
| Ética do cuidado | Tronto (1993) | `stop_rules.py` |
| Injustiça epistêmica | Fricker (2007) | `contestability.py` |
| Moralidade de agentes artificiais | Floridi & Sanders (2004), DOI 10.1023/B:MIND.0000035461.63578.9d | `claims_ledger.py` |
| Design sensível a valores | Friedman et al. (2006) | `contestability.py` |

## 6. Evidência local

- `core_cognition/data/cognitive_function_map.json`
- `core_cognition/epistemic_risk.py`
- `core_cognition/stop_rules.py`
- `core_cognition/claims_ledger.py`
- `core_cognition/contestability.py`
- `core_cognition/n_of_1.py`
- `core_cognition/doctor_checks.py`
- `core_cognition/cli.py`
- `tests/test_r1132_core_cognition.py`
- `docs/CORE_COGNITION.md`
- `docs/CORE_COGNITION_TECHNIQUES.md`

## 7. Limites

Os checks são heurísticas estruturais. Eles não medem eficácia, não validam
clinicamente o sistema e não substituem revisão humana. O protocolo N-of-1 é
um validador de desenho, não um estudo executado. O claims ledger organiza
evidência; não a produz.
