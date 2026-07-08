# SPEC-922: Integração com API Pública Datajud do CNJ

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-08
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Integrar a API pública Datajud do Conselho Nacional de Justiça (CNJ) ao módulo de raciocínio jurídico brasileiro (SPEC-921), permitindo que os motores de subsunção, ponderação, precedentes, interpretação constitucional e scoring de argumentação sejam alimentados com **dados reais de processos judiciais** dos 27 Tribunais de Justiça estaduais.

## 2. Diagnóstico — Estado Atual

O módulo `legal/` (SPEC-921) implementa os motores de raciocínio jurídico, mas opera com dados fornecidos manualmente pelo usuário. Não há conexão com fontes reais de jurisprudência e processos.

A API Datajud (`https://api-publica.datajud.cnj.jus.br`) disponibiliza acesso público a:
- Processos judiciais de todos os 27 TJs estaduais
- Movimentações processuais
- Órgãos julgadores
- Classes, assuntos e sistemas
- Dados estruturados em formato JSON (OpenAPI 3.0)

## 3. Escopo

### 3.1 Componentes

| # | Módulo | Descrição |
|---|---|---|
| 1 | `legal/datajud_client.py` | Cliente HTTP para a API Datajud com suporte a autenticação (API Key), busca por tribunal, paginação e tratamento de erros |
| 2 | `legal/integration.py` | Ponte entre dados reais do Datajud e os motores `legal/syllogism.py`, `legal/precedents.py`, `legal/constitutional.py`, `legal/argumentation.py` e `legal/balancing.py` |

### 3.2 Funcionalidades do Cliente Datajud

- Autenticação via API Key (Authorization header)
- Busca unificada em todos os 27 tribunais ou em tribunal específico
- Extração de jurisprudência (ementas, teses, fundamentos)
- Extração de movimentações processuais
- Conversão de dados da API para os formatos do módulo `legal/` (Precedent, LegalNorm, LegalFact, Principle)
- Cache resiliente com fallback para dados mockados em caso de indisponibilidade

### 3.3 Integração com Motores de Raciocínio

| Motor | Dado do Datajud | Uso |
|---|---|---|
| `LegalSyllogism.subsume()` | Classe + Assunto do processo + Norma aplicável | Verifica subsunção automática |
| `PrincipleBalancing.balance()` | Movimentos + Órgão julgador | Ponderação com dados de decisões reais |
| `PrecedentAnalyzer` | Jurisprudência por tribunal | Alimenta o repositório de precedentes |
| `ConstitutionalInterpretation` | Assuntos + Classe do processo | Contextualiza interpretação |
| `LegalArgumentScorer` | Decisões + Fundamentos | Score com base em decisões reais |

### 3.4 Critérios de Aceitação (TDD)

1. `DatajudClient.search()` retorna resultados estruturados para tribunal específico
2. `DatajudClient.search_all()` retorna resultados consolidados de tribunais disponíveis
3. `DatajudClient.get_process()` retorna detalhes de processo por número e tribunal
4. Conversão de `Processo` Datajud para `Precedent` do módulo `legal/`
5. Conversão de `Processo` Datajud para `LegalFact` do módulo `legal/`
6. Integração: `PrecedentAnalyzer.register_from_datajud()` registra precedentes reais
7. `DatajudClient` funciona em modo offline com dados mockados
8. Tratamento de erro 401 (credencial inválida)
9. Tratamento de erro 429 (rate limit)
10. Cache LRU integrado para evitar requisições repetidas

## 4. Referências

- **Resolução CNJ n. 331/2020** — Institui a Base Nacional de Dados do Poder Judiciário (Datajud)
- **Lei 13.105/2015 (CPC)** — Arts. 926-928 (precedentes)
- **Lei 12.527/2011 (LAI)** — Lei de Acesso à Informação
- **API Datajud**: `https://api-publica.datajud.cnj.jus.br`
