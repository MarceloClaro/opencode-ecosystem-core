# SPEC-927: Especialização Jurídica por Domínio ("nível PhD por ramo")

```yaml
spec_id: SPEC-927
title: Framework de especialização jurídica por domínio com roteamento, perfis e agentes especialistas
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-921, SPEC-922, SPEC-923, SPEC-924, SPEC-926]
origin: pedido do usuário para evoluir o AuxJuris/MCI em qualquer área jurídica com SDD/TDD obrigatório
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Expandir o subsistema jurídico do ecossistema para operar com **especialização por ramos do direito**, aproximando o comportamento de um “especialista por domínio” em vez de um assistente jurídico genérico.

## 2. Escopo

### 2.1 Ramos cobertos na v1

1. penal
2. trabalhista
3. tributário
4. empresarial
5. administrativo
6. ambiental
7. digital/lgpd

### 2.2 Componentes

| Componente | Função |
|---|---|
| `legal/specializations.py` | Perfis jurídicos por ramo, roteamento e avaliação de cobertura por domínio |
| extensão de `legal/agents.py` | geração de agentes especialistas por ramo |
| testes TDD | validação de perfis, roteamento e construção de agentes |

## 3. Resultado esperado

O sistema passa a:

- identificar o **ramo jurídico predominante** de uma consulta;
- oferecer um **perfil normativo e estratégico** daquele ramo;
- construir um **agente especialista por domínio** com prompt próprio;
- medir a cobertura do corpus em relação ao ramo identificado.

## 4. Critérios de Aceitação (TDD)

1. existem 7 perfis jurídicos especializados registrados
2. `route_legal_domain()` roteia corretamente consultas prototípicas
3. `get_legal_domain_profile()` retorna perfil válido por id
4. `build_domain_specialist_agent()` cria agente especialista com prompt e capacidades corretas
5. `assess_domain_coverage()` retorna score entre 0 e 100
6. um corpus com sinais de LGPD recebe cobertura digital/lgpd maior que um corpus neutro
7. `legal.__init__` exporta o novo framework

## 5. Observação de honestidade epistêmica

Esta spec **não** afirma validação externa de “PhD jurídico em qualquer área”.
Ela implementa um **framework estruturado de especialização por ramo**, passo necessário para aproximar o sistema de comportamento especialista de alto nível.
