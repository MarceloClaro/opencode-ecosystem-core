# SPEC-935-R249 — Gêmeo Digital Médico por Simulação

**Status:** proposta implementada em branch  
**Escopo:** exclusivamente casos fictícios, treinamento e pesquisa metodológica  
**Dependências:** Médico Virtual Supremo R205; MiroFish Swarm; agente Reversa

## 1. Objetivo

Toda execução pelo ponto de entrada canônico `analisar_simulacao()` DEVE anexar um gêmeo digital versionado. O gêmeo representa trajetórias contrafactuais de um caso fictício e NÃO representa prognóstico de paciente real.

## 2. Invariantes de segurança

1. `simulation_only` DEVE ser `true`.
2. `clinical_use_allowed`, `prescription_allowed` e `diagnostic_claim_allowed` DEVEM ser `false`.
3. `human_review_required` DEVE ser `true`.
4. Execuções em `professional_cds`, `patient_education` ou `research` NÃO DEVEM receber trajetórias automaticamente.
5. Consenso do enxame NÃO PODE ser descrito como probabilidade clínica.
6. Nenhuma intervenção simulada PODE ser rotulada como tratamento recomendado.
7. Dados insuficientes DEVEM acionar achado adversarial Reversa de alta severidade.

## 3. Contrato do gêmeo

Campos obrigatórios:

- `twin_id` e `run_id`;
- `created_at_utc`;
- `source_hash` SHA-256;
- `model_contract = medical-digital-twin/1.0`;
- `trajectories[]` com passo, estado, intervenção fictícia, score e incerteza;
- `mirofish` com aggregate, consensus, n_agents e interpretação;
- `reversa_review` com decisão, achados e perguntas contrafactuais;
- `safety` com bloqueios explícitos.

## 4. MiroFish

O adapter DEVE aceitar injeção de uma implementação compatível com `SwarmProtocol`, permitindo testes herméticos. Em produção, o padrão é `mirofish.swarm.MiroFishSwarm` com 15 agentes e seed explícita.

MiroFish fornece dispersão e consenso de cenários. Não fornece eficácia terapêutica, causalidade, diagnóstico ou prognóstico validado.

## 5. Reversa

O revisor adversarial DEVE verificar no mínimo:

- completude insuficiente;
- consenso excessivamente confiante;
- incerteza artificialmente baixa;
- extrapolação de simulação para uso clínico;
- perguntas contrafactuais e variáveis omitidas.

## 6. Critérios de aceitação

- CA01: quatro trajetórias por padrão.
- CA02: horizonte permitido entre 2 e 12 passos.
- CA03: hash estável para payload canônico idêntico.
- CA04: testes não iniciam daemon, socket, subprocesso ou modelo real.
- CA05: fake swarm é aceito por injeção de dependência.
- CA06: baixa completude gera `REV-DATA-001` e `block_clinical_use`.
- CA07: anexação automática ocorre apenas no modo `simulation`.
- CA08: saída mantém revisão humana obrigatória.

## 7. Comando de validação

```bash
python3 -m pytest tests/test_medical_digital_twin.py -q --tb=short
```

## 8. Limites

Esta SPEC não autoriza uso com prontuários reais, prescrição, triagem autônoma, escolha de procedimento, cálculo de dose ou substituição de profissional habilitado. Validação clínica externa exige protocolo aprovado, dados governados, avaliação ética e estudo prospectivo independente.
