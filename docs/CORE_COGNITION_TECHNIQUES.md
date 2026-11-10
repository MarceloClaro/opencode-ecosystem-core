# Técnicas avançadas adaptadas na camada de cognição (R1132)

Este documento registra **quais técnicas** de literatura avançada foram
adaptadas, **onde** entraram e **qual limite** preservam. As técnicas são
heurísticas de design e auditoria; não são intervenções validadas e não
demonstram eficácia cognitiva ou clínica.

## Mapa técnica → módulo

| Técnica | Fonte | Módulo | Como foi adaptada | Limite |
|---|---|---|---|---|
| Calibração de confiança e reliance apropriada | Lee & See (2004), DOI 10.1518/hfes.46.1.50_30392 | `epistemic_risk.py` | Detecta trust score alto sem evidência e trust sem calibração | Heurística; não mede o usuário |
| Uso, mau uso, desuso e abuso de automação | Parasuraman & Riley (1997), DOI 10.1518/001872097778543886 | `epistemic_risk.py` | Sinaliza aceitação de saída sem julgamento independente | Não classifica intenção do usuário |
| Mixed-initiative | Horvitz (1999), DOI 10.1145/302979.303030 | `stop_rules.py` | Decide entre continuar, perguntar, adiar e parar | Não substitui julgamento humano |
| Custo da interrupção e retomada | Mark et al. (2005), DOI 10.1145/1054972.1055017 | `n_of_1.py`, `stop_rules.py` | Desfecho `time_to_resume`; orçamento de sessão e trocas de contexto | Não mede fadiga real |
| Tecnologia calma | Weiser & Brown (1997), DOI 10.1007/978-1-4612-0685-9_6 | `stop_rules.py` | Horário de silêncio e decisão de adiar | Não garante baixa carga perceptual |
| N-of-1 / ensaio em paciente único | Guyatt et al. (1986), DOI 10.1056/NEJM198604033141406 | `n_of_1.py` | Valida ABAB, washout, desfechos repetidos | Não executa o estudo |
| SCRIBE 2016 | Tate et al. (2016), DOI 10.1016/j.jclinepi.2016.04.006 | `n_of_1.py` | Exige pré-registro, ética, cegamento e regras de parada | Não substitui protocolo completo |
| Pré-registro | Nosek et al. (2018), DOI 10.1073/pnas.1708274114 | `n_of_1.py` | `pre_registration` obrigatório | Não garante execução fiel |
| Descarga cognitiva e seus custos | Risko & Gilbert (2016), DOI 10.1016/j.tics.2016.07.002 | `epistemic_risk.py` | Detecta deskilling após 5 sessões sem verificação manual | Limiar heurístico |
| Contestable AI by design | Alfrink et al. (2022), DOI 10.1007/s11023-022-09611-z | `contestability.py` | Cinco portas: exportação, segunda pessoa, documentação, apelação e saída | Proxies estruturais |
| Supressão de IA contra viés de automação | JAMIA (2023), DOI 10.1093/jamia/ocad118 | `epistemic_risk.py` | Recomenda `independent_first_pass` | Não implementa supressão no runtime |
| Humildade epistêmica em IA | 2025, DOI 10.1007/s11019-025-10264-9 | `claims_ledger.py` | Status, falsificador e validação externa | Não elimina viés |
| Ética do cuidado | Tronto (1993) | `stop_rules.py` | Quatro caminhos humanos: explicação, alternativa, contato, saída | Não substitui cuidado profissional |
| Injustiça epistêmica | Fricker (2007) | `contestability.py` | Exige acesso, documentação e saída | Não mede justiça distributiva |
| Moralidade de agentes artificiais | Floridi & Sanders (2004), DOI 10.1023/B:MIND.0000035461.63578.9d | `claims_ledger.py` | Claim tem dono, status e histórico | Não resolve disputa de autoria |
| Design sensível a valores | Friedman et al. (2006) | `contestability.py` | Valores embutidos em portas de saída e apelação | Não substitui avaliação stakeholders |

## Como as técnicas foram traduzidas em código

### 1. Calibração de confiança

A literatura de confiança em automação distingue confiança calibrada de
over-trust e under-trust. No Core, o `epistemic_risk.py` não tenta medir a
confiança do usuário; ele detecta **configurações perigosas**: trust score alto
sem evidência, ausência de calibração e aceitação de saída sem julgamento
independente. A mitigação é uma prática (`calibration_exercise`,
`independent_first_pass`), não um score.

### 2. Viés de automação e supressão de IA

A estratégia de “AI suppression” mostra que esconder a saída do modelo em
alguns casos força o julgamento independente. O Core não esconde a saída por
padrão; ele **sinaliza** quando a saída foi aceita sem julgamento independente
e recomenda uma primeira passagem cega. É uma adaptação conservadora, adequada
a um sistema que não controla a interface do usuário.

### 3. Mixed-initiative e tecnologia calma

O `stop_rules.py` implementa uma versão mínima de mixed-initiative: o sistema
decide entre continuar, perguntar, adiar e parar com base em orçamento,
falhas, manutenção, atenção e horário. A tecnologia calma entra como
`quiet_hours` e como padrão de adiamento; não há promessa de invisibilidade ou
de redução de carga perceptual.

### 4. N-of-1 e SCRIBE

O validador N-of-1 segue a lógica de ensaios em paciente único e a recomendação
SCRIBE: pré-registro, ABAB, washout, desfechos repetidos, cegamento, ética e
regras de parada. O Core valida o desenho; não executa o estudo. O resumo é
descritivo e não deve ser lido como efeito causal.

### 5. Contestabilidade

A literatura de “contestable AI by design” enfatiza intervenção humana ao longo
do ciclo de vida. O `contestability.py` traduz isso em cinco portas
estruturais. O relatório é um proxy: ele verifica a presença de artefatos, não
a qualidade da experiência de contestação.

### 6. Cuidado e injustiça epistêmica

A ética do cuidado entra no `stop_rules.py` como quatro caminhos humanos. A
injustiça epistêmica entra no `contestability.py` como exigência de acesso,
documentação e saída. Nenhum dos dois resolve o problema distributivo; eles
tornam o problema visível e auditável.

## O que não foi adaptado

- Não foi implementada uma intervenção clínica.
- Não foi executado um ensaio N-of-1.
- Não foi adicionada rede, hardware ou LLM.
- Não foi declarada eficácia, prevenção ou generalização.
- Não foi transformado trust score em verdade.

## Como citar esta camada

A camada é uma implementação de design e auditoria. Para uso acadêmico, cite a
spec `SPEC-935-R1132-core-cognition-prosthesis.md` e a versão do checkout. As
referências acima sustentam as técnicas; elas não validam o Core como
intervenção.
