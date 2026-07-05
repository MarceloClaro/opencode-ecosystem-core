# SPEC-041: TorBot OSINT Integration — Governança Ostrom

**Status**: Draft
**Autor**: OpenCode Ecosystem (2026)
**Dependências**: SPEC-036 (CooperativeGovernance), SPEC-038 (TrustEngine)

---

## 1. Problema

O ecossistema não possui ferramenta de coleta de dados em redes anonimizadas (Tor/I2P) para fins de pesquisa acadêmica legítima. TorBot preenche esta lacuna.

## 2. Conceito

Integrar TorBot como MCP `tor-crawler` sob governança Ostrom DP1-DP8:

| DP | Aplicação |
|----|-----------|
| DP1 | Apenas domínios autorizados para pesquisa |
| DP2 | Custo de crawling proporcional ao benefício científico |
| DP3 | Comitê de ética revisa escopo de crawling |
| DP4 | Todo acesso registrado em JSONL auditável |
| DP5 | Violações → suspensão do MCP |
| DP6 | Conflitos de escopo resolvidos por Ostrom score |
| DP7 | Respeito a robots.txt e legislação local |
| DP8 | Crawling local alinhado com política institucional |

## 3. Critérios de Aceitação (6 CTs)

| CT | Descrição |
|----|-----------|
| TB-001 | MCP wrapper TorBot funcional |
| TB-002 | Gate preventivo bloqueia crawling não autorizado |
| TB-003 | JSONL audit trail para cada acesso |
| TB-004 | Ostrom audit: DP1-DP8 compliance |
| TB-005 | Robots.txt respeitado |
| TB-006 | Integração com Scanner Pipeline |
